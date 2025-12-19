import React, { useState, useEffect } from 'react';
import styled, { keyframes, css } from 'styled-components';
import { COLORS } from '../../styles/GlobalStyles';
import monitoringService from '../../services/MonitoringService';

const pulseAnimation = keyframes`
  0% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.02); opacity: 1; }
  100% { transform: scale(1); opacity: 0.8; }
`;

const glowAnimation = keyframes`
  0% { box-shadow: 0 0 5px ${COLORS.accent}, inset 0 0 5px ${COLORS.accent}; }
  50% { box-shadow: 0 0 20px ${COLORS.accent}, inset 0 0 10px ${COLORS.accent}; }
  100% { box-shadow: 0 0 5px ${COLORS.accent}, inset 0 0 5px ${COLORS.accent}; }
`;

const energyBurst = keyframes`
  0% {
    transform: scale(1) rotate(0deg);
    filter: hue-rotate(0deg) brightness(1);
  }
  50% {
    transform: scale(1.05) rotate(180deg);
    filter: hue-rotate(180deg) brightness(1.2);
  }
  100% {
    transform: scale(1) rotate(360deg);
    filter: hue-rotate(360deg) brightness(1);
  }
`;

const PanelContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: ${COLORS.background};
  position: relative;
  min-width: 0;
  opacity: ${props => props.$collapsed ? 0 : 1};
  visibility: ${props => props.$collapsed ? 'hidden' : 'visible'};
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform-style: preserve-3d;
  perspective: 1000px;
  box-shadow: 0 0 20px rgba(0, 255, 0, 0.1);

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
    animation: ${energyBurst} 10s linear infinite;
  }

  &:hover {
    box-shadow: 0 0 30px rgba(0, 255, 0, 0.2);
    transform: translateZ(10px);
  }
`;

const quantumPulse = keyframes`
  0% {
    transform: translateZ(0) scale(1);
    filter: brightness(1) saturate(1);
    box-shadow: 0 0 0 0 ${props => props.$connected ? 'rgba(0, 204, 0, 0.7)' : 'rgba(255, 0, 0, 0.7)'};
  }
  50% {
    transform: translateZ(20px) scale(1.02);
    filter: brightness(1.2) saturate(1.2);
    box-shadow: 0 0 20px ${props => props.$connected ? 'rgba(0, 204, 0, 0.3)' : 'rgba(255, 0, 0, 0.3)'};
  }
  100% {
    transform: translateZ(0) scale(1);
    filter: brightness(1) saturate(1);
    box-shadow: 0 0 0 0 ${props => props.$connected ? 'rgba(0, 204, 0, 0.7)' : 'rgba(255, 0, 0, 0.7)'};
  }
