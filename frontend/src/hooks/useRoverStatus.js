// Rover position + error polling hook. Owner: Person 4.
import { useEffect, useState } from "react";
import { getRoversStatus } from "../services/api.js";

export default function useRoverStatus(roverId) {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    // TODO [Person 4]:
    //   - Poll GET /rovers/status (or subscribe via WS) and pick out `roverId`.
    //   - setStatus with position, task, zone, last error.
    //   - Clear interval on unmount.
    let active = true;
    const tick = async () => {
      const all = await getRoversStatus();
      if (active) setStatus(all?.[roverId] ?? null);
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => {
      active = false;
      clearInterval(id);
    };
  }, [roverId]);

  return { status };
}
