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
  findings = [],
  unseenFindings = 0,
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
          {unseenFindings > 0 && <span className="tab-badge">{unseenFindings}</span>}
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
            <p className="side-heading">Findings · {findings.length}</p>
            {findings.length === 0 ? (
              <div className="findings-empty">
                No findings yet. When an agent detects something matching the mission
                criteria, it appears here and on the Findings screen.
              </div>
            ) : (
              findings.map((f) => (
                <div key={f.id} className="finding-side-item">
                  <span className={`finding-side-dot ${f.status || "new"}`} />
                  <span className="finding-side-label">{f.label}</span>
                  <span className="finding-side-rover">{f.rover_id}</span>
                </div>
              ))
            )}
          </>
        )}
      </div>
    </aside>
  );
}
