import React, { useState, useEffect } from 'react';
import styled, { keyframes, css } from 'styled-components';
import { COLORS } from '../../styles/GlobalStyles';
import {
  ATLASSIAN_CONFIG,
  formatJiraTitle,
  ATLASSIAN_ERRORS,
  checkAtlassianStatus
} from '../../config/atlassian';

// Enhanced Animations
const buttonGlow = keyframes`
  0% {
    box-shadow: 0 0 10px ${COLORS.accent},
                inset 0 0 5px ${COLORS.accent};
    filter: brightness(1) saturate(1);
  }
  50% {
    box-shadow: 0 0 30px ${COLORS.accent},
                0 0 50px ${COLORS.accent},
                inset 0 0 15px ${COLORS.accent};
    filter: brightness(1.3) saturate(1.5);
  }
  100% {
    box-shadow: 0 0 10px ${COLORS.accent},
                inset 0 0 5px ${COLORS.accent};
    filter: brightness(1) saturate(1);
  }
`;

const energyPulse = keyframes`
  0% {
    transform: translateY(-50%) scale(1) rotate(0deg);
    opacity: 0.8;
    filter: hue-rotate(0deg);
  }
  50% {
    transform: translateY(-50%) scale(1.2) rotate(180deg);
    opacity: 1;
    filter: hue-rotate(180deg);
  }
  100% {
    transform: translateY(-50%) scale(1) rotate(360deg);
    opacity: 0.8;
    filter: hue-rotate(360deg);
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

const quantumBurst = keyframes`
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

const plasmaWave = keyframes`
  0% {
    transform: translateZ(0) scale(1);
    filter: hue-rotate(0deg) brightness(1);
  }
  50% {
    transform: translateZ(30px) scale(1.05);
    filter: hue-rotate(180deg) brightness(1.2);
  }
  100% {
    transform: translateZ(0) scale(1);
    filter: hue-rotate(360deg) brightness(1);
  }
`;

// Styled Components
const TaskPanelContainer = styled.div`
  width: ${props => props.$collapsed ? '50px' : '40%'};
  background: linear-gradient(
    135deg,
    rgba(0, 0, 0, 0.95) 0%,
    rgba(10, 10, 10, 0.98) 100%
  );
  border-right: 2px solid ${COLORS.accent};
  display: flex;
  flex-direction: column;
  height: 100%;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  min-width: ${props => props.$collapsed ? '50px' : '500px'};
  box-shadow: ${props => props.$collapsed ?
    'none' :
    `0 0 30px ${COLORS.accent},
     0 0 50px rgba(0, 255, 0, 0.2)`
  };
  transform-style: preserve-3d;
  perspective: 1000px;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(
      to right,
      transparent 0%,
      ${COLORS.accent} 50%,
      transparent 100%
    );
    box-shadow: 0 0 20px ${COLORS.accent};
    animation: ${plasmaWave} 5s infinite;
  }

  &::after {
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
    animation: ${plasmaField} 10s infinite;
  }

  &:hover {
    box-shadow: ${props => props.$collapsed ?
      'none' :
      `0 0 40px ${COLORS.accent},
       0 0 60px rgba(0, 255, 0, 0.3),
       0 0 80px rgba(0, 255, 0, 0.2)`
    };
  }
`;

