import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { COLORS } from '../../styles/GlobalStyles';
import monitoringService from '../../services/MonitoringService';

const PanelContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: ${COLORS.background};
  position: relative;
  min-width: 0;
  opacity: ${props => props.$collapsed ? 0 : 1};
  visibility: ${props => props.$collapsed ? 'hidden' : 'visible'};
  transition: all 0.3s ease;
`;

const ConnectionBar = styled.div`
  padding: 8px 15px;
  background: ${props => props.$connected ? 'rgba(0, 204, 0, 0.05)' : 'rgba(255, 0, 0, 0.05)'};
  border-bottom: 1px solid ${props => props.$connected ? COLORS.success : COLORS.error};
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9em;
  color: ${props => props.$connected ? COLORS.success : COLORS.error};
  white-space: nowrap;
`;

const SyncButton = styled.button`
  background: transparent;
  border: none;
  color: ${COLORS.accent};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 5px;
  border-radius: 3px;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(0, 204, 0, 0.1);
  }

  .sync-icon {
    transition: transform 1s ease;
  }

  &:hover .sync-icon {
    transform: rotate(180deg);
  }
`;

const OutputSection = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  background: ${COLORS.background};

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: ${COLORS.background};
  }

  &::-webkit-scrollbar-thumb {
    background: ${COLORS.border};
    border-radius: 3px;
  }
`;

const OutputBox = styled.div`
  background: ${COLORS.background};
  border: 1px solid ${COLORS.border};
  border-radius: 4px;
  padding: 15px;
  font-family: monospace;
  white-space: pre-wrap;
  color: ${COLORS.textBright};
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 10px;
  padding: 15px;
  border-top: 1px solid ${COLORS.border};
  background: ${COLORS.background};
`;

const ActionButton = styled.button`
  flex: 1;
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: ${COLORS.text};
  border: 1px solid ${COLORS.border};
  background: ${COLORS.background};

  &.accept {
    background: rgba(0, 204, 0, 0.05);
    &:hover {
      border-color: ${COLORS.success};
      box-shadow: 0 0 5px ${COLORS.success};
    }
  }

  &.modify {
    background: rgba(204, 204, 0, 0.05);
    &:hover {
      border-color: ${COLORS.warning};
      box-shadow: 0 0 5px ${COLORS.warning};
    }
  }

  &.reject {
    background: rgba(204, 0, 0, 0.05);
    &:hover {
      border-color: ${COLORS.error};
      box-shadow: 0 0 5px ${COLORS.error};
    }
  }
`;

const BackendStatus = styled.div`
  padding: 4px 8px;
  font-size: 0.8em;
  color: ${COLORS.textDim};
  display: flex;
  align-items: center;
  gap: 8px;

  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: ${props => props.$connected ? COLORS.success : COLORS.error};
  }
`;

const AIOutputPanel = ({ collapsed, type = 'model' }) => {
  const [connected, setConnected] = useState(true);
  const [metrics, setMetrics] = useState(null);
  const [output, setOutput] = useState('');
  const isModel = type === 'model';

  useEffect(() => {
    const handleMetricsUpdate = (metricType, data) => {
      if ((isModel && metricType === 'api') || (!isModel && metricType === 'websocket')) {
        setMetrics(data);
        setConnected(data?.status === 'healthy');

        if (isModel && data?.analysis) {
          setOutput(data.analysis);
        } else if (!isModel && data?.queueStatus) {
          setOutput(data.queueStatus);
        }
      }
    };

    // Subscribe to monitoring service
    const unsubscribe = monitoringService.subscribe(handleMetricsUpdate);

    // Get initial metrics
    const initialMetrics = monitoringService.getLatestMetric(isModel ? 'api' : 'websocket');
    if (initialMetrics) {
      handleMetricsUpdate(isModel ? 'api' : 'websocket', initialMetrics);
    }

    return () => unsubscribe();
  }, [isModel]);

  const handleSync = () => {
    // Trigger immediate metrics update
    if (isModel) {
      monitoringService.checkAPIHealth();
    } else {
      // Force WebSocket reconnection for fresh data
      monitoringService.reconnectWebSocket();
    }
  };

  const getConnectionStatus = () => {
    if (isModel) {
      return {
        title: 'Connected to Model Service',
        details: metrics?.version || 'Model API v2.1.0',
        metrics: {
          latency: metrics?.responseTime || '35ms',
          requests: metrics?.requestRate || '1.2k/s'
        }
      };
    } else {
      return {
        title: 'RMQ',
        details: 'Message Queue Service',
        metrics: {
          channels: metrics?.channels || '12',
          messages: metrics?.messageRate || '1.2k/s',
          memory: metrics?.memoryUsage || '65%'
        }
      };
    }
  };

  const status = getConnectionStatus();

  const defaultOutput = isModel
    ? `Model Analysis Complete:
Detected anomaly in system performance metrics.
Recommendation: Scale up database resources.
Confidence: 87%`
    : `Queue Status:
Active Channels: ${status.metrics.channels}
Messages/sec: ${status.metrics.messages}
Memory Usage: ${status.metrics.memory}`;

  return (
    <PanelContainer $collapsed={collapsed}>
      <ConnectionBar $connected={connected}>
        <span>{status.title}</span>
        {!isModel && (
          <BackendStatus $connected={connected}>
            <div className="status-dot" />
            {`${status.metrics.channels} ch | ${status.metrics.messages} msg/s`}
          </BackendStatus>
        )}
        <SyncButton onClick={handleSync}>
          <span className="sync-icon">↻</span>
          Sync
        </SyncButton>
      </ConnectionBar>

      <OutputSection>
        <OutputBox>
          {output || defaultOutput}
        </OutputBox>
      </OutputSection>

      <ButtonGroup>
        <ActionButton className="accept">Accept</ActionButton>
        <ActionButton className="modify">Modify</ActionButton>
        <ActionButton className="reject">Reject</ActionButton>
      </ButtonGroup>
    </PanelContainer>
  );
};

export default AIOutputPanel;
