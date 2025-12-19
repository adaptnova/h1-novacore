import React, { useEffect, useRef, useState } from 'react';
import { ModelStatus, SystemHealth } from '../../types';
import CodeBlock from '../shared/CodeBlock';
import TokenCounter from '../shared/TokenCounter';
import StatusIndicator from '../shared/StatusIndicator';

interface ChatViewProps {
  selectedModel: string;
  modelStatus: ModelStatus;
  systemHealth: SystemHealth;
}

export const ChatView: React.FC<ChatViewProps> = ({
  selectedModel,
  modelStatus,
  systemHealth,
}) => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Array<{role: string; content: string}>>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setInput('');
    setIsStreaming(true);

    try {
      // Start streaming response
      const response = await window.vscode.postMessage({
        type: 'sendMessage',
        text: input,
        model: selectedModel,
      });

      // Handle streaming response
      setMessages(prev => [...prev, { role: 'assistant', content: response }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: 'Error: Failed to get response' 
      }]);
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="status-bar">
        <StatusIndicator status={modelStatus} />
        <div className="model-info">
          <span className="model-name">{selectedModel}</span>
          <span className="response-time">{modelStatus.responseTime}ms</span>
        </div>
      </div>

      <div className="messages-container">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            {msg.content.includes('```') ? (
              <CodeBlock content={msg.content} />
            ) : (
              <p>{msg.content}</p>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="input-form">
        <TokenCounter text={input} />
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={isStreaming}
          rows={3}
        />
        <button type="submit" disabled={isStreaming || !modelStatus.isAvailable}>
          {isStreaming ? 'Processing...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default ChatView;