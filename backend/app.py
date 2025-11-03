import io
import logging
from pathlib import Path
from typing import Dict, Tuple

from flask import Flask, abort, jsonify, request, send_file, Response
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session, sessionmaker

from config import Config
from models import Slide, engine

try:
    from openslide import OpenSlide
    from openslide.deepzoom import DeepZoomGenerator
except ImportError:  # pragma: no cover - handled gracefully at runtime
    OpenSlide = None
    DeepZoomGenerator = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
app.config["JSON_AS_ASCII"] = False

CORS(
    app,
    resources={r"/api/*": {"origins": Config.ALLOWED_ORIGINS}},
    supports_credentials=True,
)

SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
)


@app.teardown_appcontext
def remove_session(exception=None):  # pragma: no cover - side effect only
    SessionLocal.remove()


def ensure_openslide_available():
    if OpenSlide is None or DeepZoomGenerator is None:
        abort(503, description="OpenSlide libraries are not available in this environment")


def resolve_slide_storage() -> Path:
    return Config.ensure_storage_path()


def open_slide_resources(slide: Slide) -> Tuple["OpenSlide", "DeepZoomGenerator"]:
    ensure_openslide_available()
    storage = resolve_slide_storage()
    slide_path = storage / slide.file_path
    if not slide_path.exists():
        abort(404, description="指定的切片文件不存在")

    slide_obj = OpenSlide(str(slide_path))
    generator = DeepZoomGenerator(
        slide_obj,
        tile_size=Config.DEEPZOOM_TILE_SIZE,
        overlap=Config.DEEPZOOM_OVERLAP,
        limit_bounds=False,
    )
    return slide_obj, generator


@app.route("/api/slides", methods=["GET"])
def list_slides():
    session = SessionLocal()
    try:
        slides = session.query(Slide).order_by(Slide.created_at.desc()).all()
        return jsonify([slide.to_dict() for slide in slides])
    except SQLAlchemyError as exc:  # pragma: no cover - runtime safeguard
        logger.exception("Failed to list slides")
        abort(500, description=str(exc))
    finally:
        session.close()


@app.route("/api/slides/<int:slide_id>", methods=["GET"])
def get_slide(slide_id: int):
    session = SessionLocal()
    try:
        slide = session.get(Slide, slide_id)
        if not slide:
            abort(404, description="切片不存在")
        return jsonify(slide.to_dict())
    except SQLAlchemyError as exc:  # pragma: no cover
        logger.exception("Failed to fetch slide %s", slide_id)
        abort(500, description=str(exc))
    finally:
        session.close()


@app.route("/api/slides", methods=["POST"])
def create_slide():
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    file_path = (payload.get("file_path") or "").strip()

    if not title or not file_path:
        abort(400, description="title 和 file_path 为必填字段")

    description = (payload.get("description") or "").strip() or None
    metadata = payload.get("metadata") or {}

    if not isinstance(metadata, dict):
        abort(400, description="metadata 必须是对象")

    session = SessionLocal()
    try:
        slide = Slide(
            title=title,
            description=description,
            file_path=file_path,
            slide_metadata=metadata,
        )
        session.add(slide)
        session.commit()
        session.refresh(slide)
        return jsonify(slide.to_dict()), 201
    except SQLAlchemyError as exc:  # pragma: no cover
        session.rollback()
        logger.exception("Failed to create slide")
        abort(500, description=str(exc))
    finally:
        session.close()


@app.route("/api/slides/<int:slide_id>/dzi", methods=["GET"])
def get_slide_dzi(slide_id: int):
    session = SessionLocal()
    try:
        slide = session.get(Slide, slide_id)
        if not slide:
            abort(404, description="切片不存在")
    finally:
        session.close()

    slide_obj, generator = open_slide_resources(slide)
    try:
        width, height = slide_obj.dimensions
        max_level = generator.level_count - 1
        
        # Generate DZI XML format for OpenSeadragon
        dzi_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Image xmlns="http://schemas.microsoft.com/deepzoom/2008"
       Format="jpeg"
       Overlap="{Config.DEEPZOOM_OVERLAP}"
       TileSize="{Config.DEEPZOOM_TILE_SIZE}">
  <Size Width="{width}" Height="{height}"/>
