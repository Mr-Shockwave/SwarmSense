// SwarmSense — Mission Control + Findings, with CopilotKit assistant. Owner: Person 4.
import React, { useState, useEffect, useRef, useCallback } from "react";
import { CopilotKit } from "@copilotkit/react-core";

import SidePanel from "./components/SidePanel/SidePanel.jsx";
import WorkflowStages from "./components/Workflow/WorkflowStages.jsx";
import ChatBox from "./components/Chat/ChatBox.jsx";
import NodeSection from "./components/Nodes/NodeSection.jsx";
import FindingsScreen from "./components/Findings/FindingsScreen.jsx";
import FindingPing from "./components/Findings/FindingPing.jsx";
import CopilotOverlay from "./components/CopilotOverlay.jsx";
import useFindings from "./hooks/useFindings.js";
import useLiveSocket from "./hooks/useLiveSocket.js";
import { startMission, stopMission, getRoverImages, resetApp } from "./services/api.js";

const INITIAL_NODES = [
  { id: "rover1", label: "N1", name: "Rover 1" },
  { id: "rover2", label: "N2", name: "Rover 2" },
];

const FALLBACK_STAGES = [
  "Received mission prompt",
  "Saved prompt to shared memory (Redis)",
  "Splitting map into agent zones",
  "Dispatching mission to Agent N1",
  "Dispatching mission to Agent N2",
  "Agents exploring & capturing",
];

const POLL_MS = 5500;

// --- CopilotKit config (see notes) ---
const COPILOT_ENABLED = (import.meta.env.VITE_COPILOT_ENABLED ?? "true") !== "false";
const COPILOT_PUBLIC_KEY = import.meta.env.VITE_COPILOT_PUBLIC_KEY || "";
const COPILOT_RUNTIME_URL = import.meta.env.VITE_COPILOT_RUNTIME_URL || "/api/copilot";

