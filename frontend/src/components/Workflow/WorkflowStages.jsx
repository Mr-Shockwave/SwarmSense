// Workflow checklist shown above the chat box once a mission is sent. Owner: Person 4.
import React from "react";

// stageProgress = number of fully-completed stages; the next one is "active".
export default function WorkflowStages({ stages, stageProgress, onNewMission }) {
  return (
    <div className="workflow">
      <div className="workflow-head">
        <h3>Workflow</h3>
        <button className="new-mission-btn" onClick={onNewMission}>
          New mission
        </button>
      </div>
      {stages.map((label, i) => {
        const status = i < stageProgress ? "done" : i === stageProgress ? "active" : "pending";
        return (
          <div key={i} className={`stage ${status}`}>
            <span className="stage-icon">{status === "done" ? "✓" : status === "pending" ? "" : ""}</span>
            <span>{label}</span>
          </div>
        );
      })}
    </div>
  );
}
