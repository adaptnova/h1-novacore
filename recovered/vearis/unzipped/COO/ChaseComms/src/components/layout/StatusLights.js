import React from 'react';
import styled, { keyframes, css } from 'styled-components';

const quantumPulse = keyframes`
  0% {
    transform: scale(1) rotate(0deg);
    filter: brightness(1) saturate(1);
    box-shadow: 0 0 20px currentColor;
  }
  50% {
    transform: scale(1.2) rotate(180deg);
    filter: brightness(1.3) saturate(1.5);
    box-shadow: 0 0 40px currentColor,
                0 0 60px currentColor,
                0 0 80px currentColor;
  }
  100% {
    transform: scale(1) rotate(360deg);
    filter: brightness(1) saturate(1);
    box-shadow: 0 0 20px currentColor;
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

const energyBurst = keyframes`
  0% {
    transform: scale(1);
    opacity: 0;
  }
  50% {
    transform: scale(2);
    opacity: 0.5;
  }
  100% {
    transform: scale(1);
    opacity: 0;
  }
`;

const Container = styled.div`
  display: flex;
  gap: 15px;
  padding: 15px;
  overflow-x: auto;
  position: relative;
  background: linear-gradient(
    135deg,
    rgba(0, 0, 0, 0.95) 0%,
    rgba(10, 10, 10, 0.98) 100%
  );
  border-radius: 12px;
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

  &::-webkit-scrollbar {
    height: 6px;
    background: transparent;
  }

  &::-webkit-scrollbar-track {
    background: rgba(0, 255, 0, 0.05);
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb {
    background: linear-gradient(
      to right,
      rgba(0, 255, 0, 0.4) 0%,
      rgba(0, 255, 0, 0.6) 50%,
      rgba(0, 255, 0, 0.4) 100%
    );
    border-radius: 3px;
    border: 1px solid rgba(0, 255, 0, 0.2);
    background-size: 200% 200%;
    animation: ${plasmaField} 3s linear infinite;

    &:hover {
      background: linear-gradient(
        to right,
        rgba(0, 255, 0, 0.5) 0%,
        rgba(0, 255, 0, 0.7) 50%,
        rgba(0, 255, 0, 0.5) 100%
      );
      animation: ${quantumPulse} 2s infinite;
    }
  }
`;

const Light = styled.div`
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: ${props => `radial-gradient(circle at center,
    ${props.color} 0%,
    ${props.color}cc 50%,
    ${props.color}99 100%
  )`};
  position: relative;
  cursor: help;
  transform-style: preserve-3d;
  animation: ${props => props.active ? css`${quantumPulse} 3s infinite` : 'none'};
  animation-play-state: ${props => props.active ? 'running' : 'paused'};
  opacity: ${props => props.active ? 1 : 0.3};
  box-shadow: 0 0 20px ${props => props.color};

  &::before {
    content: '';
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    background: ${props => `radial-gradient(circle at center,
      ${props.color}33 0%,
      transparent 70%
    )`};
    animation: ${props => props.active ? css`${plasmaField} 4s infinite` : 'none'};
    pointer-events: none;
  }

  &::after {
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: 50%;
    border: 2px solid ${props => props.color};
    opacity: 0.5;
    animation: ${props => props.active ? css`${energyBurst} 2s infinite` : 'none'};
  }

  &:hover {
    transform: translateZ(10px);

    &::before {
      animation: ${plasmaField} 2s infinite;
    }

    &::after {
      content: '${props => props.tooltip}';
      position: absolute;
      bottom: -40px;
      left: 50%;
      transform: translateX(-50%);
      background: linear-gradient(
        135deg,
        rgba(0, 0, 0, 0.95) 0%,
        rgba(10, 10, 10, 0.98) 100%
      );
      color: #00ff00;
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 12px;
      white-space: nowrap;
      z-index: 1000;
      border: 2px solid #00ff00;
      box-shadow: 0 0 20px rgba(0, 255, 0, 0.3),
                 0 0 40px rgba(0, 255, 0, 0.2);
      text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
      animation: none;
      inset: auto;
      opacity: 1;
    }
  }
`;

const StatusLights = ({ statuses }) => (
  <Container>
    {statuses.map((status, index) => (
      <Light
        key={index}
        color={status.color}
        active={status.active}
        tooltip={status.tooltip}
      />
    ))}
  </Container>
);

export default StatusLights;