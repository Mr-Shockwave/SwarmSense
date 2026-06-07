// Left side panel: Agents (node list) + Findings tabs. Owner: Person 4.
import React from "react";

export default function SidePanel({
  activeTab,
  onTabChange,
  nodes,
  openNodes,
  frameCounts,
  running,
  onToggleNode,
  canAddNode = false,
  onAddNode,
}) {
  return (
    <aside className="side-panel">
      <div className="side-tabs">
        <button
          className={`side-tab ${activeTab === "agents" ? "active" : ""}`}
          onClick={() => onTabChange("agents")}
        >
          Agents
        </button>
        <button
          className={`side-tab ${activeTab === "findings" ? "active" : ""}`}
          onClick={() => onTabChange("findings")}
        >
          Findings
        </button>
      </div>

      <div className="side-body">
        {activeTab === "agents" ? (
          <>
            <p className="side-heading">Agents</p>
            {nodes.map((n) => {
              const count = frameCounts[n.id] || 0;
              const live = running && count > 0;
              return (
                <button
                  key={n.id}
                  className={`node-item ${openNodes[n.id] ? "open" : ""} ${live ? "live" : ""}`}
                  onClick={() => onToggleNode(n.id)}
                  title={`Toggle ${n.label}`}
                >
                  <span className="dot" />
                  <span className="node-tag">{n.label}</span>
                  <span className="node-name">{n.name}</span>
                  <span className="node-count">{count}</span>
                </button>
              );
            })}

            {/* + add node — disabled until a 3rd robot exists */}
            <div
              className="add-node-wrap"
              data-tooltip={canAddNode ? "Add a node" : "3rd robot doesn't exist"}
            >
              <button
                className="add-node"
                disabled={!canAddNode}
                onClick={canAddNode ? onAddNode : undefined}
              >
                + Add node
              </button>
            </div>
          </>
        ) : (
          <>
            <p className="side-heading">Findings</p>
            <div className="findings-empty">
              Detailed stats land here — what the agents found, when they found it,
              and averages across the mission. Coming next.
            </div>
          </>
        )}
      </div>
    </aside>
  );
}
