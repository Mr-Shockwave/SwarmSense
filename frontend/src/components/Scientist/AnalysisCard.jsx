// Streamed research agent analysis. Owner: Person 4.
import React, { useState } from "react";

export default function AnalysisCard({ targetId }) {
  const [analysis, setAnalysis] = useState("");

  // TODO [Person 4]:
  //   - When the scientist approves/investigates, the research agent streams
  //     analysis text (via WS or SSE from /targets/approve).
  //   - Append chunks to `analysis` so the card fills in real time.
  if (!targetId) return null;
  return (
    <div className="analysis-card">
      <h4>Research analysis</h4>
      <pre>{analysis || "Awaiting analysis…"}</pre>
    </div>
  );
}