const CollapseButton = styled.button`
  position: absolute;
  right: -15px;
  top: 50%;
  transform: translateY(-50%);
  width: 30px;
  height: 30px;
  background: ${COLORS.primary};
  border: 2px solid ${COLORS.accent};
  border-radius: 50%;
  color: ${COLORS.accent};
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: ${buttonGlow} 3s infinite;
  transform-style: preserve-3d;
  text-shadow: 0 0 10px ${COLORS.accent};

  &::before {
    content: '';
    position: absolute;
    top: -6px;
    left: -6px;
    right: -6px;
    bottom: -6px;
    border-radius: 50%;
    border: 2px solid ${COLORS.accent};
    opacity: 0.5;
    animation: ${energyPulse} 3s infinite;
  }

  &::after {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    border-radius: 50%;
    background: radial-gradient(
      circle at center,
      rgba(0, 255, 0, 0.2) 0%,
      transparent 70%
    );
    animation: ${plasmaField} 4s infinite;
    pointer-events: none;
    mix-blend-mode: screen;
  }

  &:hover {
    background: ${COLORS.secondary};
    transform: translateY(-50%) scale(1.1) translateZ(10px);
    animation: ${buttonGlow} 1s infinite, ${quantumBurst} 2s infinite;
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.4),
                0 0 40px rgba(0, 255, 0, 0.2);

    &::before {
      animation: ${energyPulse} 1s infinite, ${plasmaWave} 2s infinite;
    }

    &::after {
      animation: ${plasmaField} 2s infinite, ${quantumBurst} 3s infinite;
    }
  }

  &:active {
    transform: translateY(-50%) scale(0.95) translateZ(-5px);
    transition: transform 0.1s;
  }
`;

const CollapsedContent = styled.div`
  writing-mode: vertical-rl;
  text-orientation: mixed;
  transform: rotate(180deg);
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${COLORS.accent};
  padding: 25px 0;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 3px;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.95) 0%,
    rgba(10, 10, 10, 0.98) 50%,
    rgba(0, 0, 0, 0.95) 100%
  );
  position: relative;
  text-shadow: 0 0 15px ${COLORS.accent};
  transform-style: preserve-3d;
  perspective: 1000px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: conic-gradient(
      from 0deg at 50% 50%,
      transparent 0%,
      rgba(0, 255, 0, 0.1) 25%,
      rgba(0, 255, 0, 0.2) 50%,
      rgba(0, 255, 0, 0.1) 75%,
      transparent 100%
    );
    animation: ${plasmaField} 8s linear infinite;
    opacity: 0.5;
    mix-blend-mode: screen;
  }

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
      to bottom,
      transparent 0%,
      rgba(0, 255, 0, 0.15) 50%,
      transparent 100%
    );
    animation: ${plasmaWave} 4s infinite;
    pointer-events: none;
  }

  &:hover {
    text-shadow: 0 0 20px ${COLORS.accent},
                 0 0 40px ${COLORS.accent};
    letter-spacing: 4px;
    transform: rotate(180deg) translateZ(10px);

    &::before {
      animation: ${plasmaField} 4s linear infinite,
                 ${quantumBurst} 3s infinite;
      opacity: 0.7;
    }

    &::after {
      animation: ${plasmaWave} 2s infinite,
                 ${energyPulse} 3s infinite;
    }
  }
`;

const SectionHeader = styled.div`
  padding: 15px 20px;
  background: linear-gradient(
    135deg,
    rgba(0, 0, 0, 0.95) 0%,
    rgba(10, 10, 10, 0.98) 100%
  );
  border-bottom: 2px solid ${COLORS.border};
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
    animation: ${plasmaField} 8s linear infinite;
    opacity: 0.5;
  }

  &:hover {
    background: ${COLORS.secondary};
    border-bottom-color: ${COLORS.accent};
    transform: translateZ(10px);
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);

    &::before {
      animation: ${plasmaField} 4s linear infinite,
                 ${quantumBurst} 3s infinite;
      opacity: 0.7;
    }

    .arrow {
      animation: ${energyPulse} 1s infinite,
                 ${plasmaWave} 2s infinite;
      background: rgba(0, 204, 0, 0.2);
      box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
    }
  }

  .arrow {
    color: ${COLORS.accent};
    font-size: 12px;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 204, 0, 0.1);
    border-radius: 4px;
    margin-right: 10px;
    transition: all 0.3s ease;
    position: relative;
    transform-style: preserve-3d;

    &::before {
      content: '';
      position: absolute;
      top: -2px;
      left: -2px;
      right: -2px;
      bottom: -2px;
      border-radius: 6px;
      background: radial-gradient(
        circle at center,
        rgba(0, 255, 0, 0.2) 0%,
        transparent 70%
      );
      animation: ${plasmaField} 4s infinite;
      pointer-events: none;
    }
  }
`;

const SectionTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  color: ${COLORS.accent};
  font-size: 0.9em;
  font-weight: 500;
  text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
  position: relative;
  transform-style: preserve-3d;
  transition: all 0.3s ease;

  &:hover {
    transform: translateZ(5px);
    text-shadow: 0 0 15px rgba(0, 255, 0, 0.7),
                 0 0 30px rgba(0, 255, 0, 0.3);
  }

  &::before {
    content: '';
    position: absolute;
    top: -10px;
    left: -10px;
    right: -10px;
    bottom: -10px;
    background: radial-gradient(
      circle at center,
      rgba(0, 255, 0, 0.1) 0%,
      transparent 70%
    );
    animation: ${plasmaField} 5s infinite;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  &:hover::before {
    opacity: 1;
  }
`;

const SectionContent = styled.div`
  background: ${COLORS.primary};
  overflow: hidden;
  transition: height 0.3s ease;
  height: ${props => props.$expanded ? 'auto' : '0'};
  display: ${props => props.$expanded ? 'block' : 'none'};
`;

const FilterSection = styled.div`
  padding: 10px;
  border-bottom: 1px solid ${COLORS.border};
  background: ${COLORS.primary};
`;

const FilterGroup = styled.div`
  margin-bottom: 8px;

  &:last-child {
    margin-bottom: 0;
  }
`;

const FilterLabel = styled.div`
  font-size: 0.8em;
  color: ${COLORS.textDim};
  margin-bottom: 4px;
`;

const Select = styled.select`
  width: 100%;
  padding: 8px;
  background: ${COLORS.secondary};
  border: 1px solid ${COLORS.border};
  color: ${COLORS.text};
  border-radius: 4px;
  margin-bottom: 5px;

  &:focus {
    border-color: ${COLORS.accent};
    box-shadow: 0 0 5px ${COLORS.accent};
    outline: none;
  }
`;

const TaskList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 10px;

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: ${COLORS.primary};
  }

  &::-webkit-scrollbar-thumb {
    background: ${COLORS.border};
    border-radius: 4px;
  }
`;

const TaskItem = styled.div`
  padding: 15px;
  margin: 8px 0;
  background: ${COLORS.primary};
  border: 2px solid ${props => {
    switch(props.$priority) {
      case 'high': return COLORS.error;
      case 'medium': return COLORS.warning;
      case 'low': return COLORS.success;
      default: return COLORS.border;
    }
  }};
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
    background: ${props => {
      const color = props.$priority === 'high' ? 'rgba(255, 0, 0, 0.1)' :
                   props.$priority === 'medium' ? 'rgba(255, 204, 0, 0.1)' :
                   'rgba(0, 255, 0, 0.1)';
      return `radial-gradient(circle at center,
        ${color} 0%,
        transparent 70%
      )`;
    }};
    border-radius: 6px;
    animation: ${props => props.$priority === 'high' ?
      css`${quantumBurst} 3s infinite` :
      props.$priority === 'medium' ?
      css`${plasmaWave} 4s infinite` :
      css`${plasmaField} 5s infinite`
    };
    pointer-events: none;
    opacity: 0.5;
  }

  &:hover {
    transform: translateZ(20px) scale(1.02) rotateX(2deg);
    background: ${COLORS.secondary};
    box-shadow: ${props => {
      const color = props.$priority === 'high' ? 'rgba(255, 0, 0, ' :
                   props.$priority === 'medium' ? 'rgba(255, 204, 0, ' :
                   'rgba(0, 255, 0, ';
      return `0 0 30px ${color}0.3),
              0 0 50px ${color}0.2),
              0 0 70px ${color}0.1)`;
    }};

    &::before {
      opacity: 0.8;
      animation: ${props => props.$priority === 'high' ?
        css`${quantumBurst} 2s infinite, ${plasmaWave} 3s infinite` :
        props.$priority === 'medium' ?
        css`${plasmaWave} 2s infinite, ${plasmaField} 3s infinite` :
        css`${plasmaField} 2s infinite, ${energyPulse} 3s infinite`
      };
    }
  }
`;