export default function App() {
  const [activeTab, setActiveTab] = useState("agents"); // "agents" = mission control, "findings" = big screen
  const [prompt, setPrompt] = useState("");
  const [running, setRunning] = useState(false);

  const [nodes] = useState(INITIAL_NODES);
  const [openNodes, setOpenNodes] = useState({});
  const [images, setImages] = useState({});

  const [stages, setStages] = useState(FALLBACK_STAGES);
  const [stageProgress, setStageProgress] = useState(0);

  const [unseenFindings, setUnseenFindings] = useState(0);
  const [ping, setPing] = useState(null);

  const pollRef = useRef(null);
  const stageTimerRef = useRef(null); // kept for fallback only

  // --- Findings: poll + ping on new ones ---
  const handleNewFinding = useCallback((finding) => {
    setPing(finding);
    setUnseenFindings((n) => n + 1);
  }, []);
  const { findings, refresh: refreshFindings } = useFindings({ onNew: handleNewFinding });

  const frameCounts = Object.fromEntries(
    nodes.map((n) => [n.id, (images[n.id] || []).length])
  );

  const toggleNode = useCallback((id) => {
    setOpenNodes((prev) => ({ ...prev, [id]: !prev[id] }));
  }, []);

  const goToFindings = useCallback(() => {
    setActiveTab("findings");
    setUnseenFindings(0);
    setPing(null);
  }, []);

  const goToMission = useCallback(() => setActiveTab("agents"), []);

  // --- Poll captured frames from Redis (per node) while a mission runs ---
  const pollImages = useCallback(async () => {
    const results = await Promise.all(
      nodes.map(async (n) => {
        try {
          const data = await getRoverImages(n.id);
          return [n.id, data.frames || []];
        } catch {
          return [n.id, images[n.id] || []];
        }
      })
    );
    setImages((prev) => ({ ...prev, ...Object.fromEntries(results) }));
  }, [nodes, images]);

  // --- Live updates: WS message => instant refetch (polling stays as fallback) ---
  useLiveSocket({
    onFrame: ({ rover_id }) => {
      if (!running) return;
      if (!rover_id) { pollImages(); return; }
      // Only refetch the rover that got a new frame, not both.
      getRoverImages(rover_id).then((data) =>
        setImages((prev) => ({ ...prev, [rover_id]: data.frames || [] }))
      ).catch(() => {});
    },
    onFinding: () => refreshFindings(),
    onStage: ({ index }) => {
      if (typeof index === "number") setStageProgress(index);
    },
  });

  useEffect(() => {
    if (!running) return;
    pollImages();
    pollRef.current = setInterval(pollImages, POLL_MS);
    return () => clearInterval(pollRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [running]);

  const launchMission = useCallback(async ({ goal, criteria }) => {
    if (!goal?.trim()) return;
    setActiveTab("agents");
    setRunning(true);
    setStageProgress(0);
    setOpenNodes(Object.fromEntries(nodes.map((n) => [n.id, true])));
    try {
      const res = await startMission({ goal: goal.trim(), criteria: (criteria || goal).trim() });
      const s = res?.stages?.length ? res.stages : FALLBACK_STAGES;
      setStages(s);
    } catch {
      setStages(FALLBACK_STAGES);
    }
  }, [nodes]);

  const handleSubmit = () => launchMission({ goal: prompt, criteria: prompt });

  const handleNewMission = async () => {
    clearInterval(pollRef.current);
    try { await stopMission(); } catch { /* ignore */ }
    setRunning(false);
    setPrompt("");
    setImages({});
    setStageProgress(0);
  };

  const handleReset = async () => {
    clearInterval(pollRef.current);
    try { await resetApp(); } catch { /* ignore */ }
    setRunning(false);
    setPrompt("");
    setImages({});
    setStageProgress(0);
  };

  const onFindings = activeTab === "findings";

  const appBody = (
    <div className="app">
      <SidePanel
        activeTab={activeTab}
        onTabChange={(t) => (t === "findings" ? goToFindings() : goToMission())}
        nodes={nodes}
        openNodes={openNodes}
        frameCounts={frameCounts}
        running={running}
        onToggleNode={toggleNode}
        canAddNode={false}
        findings={findings}
        unseenFindings={unseenFindings}
      />

      <main className="main">
        <div className="topbar">
          <h1>SwarmSense · {onFindings ? "Findings" : "Mission Control"}</h1>
          <span className="mode-badge">{running ? "mission running" : "idle"}</span>
        </div>

        {onFindings ? (
          <FindingsScreen findings={findings} />
        ) : (
          <div className={`console ${running ? "" : "center"}`}>
            <div className="console-inner">
              {!running && (
                <div className="hero">
                  <h2>Start a mission</h2>
                  <p>Tell the swarm what to explore and what to look for.</p>
                </div>
              )}

              {running && (
                <WorkflowStages
                  stages={stages}
                  stageProgress={stageProgress}
                  onNewMission={handleNewMission}
                  onReset={handleReset}
                />
              )}

              <ChatBox value={prompt} onChange={setPrompt} onSubmit={handleSubmit} disabled={running} />

              <div className="nodes">
                {nodes.map((n) => (
                  <NodeSection
                    key={n.id}
                    node={n}
                    frames={images[n.id] || []}
                    open={!!openNodes[n.id]}
                    running={running}
                    onToggle={toggleNode}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* New-finding ping (only on the mission screen) */}
      {!onFindings && ping && (
        <FindingPing finding={ping} onView={goToFindings} onDismiss={() => setPing(null)} />
      )}
    </div>
  );

  if (!COPILOT_ENABLED) return appBody;

  const providerProps = COPILOT_PUBLIC_KEY
    ? { publicApiKey: COPILOT_PUBLIC_KEY }
    : { runtimeUrl: COPILOT_RUNTIME_URL };

  return (
    <CopilotKit {...providerProps}>
      {appBody}
      <CopilotOverlay
        mission={running ? { goal: prompt, status: "running" } : { status: "idle" }}
        nodes={nodes}
        frameCounts={frameCounts}
        findings={findings}
        running={running}
        onOpenFindings={goToFindings}
        onOpenMission={goToMission}
        onStartMission={launchMission}
        onToggleNode={toggleNode}
      />
    </CopilotKit>
  );
}
