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
    if (!viewerRef.current) {
      return;
    }

    if (!slideId) {
      viewerRef.current.close();
      return;
    }

    // OpenSeadragon can directly use the DZI XML file
    const dziUrl = `${API_BASE_URL}/slides/${slideId}/dzi`;
    console.log('初始化 OpenSeadragon，切片ID:', slideId);
    console.log('DZI URL:', dziUrl);
    
    // 添加事件监听器用于调试
    viewerRef.current.addHandler('open', () => {
      console.log('✓ OpenSeadragon 加载成功');
    });
    
    viewerRef.current.addHandler('open-failed', (event) => {
      console.error('✗ OpenSeadragon 加载失败:', event);
    });
    
    viewerRef.current.addHandler('tile-loaded', () => {
      console.log('瓦片加载成功');
    });
    
    viewerRef.current.addHandler('tile-load-failed', (event) => {
      console.error('瓦片加载失败:', event);
    });
    
    viewerRef.current.open(dziUrl);
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
