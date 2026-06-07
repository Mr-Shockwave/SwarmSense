// Weave scores per agent. Owner: Person 4.
import React from "react";

export default function ScoreDisplay({ roverId }) {
  // TODO [Person 4]: display Weave custom-scorer outputs per agent (vision match
  //   confidence, research quality, etc.). Source TBD with Person 1 — could be a
  //   backend endpoint that surfaces recent Weave scores, or pushed over WS.
  return (
    <div className="score-display">
      <h4>Agent scores</h4>
      <p>{/* placeholder for {roverId} scores */}—</p>
    </div>
  );
}
