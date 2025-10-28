"""KFB -> pyramidal TIFF conversion utilities."""

from __future__ import annotations

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

try:
    import pyvips  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    pyvips = None


DEFAULT_TILE_SIZE = 256
DEFAULT_OVERLAP = 0

logger = logging.getLogger(__name__)


def ensure_input(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    if path.suffix.lower() not in {".kfb", ".svs", ".tif", ".tiff"}:
        raise ValueError("Only KFB/SVS/TIFF files are supported as input")
    return path


def ensure_output_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def convert_with_pyvips(input_path: Path, output_path: Path) -> Path:
    if pyvips is None:
        raise RuntimeError("pyvips is not available")

    image = pyvips.Image.new_from_file(str(input_path), access="sequential")
    image.tiffsave(
        str(output_path),
        tile=True,
        pyramid=True,
        compression="jpeg",
        Q=90,
        tile_width=DEFAULT_TILE_SIZE,
        tile_height=DEFAULT_TILE_SIZE,
    )
    return output_path


def convert_with_vips_cli(input_path: Path, output_path: Path) -> Path:
    vips_bin = shutil.which("vips")
    if not vips_bin:
        raise RuntimeError("libvips CLI (vips) is not available")

    command = [
        vips_bin,
        "tiffsave",
        str(input_path),
        str(output_path),
        "--tile",
        "--pyramid",
        "--compression",
        "jpeg",
        "--Q",
        "90",
        "--tile-width",
        str(DEFAULT_TILE_SIZE),
        "--tile-height",
        str(DEFAULT_TILE_SIZE),
    ]
    subprocess.check_call(command)
    return output_path


def convert_kfb(input_path: Path, output_dir: Path) -> Path:
    output_dir = ensure_output_dir(output_dir)
    input_path = ensure_input(input_path)
    output_path = output_dir / f"{input_path.stem}.tif"

    try:
        if pyvips is not None:
            try:
                return convert_with_pyvips(input_path, output_path)
            except Exception as exc:  # pragma: no cover - 容错处理
                logger.warning("pyvips 转换失败，尝试使用 vips CLI：%s", exc)
        return convert_with_vips_cli(input_path, output_path)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"libvips conversion command failed: {exc}") from exc


def generate_dzi_bundle(slide_path: Path, output_dir: Path) -> Path:
    if pyvips is None:
        raise RuntimeError("pyvips is required for DZI generation")

    output_dir = ensure_output_dir(output_dir)
    dzi_base = output_dir / slide_path.stem
    pyvips.Image.new_from_file(str(slide_path), access="sequential").dzsave(
        str(dzi_base),
        suffix=".jpeg",
        overlap=DEFAULT_OVERLAP,
        tile_size=DEFAULT_TILE_SIZE,
    )
    return dzi_base.with_suffix(".dzi")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="将 KFB 切片转换为支持 DeepZoom 的金字塔 TIFF 文件"
    )
    parser.add_argument("input", type=Path, help="待转换的 KFB/SVS 文件路径")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("./converted"),
        help="输出目录（默认: ./converted）",
    )
    parser.add_argument(
        "--dzi",
        action="store_true",
        help="同时生成 DeepZoom (DZI) 切片，用于离线查看",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    args = parse_args(argv)

    try:
        tiff_path = convert_kfb(args.input, args.output_dir)
        print(f"✅ 生成金字塔 TIFF: {tiff_path}")

        if args.dzi:
            dzi_path = generate_dzi_bundle(tiff_path, args.output_dir)
            print(f"✅ 生成 DeepZoom 切片: {dzi_path}")

    except Exception as exc:  # pragma: no cover - CLI error handling
        print(f"转换失败: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
