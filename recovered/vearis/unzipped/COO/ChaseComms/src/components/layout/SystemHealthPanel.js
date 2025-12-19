import React, { useEffect, useState, useCallback } from 'react';
import styled, { keyframes, css } from 'styled-components';
import { COLORS } from '../../styles/GlobalStyles';
import monitoringService from '../../services/MonitoringService';

const quantumPulse = keyframes`
  0% {
    transform: scale(1) rotate(0deg);
    filter: brightness(1) saturate(1);
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
  }
  50% {
    transform: scale(1.1) rotate(180deg);
    filter: brightness(1.3) saturate(1.5);
    box-shadow: 0 0 40px rgba(0, 255, 0, 0.5),
                0 0 60px rgba(0, 255, 0, 0.3),
                0 0 80px rgba(0, 255, 0, 0.2);
  }
  100% {
    transform: scale(1) rotate(360deg);
    filter: brightness(1) saturate(1);
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
  }
`;

const plasmaField = keyframes`
  0% {
    background-position: 0% 0%;
    filter: hue-rotate(0deg) brightness(1);
    opacity: 0.5;
  }
  50% {
    background-position: 100% 100%;
    filter: hue-rotate(180deg) brightness(1.3);
    opacity: 0.8;
  }
  100% {
    background-position: 0% 0%;
    filter: hue-rotate(360deg) brightness(1);
    opacity: 0.5;
  }
`;

const statusGlow = keyframes`
  0% {
    box-shadow: 0 0 10px currentColor;
    filter: brightness(1);
  }
  50% {
    box-shadow: 0 0 30px currentColor,
                0 0 50px currentColor;
    filter: brightness(1.5);
  }
  100% {
    box-shadow: 0 0 10px currentColor;
    filter: brightness(1);
  }
`;

const PanelContainer = styled.div`
  display: flex;
  flex-direction: column;
  background: linear-gradient(
    135deg,
    rgba(0, 0, 0, 0.95) 0%,
    rgba(10, 10, 10, 0.98) 100%
  );
  border-top: 2px solid ${COLORS.border};
  padding: 15px;
  gap: 15px;
  position: relative;
  transform-style: preserve-3d;
  perspective: 1000px;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
      135deg,
      rgba(0, 255, 0, 0.05) 0%,
      transparent 50%,
      rgba(0, 255, 0, 0.05) 100%
    );
    pointer-events: none;
    animation: ${plasmaField} 10s linear infinite;
  }

  &::after {
    content: '';
    position: absolute;
    top: -2px;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(
      to right,
      transparent 0%,
      rgba(0, 255, 0, 0.8) 50%,
      transparent 100%
    );
    animation: ${quantumPulse} 5s infinite;
  }
`;

const IndicatorsRow = styled.div`
  display: flex;
  align-items: center;
  gap: 25px;
  justify-content: center;
  padding: 15px;
  background: linear-gradient(
    135deg,
    rgba(0, 0, 0, 0.95) 0%,
    rgba(10, 10, 10, 0.98) 100%
  );
  border-radius: 12px;
  position: relative;
  transform-style: preserve-3d;
  perspective: 1000px;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 12px;
    background: linear-gradient(
      135deg,
      rgba(0, 255, 0, 0.05) 0%,
      transparent 50%,
      rgba(0, 255, 0, 0.05) 100%
    );
    pointer-events: none;
    animation: ${plasmaField} 10s linear infinite;
    opacity: 0.5;
  }

  &::after {
    content: '';
    position: absolute;
    inset: -1px;
    border-radius: 12px;
    border: 1px solid rgba(0, 255, 0, 0.3);
    background: radial-gradient(
      circle at center,
      rgba(0, 255, 0, 0.1) 0%,
      transparent 70%
    );
    animation: ${quantumPulse} 5s infinite;
    pointer-events: none;
  }

  &:hover::after {
    animation: ${quantumPulse} 2s infinite;
  }
`;

const Indicator = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
  cursor: help;
  padding: 8px 12px;
  border-radius: 8px;
  transform-style: preserve-3d;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 8px;
    background: linear-gradient(
      135deg,
      rgba(0, 255, 0, 0.05) 0%,
      transparent 50%,
      rgba(0, 255, 0, 0.05) 100%
    );
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  &:hover {
    transform: translateZ(10px);

    &::before {
      opacity: 1;
      animation: ${plasmaField} 2s infinite;
    }

    .tooltip {
      opacity: 1;
      visibility: visible;
      transform: translateY(0) translateZ(20px);
    }
  }
