import React, { useState, useEffect, useCallback } from 'react';

// Create a wrapper component without using the color mode hook directly
const ChatbotWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Don't use the color mode hook directly to avoid context errors
  // Instead, we'll use CSS that adapts to the theme automatically
  const effectiveColorMode = 'light'; // Default value, CSS will handle theme adaptation

  // Always render the chatbot widget

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = { id: Date.now(), text: inputValue, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Use the deployed FastAPI backend URL
      // For browser environments, we can't use process.env, so we'll use a default
      // In production, you can set window.ENV or use a configuration file
      const API_BASE_URL = typeof window !== 'undefined' && window.ENV ? window.ENV.REACT_APP_API_BASE_URL : 'http://localhost:8000';
      const apiUrl = `${API_BASE_URL || 'http://localhost:8000'}/chat`;

      // Call the FastAPI backend
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: inputValue,
          conversation_id: 'docusaurus-chat-' + Date.now()
        }),
      });

      const data = await response.json();

      if (response.ok) {
        const botMessage = {
          id: Date.now() + 1,
          text: data.response,
          sender: 'bot',
          sources: data.sources || []
        };
        setMessages(prev => [...prev, botMessage]);
      } else {
        const errorMessage = {
          id: Date.now() + 1,
          text: `Error: ${data.error || 'Failed to get response'}`,
          sender: 'bot'
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        text: `Error: ${error.message}`,
        sender: 'bot'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbot-widget">
      {isOpen ? (
        <div className="chatbot-container">
          <div className="chatbot-header">
            <h3>Physical AI Assistant</h3>
            <button className="chatbot-close" onClick={toggleChat}>
              ×
            </button>
          </div>
          <div className="chatbot-messages">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`chatbot-message ${message.sender}`}
              >
                <div className="message-text">{message.text}</div>
              </div>
            ))}
            {isLoading && (
              <div className="chatbot-message bot">
                <div className="message-text">Thinking...</div>
              </div>
            )}
          </div>
          <form onSubmit={sendMessage} className="chatbot-input-form">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask about Physical AI & Humanoid Robotics..."
              className="chatbot-input"
              disabled={isLoading}
            />
            <button type="submit" className="chatbot-send" disabled={isLoading}>
              Send
            </button>
          </form>
        </div>
      ) : (
        <button className="chatbot-toggle" onClick={toggleChat}>
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12 2C6.48 2 2 6.48 2 12C2 13.54 2.36 15.01 3.02 16.35L2 22L7.65 20.98C8.99 21.64 10.46 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C8.69 20 6 17.31 6 14C6 10.69 8.69 8 12 8C15.31 8 18 10.69 18 14C18 17.31 15.31 20 12 20ZM13 9H11V11H13V9ZM13 13H11V17H13V13Z"
              fill="white"
            />
          </svg>
        </button>
      )}
      <style jsx>{`
        .chatbot-widget {
          position: fixed;
          bottom: 20px;
          right: 20px;
          z-index: 1000;
          font-family: inherit;
        }

        .chatbot-toggle {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          background: #667eea;
          border: none;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
          transition: all 0.3s ease;
        }

        .chatbot-toggle:hover {
          background: #5a6fd8;
          transform: scale(1.05);
          box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
        }

        .chatbot-toggle svg {
          transition: all 0.3s ease;
        }

        .chatbot-container {
          width: 350px;
          height: 500px;
          max-width: calc(100vw - 20px);
          max-height: calc(100vh - 20px);
          background: white;
          border-radius: 12px;
          box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
          display: flex;
          flex-direction: column;
          overflow: hidden;
          position: absolute;
          bottom: 80px; /* Position above the toggle button */
          right: 20px;
        }

        /* Use Docusaurus theme selector for dark mode */
        html[data-theme='dark'] .chatbot-container {
          background: #1c1e21;
        }

        .chatbot-header {
          background: #667eea;
          color: white;
          padding: 16px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .chatbot-header h3 {
          margin: 0;
          font-size: 16px;
        }

        .chatbot-close {
          background: none;
          border: none;
          color: white;
          font-size: 24px;
          cursor: pointer;
          padding: 0;
          width: 30px;
          height: 30px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .chatbot-messages {
          flex: 1;
          overflow-y: auto;
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 12px;
          background: #f8fafc;
        }

        html[data-theme='dark'] .chatbot-container .chatbot-messages {
          background: #2d3748;
        }

        .chatbot-message {
          max-width: 80%;
          padding: 12px 16px;
          border-radius: 18px;
          font-size: 14px;
          line-height: 1.4;
        }

        .chatbot-message.user {
          align-self: flex-end;
          background: #667eea;
          color: white;
          border-bottom-right-radius: 4px;
        }

        .chatbot-message.bot {
          align-self: flex-start;
          background: white;
          color: #334155;
          border-bottom-left-radius: 4px;
        }

        html[data-theme='dark'] .chatbot-container .chatbot-message.bot {
          background: #4a5568;
          color: white;
        }

        .message-sources {
          margin-top: 8px;
          font-size: 12px;
        }

        .message-sources ul {
          margin: 4px 0 0 0;
          padding-left: 16px;
        }

        .message-sources a {
          color: #667eea;
          text-decoration: none;
        }

        .message-sources a:hover {
          text-decoration: underline;
        }

        .chatbot-input-form {
          display: flex;
          padding: 16px;
          background: white;
          border-top: 1px solid #e2e8f0;
        }

        html[data-theme='dark'] .chatbot-container .chatbot-input-form {
          background: #2d3748;
          border-top: 1px solid #4a5568;
        }

        .chatbot-input {
          flex: 1;
          padding: 12px 16px;
          border: 1px solid #e2e8f0;
          border-radius: 24px;
          font-size: 14px;
          outline: none;
          background: #f8fafc;
        }

        html[data-theme='dark'] .chatbot-container .chatbot-input {
          background: #4a5568;
          color: white;
          border-color: #4a5568;
        }

        .chatbot-input:focus {
          border-color: #667eea;
        }

        .chatbot-send {
          background: #667eea;
          color: white;
          border: none;
          border-radius: 20px;
          padding: 12px 20px;
          margin-left: 8px;
          cursor: pointer;
          font-size: 14px;
        }

        .chatbot-send:hover {
          background: #5a6fd8;
        }

        .chatbot-send:disabled {
          background: #cbd5e0;
          cursor: not-allowed;
        }

        html[data-theme='dark'] .chatbot-container .chatbot-send:disabled {
          background: #718096;
        }
      `}</style>
    </div>
  );
};

export default ChatbotWidget;