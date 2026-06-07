// WebSocket connection manager. Owner: Person 4.

const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";

// TODO [Person 4]:
//   - Open a WebSocket to the backend /ws endpoint.
//   - Parse JSON messages and forward to onMessage.
//   - Auto-reconnect with backoff on close/error.
export function connectWebSocket(onMessage) {
  const ws = new WebSocket(WS_URL);

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      onMessage?.(msg);
    } catch (e) {
      console.error("Bad WS message", e);
    }
  };

  ws.onclose = () => {
    // TODO [Person 4]: reconnect with backoff.
  };

  return ws;
}
