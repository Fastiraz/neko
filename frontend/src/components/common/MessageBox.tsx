import React from "react";

type MessageBoxProps = {
  message: string;
  sender: "me" | "agent";
  timestamp?: string;
};

export default function MessageBox({ message, sender, timestamp }: MessageBoxProps) {
  const isMe = sender === "me";

  return (
    <div className={`message-container ${isMe ? "message-right" : "message-left"}`}>
      <div className={`message-bubble ${isMe ? "message-me" : "message-agent"}`}>
        <p className="message-text">{message}</p>
        {timestamp && (
          <div className="message-timestamp">
            {timestamp}
          </div>
        )}
      </div>
    </div>
  );
}