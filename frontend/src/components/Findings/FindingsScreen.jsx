// Full-screen "SwarmSense · Findings" view. Owner: Person 4.
import React, { useMemo, useState } from "react";
import FindingCard from "./FindingCard.jsx";

export default function FindingsScreen({ findings = [] }) {
  const [filter, setFilter] = useState("all"); // all | new | collected | ignored

  const shown = useMemo(() => {
    if (filter === "all") return findings;
    return findings.filter((f) => (f.status || "new") === filter);
  }, [findings, filter]);

  const counts = useMemo(() => {
    const c = { all: findings.length, new: 0, collected: 0, ignored: 0 };
    findings.forEach((f) => { c[f.status || "new"] = (c[f.status || "new"] || 0) + 1; });
    return c;
  }, [findings]);

  return (
    <div className="findings-screen">
      <div className="findings-bar">
        {["all", "new", "collected", "ignored"].map((k) => (
          <button
            key={k}
            className={`findings-filter ${filter === k ? "active" : ""}`}
            onClick={() => setFilter(k)}
          >
            {k} <span className="findings-filter-count">{counts[k] || 0}</span>
          </button>
        ))}
      </div>

      {shown.length === 0 ? (
        <div className="findings-screen-empty">
          <h3>No findings yet</h3>
          <p>
            When an agent detects something matching the mission criteria, it lands
            here — with its photo, location, and analysis.
          </p>
        </div>
      ) : (
        <div className="findings-grid">
          {shown.map((f) => (
            <FindingCard key={f.id} finding={f} />
          ))}
        </div>
      )}
    </div>
  );
}