const TaskHeader = styled.div`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 5px;
`;

const TaskTitle = styled.div`
  font-weight: 500;
`;

const TaskMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 5px;
`;

const TeamTag = styled.span`
  background: ${COLORS.secondary};
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.8em;
  color: ${COLORS.accent};
`;

const StatusTag = styled.span`
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.8em;
  position: relative;
  transform-style: preserve-3d;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: ${props => {
    switch(props.$status) {
      case 'in_progress': return 'rgba(0, 255, 255, 0.15)';
      case 'blocked': return 'rgba(255, 0, 0, 0.15)';
      case 'review': return 'rgba(255, 255, 0, 0.15)';
      default: return 'rgba(128, 128, 128, 0.15)';
    }
  }};
  color: ${props => {
    switch(props.$status) {
      case 'in_progress': return '#00FFFF';
      case 'blocked': return COLORS.error;
      case 'review': return COLORS.warning;
      default: return COLORS.textDim;
    }
  }};
  text-shadow: 0 0 10px ${props => {
    switch(props.$status) {
      case 'in_progress': return 'rgba(0, 255, 255, 0.5)';
      case 'blocked': return 'rgba(255, 0, 0, 0.5)';
      case 'review': return 'rgba(255, 255, 0, 0.5)';
      default: return 'rgba(128, 128, 128, 0.5)';
    }
  }};
  animation: ${props => {
    switch(props.$status) {
      case 'in_progress': return css`${plasmaWave} 4s infinite`;
      case 'blocked': return css`${quantumBurst} 2s infinite`;
      case 'review': return css`${plasmaField} 3s infinite`;
      default: return 'none';
    }
  }};

  &::before {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    border-radius: 14px;
    background: ${props => {
      const color = props.$status === 'in_progress' ? 'rgba(0, 255, 255, ' :
                   props.$status === 'blocked' ? 'rgba(255, 0, 0, ' :
                   props.$status === 'review' ? 'rgba(255, 255, 0, ' :
                   'rgba(128, 128, 128, ';
      return `radial-gradient(circle at center,
        ${color}0.2) 0%,
        transparent 70%
      )`;
    }};
    animation: ${props => {
      switch(props.$status) {
        case 'in_progress': return css`${energyPulse} 3s infinite`;
        case 'blocked': return css`${plasmaWave} 2s infinite`;
        case 'review': return css`${quantumBurst} 4s infinite`;
        default: return 'none';
      }
    }};
    pointer-events: none;
  }

  &:hover {
    transform: translateZ(10px) scale(1.1);
    box-shadow: ${props => {
      const color = props.$status === 'in_progress' ? 'rgba(0, 255, 255, ' :
                   props.$status === 'blocked' ? 'rgba(255, 0, 0, ' :
                   props.$status === 'review' ? 'rgba(255, 255, 0, ' :
                   'rgba(128, 128, 128, ';
      return `0 0 20px ${color}0.5),
              0 0 40px ${color}0.3),
              0 0 60px ${color}0.1)`;
    }};
  }
`;

const JiraLink = styled.a`
  color: ${COLORS.accent};
  text-decoration: none;
  font-size: 0.8em;
  display: flex;
  align-items: center;
  gap: 4px;

  &:hover {
    text-decoration: underline;
  }
`;

const AddTaskButton = styled.button`
  margin: 10px;
  padding: 10px;
  background: ${COLORS.secondary};
  border: 1px solid ${COLORS.border};
  color: ${COLORS.text};
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  width: calc(100% - 20px);

  &:hover {
    border-color: ${COLORS.accent};
    box-shadow: 0 0 5px ${COLORS.accent};
  }
