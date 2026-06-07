// One finding tab/card. Owner: Person 4.
import React, { useState } from "react";

export default function FindingCard({ finding }) {
  const [expanded, setExpanded] = useState(false);
  const f = finding;

  return (
    <div className={`finding-card ${expanded ? "expanded" : ""}`} onClick={() => setExpanded((e) => !e)}>
      <div className="finding-img-wrap">
        {f.photo ? (
          <img src={f.photo} alt={f.label} className="finding-img" />
        ) : (
          <div className="finding-img placeholder">no image</div>
        )}
        {f.status && f.status !== "new" && (
          <span className={`finding-status-badge ${f.status}`}>{f.status}</span>
        )}
      </div>

      <div className="finding-body">
        <div className="finding-title-row">
          <h3 className="finding-label">{f.label}</h3>
          {typeof f.confidence === "number" && (
            <span className="finding-conf">{Math.round(f.confidence * 100)}%</span>
          )}
        </div>

        <div className="finding-sub">
          {f.rover_id && <span className="finding-tag">{f.rover_id}</span>}
          {f.coord?.x != null && <span>({f.coord.x}, {f.coord.y})</span>}
          {f.ts && <span>{new Date(f.ts * 1000).toLocaleTimeString()}</span>}
        </div>

        {f.summary && <p className="finding-summary">{f.summary}</p>}

        {expanded && (
          <>
            {f.description && <p className="finding-desc">{f.description}</p>}
            {f.criteria && (
              <p className="finding-criteria">matched: <em>{f.criteria}</em></p>
            )}
          </>
        )}
        {!expanded && (f.description || f.criteria) && (
          <span className="finding-more">click to expand ▾</span>
        )}
      </div>
    </div>
  );
}
