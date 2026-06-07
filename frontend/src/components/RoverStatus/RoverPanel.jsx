// Per-rover status panel. Owner: Person 4.
import React from "react";
import useRoverStatus from "../../hooks/useRoverStatus.js";
import ScoreDisplay from "./ScoreDisplay.jsx";
import ErrorLog from "./ErrorLog.jsx";

export default function RoverPanel({ roverId }) {
  const { status } = useRoverStatus(roverId);

  // TODO [Person 4]: show live position, current task, zone assignment, last error.
  return (
    <div className="rover-panel">
      <h3>{roverId}</h3>
      <p>Position: {status ? `(${status.x}, ${status.y}) @ ${status.heading}°` : "—"}</p>
      <p>Task: {status?.task || "idle"}</p>
      <p>Zone: {status?.zone ? JSON.stringify(status.zone) : "—"}</p>
      <ScoreDisplay roverId={roverId} />
      <ErrorLog roverId={roverId} />
    </div>
  );
}
