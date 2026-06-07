// Object ping notification card. Owner: Person 4.
import React from "react";
import ApprovalButtons from "./ApprovalButtons.jsx";
import AnalysisCard from "./AnalysisCard.jsx";

export default function PingCard({ ping }) {
  // TODO [Person 4]:
  //   - Appears when the vision agent detects a match (scientist:ping over WS).
  //   - Show photo thumbnail + coordinates + object description.
  //   - Render ApprovalButtons; on INVESTIGATE, show AnalysisCard stream.
  if (!ping) return null;
  return (
    <div className="ping-card">
      <h3>Object detected</h3>
      {/* <img src={`data:image/jpeg;base64,${ping.photo}`} alt="detection" /> */}
      <p>At ({ping?.x}, {ping?.y})</p>
      <p>{ping?.description}</p>
      <ApprovalButtons targetId={ping?.target_id} x={ping?.x} y={ping?.y} />
      <AnalysisCard targetId={ping?.target_id} />
    </div>
  );
}
