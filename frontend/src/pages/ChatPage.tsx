import React, { useState } from "react";
import ChatForm from "../components/forms/ChatForm";
import MessageBox from "../components/common/MessageBox";
import { sendMessageToAgent } from "../services/chatService";

type ChatMessage = {
  sender: "me" | "agent";
  text: string;
};

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async (prompt: string) => {
    setMessages((prev) => [...prev, { sender: "me", text: prompt }]);
    setIsLoading(true);

    try {
      const reply = await sendMessageToAgent(prompt);
      setMessages((prev) => [...prev, { sender: "agent", text: reply }]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { sender: "agent", text: "⚠️ Error: Failed to get response." },
      ]);
      console.error("Chat error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.map((msg, i) => (
          <MessageBox key={i} message={msg.text} sender={msg.sender} />
        ))}
      </div>
      <ChatForm onSend={handleSend} disabled={isLoading} />
    </div>
  );
}
