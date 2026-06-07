// Axios wrapper for backend calls. Owner: Person 4.
import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "";
const client = axios.create({ baseURL });

// TODO [Person 4]: implement each call against the backend routes (Person 2).

export async function startMission({ goal, criteria }) {
  const { data } = await client.post("/mission/start", { goal, criteria });
  return data;
}

export async function getMissionStatus() {
  const { data } = await client.get("/mission/status");
  return data;
}

export async function getMapState() {
  const { data } = await client.get("/map/state");
  return data;
}

export async function stopMission() {
  const { data } = await client.post("/mission/stop");
  return data;
}

export async function getRoversStatus() {
  const { data } = await client.get("/rovers/status");
  return data;
}

export async function getRoverImages(roverId, limit = 100) {
  const { data } = await client.get(`/rovers/${roverId}/images`, { params: { limit } });
  return data; // { rover_id, count, frames: [{ ts, photo, caption, coord }] }
}

export async function approveTarget({ target_id, decision, x, y, description }) {
  const { data } = await client.post("/targets/approve", {
    target_id,
    decision,
    x,
    y,
    description,
  });
  return data;
}

export async function listTargets() {
  const { data } = await client.get("/targets/list");
  return data;
}

// --- Findings (scientist-relevant detections) ---
export async function getFindings(limit = 200) {
  const { data } = await client.get("/findings", { params: { limit } });
  return data; // { count, findings: [{ id, rover_id, label, summary, description, photo, coord, criteria, confidence, status, ts }] }
}

export async function createFinding(finding) {
  const { data } = await client.post("/findings", finding);
  return data;
}

export async function setFindingStatus(findingId, status) {
  const { data } = await client.post(`/findings/${findingId}/status`, { status });
  return data;
}
