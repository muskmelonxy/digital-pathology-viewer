import React from 'react';
import PropTypes from 'prop-types';
import './SlideInfo.css';

function SlideInfo({ slide }) {
  if (!slide) {
    return (
      <div className="slide-info">
        <h2>切片信息</h2>
        <p>请选择一张切片开始浏览。</p>
      </div>
    );
  }

  const metadataEntries = Object.entries(slide.metadata || {});

  return (
    <div className="slide-info">
      <h2>{slide.title}</h2>
      {slide.description && <p className="slide-info__description">{slide.description}</p>}
      <div className="slide-info__meta">
        <div>
          <span className="slide-info__label">文件路径：</span>
          <span className="slide-info__value">{slide.file_path}</span>
        </div>
        <div>
          <span className="slide-info__label">上传时间：</span>
          <span className="slide-info__value">{new Date(slide.created_at).toLocaleString()}</span>
        </div>
      </div>
      {metadataEntries.length > 0 && (
        <div className="slide-info__extra">
          <h3>元数据</h3>
          <ul>
            {metadataEntries.map(([key, value]) => (
              <li key={key}>
                <span className="slide-info__label">{key}：</span>
                <span className="slide-info__value">
                  {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

SlideInfo.propTypes = {
  slide: PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
    description: PropTypes.string,
    file_path: PropTypes.string.isRequired,
    created_at: PropTypes.string.isRequired,
    metadata: PropTypes.object,
  }),
};

SlideInfo.defaultProps = {
  slide: null,
};

export default SlideInfo;
