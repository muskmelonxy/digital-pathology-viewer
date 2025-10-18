import React, { useEffect, useMemo, useState } from 'react';
import SlideList from './components/SlideList';
import SlideViewer from './components/SlideViewer';
import SlideInfo from './components/SlideInfo';
import { fetchSlides, fetchSlideDzi } from './api/slides';
import './App.css';

function App() {
  const [slides, setSlides] = useState([]);
  const [selectedId, setSelectedId] = useState();
  const [dzi, setDzi] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState();

  useEffect(() => {
    async function loadSlides() {
      try {
        const data = await fetchSlides();
        setSlides(data);
        if (data.length) {
          setSelectedId(data[0].id);
        }
      } catch (err) {
        setError(err.message || '加载切片失败');
      } finally {
        setLoading(false);
      }
    }

    loadSlides();
  }, []);

  const selectedSlide = useMemo(
    () => slides.find((slide) => slide.id === selectedId),
    [slides, selectedId]
  );

  useEffect(() => {
    async function loadDzi(id) {
      if (!id) {
        setDzi(null);
        return;
      }

      try {
        const data = await fetchSlideDzi(id);
        setDzi(data);
        setError(undefined);
      } catch (err) {
        setError(err.message || '加载 DZI 信息失败');
        setDzi(null);
      }
    }

    loadDzi(selectedId);
  }, [selectedId]);

  const handleSelect = (slide) => {
    setSelectedId(slide.id);
    setError(undefined);
  };

  return (
    <div className="app">
      <header className="app__header">
        <h1>数字病理切片在线浏览系统</h1>
        <p>支持 KFB 转换、元数据管理与在线深度缩放浏览</p>
      </header>

      <main className="app__content">
        <aside className="app__sidebar">
          {loading ? <div className="app__status">加载中...</div> : null}
          {error ? <div className="app__error">{error}</div> : null}
          <SlideList slides={slides} selectedId={selectedId} onSelect={handleSelect} />
        </aside>

        <section className="app__viewer-section">
          <SlideViewer slideId={selectedId} dzi={dzi} />
          <SlideInfo slide={selectedSlide} />
        </section>
      </main>
    </div>
  );
}

export default App;
