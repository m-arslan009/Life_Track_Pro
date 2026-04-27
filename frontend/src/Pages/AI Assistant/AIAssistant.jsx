import { useEffect, useRef, useState } from "react";
import { Button, Input, Spin, Typography } from "antd";
import { SendOutlined, RobotOutlined, UserOutlined } from "@ant-design/icons";
import { sendChatMessage } from "../../Services/chatbotServices";
import "./AIAssistant.css";

const { Text } = Typography;

const generateSessionId = () => {
  const stored = localStorage.getItem("chatbot_session_id");
  if (stored) return stored;
  const newId = `session_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
  localStorage.setItem("chatbot_session_id", newId);
  return newId;
};

const INITIAL_WELCOME = [
  {
    id: "welcome",
    role: "bot",
    content: "Hello! I'm your AI Assistant. How can I help you today?",
  },
];

export default function AIAssistant() {
  const [messages, setMessages] = useState(INITIAL_WELCOME);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(generateSessionId);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    const userMessage = inputValue.trim();
    if (!userMessage || isLoading) return;

    const userMsg = { id: `user_${Date.now()}`, role: "user", content: userMessage };
    setMessages((prev) => [...prev, userMsg]);
    setInputValue("");
    setError(null);
    setIsLoading(true);

    try {
      const data = await sendChatMessage(userMessage, sessionId, {});
      setIsLoading(false);

      const botResponse = data.response || "Got your message. What's next?";
      const missingFields = data.missing_fields || [];
      const errors = data.errors || [];

      setMessages((prev) => [
        ...prev,
        { id: `bot_${Date.now()}`, role: "bot", content: botResponse },
      ]);

      if (errors.length > 0) {
        setError(errors[0]);
      }

      if (missingFields.length > 0) {
        setMessages((prev) => [
          ...prev,
          {
            id: `followup_${Date.now()}`,
            role: "bot",
            content: `I need some additional information: ${missingFields.join(", ")}`,
            isFollowUp: true,
          },
        ]);
      }
    } catch (err) {
      setIsLoading(false);
      const errorMsg = err.message || "Failed to connect to AI. Please try again.";
      setError(errorMsg);
      setMessages((prev) => [
        ...prev,
        { id: `bot_error_${Date.now()}`, role: "bot", content: errorMsg, isError: true },
      ]);
    }

    inputRef.current?.focus();
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="ai-assistant-page">
      <div className="ai-assistant-header">
        <RobotOutlined className="ai-header-icon" />
        <Text className="ai-header-title">AI Assistant</Text>
      </div>

      <div className="ai-chat-container">
        <div className="ai-messages">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`ai-message ${msg.role} ${msg.isError ? "error" : ""} ${
                msg.isFollowUp ? "followup" : ""
              }`}
            >
              <div className="ai-message-avatar">
                {msg.role === "bot" ? <RobotOutlined /> : <UserOutlined />}
              </div>
              <div className="ai-message-content">{msg.content}</div>
            </div>
          ))}
          {isLoading && (
            <div className="ai-message bot loading">
              <div className="ai-message-avatar">
                <Spin size="small" />
              </div>
              <div className="ai-message-content">Thinking...</div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {error && (
          <div className="ai-error-banner">
            <Text type="danger">{error}</Text>
          </div>
        )}

        <div className="ai-input-container">
          <Input.TextArea
            ref={inputRef}
            className="ai-input"
            placeholder="Type your message..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyPress}
            autoSize={{ minRows: 1, maxRows: 4 }}
            disabled={isLoading}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={isLoading}
            disabled={!inputValue.trim()}
            className="ai-send-btn"
          />
        </div>
      </div>
    </div>
  );
}