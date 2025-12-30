import React from 'react';
import { useEffect } from 'react';
import { createRoot } from 'react-dom/client';

const ChatbotInjector = () => {
  useEffect(() => {
    // Dynamically load the chatbot component when DOM is ready
    const loadChatbot = async () => {
      // Wait for the DOM to be fully loaded
      if (document.readyState !== 'loading') {
        // Create the container for the chatbot
        let chatbotContainer = document.getElementById('chatbot-root');
        if (!chatbotContainer) {
          chatbotContainer = document.createElement('div');
          chatbotContainer.id = 'chatbot-root';
          document.body.appendChild(chatbotContainer);
        }

        // Import and render the chatbot component
        const { default: ChatbotWidget } = await import('../components/ChatbotWidget');

        const root = createRoot(chatbotContainer);
        root.render(<ChatbotWidget />);
      }
    };

    loadChatbot();
  }, []);

  // This component doesn't render anything visible
  return null;
};

export default ChatbotInjector;