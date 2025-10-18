import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import OpenSeadragon from 'openseadragon';
import { API_BASE_URL } from '../api/slides';
import './SlideViewer.css';
import 'openseadragon/build/openseadragon/openseadragon.css';

const NAV_IMAGES = {
  zoomIn: {
    REST: 'https://openseadragon.github.io/openseadragon/images/zoom-in-rest.png',
    GROUP: 'https://openseadragon.github.io/openseadragon/images/zoom-in-pressed.png',
    HOVER: 'https://openseadragon.github.io/openseadragon/images/zoom-in-hover.png',
    DOWN: 'https://openseadragon.github.io/openseadragon/images/zoom-in-pressed.png',
  },
  zoomOut: {
    REST: 'https://openseadragon.github.io/openseadragon/images/zoom-out-rest.png',
    GROUP: 'https://openseadragon.github.io/openseadragon/images/zoom-out-pressed.png',
    HOVER: 'https://openseadragon.github.io/openseadragon/images/zoom-out-hover.png',
    DOWN: 'https://openseadragon.github.io/openseadragon/images/zoom-out-pressed.png',
  },
  home: {
    REST: 'https://openseadragon.github.io/openseadragon/images/home-rest.png',
    GROUP: 'https://openseadragon.github.io/openseadragon/images/home-pressed.png',
    HOVER: 'https://openseadragon.github.io/openseadragon/images/home-hover.png',
    DOWN: 'https://openseadragon.github.io/openseadragon/images/home-pressed.png',
  },
  fullpage: {
    REST: 'https://openseadragon.github.io/openseadragon/images/fullpage-rest.png',
    GROUP: 'https://openseadragon.github.io/openseadragon/images/fullpage-pressed.png',
    HOVER: 'https://openseadragon.github.io/openseadragon/images/fullpage-hover.png',
    DOWN: 'https://openseadragon.github.io/openseadragon/images/fullpage-pressed.png',
  },
  previous: {
    REST: 'https://openseadragon.github.io/openseadragon/images/previous-rest.png',
    GROUP: 'https://openseadragon.github.io/openseadragon/images/previous-pressed.png',
    HOVER: 'https://openseadragon.github.io/openseadragon/images/previous-hover.png',
    DOWN: 'https://openseadragon.github.io/openseadragon/images/previous-pressed.png',
  },
  next: {
    REST: 'https://openseadragon.github.io/openseadragon/images/next-rest.png',
    GROUP: 'https://openseadragon.github.io/openseadragon/images/next-pressed.png',
    HOVER: 'https://openseadragon.github.io/openseadragon/images/next-hover.png',
    DOWN: 'https://openseadragon.github.io/openseadragon/images/next-pressed.png',
  },
};

function SlideViewer({ slideId, dzi }) {
  const containerRef = useRef(null);
  const viewerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) {
      return undefined;
    }

    viewerRef.current = OpenSeadragon({
      element: containerRef.current,
      prefixUrl: 'https://openseadragon.github.io/openseadragon/images/',
      showRotationControl: true,
      showNavigator: true,
      animationTime: 0.9,
      blendTime: 0.5,
      navImages: NAV_IMAGES,
      gestureSettingsMouse: {
        clickToZoom: true,
        dblClickToZoom: true,
        dragToPan: true,
        scrollToZoom: true,
      },
      gestureSettingsTouch: {
        pinchToZoom: true,
        dblTapToZoom: true,
        dragToPan: true,
      },
    });

    return () => {
      if (viewerRef.current) {
        viewerRef.current.destroy();
        viewerRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!viewerRef.current) {
      return;
    }

    if (!dzi || !slideId) {
      viewerRef.current.close();
      return;
    }

    viewerRef.current.open({
      width: dzi.width,
      height: dzi.height,
      tileWidth: dzi.tile_size,
      tileHeight: dzi.tile_size,
      tileOverlap: dzi.tile_overlap,
      minLevel: dzi.min_level ?? 0,
      maxLevel: dzi.max_level,
      getTileUrl: (level, x, y) =>
        `${API_BASE_URL}/slides/${slideId}/tiles/${level}/${x}/${y}`,
    });
  }, [slideId, dzi]);

  return <div className="slide-viewer" ref={containerRef} />;
}

SlideViewer.propTypes = {
  slideId: PropTypes.number,
  dzi: PropTypes.shape({
    width: PropTypes.number,
    height: PropTypes.number,
    tile_size: PropTypes.number,
    tile_overlap: PropTypes.number,
    min_level: PropTypes.number,
    max_level: PropTypes.number,
  }),
};

SlideViewer.defaultProps = {
  slideId: undefined,
  dzi: null,
};

export default SlideViewer;
