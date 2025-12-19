// Model and System Types
export interface ModelStatus {
  isAvailable: boolean;
  responseTime: number;
  errorRate: number;
  uptime: number;
  capabilities: string[];
}

export interface SystemHealth {
  dbConnection: boolean;
  messageQueue: boolean;
  apiGateway: boolean;
  serviceMesh: boolean;
  performance: {
    cpu: number;
    memory: number;
    latency: number;
  };
}

// VSCode WebView Types
declare global {
  interface Window {
    vscode: {
      postMessage: (message: any) => void;
      getState: () => any;
      setState: (state: any) => void;
    };
  }
}

// Message Types
export interface ExtensionMessage {
  type: string;
  text?: string;
  model?: string;
  status?: ModelStatus;
  health?: SystemHealth;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: number;
}

// Component Props Types
export interface CodeBlockProps {
  content: string;
  language?: string;
}

export interface TokenCounterProps {
  text: string;
  maxTokens?: number;
}

export interface StatusIndicatorProps {
  status: ModelStatus;
}

// Configuration Types
export interface ModelConfig {
  id: string;
  name: string;
  capabilities: string[];
  maxTokens: number;
  responseTime: number;
}

export interface SystemConfig {
  theme: 'light' | 'dark';
  fontSize: number;
  showTokenCount: boolean;
  showPerformance: boolean;
}

// Performance Types
export interface PerformanceMetrics {
  responseTime: number;
  tokenRate: number;
  errorRate: number;
  uptime: number;
}

export interface ResourceUsage {
  cpu: number;
  memory: number;
  network: {
    in: number;
    out: number;
  };
}