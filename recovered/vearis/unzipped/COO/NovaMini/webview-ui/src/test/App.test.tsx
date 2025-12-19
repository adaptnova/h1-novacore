import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../App';

// Mock VSCode API
const mockPostMessage = jest.fn();
(global as any).vscode = {
  postMessage: mockPostMessage,
};

describe('App Component', () => {
  beforeEach(() => {
    mockPostMessage.mockClear();
  });

  test('renders chat interface', () => {
    render(<App />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  test('sends message on submit', async () => {
    render(<App />);
    const input = screen.getByRole('textbox');
    const testMessage = 'Hello, Nova!';

    fireEvent.change(input, { target: { value: testMessage } });
    fireEvent.submit(input);

    await waitFor(() => {
      expect(mockPostMessage).toHaveBeenCalledWith({
        type: 'sendMessage',
        text: testMessage,
        model: 'gpt-4o',
      });
    });
  });

  test('updates model status', async () => {
    render(<App />);
    const mockStatus = {
      isAvailable: true,
      responseTime: 300,
      errorRate: 0,
      uptime: 3600,
      capabilities: ['chat', 'code'],
    };

    // Simulate message from extension
    window.dispatchEvent(
      new MessageEvent('message', {
        data: {
          type: 'updateModelStatus',
          status: mockStatus,
        },
      })
    );

    await waitFor(() => {
      expect(screen.getByText('Online')).toBeInTheDocument();
      expect(screen.getByText('300ms')).toBeInTheDocument();
    });
  });

  test('updates system health', async () => {
    render(<App />);
    const mockHealth = {
      dbConnection: true,
      messageQueue: true,
      apiGateway: true,
      serviceMesh: true,
      performance: {
        cpu: 30,
        memory: 40,
        latency: 50,
      },
    };

    // Simulate message from extension
    window.dispatchEvent(
      new MessageEvent('message', {
        data: {
          type: 'updateSystemHealth',
          health: mockHealth,
        },
      })
    );

    await waitFor(() => {
      expect(screen.getByText('CPU: 30%')).toBeInTheDocument();
      expect(screen.getByText('Memory: 40%')).toBeInTheDocument();
    });
  });

  test('handles code blocks', async () => {
    render(<App />);
    const codeMessage = '```typescript\nconst x = 1;\n```';

    // Simulate receiving a code message
    window.dispatchEvent(
      new MessageEvent('message', {
        data: {
          type: 'receiveMessage',
          role: 'assistant',
          content: codeMessage,
        },
      })
    );

    await waitFor(() => {
      expect(screen.getByText('typescript')).toBeInTheDocument();
      expect(screen.getByText('const x = 1;')).toBeInTheDocument();
    });
  });

  test('shows token counter', () => {
    render(<App />);
    const input = screen.getByRole('textbox');
    const testMessage = 'Hello, Nova!';

    fireEvent.change(input, { target: { value: testMessage } });

    expect(screen.getByText('3 / 8192')).toBeInTheDocument();
  });

  test('disables input when processing', async () => {
    render(<App />);
    const input = screen.getByRole('textbox');
    const submitButton = screen.getByText('Send');

    fireEvent.change(input, { target: { value: 'Test' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(input).toBeDisabled();
      expect(submitButton).toBeDisabled();
      expect(screen.getByText('Processing...')).toBeInTheDocument();
    });
  });
});