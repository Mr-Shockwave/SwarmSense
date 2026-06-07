// Root app — layout (map + sidebar) wrapped in CopilotKit. Owner: Person 4.
import React from "react";
// TODO [Person 4]: import CopilotKit provider + UI:
// import { CopilotKit } from "@copilotkit/react-core";
// import "@copilotkit/react-ui/styles.css";

import MapGrid from "./components/Map/MapGrid.jsx";
import MissionInput from "./components/Scientist/MissionInput.jsx";
import PingCard from "./components/Scientist/PingCard.jsx";
import RoverPanel from "./components/RoverStatus/RoverPanel.jsx";
import CopilotOverlay from "./components/CopilotOverlay.jsx";

export default function App() {
  // TODO [Person 4]:
  //   - Wrap everything in <CopilotKit runtimeUrl="/api/copilot"> ... </CopilotKit>
  //   - Lay out: left = MapGrid (2D canvas), right sidebar = MissionInput,
  //     PingCards, RoverPanels. Add CopilotOverlay chat.
  //   - Wire live data via hooks (useMapState, useMission, useRoverStatus).
  return (
    <div className="app" style={{ display: "flex", height: "100vh" }}>
      <main style={{ flex: 2 }}>
        <h1>RoverSwarm — Mission Control</h1>
        <MapGrid />
      </main>
      <aside style={{ flex: 1, overflowY: "auto" }}>
        <MissionInput />
        {/* TODO [Person 4]: render a PingCard per active ping */}
        <PingCard />
        {/* TODO [Person 4]: render a RoverPanel per rover */}
        <RoverPanel roverId="rover1" />
        <RoverPanel roverId="rover2" />
      </aside>
      <CopilotOverlay />
    </div>
  );
}