`;

const ConnectionBar = styled.div`
  padding: 15px 25px;
  background: ${props => props.$connected ?
    `linear-gradient(135deg,
      rgba(0, 204, 0, 0.05) 0%,
      rgba(0, 204, 0, 0.1) 50%,
      rgba(0, 204, 0, 0.05) 100%
    )` :
    `linear-gradient(135deg,
      rgba(255, 0, 0, 0.05) 0%,
      rgba(255, 0, 0, 0.1) 50%,
      rgba(255, 0, 0, 0.05) 100%
    )`
  };
  border-bottom: 2px solid ${props => props.$connected ?
    'rgba(0, 255, 0, 0.5)' :
    'rgba(255, 0, 0, 0.5)'
  };
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9em;
  color: ${props => props.$connected ? COLORS.success : COLORS.error};
  white-space: nowrap;
  position: relative;
  transform-style: preserve-3d;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: ${props => props.$connected ?
    css`${quantumPulse} 3s infinite, ${plasmaWave} 10s infinite` :
    'none'
  };
  text-shadow: 0 0 10px ${props => props.$connected ?
    'rgba(0, 255, 0, 0.5)' :
    'rgba(255, 0, 0, 0.5)'
  };

  &::before {
    content: '';
    position: absolute;
    top: -1px;
    left: 0;
    right: 0;
    bottom: -1px;
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
      css`${energyBurst} 5s infinite, ${plasmaField} 8s infinite` :
      css`${energyBurst} 5s infinite`
    };
    pointer-events: none;
    mix-blend-mode: screen;
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
      css`${quantumBurst} 4s infinite` :
      css`${shockwave} 2s infinite`
    };
  }

  &:hover {
    transform: translateZ(15px) rotateX(2deg);
    box-shadow: ${props => props.$connected ?
      `0 0 30px rgba(0, 255, 0, 0.2),
       0 0 50px rgba(0, 255, 0, 0.1),
       inset 0 0 20px rgba(0, 255, 0, 0.1)` :
      `0 0 30px rgba(255, 0, 0, 0.2),
       0 0 50px rgba(255, 0, 0, 0.1),
       inset 0 0 20px rgba(255, 0, 0, 0.1)`
    };

    &::before {
      animation: ${props => props.$connected ?
        css`${energyBurst} 3s infinite, ${plasmaField} 5s infinite, ${plasmaWave} 8s infinite` :
        css`${energyBurst} 3s infinite, ${shockwave} 4s infinite`
      };
    }

    &::after {
      animation: ${props => props.$connected ?
        css`${quantumBurst} 2s infinite, ${plasmaWave} 4s infinite` :
        css`${shockwave} 1s infinite`
      };
    }
  }
`;

const syncRotate = keyframes`
  0% {
    transform: rotate(0deg) scale(1);
    filter: brightness(1);
  }
  50% {
    transform: rotate(180deg) scale(1.2);
    filter: brightness(1.5);
  }
  100% {
    transform: rotate(360deg) scale(1);
    filter: brightness(1);
  }
`;

const SyncButton = styled.button`
  background: transparent;
  border: 2px solid transparent;
  color: ${COLORS.accent};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  transform-style: preserve-3d;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9em;
  letter-spacing: 0.5px;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 8px;
    background: radial-gradient(
      circle at center,
      rgba(0, 255, 0, 0.1) 0%,
      transparent 70%
    );
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  &:hover {
    background: rgba(0, 204, 0, 0.1);
    border-color: rgba(0, 255, 0, 0.3);
    transform: translateZ(5px);
    box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);

    &::before {
      opacity: 1;
      animation: ${pulseAnimation} 2s infinite;
    }
  }

  .sync-icon {
    transition: transform 0.3s ease;
    display: inline-block;
    transform-origin: center;
  }

  &:hover .sync-icon {
    animation: ${syncRotate} 1.5s infinite;
  }

  &:active {
    transform: translateZ(-2px) scale(0.95);
    transition: transform 0.1s;
  }
`;

const scrollGlow = keyframes`
  0% {
    background-position: 0% 0%;
    opacity: 0.5;
    filter: hue-rotate(0deg) brightness(1);
  }
  50% {
    background-position: 100% 100%;
    opacity: 0.8;
    filter: hue-rotate(180deg) brightness(1.3);
  }
  100% {
    background-position: 0% 0%;
    opacity: 0.5;
    filter: hue-rotate(360deg) brightness(1);
  }
`;

const dataBurst = keyframes`
  0% {
    transform: scale(1) translateZ(0);
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
  }
  50% {
    transform: scale(1.05) translateZ(20px);
    box-shadow: 0 0 40px rgba(0, 255, 0, 0.5),
                0 0 60px rgba(0, 255, 0, 0.3),
                0 0 80px rgba(0, 255, 0, 0.2);
  }
  100% {
    transform: scale(1) translateZ(0);
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
  }
`;

const shockwave = keyframes`
  0% {
    transform: scale(1);
    opacity: 0;
  }
  25% {
    opacity: 0.3;
  }
  50% {
    transform: scale(3);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 0;
  }
