import React from 'react';
import PropTypes from 'prop-types';
import './SlideList.css';

function SlideList({ slides, selectedId, onSelect }) {
  if (!slides.length) {
    return <div className="slide-list">暂无切片</div>;
  }

  return (
    <div className="slide-list">
      {slides.map((slide) => {
        const isActive = slide.id === selectedId;
        return (
          <button
            key={slide.id}
            type="button"
            className={`slide-list__item ${isActive ? 'slide-list__item--active' : ''}`}
            onClick={() => onSelect(slide)}
          >
            <span className="slide-list__title">{slide.title}</span>
            {slide.description && (
              <span className="slide-list__description">{slide.description}</span>
            )}
          </button>
        );
      })}
    </div>
  );
}

SlideList.propTypes = {
  slides: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      title: PropTypes.string.isRequired,
      description: PropTypes.string,
    })
  ).isRequired,
  selectedId: PropTypes.number,
  onSelect: PropTypes.func.isRequired,
};

SlideList.defaultProps = {
  selectedId: undefined,
};

export default SlideList;
