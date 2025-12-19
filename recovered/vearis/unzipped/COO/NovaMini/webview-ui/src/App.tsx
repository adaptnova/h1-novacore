import React, { useEffect, useState } from 'react';
import ChatView from '@components/chat/ChatView';
import { ModelStatus, SystemHealth } from '@types/index';

const App: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState<string>('gpt-4o');
  const [modelStatus, setModelStatus] = useState<ModelStatus>({
    isAvailable: true,
    responseTime: 300,
    errorRate: 0,
    uptime: 3600,
    capabilities: ['chat', 'code', 'analysis']
  });
  const [systemHealth, setSystemHealth] = useState<SystemHealth>({
    dbConnection: true,
    messageQueue: true,
    apiGateway: true,
    serviceMesh: true,
    performance: {
      cpu: 30,
      memory: 40,
      latency: 50
    }
  });

  useEffect(() => {
    // Listen for messages from the extension
    window.addEventListener('message', event => {
      const message = event.data;
      switch (message.type) {
        case 'updateModelStatus':
          setModelStatus(message.status);
          break;
        case 'updateSystemHealth':
          setSystemHealth(message.health);
          break;
        case 'modelSelected':
          setSelectedModel(message.model);
          break;
      }
    });

    // Initial state request
    window.vscode?.postMessage({ type: 'requestInitialState' });
  }, []);

  return (
    <div className="app-container">
      <ChatView
        selectedModel={selectedModel}
        modelStatus={modelStatus}
        systemHealth={systemHealth}
      />
      <style jsx>{`
        .app-container {
          height: 100vh;
          display: flex;
          flex-direction: column;
          background: var(--vscode-editor-background);
          color: var(--vscode-editor-foreground);
        }
      `}</style>
    </div>
  );
};

export default App;