`;

const OutputSection = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: ${COLORS.background};
  position: relative;
  transform-style: preserve-3d;
  perspective: 1000px;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 40px;
    background: linear-gradient(
      to bottom,
      ${COLORS.background} 0%,
      transparent 100%
    );
    pointer-events: none;
    z-index: 2;
    animation: ${dataBurst} 5s infinite;
  }

  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 40px;
    background: linear-gradient(
      to top,
      ${COLORS.background} 0%,
      transparent 100%
    );
    pointer-events: none;
    z-index: 2;
    animation: ${dataBurst} 5s infinite;
  }

  &::-webkit-scrollbar {
    width: 10px;
    background: transparent;
  }

  &::-webkit-scrollbar-track {
    background: rgba(0, 255, 0, 0.05);
    border-radius: 5px;
    margin: 40px 0;
    position: relative;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: radial-gradient(
        circle at center,
        rgba(0, 255, 0, 0.1) 0%,
        transparent 70%
      );
      animation: ${plasmaField} 8s infinite;
    }
  }

  &::-webkit-scrollbar-thumb {
    background: linear-gradient(
      to bottom,
      rgba(0, 255, 0, 0.4) 0%,
      rgba(0, 255, 0, 0.6) 50%,
      rgba(0, 255, 0, 0.4) 100%
    );
    border-radius: 5px;
    border: 2px solid rgba(0, 255, 0, 0.2);
    background-size: 200% 200%;
    animation: ${scrollGlow} 3s linear infinite;
    position: relative;
    transform-style: preserve-3d;

    &::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      right: -50%;
      bottom: -50%;
      background: radial-gradient(
        circle at center,
        rgba(0, 255, 0, 0.3) 0%,
        transparent 70%
      );
      animation: ${shockwave} 3s infinite;
    }

    &:hover {
      background: linear-gradient(
        to bottom,
        rgba(0, 255, 0, 0.5) 0%,
        rgba(0, 255, 0, 0.7) 50%,
        rgba(0, 255, 0, 0.5) 100%
      );
      animation: ${quantumBurst} 2s infinite;
    }
  }

  &:hover::-webkit-scrollbar-thumb {
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.4),
                0 0 40px rgba(0, 255, 0, 0.2),
                0 0 60px rgba(0, 255, 0, 0.1);
  }

  &:hover::before,
  &:hover::after {
    animation: ${dataBurst} 2s infinite, ${shockwave} 3s infinite;
  }
`;

const OutputBox = styled.div`
  background: ${COLORS.background};
  border: 2px solid ${COLORS.border};
  border-radius: 12px;
  padding: 25px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  color: ${COLORS.textBright};
  position: relative;
  transform-style: preserve-3d;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 30px rgba(0, 255, 0, 0.1);
  perspective: 1000px;

  &::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    right: -50%;
    bottom: -50%;
    background: conic-gradient(
      from 0deg at 50% 50%,
      transparent 0%,
      rgba(0, 255, 0, 0.1) 25%,
      rgba(0, 255, 0, 0.2) 50%,
      rgba(0, 255, 0, 0.1) 75%,
      transparent 100%
    );
    pointer-events: none;
    animation: ${props => props.isModel ?
      css`${plasmaField} 15s linear infinite, ${plasmaWave} 20s infinite` :
      css`${plasmaField} 15s linear infinite`
    };
    opacity: 0.5;
    mix-blend-mode: screen;
    border-radius: 12px;
    transform-style: preserve-3d;
  }

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 12px;
    background: ${props => props.isModel ?
      `radial-gradient(
        circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
        rgba(0, 255, 0, 0.2) 0%,
        rgba(0, 255, 0, 0.1) 30%,
        transparent 70%
      )` :
      'none'
    };
    animation: ${props => props.isModel ?
      css`${quantumPulse} 4s infinite, ${energyBurst} 6s infinite` :
      'none'
    };
    pointer-events: none;
    mix-blend-mode: screen;
    filter: blur(2px);
  }

  &:hover {
    transform: translateZ(30px) scale(1.02) rotateX(2deg);
    box-shadow: 0 0 50px rgba(0, 255, 0, 0.2),
                0 0 80px rgba(0, 255, 0, 0.1),
                inset 0 0 30px rgba(0, 255, 0, 0.1);
    border-color: rgba(0, 255, 0, 0.4);

    &::before {
      animation: ${props => props.isModel ?
        css`${plasmaField} 8s linear infinite, ${plasmaWave} 10s infinite, ${quantumBurst} 5s infinite` :
        css`${plasmaField} 8s linear infinite, ${energyBurst} 4s infinite`
      };
      opacity: 0.7;
    }

    &::after {
      animation: ${props => props.isModel ?
        css`${quantumPulse} 3s infinite, ${energyBurst} 4s infinite, ${shockwave} 5s infinite` :
        css`${energyBurst} 4s infinite`
      };
      filter: blur(1px);
    }
  }

  .highlight {
    color: rgba(0, 255, 0, 0.9);
    text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
    animation: ${pulseAnimation} 2s infinite;
  }

  .value {
    color: rgba(0, 255, 128, 0.9);
    font-weight: bold;
    text-shadow: 0 0 8px rgba(0, 255, 128, 0.4);
  }

  .warning {
    color: rgba(255, 204, 0, 0.9);
    text-shadow: 0 0 8px rgba(255, 204, 0, 0.4);
  }

  .error {
    color: rgba(255, 68, 68, 0.9);
    text-shadow: 0 0 8px rgba(255, 68, 68, 0.4);
  }
`;

