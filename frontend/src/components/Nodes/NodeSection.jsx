// Expandable per-robot section streaming captured frames from Redis. Owner: Person 4.
import React from "react";

export default function NodeSection({ node, frames = [], open, running, onToggle }) {
  const live = running && frames.length > 0;
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
          {frames.length === 0 ? (
            <div className="frames-empty">
              {running ? "Waiting for first capture…" : "No frames yet — start a mission."}
            </div>
          ) : (
            // Newest first; each new frame fades in one-by-one.
            frames.map((f, i) => (
              <div className="frame" key={`${f.ts}-${i}`}>
                <img src={f.photo} alt={f.caption || "capture"} />
                <div className="frame-meta">
                  <span className="cap">{f.caption || "Captured frame"}</span>
                  {f.coord && (f.coord.x != null) && (
                    <span className="sub">
                      coord ({f.coord.x}, {f.coord.y})
                    </span>
                  )}
                  {f.ts && (
                    <span className="sub">{new Date(f.ts * 1000).toLocaleTimeString()}</span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </section>
  );
}
