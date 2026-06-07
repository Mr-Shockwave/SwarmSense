// CopilotKit chat sidebar — scientist asks about mission state / findings. Owner: Person 4.
import React from "react";
import { useCopilotReadable, useCopilotAction } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

export default function CopilotOverlay({
  mission,
  nodes = [],
  frameCounts = {},
  findings = [],
  running,
  onOpenFindings,
  onOpenMission,
  onStartMission,
  onToggleNode,
}) {
  // --- Make app state READABLE by the assistant ---
  useCopilotReadable({
    description: "Current mission goal, detection criteria, and status",
    value: mission || { status: "idle" },
  });

  useCopilotReadable({
    description: "The rover agents (nodes) and how many frames each has captured",
    value: nodes.map((n) => ({
      id: n.id,
      label: n.label,
      name: n.name,
      frames: frameCounts[n.id] || 0,
    })),
  });

  useCopilotReadable({
    description: "All findings the agents have detected for the scientist",
    value: findings.map((f) => ({
      id: f.id,
      label: f.label,
      rover: f.rover_id,
      coord: f.coord,
      status: f.status,
      summary: f.summary,
      criteria: f.criteria,
    })),
  });

  // --- Give the assistant ACTIONS it can take ---
  useCopilotAction({
    name: "openFindings",
    description: "Switch the UI to the Findings screen",
    parameters: [],
    handler: async () => { onOpenFindings?.(); },
  });

  useCopilotAction({
    name: "openMissionControl",
    description: "Switch the UI to the Mission Control (prompt) screen",
    parameters: [],
    handler: async () => { onOpenMission?.(); },
  });

  useCopilotAction({
    name: "startMission",
    description: "Start a new mission with a goal and detection criteria",
    parameters: [
      { name: "goal", type: "string", description: "What the swarm should do", required: true },
      { name: "criteria", type: "string", description: "What to look for / ping about", required: false },
    ],
    handler: async ({ goal, criteria }) => {
      if (running) return "A mission is already running.";
      onStartMission?.({ goal, criteria: criteria || goal });
      return "Mission started.";
    },
  });

  useCopilotAction({
    name: "focusNode",
    description: "Open/expand a specific rover node (e.g. N1 or N2)",
    parameters: [
      { name: "nodeId", type: "string", description: "Node id like rover1 or rover2", required: true },
    ],
    handler: async ({ nodeId }) => { onToggleNode?.(nodeId); },
  });

  return (
    <CopilotSidebar
      defaultOpen={false}
      clickOutsideToClose
      labels={{
        title: "SwarmSense Assistant",
        initial: "Ask me about the mission, the rovers, or the findings.",
      }}
      instructions={
        "You are the SwarmSense mission assistant. You can read the current mission, " +
        "rover nodes, and findings, and you can switch screens or start a mission. " +
        "Be concise."
      }
    />
  );
}
