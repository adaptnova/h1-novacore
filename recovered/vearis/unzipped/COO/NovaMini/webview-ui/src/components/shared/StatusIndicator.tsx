import React from 'react';
import { StatusIndicatorProps } from '../../types';

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status }) => {
  const getStatusColor = () => {
    if (!status.isAvailable) return '#ff4444'; // Red
    if (status.errorRate > 0.01) return '#ffaa44'; // Orange
    if (status.responseTime > 1000) return '#ffff44'; // Yellow
    return '#44ff44'; // Green
  };

  const getStatusText = () => {
    if (!status.isAvailable) return 'Offline';
    if (status.errorRate > 0.01) return 'Degraded';
    if (status.responseTime > 1000) return 'Slow';
    return 'Online';
  };

  const getCapabilityBadges = () => {
    return status.capabilities.map((capability, index) => (
      <span key={index} className="capability-badge">
        {capability}
      </span>
    ));
  };

  const formatUptime = (uptime: number) => {
    const hours = Math.floor(uptime / 3600);
    const minutes = Math.floor((uptime % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  return (
    <div className="status-indicator">
      <div className="status-main">
        <div 
          className="status-dot"
          style={{ backgroundColor: getStatusColor() }}
        />
        <span className="status-text">{getStatusText()}</span>
      </div>
      
      <div className="status-details">
        <div className="status-metric">
          <span className="metric-label">Response:</span>
          <span className="metric-value">
            {status.responseTime}ms
          </span>
        </div>
        
        <div className="status-metric">
          <span className="metric-label">Error Rate:</span>
          <span className="metric-value">
            {(status.errorRate * 100).toFixed(2)}%
          </span>
        </div>
        
        <div className="status-metric">
          <span className="metric-label">Uptime:</span>
          <span className="metric-value">
            {formatUptime(status.uptime)}
          </span>
        </div>
      </div>

      <div className="capability-badges">
        {getCapabilityBadges()}
      </div>

      <style jsx>{`
        .status-indicator {
          padding: 8px;
          border-radius: 4px;
          background: var(--vscode-editor-background);
          border: 1px solid var(--vscode-panel-border);
        }

        .status-main {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }

        .status-details {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 8px;
          margin-bottom: 8px;
        }

        .status-metric {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
        }

        .metric-label {
          font-size: 0.8em;
          color: var(--vscode-descriptionForeground);
        }

        .capability-badges {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
        }

        .capability-badge {
          padding: 2px 6px;
          border-radius: 12px;
          background: var(--vscode-badge-background);
          color: var(--vscode-badge-foreground);
          font-size: 0.8em;
        }
      `}</style>
    </div>
  );
};

export default StatusIndicator;