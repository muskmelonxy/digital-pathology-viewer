import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import OpenSeadragon from 'openseadragon';
import { API_BASE_URL } from '../api/slides';
import './SlideViewer.css';
import 'openseadragon/build/openseadragon/openseadragon.css';

function SlideViewer({ slideId }) {
  const containerRef = useRef(null);
  const viewerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) {
      return undefined;
    }

    viewerRef.current = OpenSeadragon({
      element: containerRef.current,
      prefixUrl: '//openseadragon.github.io/openseadragon/images/',
      showRotationControl: true,
      showNavigator: true,
      animationTime: 0.9,
      blendTime: 0.5,
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
    const viewer = viewerRef.current;

    if (!viewer) {
      return undefined;
    }

    if (!slideId) {
      viewer.close();
      return undefined;
    }

    const dziUrl = `${API_BASE_URL}/slides/${slideId}/dzi`;
    const handleOpen = () => {
      console.log('✓ OpenSeadragon 加载成功');
    };
    const handleOpenFailed = (event) => {
      console.error('✗ OpenSeadragon 加载失败:', event);
    };

    console.log('初始化 OpenSeadragon，切片ID:', slideId);
    console.log('DZI URL:', dziUrl);

    viewer.addHandler('open', handleOpen);
    viewer.addHandler('open-failed', handleOpenFailed);
    viewer.open(dziUrl);

    return () => {
      viewer.removeHandler('open', handleOpen);
      viewer.removeHandler('open-failed', handleOpenFailed);
    };
  }, [slideId]);

  return <div className="slide-viewer" ref={containerRef} />;
}

SlideViewer.propTypes = {
  slideId: PropTypes.number,
};

SlideViewer.defaultProps = {
  slideId: undefined,
};

export default SlideViewer;
