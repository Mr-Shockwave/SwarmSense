// COLLECT / IGNORE / INVESTIGATE FURTHER buttons. Owner: Person 4.
import React from "react";
import { approveTarget } from "../../services/api.js";

export default function ApprovalButtons({ targetId, x, y }) {
  // TODO [Person 4]: POST decision to /targets/approve via services/api.approveTarget.
  const decide = (decision) => approveTarget({ target_id: targetId, decision, x, y });

  return (
    <div className="approval-buttons">
      <button onClick={() => decide("collect")}>COLLECT</button>
      <button onClick={() => decide("ignore")}>IGNORE</button>
      <button onClick={() => decide("investigate")}>INVESTIGATE FURTHER</button>
    </div>
  );
}
