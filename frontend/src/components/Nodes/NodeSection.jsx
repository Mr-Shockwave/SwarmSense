import React, { useState, useEffect } from "react";

export default function NodeSection({ node, frames = [], open, running, onToggle }) {
  const live = running && frames.length > 0;

  // null = tracking latest. Otherwise, the ts of the frame we're pinned to.
  const [pinnedTs, setPinnedTs] = useState(null);

  const frame = pinnedTs == null
    ? frames[0]
    : frames.find((f) => f.ts === pinnedTs) ?? frames[0];

  const currentIdx = frame ? frames.indexOf(frame) : 0;

  const goOlder = () => {
    const next = frames[currentIdx + 1];
    if (next) setPinnedTs(next.ts);
  };

  const goNewer = () => {
    if (currentIdx === 1) {
      // one step from latest — just resume tracking
      setPinnedTs(null);
    } else {
      const next = frames[currentIdx - 1];
      if (next) setPinnedTs(next.ts);
    }
  };

  const resume = () => setPinnedTs(null);

  const tracking = pinnedTs == null;
  const atOldest = currentIdx >= frames.length - 1;
  const atLatest = currentIdx === 0;

  return (
    <section className={`node-section ${open ? "open" : ""} ${live ? "live" : ""}`}>
      <button className="node-header" onClick={() => onToggle(node.id)}>
        <span className="caret">▶</span>
        <span className="live-dot" />
        <span className="node-tag">{node.label}</span>
        <span className="node-name">{node.name}</span>
        <span className="count">{frames.length} frame{frames.length === 1 ? "" : "s"}</span>
      </button>

      {open && (
        <div className="node-body">
          {!frame ? (
            <div className="frames-empty">
              {running ? "Waiting for first capture…" : "No frames yet — start a mission."}
            </div>
          ) : (
            <div className="frame-viewer">
              <div className="frame-img-wrap">
                <img key={frame.ts} src={frame.photo} alt={frame.caption || "capture"} className="frame-img" />

                {frames.length > 1 && (
                  <div className="frame-arrows">
                    <button className="frame-arrow" onClick={goOlder} disabled={atOldest} title="Older">‹</button>
                    <button className="frame-arrow" onClick={goNewer} disabled={atLatest} title="Newer">›</button>
                  </div>
                )}
              </div>

              <div className="frame-footer">
                <div className="frame-meta">
                  <span className="cap">{frame.caption || "Captured frame"}</span>
                  <span className="sub">
                    {frame.coord?.x != null && `(${frame.coord.x}, ${frame.coord.y}) · `}
                    {frame.ts && new Date(frame.ts * 1000).toLocaleTimeString()}
                  </span>
                </div>

                <div className="frame-controls">
                  {tracking ? (
                    <span className="slideshow-status">● live</span>
                  ) : (
                    <button className="resume-btn" onClick={resume}>▶ Resume</button>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
