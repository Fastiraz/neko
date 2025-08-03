import React, { useState, useEffect, useRef } from "react";
import ChatForm from "../components/forms/ChatForm";
import MessageBox from "../components/common/MessageBox";
import { sendMessageToAgent } from "../services/chatService";

type ChatMessage = {
  sender: "me" | "agent";
  text: string;
  timestamp?: string;
};

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (prompt: string) => {
    const timestamp = new Date().toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });

    setMessages((prev) => [...prev, {
      sender: "me",
      text: prompt,
      timestamp
    }]);
    setIsLoading(true);

    try {
      const reply = await sendMessageToAgent(prompt);
      const replyTimestamp = new Date().toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
      });

      setMessages((prev) => [...prev, {
        sender: "agent",
        text: reply,
        timestamp: replyTimestamp
      }]);
    } catch (error) {
      const errorTimestamp = new Date().toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
      });

      setMessages((prev) => [
        ...prev,
        {
          sender: "agent",
          text: "⚠️ Error: Failed to get response.",
          timestamp: errorTimestamp
        },
      ]);
      console.error("Chat error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-page">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-welcome">
            <p>Welcome! Start a conversation with Neko.</p>
          </div>
        ) : (
          messages.map((msg, i) => (
            <MessageBox
              key={i}
              message={msg.text}
              sender={msg.sender}
              timestamp={msg.timestamp}
            />
          ))
        )}

        {isLoading && (
          <div className="message-container message-left">
            <div className="message-bubble message-agent">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />

        <div className="chat-form-floating">
          <ChatForm onSend={handleSend} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
}