const plasmaWave = keyframes`
  0% {
    transform: translateZ(0) scale(1) rotate(0deg);
    filter: hue-rotate(0deg) brightness(1) saturate(1);
    box-shadow:
      0 0 20px rgba(0, 255, 0, 0.3),
      inset 0 0 10px rgba(0, 255, 0, 0.2);
  }
  50% {
    transform: translateZ(40px) scale(1.05) rotate(180deg);
    filter: hue-rotate(180deg) brightness(1.4) saturate(1.4);
    box-shadow:
      0 0 40px rgba(0, 255, 0, 0.5),
      0 0 60px rgba(0, 255, 0, 0.3),
      0 0 80px rgba(0, 255, 0, 0.2),
      inset 0 0 20px rgba(0, 255, 0, 0.4);
  }
  100% {
    transform: translateZ(0) scale(1) rotate(360deg);
    filter: hue-rotate(360deg) brightness(1) saturate(1);
    box-shadow:
      0 0 20px rgba(0, 255, 0, 0.3),
      inset 0 0 10px rgba(0, 255, 0, 0.2);
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

const ButtonGroup = styled.div`
  display: flex;
  gap: 15px;
  padding: 20px;
  border-top: 2px solid ${COLORS.border};
  background: ${COLORS.background};
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
    top: -1px;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(
      to right,
      transparent 0%,
      rgba(0, 255, 0, 0.5) 50%,
      transparent 100%
    );
    animation: ${quantumBurst} 5s infinite;
  }

  &:hover {
    &::after {
      animation: ${quantumBurst} 2s infinite;
    }
  }
