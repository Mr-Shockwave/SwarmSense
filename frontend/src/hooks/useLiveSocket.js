// Live WebSocket to the backend bridge. Owner: Person 4.
// Receives {type:"frame"|"finding", ...} messages and invokes callbacks so the
// UI can refetch instantly instead of waiting for the next poll. Auto-reconnects.
import { useEffect, useRef } from "react";

// Prefer an explicit URL; otherwise connect to /ws on the same origin (Vite
// proxies it to the backend), which avoids CORS/host issues.
function resolveUrl() {
  const explicit = import.meta.env.VITE_WS_URL;
  if (explicit) return explicit;
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${proto}//${window.location.host}/ws`;
}

export default function useLiveSocket({ onFrame, onFinding, onStatusChange } = {}) {
  const onFrameRef = useRef(onFrame);
  const onFindingRef = useRef(onFinding);
  const onStatusRef = useRef(onStatusChange);
  onFrameRef.current = onFrame;
  onFindingRef.current = onFinding;
  onStatusRef.current = onStatusChange;

  useEffect(() => {
    let closed = false;
    let ws = null;
    let reconnectTimer = null;

    const scheduleReconnect = () => {
      clearTimeout(reconnectTimer);
      reconnectTimer = setTimeout(connect, 2000);
    };

    function connect() {
      if (closed) return;
      try {
        ws = new WebSocket(resolveUrl());
      } catch {
        scheduleReconnect();
        return;
      }

      ws.onopen = () => onStatusRef.current?.("connected");

      ws.onmessage = (ev) => {
        let msg;
        try {
          msg = JSON.parse(ev.data);
        } catch {
          return;
        }
        if (msg.type === "frame") onFrameRef.current?.(msg);
        else if (msg.type === "finding") onFindingRef.current?.(msg);
      };

      ws.onclose = () => {
        onStatusRef.current?.("disconnected");
        if (!closed) scheduleReconnect();
      };

      ws.onerror = () => {
        try {
          ws.close();
        } catch {
          /* ignore */
        }
      };
    }

    connect();

    return () => {
      closed = true;
      clearTimeout(reconnectTimer);
      try {
        ws?.close();
      } catch {
        /* ignore */
      }
    };
  }, []);
}