`;

const ErrorMessage = styled.div`
  padding: 10px;
  margin: 10px;
  background: rgba(255, 0, 0, 0.1);
  border: 1px solid ${COLORS.error};
  border-radius: 4px;
  color: ${COLORS.error};
  font-size: 0.9em;
`;

const ConnectionStatus = styled.div`
  padding: 12px 20px;
  background: ${props => props.$connected ?
    `linear-gradient(135deg,
      rgba(0, 204, 0, 0.1) 0%,
      rgba(0, 204, 0, 0.15) 50%,
      rgba(0, 204, 0, 0.1) 100%
    )` :
    `linear-gradient(135deg,
      rgba(255, 0, 0, 0.1) 0%,
      rgba(255, 0, 0, 0.15) 50%,
      rgba(255, 0, 0, 0.1) 100%
    )`
  };
  border-bottom: 2px solid ${props => props.$connected ? COLORS.success : COLORS.error};
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9em;
  color: ${props => props.$connected ? COLORS.success : COLORS.error};
  position: relative;
  transform-style: preserve-3d;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-shadow: 0 0 10px ${props => props.$connected ?
    'rgba(0, 255, 0, 0.5)' :
    'rgba(255, 0, 0, 0.5)'
  };
  animation: ${props => props.$connected ?
    css`${plasmaWave} 5s infinite` :
    css`${quantumBurst} 2s infinite`
  };

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: ${props => props.$connected ?
      `radial-gradient(circle at center,
        rgba(0, 255, 0, 0.15) 0%,
        rgba(0, 255, 0, 0.1) 30%,
        transparent 70%
      )` :
      `radial-gradient(circle at center,
        rgba(255, 0, 0, 0.15) 0%,
        rgba(255, 0, 0, 0.1) 30%,
        transparent 70%
      )`
    };
    animation: ${props => props.$connected ?
      css`${plasmaField} 8s infinite` :
      css`${energyPulse} 3s infinite`
    };
    pointer-events: none;
  }

  &::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    right: 0;
    height: 2px;
    background: ${props => props.$connected ?
      `linear-gradient(to right,
        transparent 0%,
        rgba(0, 255, 0, 0.8) 50%,
        transparent 100%
      )` :
      `linear-gradient(to right,
        transparent 0%,
        rgba(255, 0, 0, 0.8) 50%,
        transparent 100%
      )`
    };
    animation: ${props => props.$connected ?
      css`${plasmaWave} 4s infinite` :
      css`${quantumBurst} 2s infinite`
    };
  }

  &:hover {
    transform: translateZ(10px);
    box-shadow: ${props => props.$connected ?
      `0 0 30px rgba(0, 255, 0, 0.2),
       0 0 50px rgba(0, 255, 0, 0.1)` :
      `0 0 30px rgba(255, 0, 0, 0.2),
       0 0 50px rgba(255, 0, 0, 0.1)`
    };
  }
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

