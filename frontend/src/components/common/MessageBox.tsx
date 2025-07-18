import React from "react";

type MessageBoxProps = {
  message: string;
  sender: "me" | "bot";
  timestamp?: string;
};

export default function MessageBox({ message, sender, timestamp }: MessageBoxProps) {
  const isMe = sender === "me";

  return (
    <div className={`flex ${isMe ? "justify-end" : "justify-start"} mb-2`}>
      <div
        className={`
          max-w-xs sm:max-w-md px-4 py-2 rounded-lg shadow
          ${isMe ? "bg-blue-600 text-white rounded-br-none" : "bg-gray-200 text-black rounded-bl-none"}
        `}
      >
        <p className="whitespace-pre-wrap break-words">{message}</p>
        {timestamp && (
          <div className="text-xs text-gray-400 mt-1 text-right">
            {timestamp}
          </div>
        )}
      </div>
    </div>
  );
}
