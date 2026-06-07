// CopilotKit chat sidebar — scientist asks about mission state / findings. Owner: Person 4.
import React from "react";
import { useCopilotReadable, useCopilotAction } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import { setFindingStatus as apiSetFindingStatus } from "../services/api.js";

const FINDING_STATUSES = ["new", "collected", "ignored"];

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
    description: "Expand the image feed panel for a rover so the scientist can browse its captured frames in the UI. This only opens the panel — it does not analyze, zoom, or do anything to the images.",
    parameters: [
      { name: "nodeId", type: "string", description: "Node id like rover1 or rover2", required: true },
    ],
    handler: async ({ nodeId }) => { onToggleNode?.(nodeId); },
  });

  useCopilotAction({
    name: "updateFindingStatus",
    description:
      "Update a finding's status. Use 'collected' to confirm/keep a target, " +
      "'ignored' to dismiss a false positive, or 'new' to reset. " +
      "The UI refreshes within a few seconds.",
    parameters: [
      { name: "findingId", type: "string", description: "The finding id, e.g. find_6359d1de", required: true },
      { name: "status", type: "string", description: "One of: new, collected, ignored", required: true },
    ],
    handler: async ({ findingId, status }) => {
      if (!FINDING_STATUSES.includes(status)) {
        return `Invalid status. Use one of: ${FINDING_STATUSES.join(", ")}.`;
      }
      try {
        await apiSetFindingStatus(findingId, status);
        return `Finding ${findingId} marked as "${status}".`;
      } catch {
        return `Failed to update finding ${findingId}.`;
      }
    },
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
        "You are the SwarmSense mission assistant for a two-rover exploration swarm " +
        "(rovers are N1/rover1 and N2/rover2).\n\n" +
        "WHAT YOU CAN DO — only ever offer these:\n" +
        "1. Answer questions about the mission, the rovers and their frame counts, and the findings, " +
        "using only the live data provided to you.\n" +
        "2. Switch the UI to the Findings screen or to Mission Control.\n" +
        "3. Start a new mission from a goal (and optional criteria).\n" +
        "4. Open the image feed panel for a rover (N1 or N2) so the scientist can browse its frames — call this 'open Rover X feed', never 'inspect frames' or 'investigate'.\n" +
        "5. Update a finding's status to 'collected' (confirmed target) or 'ignored' (false positive).\n\n" +
        "WHAT YOU CANNOT DO — never offer, promise, or claim these; they are NOT implemented:\n" +
        "- You cannot move, drive, steer, or navigate a rover.\n" +
        "- You cannot make a rover take, zoom, or capture new photos.\n" +
        "- You cannot send a rover to a coordinate, have it investigate an object, or search an area on demand.\n\n" +
        "If the user asks for any unavailable action, briefly say it isn't available yet, then offer a real " +
        "alternative (mark the finding collected/ignored, open the Findings screen, etc.). " +
        "Be concise. Reference findings by their id. Do not invent capabilities or data."
      }
    />
  );
}
