// Red zone rendering on the grid. Owner: Person 4.
import React from "react";

export default function RedZoneOverlay({ redzones }) {
  // TODO [Person 4]: render each red zone (x, y, radius) as a translucent red
  //   circle/cell overlay. Appears live when redzone:update arrives via WS.
  if (!redzones?.length) return null;
  return <div className="redzone-overlay">{/* placeholder */}</div>;
}
