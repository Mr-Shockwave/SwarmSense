// 2D canvas grid — the live mission map. Owner: Person 4.
import React, { useRef, useEffect } from "react";
import useMapState from "../../hooks/useMapState.js";
import RoverMarker from "./RoverMarker.jsx";
import RedZoneOverlay from "./RedZoneOverlay.jsx";
import ObjectMarker from "./ObjectMarker.jsx";

// Cell color legend:
//   unexplored -> dark, explored -> green, redzone -> red,
//   object -> blue, target (approved) -> star, rover -> animated dot
const COLORS = {
  unexplored: "#1a1a1a",
  explored: "#1f7a1f",
  redzone: "#c0392b",
  object: "#2980b9",
  target: "#f1c40f",
};

export default function MapGrid() {
  const canvasRef = useRef(null);
  const { grid, redzones, rovers, objects } = useMapState();

  useEffect(() => {
    // TODO [Person 4]:
    //   - Draw the grid cells from `grid` using COLORS.
    //   - Overlay red zones, object markers, approved-target stars.
    //   - Draw animated rover dots from `rovers`.
    //   - Redraw on every WebSocket update (grid/redzones/rovers change).
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // ...render here...
  }, [grid, redzones, rovers, objects]);

  // TODO [Person 4]: make cells clickable to show object details (onClick -> hit-test).
  return (
    <div className="map-grid">
      <canvas ref={canvasRef} width={600} height={600} style={{ background: "#000" }} />
      {/* These helper components can render as canvas draws or absolutely-positioned overlays */}
      <RedZoneOverlay redzones={redzones} />
      {objects?.map((o) => (
        <ObjectMarker key={o.id} object={o} />
      ))}
      {rovers?.map((r) => (
        <RoverMarker key={r.rover_id} rover={r} />
      ))}
    </div>
  );
}
