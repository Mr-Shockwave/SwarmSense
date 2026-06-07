// Mission Control landing — chat → workflow → live agent node sections. Owner: Person 4.
import React, { useState, useEffect, useRef, useCallback } from "react";
import SidePanel from "./components/SidePanel/SidePanel.jsx";
import WorkflowStages from "./components/Workflow/WorkflowStages.jsx";
import ChatBox from "./components/Chat/ChatBox.jsx";
import NodeSection from "./components/Nodes/NodeSection.jsx";
import { startMission, stopMission, getRoverImages } from "./services/api.js";

// Initial robots. N3+ stay locked until a 3rd robot exists.
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

const POLL_MS = 5500; // matches the ~5-6s capture cadence

export default function App() {
  const [activeTab, setActiveTab] = useState("agents");
  const [prompt, setPrompt] = useState("");
  const [running, setRunning] = useState(false);

  const [nodes] = useState(INITIAL_NODES);
  const [openNodes, setOpenNodes] = useState({});      // { rover1: true }
  const [images, setImages] = useState({});            // { rover1: [...frames] }

  const [stages, setStages] = useState(FALLBACK_STAGES);
  const [stageProgress, setStageProgress] = useState(0);

  const pollRef = useRef(null);
  const stageTimerRef = useRef(null);

  const frameCounts = Object.fromEntries(
    nodes.map((n) => [n.id, (images[n.id] || []).length])
  );

  const toggleNode = useCallback((id) => {
    setOpenNodes((prev) => ({ ...prev, [id]: !prev[id] }));
  }, []);

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

  useEffect(() => {
    if (!running) return;
    pollImages();
    pollRef.current = setInterval(pollImages, POLL_MS);
    return () => clearInterval(pollRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [running]);

  // --- Animate the workflow checklist after submit ---
  const animateStages = useCallback((count) => {
    clearInterval(stageTimerRef.current);
    setStageProgress(0);
    stageTimerRef.current = setInterval(() => {
      setStageProgress((p) => {
        if (p >= count - 1) {
          clearInterval(stageTimerRef.current);
          return count - 1; // leave the final "exploring" stage active
        }
        return p + 1;
      });
    }, 850);
  }, []);

  const handleSubmit = async () => {
    if (!prompt.trim()) return;
    setRunning(true);
    // Open both nodes so the scientist immediately sees frames stream in.
    setOpenNodes(Object.fromEntries(nodes.map((n) => [n.id, true])));
    try {
      const res = await startMission({ goal: prompt.trim(), criteria: prompt.trim() });
      const s = res?.stages?.length ? res.stages : FALLBACK_STAGES;
      setStages(s);
      animateStages(s.length);
    } catch {
      // Backend offline — still show the workflow UI optimistically.
      setStages(FALLBACK_STAGES);
      animateStages(FALLBACK_STAGES.length);
    }
  };

  const handleNewMission = async () => {
    clearInterval(pollRef.current);
    clearInterval(stageTimerRef.current);
    try {
      await stopMission();
    } catch { /* ignore */ }
    setRunning(false);
    setPrompt("");
    setImages({});
    setStageProgress(0);
  };

  return (
    <div className="app">
      <SidePanel
        activeTab={activeTab}
        onTabChange={setActiveTab}
        nodes={nodes}
        openNodes={openNodes}
        frameCounts={frameCounts}
        running={running}
        onToggleNode={toggleNode}
        canAddNode={false}
      />

      <main className="main">
        <div className="topbar">
          <h1>SwarmSense · Mission Control</h1>
          <span className="mode-badge">{running ? "mission running" : "idle"}</span>
        </div>

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
              />
            )}

            <ChatBox
              value={prompt}
              onChange={setPrompt}
              onSubmit={handleSubmit}
              disabled={running}
            />

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
      </main>
    </div>
  );
}
