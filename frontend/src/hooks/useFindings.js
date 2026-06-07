// Polls /findings and reports newly-arrived findings so the UI can ping. Owner: Person 4.
import { useState, useEffect, useRef, useCallback } from "react";
import { getFindings } from "../services/api.js";

const POLL_MS = 4000;

export default function useFindings({ onNew } = {}) {
  const [findings, setFindings] = useState([]);
  const seenIds = useRef(new Set());
  const firstLoad = useRef(true);
  const onNewRef = useRef(onNew);
  onNewRef.current = onNew;

  const poll = useCallback(async () => {
    try {
      const data = await getFindings();
      const list = data.findings || [];
      setFindings(list);

      // Detect ids we haven't seen before.
      const fresh = list.filter((f) => !seenIds.current.has(f.id));
      list.forEach((f) => seenIds.current.add(f.id));

      // Skip pinging on the very first load (don't ping for pre-existing findings).
      if (!firstLoad.current && fresh.length && onNewRef.current) {
        // newest first → ping for each new one (caller can throttle)
        fresh.forEach((f) => onNewRef.current(f));
      }
      firstLoad.current = false;
    } catch {
      /* backend offline — keep last known */
    }
  }, []);

  useEffect(() => {
    poll();
    const id = setInterval(poll, POLL_MS);
    return () => clearInterval(id);
  }, [poll]);

  return { findings, refresh: poll };
}
