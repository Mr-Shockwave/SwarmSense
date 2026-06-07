// Initial-prompt chat box. Locks once a mission is sent. Owner: Person 4.
import React from "react";

export default function ChatBox({ value, onChange, onSubmit, disabled }) {
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey && !disabled) {
      e.preventDefault();
      if (value.trim()) onSubmit();
    }
  };

  return (
    <div className={`chatbox ${disabled ? "locked" : ""}`}>
      <textarea
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder='Describe the mission — e.g. "Explore the room and ping me if you see anything blue or circular"'
      />
      <div className="chat-row">
        <span className="chat-hint">
          {disabled ? "Mission running — chat locked" : "Enter to send · Shift+Enter for newline"}
        </span>
        <button className="send-btn" disabled={disabled || !value.trim()} onClick={onSubmit}>
          {disabled ? "Sent" : "Send"}
        </button>
      </div>
      {disabled && (
        <div className="locked-banner">
          Prompt dispatched to shared memory — the per-robot agents are on it.
        </div>
      )}
    </div>
  );
}
