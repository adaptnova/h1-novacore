import React, { useEffect, useState, useCallback } from 'react';
import styled from 'styled-components';
import { COLORS } from '../../styles/GlobalStyles';
import monitoringService from '../../services/MonitoringService';

const PanelContainer = styled.div`
  display: flex;
  flex-direction: column;
  background: ${COLORS.background};
  border-top: 1px solid ${COLORS.border};
  padding: 10px;
  gap: 10px;
`;

const IndicatorsRow = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
  justify-content: center;
`;

const Indicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  cursor: help;

  &:hover .tooltip {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
  }
`;

const StatusDot = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: ${props => {
    switch(props.$status) {
      case 'critical': return COLORS.error;
      case 'warning': return COLORS.warning;
      case 'healthy': return COLORS.success;
      default: return COLORS.border;
    }
  }};
  position: relative;

  &::after {
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: 50%;
    border: 1px solid currentColor;
    opacity: 0.3;
  }
`;

const Label = styled.span`
  font-size: 12px;
  color: ${COLORS.text};
  white-space: nowrap;
`;

const Value = styled.span`
  font-size: 12px;
  font-family: monospace;
  color: ${props => {
    switch(props.$status) {
      case 'critical': return COLORS.error;
      case 'warning': return COLORS.warning;
      case 'healthy': return COLORS.success;
      default: return COLORS.textDim;
    }
  }};
`;

const Tooltip = styled.div`
  position: absolute;
  bottom: calc(100% + 10px);
  left: 50%;
  transform: translateX(-50%) translateY(5px);
  background: ${COLORS.overlay};
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 11px;
  white-space: pre-wrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  z-index: 9999;
  min-width: 150px;
  border: 1px solid ${props => {
    switch(props.$status) {
      case 'critical': return COLORS.error;
      case 'warning': return COLORS.warning;
      case 'healthy': return COLORS.success;
      default: return COLORS.border;
    }
  }};

  .title {
    color: ${COLORS.textBright};
    font-weight: bold;
    margin-bottom: 4px;
  }

  &::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 4px solid transparent;
    border-top-color: ${props => {
      switch(props.$status) {
        case 'critical': return COLORS.error;
        case 'warning': return COLORS.warning;
        case 'healthy': return COLORS.success;
        default: return COLORS.border;
      }
    }};
  }
`;

const MetricsRow = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 0 10px;
  font-size: 11px;
  color: ${COLORS.textDim};
`;

const SystemHealthPanel = () => {
  const [health, setHealth] = useState(null);
  const [performance, setPerformance] = useState(null);

  const updateMetrics = useCallback(() => {
    const systemHealth = monitoringService.getSystemHealth();
    const performanceMetrics = monitoringService.getPerformanceMetrics();
    
    setHealth(systemHealth);
    setPerformance(performanceMetrics);
  }, []);

  useEffect(() => {
    // Initialize monitoring service
    monitoringService.initialize();

    // Subscribe to updates
    const unsubscribe = monitoringService.subscribe((type, data) => {
      updateMetrics();
    });

    // Initial metrics update
    updateMetrics();

    return () => {
      unsubscribe();
    };
  }, [updateMetrics]);

  if (!health) return null;

  const getStatusIndicator = (component) => {
    const status = component?.healthy ? 'healthy' : component?.warning ? 'warning' : 'critical';
    return status;
  };

  const formatMetric = (value, unit = '') => {
    if (typeof value === 'number') {
      return `${value.toFixed(1)}${unit}`;
    }
    return 'N/A';
  };

  return (
    <PanelContainer>
      <IndicatorsRow>
        <Indicator>
          <StatusDot $status={getStatusIndicator(health.components.api)} />
          <Label>API</Label>
          <Value $status={getStatusIndicator(health.components.api)}>
            {formatMetric(performance?.avgResponseTime, 'ms')}
          </Value>
          <Tooltip $status={getStatusIndicator(health.components.api)} className="tooltip">
            <div className="title">API Health</div>
            Response Time: {formatMetric(performance?.avgResponseTime, 'ms')}
            Error Rate: {formatMetric(performance?.errorRate, '%')}
            Requests: {performance?.requestCount || 0}
          </Tooltip>
        </Indicator>

        <Indicator>
          <StatusDot $status={getStatusIndicator(health.components.circuitBreakers)} />
          <Label>Circuit Breakers</Label>
          <Tooltip $status={getStatusIndicator(health.components.circuitBreakers)} className="tooltip">
            <div className="title">Circuit Breakers</div>
            {Object.entries(performance?.circuitBreakerTrips || {}).map(([name, trips]) => (
              `${name}: ${trips} trips\n`
            ))}
          </Tooltip>
        </Indicator>

        <Indicator>
          <StatusDot $status={getStatusIndicator(health.components.memory)} />
          <Label>Memory</Label>
          <Value $status={getStatusIndicator(health.components.memory)}>
            {formatMetric(health.components.memory?.usage, '%')}
          </Value>
          <Tooltip $status={getStatusIndicator(health.components.memory)} className="tooltip">
            <div className="title">Memory Usage</div>
            Used: {formatMetric(health.components.memory?.usage, '%')}
            Available: {formatMetric(health.components.memory?.available, 'GB')}
          </Tooltip>
        </Indicator>

        <Indicator>
          <StatusDot $status={getStatusIndicator(health.components.patterns)} />
          <Label>Patterns</Label>
          <Value $status={getStatusIndicator(health.components.patterns)}>
            {formatMetric(health.components.patterns?.quality * 100, '%')}
          </Value>
          <Tooltip $status={getStatusIndicator(health.components.patterns)} className="tooltip">
            <div className="title">Pattern Quality</div>
            Quality: {formatMetric(health.components.patterns?.quality * 100, '%')}
            Strength: {formatMetric(health.components.patterns?.strength * 100, '%')}
            Rate: {formatMetric(health.components.patterns?.rate, '/min')}
          </Tooltip>
        </Indicator>
      </IndicatorsRow>

      <MetricsRow>
        <span>Response: {formatMetric(performance?.avgResponseTime, 'ms')}</span>
        <span>Errors: {formatMetric(performance?.errorRate, '%')}</span>
        <span>Requests: {performance?.requestCount || 0}</span>
        <span>Memory: {formatMetric(health.components.memory?.usage, '%')}</span>
      </MetricsRow>
    </PanelContainer>
  );
};

export default SystemHealthPanel;
