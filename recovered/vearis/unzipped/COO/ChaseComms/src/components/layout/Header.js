import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { COLORS } from '../../styles/GlobalStyles';
import monitoringService from '../../services/MonitoringService';

const HeaderContainer = styled.header`
  background: ${COLORS.background};
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid ${COLORS.border};
`;

const TopBar = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 40px;
`;

const ProjectInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
`;

const ProjectName = styled.div`
  font-size: 16px;
  font-weight: 500;
  color: ${COLORS.textBright};
  display: flex;
  align-items: center;
  gap: 10px;

  .version {
    font-size: 12px;
    color: ${COLORS.textDim};
    font-weight: normal;
  }
`;

const StatusIndicators = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
  overflow-x: auto;
  padding: 0 10px;

  &::-webkit-scrollbar {
    display: none;
  }
`;

const Controls = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
`;

const SettingsButton = styled.button`
  background: transparent;
  border: none;
  color: ${COLORS.text};
  width: 32px;
  height: 32px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    color: ${COLORS.accent};
    background: rgba(0, 204, 0, 0.1);
  }

  .icon {
    font-size: 18px;
  }
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  position: relative;
  padding: 4px;
  cursor: help;

  &:hover .tooltip {
    opacity: 1;
    visibility: visible;
    transform: translateX(-50%) translateY(0);
  }
`;

const StatusDot = styled.div`
  width: 6px;
  height: 6px;
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

const StatusLabel = styled.span`
  font-size: 11px;
  color: ${COLORS.textDim};
  min-width: 40px;
`;

const StatusValue = styled.span`
  font-size: 11px;
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

const StatusTooltip = styled.div`
  position: absolute;
  top: calc(100% + 10px);
  left: 50%;
  transform: translateX(-50%) translateY(-5px);
  background: ${COLORS.overlay};
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid ${props => {
    switch(props.$status) {
      case 'critical': return COLORS.error;
      case 'warning': return COLORS.warning;
      case 'healthy': return COLORS.success;
      default: return COLORS.border;
    }
  }};
  font-size: 11px;
  white-space: pre-wrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  z-index: 9999;
  min-width: 150px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);

  .title {
    color: ${COLORS.textBright};
    font-weight: bold;
    margin-bottom: 4px;
  }

  &::before {
    content: '';
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 4px solid transparent;
    border-bottom-color: ${props => {
      switch(props.$status) {
        case 'critical': return COLORS.error;
        case 'warning': return COLORS.warning;
        case 'healthy': return COLORS.success;
        default: return COLORS.border;
      }
    }};
  }
`;

const Header = () => {
  const [serviceStatuses, setServiceStatuses] = useState([]);

  useEffect(() => {
    const updateStatuses = () => {
      const health = monitoringService.getSystemHealth();

      const statuses = [
        // PostgreSQL
        {
          name: 'PostgreSQL',
          label: 'PG',
          status: health?.components?.postgresql?.healthy ? 'healthy' : 'critical',
          value: `${health?.components?.postgresql?.responseTime || '0'}ms`,
          details: `Host: nova-postgres.internal
Port: 5432
Response Time: ${health?.components?.postgresql?.responseTime || 'N/A'}ms
Connections: ${health?.components?.postgresql?.connections || 'N/A'}`
        },
        // Redis
        {
          name: 'Redis',
          label: 'RD',
          status: health?.components?.redis?.healthy ? 'healthy' : 'critical',
          value: `${health?.components?.redis?.memory || '0'}%`,
          details: `Host: nova-redis.internal
Port: 6379
Memory Usage: ${health?.components?.redis?.memory || 'N/A'}%
Keys: ${health?.components?.redis?.keys || 'N/A'}`
        },
        // RabbitMQ
        {
          name: 'RabbitMQ',
          label: 'RQ',
          status: health?.components?.rabbitmq?.healthy ? 'healthy' : 'critical',
          value: `${health?.components?.rabbitmq?.messages || '0'}/s`,
          details: `Host: nova-rabbitmq.internal
Ports: 5672, 15672
Messages/s: ${health?.components?.rabbitmq?.messages || 'N/A'}
Channels: ${health?.components?.rabbitmq?.channels || 'N/A'}`
        }
      ];

      setServiceStatuses(statuses);
    };

    // Initial update
    updateStatuses();

    // Subscribe to monitoring updates
    const unsubscribe = monitoringService.subscribe(() => {
      updateStatuses();
    });

    return () => unsubscribe();
  }, []);

  return (
    <HeaderContainer>
      <TopBar>
        <ProjectInfo>
          <ProjectName>
            NOVA COMMS
            <span className="version">v1.1.0</span>
          </ProjectName>
          <StatusIndicators>
            {serviceStatuses.map((service, index) => (
              <StatusIndicator key={index}>
                <StatusDot $status={service.status} />
                <StatusLabel>{service.label}</StatusLabel>
                {service.value && (
                  <StatusValue $status={service.status}>
                    {service.value}
                  </StatusValue>
                )}
                <StatusTooltip $status={service.status} className="tooltip">
                  <div className="title">{service.name}</div>
                  {service.details}
                </StatusTooltip>
              </StatusIndicator>
            ))}
          </StatusIndicators>
        </ProjectInfo>
        <Controls>
          <SettingsButton>
            <span className="icon">⚙</span>
          </SettingsButton>
        </Controls>
      </TopBar>
    </HeaderContainer>
  );
};

export default Header;
