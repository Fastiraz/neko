import React, { useState, useRef, useEffect } from "react";
import Button from "../common/Button";

type ChatFormProps = {
  onSend: (message: string) => void;
  disabled?: boolean;
};

export default function ChatForm({ onSend, disabled }: ChatFormProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() === "" || disabled) return;
    onSend(message.trim());
    setMessage("");
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (message.trim() && !disabled) {
        onSend(message.trim());
        setMessage("");
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="chat-form">
      <div className="chat-input-container">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
          disabled={disabled}
          className="chat-input"
          rows={1}
          style={{ minHeight: '1.5rem', maxHeight: '150px' }}
        />
        <Button 
          type="submit" 
          disabled={disabled || !message.trim()}
          className="chat-send-button"
        >
          {disabled ? "..." : "Send"}
        </Button>
      </div>
    </form>
  );
}