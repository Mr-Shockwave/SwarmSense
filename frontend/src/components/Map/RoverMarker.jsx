// Individual rover dot on the map. Owner: Person 4.
import React from "react";

export default function RoverMarker({ rover }) {
  // TODO [Person 4]: render an animated dot at rover.{x,y}, oriented by heading,
  //   labeled with rover_id. Animate transitions between position updates.
  if (!rover) return null;
  return (
    <div className="rover-marker" title={`${rover.rover_id} @ (${rover.x}, ${rover.y})`}>
      {/* placeholder */}
    </div>
  );
}
