// Toast ping shown on the mission screen when a new finding arrives. Owner: Person 4.
import React, { useEffect } from "react";

export default function FindingPing({ finding, onView, onDismiss }) {
  // Auto-dismiss after a while
  useEffect(() => {
    const t = setTimeout(onDismiss, 9000);
    return () => clearTimeout(t);
  }, [finding, onDismiss]);

  if (!finding) return null;

  return (
    <div className="finding-ping" onClick={onView}>
      {finding.photo && <img src={finding.photo} alt={finding.label} className="finding-ping-img" />}
      <div className="finding-ping-body">
        <span className="finding-ping-title">New finding · {finding.label}</span>
        <span className="finding-ping-sub">
          {finding.rover_id}
          {finding.coord?.x != null && ` · (${finding.coord.x}, ${finding.coord.y})`}
        </span>
        <span className="finding-ping-cta">View in Findings →</span>
      </div>
      <button
        className="finding-ping-x"
        onClick={(e) => { e.stopPropagation(); onDismiss(); }}
        title="Dismiss"
      >×</button>
    </div>
  );
}
