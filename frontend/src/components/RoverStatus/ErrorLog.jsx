// Live error log per rover. Owner: Person 4.
import React from "react";

export default function ErrorLog({ roverId }) {
  // TODO [Person 4]: show the rover's recent faults (from /rovers/status or WS).
  //   Highlight when the per-rover error subagent posts a fix.
  return (
    <div className="error-log">
      <h4>Errors</h4>
      <ul>{/* placeholder: map errors for {roverId} */}</ul>
    </div>
  );
}