`;

const StatusDot = styled.div`
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: ${props => {
    const color = props.$status === 'critical' ? COLORS.error :
                 props.$status === 'warning' ? COLORS.warning :
                 props.$status === 'healthy' ? COLORS.success :
                 COLORS.border;
    return `radial-gradient(circle at center,
      ${color} 0%,
      ${color}cc 50%,
      ${color}99 100%
    )`;
  }};
  position: relative;
  transform-style: preserve-3d;
  animation: ${props => props.$status === 'critical' ?
    css`${quantumPulse} 1s infinite` :
    props.$status === 'warning' ?
    css`${statusGlow} 2s infinite` :
    css`${plasmaField} 3s infinite`
  };

  &::before {
    content: '';
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    background: ${props => {
      const color = props.$status === 'critical' ? 'rgba(255, 0, 0, ' :
                   props.$status === 'warning' ? 'rgba(255, 204, 0, ' :
                   'rgba(0, 255, 0, ';
      return `radial-gradient(circle at center,
        ${color}0.3) 0%,
        transparent 70%
      )`;
    }};
    animation: ${props => props.$status === 'critical' ?
      css`${quantumPulse} 2s infinite` :
      props.$status === 'warning' ?
      css`${plasmaField} 3s infinite` :
      css`${statusGlow} 4s infinite`
    };
  }

  &::after {
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: 50%;
    border: 2px solid ${props => {
      switch(props.$status) {
        case 'critical': return COLORS.error;
        case 'warning': return COLORS.warning;
        case 'healthy': return COLORS.success;
        default: return COLORS.border;
      }
    }};
    opacity: 0.5;
    animation: ${statusGlow} 2s infinite;
  }
`;

const Label = styled.span`
  font-size: 12px;
  color: ${COLORS.text};
  white-space: nowrap;
  text-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
  transition: all 0.3s ease;
  position: relative;
  transform-style: preserve-3d;

  ${Indicator}:hover & {
    text-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
    transform: translateZ(5px);
  }
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
  text-shadow: ${props => {
    const color = props.$status === 'critical' ? 'rgba(255, 0, 0, ' :
                 props.$status === 'warning' ? 'rgba(255, 204, 0, ' :
                 'rgba(0, 255, 0, ';
    return `0 0 10px ${color}0.5)`;
  }};
  transition: all 0.3s ease;
  position: relative;
  transform-style: preserve-3d;

  ${Indicator}:hover & {
    text-shadow: ${props => {
      const color = props.$status === 'critical' ? 'rgba(255, 0, 0, ' :
                   props.$status === 'warning' ? 'rgba(255, 204, 0, ' :
                   'rgba(0, 255, 0, ';
      return `0 0 15px ${color}0.7)`;
    }};
    transform: translateZ(5px);
  }
`;

const Tooltip = styled.div`
  position: absolute;
  bottom: calc(100% + 15px);
  left: 50%;
  transform: translateX(-50%) translateY(5px) translateZ(0);
  background: linear-gradient(
    135deg,
    rgba(0, 0, 0, 0.95) 0%,
    rgba(10, 10, 10, 0.98) 100%
  );
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 11px;
  white-space: pre-wrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 9999;
  min-width: 180px;
  transform-style: preserve-3d;
  border: 2px solid ${props => {
    switch(props.$status) {
      case 'critical': return COLORS.error;
      case 'warning': return COLORS.warning;
      case 'healthy': return COLORS.success;
      default: return COLORS.border;
    }
  }};
  box-shadow: ${props => {
    const color = props.$status === 'critical' ? 'rgba(255, 0, 0, ' :
                 props.$status === 'warning' ? 'rgba(255, 204, 0, ' :
                 'rgba(0, 255, 0, ';
    return `0 0 20px ${color}0.3),
            0 0 40px ${color}0.2)`;
  }};

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 6px;
    background: ${props => {
      const color = props.$status === 'critical' ? 'rgba(255, 0, 0, ' :
                   props.$status === 'warning' ? 'rgba(255, 204, 0, ' :
                   'rgba(0, 255, 0, ';
      return `radial-gradient(circle at center,
        ${color}0.1) 0%,
        transparent 70%
      )`;
    }};
    animation: ${plasmaField} 4s infinite;
    pointer-events: none;
  }

  .title {
    color: ${COLORS.textBright};
    font-weight: bold;
    margin-bottom: 6px;
    text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
  }

  &::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 6px solid transparent;
    border-top-color: ${props => {
      switch(props.$status) {
        case 'critical': return COLORS.error;
        case 'warning': return COLORS.warning;
        case 'healthy': return COLORS.success;
        default: return COLORS.border;
      }
    }};
    filter: drop-shadow(0 0 5px rgba(0, 255, 0, 0.5));
  }
`;

const MetricsRow = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 15px 20px;
  font-size: 11px;
  color: ${COLORS.textDim};
  background: linear-gradient(
    135deg,
    rgba(0, 0, 0, 0.95) 0%,
    rgba(10, 10, 10, 0.98) 100%
  );
  border-radius: 8px;
  position: relative;
  transform-style: preserve-3d;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 8px;
    background: linear-gradient(
      135deg,
      rgba(0, 255, 0, 0.05) 0%,
      transparent 50%,
      rgba(0, 255, 0, 0.05) 100%
    );
    pointer-events: none;
    animation: ${plasmaField} 8s linear infinite;
    opacity: 0.5;
  }

  span {
    position: relative;
    text-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
    transition: all 0.3s ease;
    transform-style: preserve-3d;
    padding: 5px 10px;
    border-radius: 4px;

    &:hover {
      text-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
      transform: translateZ(5px);
      background: rgba(0, 255, 0, 0.1);
      animation: ${quantumPulse} 2s infinite;
    }

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      border-radius: 4px;
      background: radial-gradient(
        circle at center,
        rgba(0, 255, 0, 0.1) 0%,
        transparent 70%
      );
      opacity: 0;
      transition: opacity 0.3s ease;
    }

    &:hover::before {
      opacity: 1;
      animation: ${plasmaField} 2s infinite;
    }
  }
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
