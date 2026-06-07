// Interesting object marker on the map. Owner: Person 4.
import React from "react";

export default function ObjectMarker({ object }) {
  // TODO [Person 4]: render a marker at object.{x,y}. Blue = detected,
  //   star = scientist-approved target. Click -> open details / PingCard.
  if (!object) return null;
  return (
    <div className="object-marker" title={object.description || "object"}>
      {/* placeholder */}
    </div>
  );
}
