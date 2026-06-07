// WebSocket hook for live map updates. Owner: Person 4.
import { useEffect, useState } from "react";
import { connectWebSocket } from "../services/websocket.js";

export default function useMapState() {
  const [grid, setGrid] = useState([]);
  const [redzones, setRedzones] = useState([]);
  const [rovers, setRovers] = useState([]);
  const [objects, setObjects] = useState([]);

  useEffect(() => {
    // TODO [Person 4]:
    //   - Open the WS via connectWebSocket().
    //   - On map:update    -> setGrid / setObjects
    //   - On redzone:update -> setRedzones (append)
    //   - On rover position -> setRovers (update by rover_id)
    //   - On scientist:ping -> surface to PingCard (lift state or context)
    //   - Clean up on unmount.
    const ws = connectWebSocket((msg) => {
      // switch (msg.type) { ... }
    });
    return () => ws?.close?.();
  }, []);

  return { grid, redzones, rovers, objects };
}
