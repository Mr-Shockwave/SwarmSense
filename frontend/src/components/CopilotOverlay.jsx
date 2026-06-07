// CopilotKit chat + ping overlay. Owner: Person 4.
import React from "react";
// TODO [Person 4]: import the CopilotKit sidebar/popup:
// import { CopilotSidebar } from "@copilotkit/react-ui";

export default function CopilotOverlay() {
  // TODO [Person 4]:
  //   - Render the CopilotKit chat sidebar so the scientist can ask questions
  //     about mission state ("where is rover2?", "summarize findings").
  //   - Must sit inside the <CopilotKit> provider from App.jsx.
  return (
    <div className="copilot-overlay">
      {/* <CopilotSidebar instructions="You help a scientist run a rover swarm mission." /> */}
    </div>
  );
}
