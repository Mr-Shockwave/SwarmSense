// Mission goal + object criteria input. Owner: Person 4.
import React, { useState } from "react";
import useMission from "../../hooks/useMission.js";

export default function MissionInput() {
  const [goal, setGoal] = useState("");
  const [criteria, setCriteria] = useState("");
  const { startMission } = useMission();

  // TODO [Person 4]: POST {goal, criteria} to /mission/start via useMission/startMission.
  const onSubmit = (e) => {
    e.preventDefault();
    startMission({ goal, criteria });
  };

  return (
    <form className="mission-input" onSubmit={onSubmit}>
      <h2>New Mission</h2>
      <label>
        Goal
        <textarea value={goal} onChange={(e) => setGoal(e.target.value)}
          placeholder="Explore the room and map it" />
      </label>
      <label>
        Detection criteria
        <textarea value={criteria} onChange={(e) => setCriteria(e.target.value)}
          placeholder="Ping me if you see anything blue or circular" />
      </label>
      <button type="submit">Start Mission</button>
    </form>
  );
}
