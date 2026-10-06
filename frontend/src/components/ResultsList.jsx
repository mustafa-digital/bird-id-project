// src/components/ResultsList.jsx
import { useEffect, useMemo, useRef, useState } from "react";

const titleCase = (s) => s.replace(/\b\w/g, (c) => c.toUpperCase());

function ResultsList({ results }) {
  // Hooks must run on every render, so they all come before any early return.
  const trackRef = useRef(null);
  const [index, setIndex] = useState(0);

  // One slide per predicted species, highest confidence first within each result.
  const slides = useMemo(
    () =>
      results.flatMap((r) =>
        [...r.predictions]
          .sort((a, b) => b.confidence - a.confidence)
          .map((p) => ({
            key: `${r.id}-${p.species_code}`,
            timestamp: r.timestamp,
            ...p,
          }))
      ),
    [results]
  );

  // If the list changes (new results arrive), jump back to the first slide.
  useEffect(() => {
    const track = trackRef.current;
    if (track) track.scrollTo({ left: 0, behavior: "auto" });
    setIndex(0);
  }, [results]);

  // Keep the current slide aligned if the container is resized.
  useEffect(() => {
    const track = trackRef.current;
    if (!track) return;
    const onResize = () =>
      track.scrollTo({ left: track.clientWidth * index, behavior: "auto" });
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, [index]);

  if (slides.length === 0) {
    return <p className="empty-state">No species detected</p>;
  }

  const lastIndex = slides.length - 1;

  const goToIndex = (i) => {
    const track = trackRef.current;
    if (!track) return;
    const clamped = Math.max(0, Math.min(i, lastIndex));
    track.scrollTo({ left: track.clientWidth * clamped, behavior: "smooth" });
    setIndex(clamped);
  };

  const handleScroll = () => {
    const track = trackRef.current;
    if (!track) return;
    const newIndex = Math.round(track.scrollLeft / (track.clientWidth || 1));
    if (newIndex !== index) setIndex(newIndex);
  };

  const handleKeyDown = (e) => {
    if (e.key === "ArrowLeft") goToIndex(index - 1);
    if (e.key === "ArrowRight") goToIndex(index + 1);
  };

  const containerStyle = {
    position: "relative",
    width: "100%",
    overflow: "hidden",
  };

  const trackStyle = {
    display: "flex",
    width: "100%",
    overflowX: "auto",
    scrollSnapType: "x mandatory",
    scrollBehavior: "smooth",
    WebkitOverflowScrolling: "touch",
    scrollbarWidth: "none",
    msOverflowStyle: "none",
  };

  const slideStyle = {
    flex: "0 0 100%",
    width: "100%",
    scrollSnapAlign: "start",
    boxSizing: "border-box",
    padding: "0 8px",
  };

  const cardStyle = {
    width: "100%",
    maxWidth: 448,
    margin: "0 auto",
  };

  const buttonBaseStyle = {
    position: "absolute",
    top: "50%",
    transform: "translateY(-50%)",
    zIndex: 10,
    border: "none",
    borderRadius: "9999px",
    backgroundColor: "rgba(255,255,255,0.9)",
    padding: "0.25rem 0.75rem",
    fontSize: "1.5rem",
    color: "#374151",
    boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
    cursor: "pointer",
  };

  const prevButtonStyle = {
    ...buttonBaseStyle,
    left: "8px",
    opacity: index === 0 ? 0.3 : 1,
    pointerEvents: index === 0 ? "none" : "auto",
  };

  const nextButtonStyle = {
    ...buttonBaseStyle,
    right: "8px",
    opacity: index === lastIndex ? 0.3 : 1,
    pointerEvents: index === lastIndex ? "none" : "auto",
  };

  return (
    <div
      style={containerStyle}
      tabIndex={0}
      onKeyDown={handleKeyDown}
      role="region"
      aria-roledescription="carousel"
      aria-label="Detected species"
    >
      <button
        type="button"
        aria-label="Previous"
        onClick={() => goToIndex(index - 1)}
        style={prevButtonStyle}
      >
        ‹
      </button>

      <div ref={trackRef} onScroll={handleScroll} style={trackStyle}>
        {slides.map((s, i) => (
          <div
            key={s.key}
            style={slideStyle}
            role="group"
            aria-roledescription="slide"
            aria-label={`${i + 1} of ${slides.length}`}
          >
            <div
              style={cardStyle}
              className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
            >
              <div className="mb-2 flex items-center justify-center">
                <span className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  {s.timestamp.toLocaleTimeString()}
                </span>
              </div>

              <div className="flex w-full flex-col items-center gap-2">
                <span className="text-center text-sm text-gray-800">
                  {titleCase(s.species_name)} — {(s.confidence * 100).toFixed(1)}%
                </span>
                <img
                  src={`/src/assets/birds/${s.species_code}.jpg`}
                  alt={`Image of ${s.species_name}`}
                  className="h-80 w-80 max-w-full rounded-md object-cover"
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      <button
        type="button"
        aria-label="Next"
        onClick={() => goToIndex(index + 1)}
        style={nextButtonStyle}
      >
        ›
      </button>

      {/* Position indicator */}
      <div className="mt-3 flex items-center justify-center gap-2">
        {slides.length <= 10 ? (
          slides.map((s, i) => (
            <button
              key={s.key}
              type="button"
              aria-label={`Go to result ${i + 1}`}
              aria-current={i === index}
              onClick={() => goToIndex(i)}
              className={`h-2 w-2 rounded-full ${
                i === index ? "bg-gray-700" : "bg-gray-300"
              }`}
            />
          ))
        ) : (
          <span className="text-xs text-gray-500">
            {index + 1} / {slides.length}
          </span>
        )}
      </div>
    </div>
  );
}

export default ResultsList;