const TaskPanel = ({ collapsed, onCollapse }) => {
  const [sections, setSections] = useState({
    filters: true,
    tasks: true
  });
  const [atlassianStatus, setAtlassianStatus] = useState({
    connected: true,
    error: null
  });

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const status = await checkAtlassianStatus();
        setAtlassianStatus({
          connected: status,
          error: null
        });
      } catch (error) {
        setAtlassianStatus({
          connected: false,
          error: error.message || ATLASSIAN_ERRORS.CONNECTION_FAILED
        });
      }
    };

    checkConnection();
    // Check connection status periodically
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  const toggleSection = (section) => {
    setSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const mockTasks = [
    {
      id: 'NOVA-1234',
      title: formatJiraTitle('Leads', 'Review System Architecture'),
      team: 'Leads',
      priority: 'high',
      status: 'in_progress',
      assignee: 'John Doe',
      description: 'Complete system architecture review for Nova field integration'
    },
    {
      id: 'NOVA-1235',
      title: formatJiraTitle('Orchestrators', 'Update Deployment Scripts'),
      team: 'Orchestrators',
      priority: 'medium',
      status: 'review',
      assignee: 'Jane Smith',
      description: 'Update deployment scripts for new system configuration'
    },
    {
      id: 'NOVA-1236',
      title: formatJiraTitle('Leads', 'Monitor System Health'),
      team: 'Leads',
      priority: 'low',
      status: 'blocked',
      assignee: 'Alice Johnson',
      description: 'Implement continuous monitoring for system health metrics'
    }
  ];

  if (collapsed) {
    return (
      <TaskPanelContainer $collapsed={collapsed}>
        <CollapseButton onClick={() => onCollapse(false)}>→</CollapseButton>
        <CollapsedContent>Tasks</CollapsedContent>
      </TaskPanelContainer>
    );
  }

  return (
    <TaskPanelContainer $collapsed={collapsed}>
      <CollapseButton onClick={() => onCollapse(true)}>←</CollapseButton>

      <ConnectionStatus $connected={atlassianStatus.connected}>
        <span>
          {atlassianStatus.connected
            ? 'Connected to Jira'
            : 'Jira Connection Failed'}
        </span>
        {atlassianStatus.connected && (
          <SyncButton onClick={() => checkAtlassianStatus()}>
            <span className="sync-icon">↻</span>
            Sync
          </SyncButton>
        )}
      </ConnectionStatus>

      {atlassianStatus.error && (
        <ErrorMessage>{atlassianStatus.error}</ErrorMessage>
      )}

      <SectionHeader onClick={() => toggleSection('filters')}>
        <SectionTitle>
          <span className="arrow">{sections.filters ? '▼' : '▶'}</span>
          <span>Filters</span>
        </SectionTitle>
      </SectionHeader>

      <SectionContent $expanded={sections.filters}>
        <FilterSection>
          <FilterGroup>
            <FilterLabel>Team</FilterLabel>
            <Select defaultValue="">
              <option value="">All Teams</option>
              <option value="leads">Leads</option>
              <option value="orchestrators">Orchestrators</option>
              <option value="monitoring">Monitoring</option>
            </Select>
          </FilterGroup>

          <FilterGroup>
            <FilterLabel>Priority</FilterLabel>
            <Select defaultValue="">
              <option value="">All Priorities</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </Select>
          </FilterGroup>

          <FilterGroup>
            <FilterLabel>Status</FilterLabel>
            <Select defaultValue="">
              <option value="">All Statuses</option>
              <option value="in_progress">In Progress</option>
              <option value="review">In Review</option>
              <option value="blocked">Blocked</option>
            </Select>
          </FilterGroup>
        </FilterSection>
      </SectionContent>

      <SectionHeader onClick={() => toggleSection('tasks')}>
        <SectionTitle>
          <span className="arrow">{sections.tasks ? '▼' : '▶'}</span>
          <span>Tasks</span>
        </SectionTitle>
      </SectionHeader>

      <SectionContent $expanded={sections.tasks}>
        <TaskList>
          {mockTasks.map(task => (
            <TaskItem key={task.id} $priority={task.priority}>
              <TaskHeader>
                <TaskTitle>{task.title}</TaskTitle>
              </TaskHeader>
              <TaskMeta>
                <TeamTag>{task.team}</TeamTag>
                <StatusTag $status={task.status}>
                  {task.status.replace('_', ' ')}
                </StatusTag>
              </TaskMeta>
              <JiraLink
                href={`https://levelup2x.atlassian.net/browse/${task.id}`}
                target="_blank"
                rel="noopener noreferrer"
              >
                {task.id} →
              </JiraLink>
            </TaskItem>
          ))}
        </TaskList>
        <AddTaskButton>+ Add Task</AddTaskButton>
      </SectionContent>
    </TaskPanelContainer>
  );
};

export default TaskPanel;
