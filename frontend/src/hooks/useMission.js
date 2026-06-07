// Mission start/status hook. Owner: Person 4.
import { useState } from "react";
import { startMission as apiStart, getMissionStatus } from "../services/api.js";

export default function useMission() {
  const [status, setStatus] = useState(null);

  // TODO [Person 4]: call POST /mission/start and refresh GET /mission/status.
  const startMission = async ({ goal, criteria }) => {
    const res = await apiStart({ goal, criteria });
    setStatus(res);
    return res;
  };

  const refreshStatus = async () => {
    const res = await getMissionStatus();
    setStatus(res);
    return res;
  };

  return { status, startMission, refreshStatus };
}