</Image>'''
        
        response = Response(dzi_xml, mimetype='application/xml')
        response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
        return response
    finally:
        slide_obj.close()


@app.route(
    "/api/slides/<int:slide_id>/tiles/<int:level>/<int:col>/<int:row>.jpeg",
    methods=["GET"],
)
def get_slide_tile_jpeg(slide_id: int, level: int, col: int, row: int):
    return _get_slide_tile(slide_id, level, col, row)


@app.route(
    "/api/slides/<int:slide_id>/tiles/<int:level>/<int:col>/<int:row>",
    methods=["GET"],
)
def get_slide_tile(slide_id: int, level: int, col: int, row: int):
    return _get_slide_tile(slide_id, level, col, row)


def _get_slide_tile(slide_id: int, level: int, col: int, row: int):
    session = SessionLocal()
    try:
        slide = session.get(Slide, slide_id)
        if not slide:
            abort(404, description="切片不存在")
    finally:
        session.close()

    slide_obj, generator = open_slide_resources(slide)
    try:
        max_level = generator.level_count - 1
        if level < 0 or level > max_level:
            abort(404, description="请求的层级不存在")

        dzi_level = max_level - level
        tiles_x, tiles_y = generator.level_tiles[dzi_level]
        if col < 0 or col >= tiles_x or row < 0 or row >= tiles_y:
            abort(404, description="请求的瓦片超出范围")

        tile = generator.get_tile(dzi_level, (col, row))
        # Convert to RGB to ensure JPEG compatibility
        if tile.mode in ('RGBA', 'LA', 'P'):
            tile = tile.convert('RGB')
        
        buffer = io.BytesIO()
        tile.save(buffer, format="JPEG", quality=90, optimize=True)
        buffer.seek(0)
        
        response = send_file(buffer, mimetype="image/jpeg")
        response.headers['Cache-Control'] = 'public, max-age=31536000'  # Cache for 1 year
        # Add ETag for better caching
        response.headers['ETag'] = f'"{slide_id}-{level}-{col}-{row}"'
        return response
    finally:
        slide_obj.close()


@app.route("/api/slides/<int:slide_id>/info", methods=["GET"])
def get_slide_info(slide_id: int):
    """Enhanced slide information endpoint with technical details."""
    session = SessionLocal()
    try:
        slide = session.get(Slide, slide_id)
        if not slide:
            abort(404, description="切片不存在")
    finally:
        session.close()

    slide_obj, generator = open_slide_resources(slide)
    try:
        width, height = slide_obj.dimensions
        max_level = generator.level_count - 1
        
        # Get level dimensions for all pyramid levels
        level_dimensions = []
        for level in range(generator.level_count):
            level_dims = generator.level_dimensions[level]
            level_dimensions.append(list(level_dims))
        
        # Get slide properties
        try:
            properties = dict(slide_obj.properties)
        except Exception:
            properties = {}
        
        info = {
            "id": slide.id,
            "title": slide.title,
            "description": slide.description,
            "file_path": slide.file_path,
            "dimensions": [width, height],
            "level_count": generator.level_count,
            "level_dimensions": level_dimensions,
            "tile_size": Config.DEEPZOOM_TILE_SIZE,
            "overlap": Config.DEEPZOOM_OVERLAP,
            "format": "jpeg",
            "properties": properties,
            "metadata": slide.slide_metadata or {},
            "created_at": slide.created_at.isoformat() if slide.created_at else None,
        }
        
        response = jsonify(info)
        response.headers['Cache-Control'] = 'public, max-age=300'  # Cache for 5 minutes
        return response
    finally:
        slide_obj.close()


@app.route("/api/health", methods=["GET"])
def healthcheck():
    return jsonify({"status": "ok"})


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=5000)