`;

const ActionButton = styled.button`
  flex: 1;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: ${COLORS.text};
  border: 2px solid ${COLORS.border};
  background: ${COLORS.background};
  position: relative;
  transform-style: preserve-3d;
  overflow: hidden;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9em;
  letter-spacing: 0.5px;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
      135deg,
      transparent 0%,
      rgba(0, 255, 0, 0.05) 50%,
      transparent 100%
    );
    pointer-events: none;
    transition: all 0.3s ease;
  }

  &.accept {
    background: linear-gradient(
      to bottom,
      rgba(0, 204, 0, 0.05) 0%,
      rgba(0, 204, 0, 0.1) 100%
    );
    &:hover {
      transform: translateZ(10px) scale(1.02);
      border-color: ${COLORS.success};
      box-shadow: 0 0 20px rgba(0, 204, 0, 0.3),
                  inset 0 0 10px rgba(0, 204, 0, 0.2);
      animation: ${energyBurst} 2s infinite;
      &::before {
        background: radial-gradient(
          circle at center,
          rgba(0, 204, 0, 0.2) 0%,
          transparent 70%
        );
        animation: ${pulseAnimation} 2s infinite;
      }
    }
  }

  &.modify {
    background: linear-gradient(
      to bottom,
      rgba(204, 204, 0, 0.05) 0%,
      rgba(204, 204, 0, 0.1) 100%
    );
    &:hover {
      transform: translateZ(10px) scale(1.02);
      border-color: ${COLORS.warning};
      box-shadow: 0 0 20px rgba(204, 204, 0, 0.3),
                  inset 0 0 10px rgba(204, 204, 0, 0.2);
      animation: ${glowAnimation} 2s infinite;
      &::before {
        background: radial-gradient(
          circle at center,
          rgba(204, 204, 0, 0.2) 0%,
          transparent 70%
        );
        animation: ${pulseAnimation} 2s infinite;
      }
    }
  }

  &.reject {
    background: linear-gradient(
      to bottom,
      rgba(204, 0, 0, 0.05) 0%,
      rgba(204, 0, 0, 0.1) 100%
    );
    &:hover {
      transform: translateZ(10px) scale(1.02);
      border-color: ${COLORS.error};
      box-shadow: 0 0 20px rgba(204, 0, 0, 0.3),
                  inset 0 0 10px rgba(204, 0, 0, 0.2);
      animation: ${energyBurst} 2s infinite;
      &::before {
        background: radial-gradient(
          circle at center,
          rgba(204, 0, 0, 0.2) 0%,
          transparent 70%
        );
        animation: ${pulseAnimation} 2s infinite;
      }
    }
  }

  &:active {
    transform: translateZ(-5px) scale(0.98);
    transition: transform 0.1s;
  }
`;

const statusPulse = keyframes`
  0% {
    transform: scale(1);
    opacity: 0.8;
    box-shadow: 0 0 0 0 ${props => props.$connected ? 'rgba(0, 204, 0, 0.7)' : 'rgba(255, 0, 0, 0.7)'};
  }
  50% {
    transform: scale(1.3);
    opacity: 1;
    box-shadow: 0 0 10px ${props => props.$connected ? 'rgba(0, 204, 0, 0.3)' : 'rgba(255, 0, 0, 0.3)'};
  }
  100% {
    transform: scale(1);
    opacity: 0.8;
    box-shadow: 0 0 0 0 ${props => props.$connected ? 'rgba(0, 204, 0, 0.7)' : 'rgba(255, 0, 0, 0.7)'};
  }
`;

const BackendStatus = styled.div`
  padding: 6px 12px;
  font-size: 0.8em;
  color: ${COLORS.textDim};
  display: flex;
  align-items: center;
  gap: 10px;
  background: ${props => props.$connected ?
    'rgba(0, 204, 0, 0.05)' :
    'rgba(255, 0, 0, 0.05)'
  };
  border-radius: 12px;
  transform-style: preserve-3d;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 12px;
    background: ${props => props.$connected ?
      'radial-gradient(circle at center, rgba(0, 204, 0, 0.1) 0%, transparent 70%)' :
      'radial-gradient(circle at center, rgba(255, 0, 0, 0.1) 0%, transparent 70%)'
    };
    animation: ${energyBurst} 5s infinite;
    pointer-events: none;
  }

  &:hover {
    transform: translateZ(5px);
    box-shadow: 0 0 15px ${props => props.$connected ?
      'rgba(0, 204, 0, 0.2)' :
      'rgba(255, 0, 0, 0.2)'
    };
  }

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: ${props => props.$connected ? COLORS.success : COLORS.error};
    position: relative;
    animation: ${statusPulse} 2s infinite;

    &::after {
      content: '';
      position: absolute;
      top: -2px;
      left: -2px;
      right: -2px;
      bottom: -2px;
      border-radius: 50%;
      background: inherit;
      opacity: 0.5;
      filter: blur(2px);
      animation: ${pulseAnimation} 2s infinite;
    }
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
