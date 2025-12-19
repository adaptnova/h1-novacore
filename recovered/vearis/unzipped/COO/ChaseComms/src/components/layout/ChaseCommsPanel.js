import React, { useState, useEffect, useRef } from 'react';
import StatusLights from './StatusLights';
import styled, { keyframes, css } from 'styled-components';
import chaseCommsService from '../../services/ChaseCommsService';
import monitoringService from '../../services/MonitoringService';

// Enhanced Animations
const pulseAnimation = keyframes`
  0% { transform: scale(1); opacity: 0.8; box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7); }
  50% { transform: scale(1.1); opacity: 1; box-shadow: 0 0 20px 10px rgba(0, 255, 0, 0); }
  100% { transform: scale(1); opacity: 0.8; box-shadow: 0 0 0 0 rgba(0, 255, 0, 0); }
`;

const glowAnimation = keyframes`
  0% { box-shadow: 0 0 5px #00ff00, inset 0 0 5px #00ff00; }
  50% { box-shadow: 0 0 20px #00ff00, inset 0 0 10px #00ff00; }
  100% { box-shadow: 0 0 5px #00ff00, inset 0 0 5px #00ff00; }
`;

const alertAnimation = keyframes`
  0% { background-color: #ff0000; box-shadow: 0 0 10px #ff0000; }
  50% { background-color: #ff6b6b; box-shadow: 0 0 20px #ff0000; }
  100% { background-color: #ff0000; box-shadow: 0 0 10px #ff0000; }
`;

const matrixRain = keyframes`
  0% { transform: translateY(-100%); opacity: 1; }
  100% { transform: translateY(100%); opacity: 0; }
`;

const energyBurst = keyframes`
  0% {
    transform: scale(0.8) rotate(0deg) translateZ(0) perspective(1000px) rotateX(0deg);
    opacity: 0.3;
    filter: hue-rotate(0deg) brightness(1) blur(2px) contrast(1.2);
    box-shadow: 0 0 10px rgba(0, 255, 0, 0.5),
                0 0 20px rgba(0, 255, 0, 0.3),
                0 0 30px rgba(0, 255, 0, 0.1),
                inset 0 0 20px rgba(0, 255, 0, 0.2);
  }
  20% {
    transform: scale(1.5) rotate(90deg) translateZ(40px) perspective(1000px) rotateX(180deg);
    opacity: 0.9;
    filter: hue-rotate(90deg) brightness(2) blur(0) contrast(1.5);
    box-shadow: 0 0 40px rgba(0, 255, 0, 0.8),
                0 0 60px rgba(0, 255, 0, 0.5),
                0 0 80px rgba(0, 255, 0, 0.3),
                inset 0 0 40px rgba(0, 255, 0, 0.4);
  }
  40% {
    transform: scale(0.9) rotate(180deg) translateZ(-20px) perspective(1000px) rotateX(360deg);
    opacity: 0.6;
    filter: hue-rotate(180deg) brightness(1.6) blur(1px) contrast(1.8);
    box-shadow: 0 0 30px rgba(0, 255, 0, 0.6),
                0 0 50px rgba(0, 255, 0, 0.4),
                0 0 70px rgba(0, 255, 0, 0.2),
                inset 0 0 30px rgba(0, 255, 0, 0.3);
  }
  60% {
    transform: scale(1.3) rotate(270deg) translateZ(60px) perspective(1000px) rotateX(540deg);
    opacity: 0.8;
    filter: hue-rotate(270deg) brightness(2.2) blur(0) contrast(2);
    box-shadow: 0 0 50px rgba(0, 255, 0, 0.9),
                0 0 70px rgba(0, 255, 0, 0.6),
                0 0 90px rgba(0, 255, 0, 0.3),
                inset 0 0 50px rgba(0, 255, 0, 0.5);
  }
  80% {
    transform: scale(0.95) rotate(360deg) translateZ(-40px) perspective(1000px) rotateX(720deg);
    opacity: 0.7;
    filter: hue-rotate(360deg) brightness(1.8) blur(1px) contrast(1.6);
    box-shadow: 0 0 35px rgba(0, 255, 0, 0.7),
                0 0 55px rgba(0, 255, 0, 0.5),
                0 0 75px rgba(0, 255, 0, 0.2),
                inset 0 0 35px rgba(0, 255, 0, 0.3);
  }
  100% {
    transform: scale(1) rotate(720deg) translateZ(0) perspective(1000px) rotateX(1080deg);
    opacity: 1;
    filter: hue-rotate(0deg) brightness(1) blur(0) contrast(1.2);
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.5),
                0 0 40px rgba(0, 255, 0, 0.3),
                0 0 60px rgba(0, 255, 0, 0.1),
                inset 0 0 20px rgba(0, 255, 0, 0.2);
  }
`;

const quantumBurst = keyframes`
  0% {
    transform: perspective(1000px) rotateX(0deg) rotateY(0deg) rotateZ(0deg) scale(1) translateZ(0);
    filter: brightness(1) contrast(1) saturate(1) hue-rotate(0deg);
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.5),
                inset 0 0 10px rgba(0, 255, 0, 0.3);
    text-shadow: 0 0 10px rgba(0, 255, 0, 0.8);
  }
  25% {
    transform: perspective(1000px) rotateX(180deg) rotateY(90deg) rotateZ(45deg) scale(1.5) translateZ(50px);
    filter: brightness(2.5) contrast(1.8) saturate(1.5) hue-rotate(90deg);
    box-shadow: 0 0 60px rgba(0, 255, 0, 0.8),
                0 0 120px rgba(0, 255, 0, 0.4),
                inset 0 0 30px rgba(0, 255, 0, 0.6);
    text-shadow: 0 0 20px rgba(0, 255, 0, 1);
  }
  50% {
    transform: perspective(1000px) rotateX(360deg) rotateY(180deg) rotateZ(90deg) scale(0.8) translateZ(-30px);
    filter: brightness(2) contrast(2.2) saturate(2) hue-rotate(180deg);
    box-shadow: 0 0 100px rgba(0, 255, 0, 0.9),
                0 0 150px rgba(0, 255, 0, 0.5),
                inset 0 0 50px rgba(0, 255, 0, 0.8);
    text-shadow: 0 0 30px rgba(0, 255, 0, 1);
  }
  75% {
    transform: perspective(1000px) rotateX(540deg) rotateY(270deg) rotateZ(180deg) scale(1.2) translateZ(80px);
    filter: brightness(3) contrast(2.5) saturate(2.5) hue-rotate(270deg);
    box-shadow: 0 0 140px rgba(0, 255, 0, 1),
                0 0 200px rgba(0, 255, 0, 0.6),
                inset 0 0 70px rgba(0, 255, 0, 1);
    text-shadow: 0 0 40px rgba(0, 255, 0, 1);
  }
  100% {
    transform: perspective(1000px) rotateX(720deg) rotateY(360deg) rotateZ(360deg) scale(1) translateZ(0);
    filter: brightness(1) contrast(1) saturate(1) hue-rotate(360deg);
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.5),
                inset 0 0 10px rgba(0, 255, 0, 0.3);
    text-shadow: 0 0 10px rgba(0, 255, 0, 0.8);
  }
`;

const plasmaWave = keyframes`
  0% {
    clip-path: circle(10% at 50% 50%);
    background: radial-gradient(circle at center,
                rgba(0, 255, 0, 0.8) 0%,
                rgba(0, 255, 0, 0.4) 30%,
                rgba(0, 255, 0, 0.2) 50%,
                transparent 70%),
              conic-gradient(from 0deg at 50% 50%,
                rgba(0, 255, 0, 0.6) 0%,
                transparent 25%,
                rgba(0, 255, 0, 0.6) 50%,
                transparent 75%,
                rgba(0, 255, 0, 0.6) 100%);
    transform: scale(0.8) rotate(0deg);
    filter: blur(2px) brightness(1.2);
    opacity: 0.8;
  }
  25% {
    clip-path: circle(40% at 50% 50%);
    background: radial-gradient(circle at center,
                rgba(0, 255, 0, 0.9) 0%,
                rgba(0, 255, 0, 0.5) 40%,
                rgba(0, 255, 0, 0.3) 60%,
                transparent 80%),
              conic-gradient(from 90deg at 50% 50%,
                rgba(0, 255, 0, 0.7) 0%,
                transparent 25%,
                rgba(0, 255, 0, 0.7) 50%,
                transparent 75%,
                rgba(0, 255, 0, 0.7) 100%);
    transform: scale(1.1) rotate(90deg);
    filter: blur(0px) brightness(1.5);
    opacity: 1;
  }
  50% {
    clip-path: circle(80% at 50% 50%);
    background: radial-gradient(circle at center,
                rgba(0, 255, 0, 1) 0%,
                rgba(0, 255, 0, 0.6) 50%,
                rgba(0, 255, 0, 0.4) 70%,
                transparent 90%),
              conic-gradient(from 180deg at 50% 50%,
                rgba(0, 255, 0, 0.8) 0%,
                transparent 25%,
                rgba(0, 255, 0, 0.8) 50%,
                transparent 75%,
                rgba(0, 255, 0, 0.8) 100%);
    transform: scale(1.2) rotate(180deg);
    filter: blur(1px) brightness(2);
    opacity: 0.9;
  }
  75% {
    clip-path: circle(40% at 50% 50%);
    background: radial-gradient(circle at center,
                rgba(0, 255, 0, 0.9) 0%,
                rgba(0, 255, 0, 0.5) 40%,
                rgba(0, 255, 0, 0.3) 60%,
                transparent 80%),
              conic-gradient(from 270deg at 50% 50%,
                rgba(0, 255, 0, 0.7) 0%,
                transparent 25%,
                rgba(0, 255, 0, 0.7) 50%,
                transparent 75%,
                rgba(0, 255, 0, 0.7) 100%);
    transform: scale(1.1) rotate(270deg);
    filter: blur(0px) brightness(1.8);
    opacity: 1;
  }
  100% {
    clip-path: circle(10% at 50% 50%);
    background: radial-gradient(circle at center,
                rgba(0, 255, 0, 0.8) 0%,
                rgba(0, 255, 0, 0.4) 30%,
                rgba(0, 255, 0, 0.2) 50%,
                transparent 70%),
              conic-gradient(from 360deg at 50% 50%,
                rgba(0, 255, 0, 0.6) 0%,
                transparent 25%,
                rgba(0, 255, 0, 0.6) 50%,
                transparent 75%,
                rgba(0, 255, 0, 0.6) 100%);
    transform: scale(0.8) rotate(360deg);
    filter: blur(2px) brightness(1.2);
    opacity: 0.8;
  }
`;

const superBurst = keyframes`
  0% {
    transform: scale(1) rotate(0deg) perspective(1000px) rotateX(0deg) translateZ(0);
    filter: hue-rotate(0deg) brightness(1) contrast(1) saturate(1);
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.7),
                0 0 40px rgba(0, 255, 0, 0.4),
                0 0 60px rgba(0, 255, 0, 0.2),
                inset 0 0 20px rgba(0, 255, 0, 0.5);
    text-shadow: 0 0 10px rgba(0, 255, 0, 1);
  }
  25% {
    transform: scale(1.8) rotate(180deg) perspective(1000px) rotateX(180deg) translateZ(100px);
    filter: hue-rotate(180deg) brightness(2.5) contrast(2) saturate(2);
    box-shadow: 0 0 80px rgba(0, 255, 0, 1),
                0 0 120px rgba(0, 255, 0, 0.7),
                0 0 160px rgba(0, 255, 0, 0.5),
                inset 0 0 60px rgba(0, 255, 0, 0.8);
    text-shadow: 0 0 30px rgba(0, 255, 0, 1);
  }
  50% {
    transform: scale(0.6) rotate(360deg) perspective(1000px) rotateX(360deg) translateZ(-50px);
    filter: hue-rotate(360deg) brightness(2) contrast(2.5) saturate(1.5);
    box-shadow: 0 0 100px rgba(0, 255, 0, 0.9),
                0 0 150px rgba(0, 255, 0, 0.6),
                0 0 200px rgba(0, 255, 0, 0.4),
                inset 0 0 80px rgba(0, 255, 0, 0.7);
    text-shadow: 0 0 20px rgba(0, 255, 0, 1);
  }
  75% {
    transform: scale(1.5) rotate(540deg) perspective(1000px) rotateX(540deg) translateZ(150px);
    filter: hue-rotate(540deg) brightness(3) contrast(3) saturate(2.5);
    box-shadow: 0 0 120px rgba(0, 255, 0, 1),
                0 0 180px rgba(0, 255, 0, 0.8),
                0 0 240px rgba(0, 255, 0, 0.6),
                inset 0 0 100px rgba(0, 255, 0, 0.9);
    text-shadow: 0 0 40px rgba(0, 255, 0, 1);
  }
  100% {
    transform: scale(1) rotate(720deg) perspective(1000px) rotateX(720deg) translateZ(0);
    filter: hue-rotate(720deg) brightness(1) contrast(1) saturate(1);
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.7),
                0 0 40px rgba(0, 255, 0, 0.4),
                0 0 60px rgba(0, 255, 0, 0.2),
                inset 0 0 20px rgba(0, 255, 0, 0.5);
    text-shadow: 0 0 10px rgba(0, 255, 0, 1);
  }
`;

const shockwave = keyframes`
  0% {
    transform: scale(1) perspective(1000px) rotateX(0deg);
    opacity: 0;
    border: 4px solid rgba(0, 255, 0, 0);
    box-shadow: 0 0 0 0 rgba(0, 255, 0, 0),
                inset 0 0 0 0 rgba(0, 255, 0, 0);
    filter: blur(0px) brightness(1);
  }
  15% {
    transform: scale(1.3) perspective(1000px) rotateX(45deg);
    opacity: 0.9;
    border: 4px solid rgba(0, 255, 0, 0.9);
    box-shadow: 0 0 30px rgba(0, 255, 0, 0.8),
                inset 0 0 20px rgba(0, 255, 0, 0.6);
    filter: blur(1px) brightness(1.5);
  }
  30% {
    transform: scale(1.8) perspective(1000px) rotateX(90deg);
    opacity: 0.7;
    border: 4px solid rgba(0, 255, 0, 0.7);
    box-shadow: 0 0 50px rgba(0, 255, 0, 0.6),
                inset 0 0 35px rgba(0, 255, 0, 0.5);
    filter: blur(2px) brightness(2);
  }
  45% {
    transform: scale(2.2) perspective(1000px) rotateX(180deg);
    opacity: 0.5;
    border: 4px solid rgba(0, 255, 0, 0.5);
    box-shadow: 0 0 70px rgba(0, 255, 0, 0.5),
                inset 0 0 50px rgba(0, 255, 0, 0.4);
    filter: blur(3px) brightness(2.5);
  }
  60% {
    transform: scale(2.6) perspective(1000px) rotateX(270deg);
    opacity: 0.3;
    border: 4px solid rgba(0, 255, 0, 0.3);
    box-shadow: 0 0 90px rgba(0, 255, 0, 0.4),
                inset 0 0 65px rgba(0, 255, 0, 0.3);
    filter: blur(4px) brightness(3);
  }
  75% {
    transform: scale(3.0) perspective(1000px) rotateX(360deg);
    opacity: 0.2;
    border: 4px solid rgba(0, 255, 0, 0.2);
    box-shadow: 0 0 110px rgba(0, 255, 0, 0.3),
                inset 0 0 80px rgba(0, 255, 0, 0.2);
    filter: blur(5px) brightness(2.5);
  }
  90% {
    transform: scale(3.4) perspective(1000px) rotateX(450deg);
    opacity: 0.1;
    border: 4px solid rgba(0, 255, 0, 0.1);
    box-shadow: 0 0 130px rgba(0, 255, 0, 0.2),
                inset 0 0 95px rgba(0, 255, 0, 0.1);
    filter: blur(6px) brightness(2);
  }
  100% {
    transform: scale(3.8) perspective(1000px) rotateX(540deg);
    opacity: 0;
    border: 4px solid rgba(0, 255, 0, 0);
    box-shadow: 0 0 150px rgba(0, 255, 0, 0),
                inset 0 0 110px rgba(0, 255, 0, 0);
    filter: blur(8px) brightness(1);
  }
`;

const plasmaField = keyframes`
  0% {
    background-position: 0% 0%;
    filter: hue-rotate(0deg) brightness(1) contrast(1);
    opacity: 0.7;
    transform: scale(1) rotate(0deg);
  }
  25% {
    background-position: 50% 25%;
    filter: hue-rotate(90deg) brightness(1.5) contrast(1.2);
    opacity: 0.9;
    transform: scale(1.1) rotate(90deg);
  }
  50% {
    background-position: 100% 100%;
    filter: hue-rotate(180deg) brightness(2) contrast(1.4);
    opacity: 1;
    transform: scale(1.2) rotate(180deg);
  }
  75% {
    background-position: 50% 75%;
    filter: hue-rotate(270deg) brightness(1.5) contrast(1.2);
    opacity: 0.9;
    transform: scale(1.1) rotate(270deg);
  }
  100% {
    background-position: 0% 0%;
    filter: hue-rotate(360deg) brightness(1) contrast(1);
    opacity: 0.7;
    transform: scale(1) rotate(360deg);
  }
`;

const plasmaFieldGradient = `
  repeating-linear-gradient(
    45deg,
    rgba(0, 255, 0, 0.1) 0px,
    rgba(0, 255, 0, 0.2) 10px,
    rgba(0, 255, 0, 0.1) 20px
  ),
  repeating-linear-gradient(
    -45deg,
    rgba(0, 255, 0, 0.15) 0px,
    rgba(0, 255, 0, 0.25) 10px,
    rgba(0, 255, 0, 0.15) 20px
  ),
  radial-gradient(
    circle at 50% 50%,
    rgba(0, 255, 0, 0.3) 0%,
    rgba(0, 255, 0, 0.2) 30%,
    rgba(0, 255, 0, 0.1) 60%,
    transparent 80%
  )
`;

const energyRipple = keyframes`
  0% {
    transform: scale(1) rotate(0deg) perspective(1000px);
    border-width: 2px;
    border-color: rgba(0, 255, 0, 0.7);
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.5),
                inset 0 0 10px rgba(0, 255, 0, 0.3);
    filter: brightness(1) contrast(1) blur(0px);
  }
  25% {
    transform: scale(1.3) rotate(90deg) perspective(1000px) rotateX(45deg);
    border-width: 3px;
    border-color: rgba(0, 255, 0, 0.9);
    box-shadow: 0 0 40px rgba(0, 255, 0, 0.7),
                inset 0 0 20px rgba(0, 255, 0, 0.5);
    filter: brightness(1.5) contrast(1.2) blur(1px);
  }
  50% {
    transform: scale(1.5) rotate(180deg) perspective(1000px) rotateX(90deg);
    border-width: 1px;
    border-color: rgba(0, 255, 0, 0);
    box-shadow: 0 0 60px rgba(0, 255, 0, 0.9),
                inset 0 0 30px rgba(0, 255, 0, 0.7);
    filter: brightness(2) contrast(1.4) blur(2px);
  }
  75% {
    transform: scale(1.3) rotate(270deg) perspective(1000px) rotateX(45deg);
    border-width: 3px;
    border-color: rgba(0, 255, 0, 0.9);
    box-shadow: 0 0 40px rgba(0, 255, 0, 0.7),
                inset 0 0 20px rgba(0, 255, 0, 0.5);
    filter: brightness(1.5) contrast(1.2) blur(1px);
  }
  100% {
    transform: scale(1) rotate(360deg) perspective(1000px);
    border-width: 2px;
    border-color: rgba(0, 255, 0, 0.7);
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.5),
                inset 0 0 10px rgba(0, 255, 0, 0.3);
    filter: brightness(1) contrast(1) blur(0px);
  }
`;

const dataBurst = keyframes`
  0% {
    clip-path: polygon(50% 50%, 50% 50%, 50% 50%, 50% 50%);
    transform: scale(0.8) rotate(0deg) perspective(1000px);
    filter: brightness(1) contrast(1) saturate(1);
    box-shadow: 0 0 0 0 rgba(0, 255, 0, 0);
    opacity: 0;
  }
  15% {
    clip-path: polygon(25% 25%, 75% 25%, 75% 75%, 25% 75%);
    transform: scale(1.2) rotate(45deg) perspective(1000px) rotateX(45deg);
    filter: brightness(1.5) contrast(1.2) saturate(1.5);
    box-shadow: 0 0 30px rgba(0, 255, 0, 0.5);
    opacity: 0.7;
  }
  30% {
    clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
    transform: scale(1.4) rotate(90deg) perspective(1000px) rotateX(90deg);
    filter: brightness(2) contrast(1.4) saturate(2);
    box-shadow: 0 0 50px rgba(0, 255, 0, 0.7);
    opacity: 1;
  }
  45% {
    clip-path: polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%);
    transform: scale(1.6) rotate(180deg) perspective(1000px) rotateX(180deg);
    filter: brightness(2.5) contrast(1.6) saturate(2.5);
    box-shadow: 0 0 70px rgba(0, 255, 0, 0.9);
    opacity: 0.8;
  }
  60% {
    clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
    transform: scale(1.4) rotate(270deg) perspective(1000px) rotateX(270deg);
    filter: brightness(2) contrast(1.4) saturate(2);
    box-shadow: 0 0 50px rgba(0, 255, 0, 0.7);
    opacity: 1;
  }
  75% {
    clip-path: polygon(25% 25%, 75% 25%, 75% 75%, 25% 75%);
    transform: scale(1.2) rotate(315deg) perspective(1000px) rotateX(315deg);
    filter: brightness(1.5) contrast(1.2) saturate(1.5);
    box-shadow: 0 0 30px rgba(0, 255, 0, 0.5);
    opacity: 0.7;
  }
  90% {
    clip-path: polygon(40% 40%, 60% 40%, 60% 60%, 40% 60%);
    transform: scale(1) rotate(360deg) perspective(1000px) rotateX(360deg);
    filter: brightness(1.2) contrast(1.1) saturate(1.2);
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
    opacity: 0.3;
  }
  100% {
    clip-path: polygon(50% 50%, 50% 50%, 50% 50%, 50% 50%);
    transform: scale(0.8) rotate(360deg) perspective(1000px);
    filter: brightness(1) contrast(1) saturate(1);
    box-shadow: 0 0 0 0 rgba(0, 255, 0, 0);
    opacity: 0;
  }
`;

const priorityPulse = keyframes`
  0% {
    transform: scale(1);
    filter: brightness(1);
  }
  50% {
    transform: scale(1.1);
    filter: brightness(1.5);
  }
  100% {
    transform: scale(1);
    filter: brightness(1);
  }
`;

const inputGlow = keyframes`
  0% {
    box-shadow: 0 0 5px #00ff00, inset 0 0 2px #00ff00;
    border-color: rgba(0, 255, 0, 0.5);
  }
  50% {
    box-shadow: 0 0 20px #00ff00, inset 0 0 10px #00ff00;
    border-color: rgba(0, 255, 0, 1);
  }
  100% {
    box-shadow: 0 0 5px #00ff00, inset 0 0 2px #00ff00;
    border-color: rgba(0, 255, 0, 0.5);
  }
`;

const buttonGlow = keyframes`
  0% {
    filter: brightness(1) hue-rotate(0deg);
  }
  50% {
    filter: brightness(1.5) hue-rotate(180deg);
  }
  100% {
    filter: brightness(1) hue-rotate(360deg);
  }
`;

const logEntryAnimation = keyframes`
  0% {
    transform: translateX(-10px);
    opacity: 0;
    background: rgba(0, 255, 0, 0.2);
  }
  50% {
    transform: translateX(5px);
    opacity: 1;
    background: rgba(0, 255, 0, 0.1);
  }
  100% {
    transform: translateX(0);
    opacity: 1;
    background: transparent;
  }
`;

const scanline = keyframes`
  0% {
    transform: translateY(-100%) scale(1.2);
    opacity: 0;
    background: linear-gradient(
      to bottom,
      transparent 0%,
      rgba(0, 255, 0, 0.2) 20%,
      rgba(0, 255, 0, 0.5) 50%,
      rgba(0, 255, 0, 0.2) 80%,
      transparent 100%
    );
    box-shadow: 0 0 15px rgba(0, 255, 0, 0.5),
                0 0 30px rgba(0, 255, 0, 0.3),
                0 0 45px rgba(0, 255, 0, 0.1);
    filter: brightness(1.5) blur(2px);
  }
  25% {
    transform: translateY(-50%) scale(1);
    opacity: 1;
    background: linear-gradient(
      to bottom,
      transparent 0%,
      rgba(0, 255, 0, 0.3) 20%,
      rgba(0, 255, 0, 0.7) 50%,
      rgba(0, 255, 0, 0.3) 80%,
      transparent 100%
    );
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.7),
                0 0 40px rgba(0, 255, 0, 0.4),
                0 0 60px rgba(0, 255, 0, 0.2);
    filter: brightness(2) blur(1px);
  }
  50% {
    transform: translateY(0%) scale(0.8);
    opacity: 0.8;
    background: linear-gradient(
      to bottom,
      transparent 0%,
      rgba(0, 255, 0, 0.4) 20%,
      rgba(0, 255, 0, 0.9) 50%,
      rgba(0, 255, 0, 0.4) 80%,
      transparent 100%
    );
    box-shadow: 0 0 25px rgba(0, 255, 0, 0.9),
                0 0 50px rgba(0, 255, 0, 0.5),
                0 0 75px rgba(0, 255, 0, 0.3);
    filter: brightness(2.5) blur(0px);
  }
  75% {
    transform: translateY(50%) scale(1);
    opacity: 1;
    background: linear-gradient(
      to bottom,
      transparent 0%,
      rgba(0, 255, 0, 0.3) 20%,
      rgba(0, 255, 0, 0.7) 50%,
      rgba(0, 255, 0, 0.3) 80%,
      transparent 100%
    );
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.7),
                0 0 40px rgba(0, 255, 0, 0.4),
                0 0 60px rgba(0, 255, 0, 0.2);
    filter: brightness(2) blur(1px);
  }
  100% {
    transform: translateY(100%) scale(1.2);
    opacity: 0;
    background: linear-gradient(
      to bottom,
      transparent 0%,
      rgba(0, 255, 0, 0.2) 20%,
      rgba(0, 255, 0, 0.5) 50%,
      rgba(0, 255, 0, 0.2) 80%,
      transparent 100%
    );
    box-shadow: 0 0 15px rgba(0, 255, 0, 0.5),
                0 0 30px rgba(0, 255, 0, 0.3),
                0 0 45px rgba(0, 255, 0, 0.1);
    filter: brightness(1.5) blur(2px);
  }
`;

const PanelContainer = styled.div`
  position: relative;
  width: 300px;
  height: 100vh;
  background: #1a1a1a;
  color: #00ff00;
  padding: 20px;
  border-right: 2px solid rgba(0, 255, 0, 0.5);
  overflow-y: auto;
  font-family: 'JetBrains Mono', monospace;
  box-shadow: 0 0 30px rgba(0, 255, 0, 0.3),
              inset 0 0 20px rgba(0, 255, 0, 0.2);
  transform-style: preserve-3d;
  perspective: 1000px;
  transition: all 0.3s ease;

  &:hover {
    border-right-color: rgba(0, 255, 0, 0.8);
    box-shadow: 0 0 40px rgba(0, 255, 0, 0.4),
                inset 0 0 30px rgba(0, 255, 0, 0.3);
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(
      to right,
      transparent,
      rgba(0, 255, 0, 0.8),
      transparent
    );
    animation: ${scanline} 4s linear infinite;
    pointer-events: none;
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.8),
                0 0 40px rgba(0, 255, 0, 0.4),
                0 0 60px rgba(0, 255, 0, 0.2);
    filter: brightness(1.5) blur(1px);
  }

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: ${plasmaFieldGradient};
    background-size: 200% 200%, 200% 200%, 100% 100%;
    pointer-events: none;
    animation: ${plasmaField} 10s linear infinite;
    opacity: 0.7;
    mix-blend-mode: screen;
  }

  /* Custom Scrollbar */
  &::-webkit-scrollbar {
    width: 8px;
    background: rgba(0, 0, 0, 0.3);
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(0, 255, 0, 0.5);
    border-radius: 4px;
    box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
  }

  &::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 255, 0, 0.7);
    box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
  }

  &::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 4px;
    box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
  }
`;

const MatrixBackground = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  opacity: 0.15;
  pointer-events: none;
  perspective: 1000px;
  transform-style: preserve-3d;

  &::before, &::after {
    content: '01100101 10101010 11001100 10011001';
    position: absolute;
    top: -50%;
    left: -50%;
    right: -50%;
    bottom: -50%;
    white-space: pre-wrap;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    line-height: 1;
    background: linear-gradient(
      180deg,
      transparent 0%,
      rgba(0, 255, 0, 0.3) 50%,
      transparent 100%
    );
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    transform-origin: center;
    animation: ${matrixRain} 10s linear infinite;
    animation-delay: ${props => props.delay || '0s'};
    text-shadow: 0 0 8px rgba(0, 255, 0, 0.5);
    filter: brightness(1.5) contrast(1.2);
  }

  &::after {
    content: '10011001 11001100 10101010 01100101';
    animation-duration: 8s;
    animation-delay: ${props => props.delay ? `calc(${props.delay} + 2s)` : '2s'};
    opacity: 0.7;
    filter: brightness(1.2) contrast(1.1) blur(1px);
    transform: translateZ(-20px) rotateX(45deg);
  }

  @media (prefers-reduced-motion: no-preference) {
    &::before, &::after {
      animation-timing-function: cubic-bezier(0.645, 0.045, 0.355, 1);
    }
  }
`;

const StatusIndicator = styled.div`
  position: absolute;
  top: 20px;
  right: 20px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: ${props => props.active ?
    `radial-gradient(circle at center,
      rgba(0, 255, 0, 1) 0%,
      rgba(0, 255, 0, 0.8) 40%,
      rgba(0, 255, 0, 0.4) 70%,
      rgba(0, 255, 0, 0.2) 100%)`
    :
    `radial-gradient(circle at center,
      rgba(255, 0, 0, 1) 0%,
      rgba(255, 0, 0, 0.8) 40%,
      rgba(255, 0, 0, 0.4) 70%,
      rgba(255, 0, 0, 0.2) 100%)`
  };
  animation: ${props => {
    if (!props.active) return 'none';
    switch (props.effect) {
      case 'burst': return css`${superBurst} 3s infinite`;
      case 'alert': return css`${alertAnimation} 0.5s infinite, ${shockwave} 1s infinite`;
      case 'energyBurst': return css`${energyBurst} 2s infinite, ${plasmaWave} 3s infinite`;
      default: return css`${glowAnimation} 2s infinite, ${energyRipple} 3s infinite`;
    }
  }};
  z-index: 100;
  transform-style: preserve-3d;
  transition: all 0.3s ease;
  box-shadow: ${props => props.active ?
    `0 0 20px rgba(0, 255, 0, 0.7),
     0 0 40px rgba(0, 255, 0, 0.4),
     0 0 60px rgba(0, 255, 0, 0.2),
     inset 0 0 15px rgba(0, 255, 0, 0.8)`
    :
    `0 0 20px rgba(255, 0, 0, 0.7),
     0 0 40px rgba(255, 0, 0, 0.4),
     0 0 60px rgba(255, 0, 0, 0.2),
     inset 0 0 15px rgba(255, 0, 0, 0.8)`
  };

  &::before {
    content: '';
    position: absolute;
    top: -12px;
    left: -12px;
    right: -12px;
    bottom: -12px;
    border-radius: 50%;
    border: 3px solid ${props => props.active ?
      'rgba(0, 255, 0, 0.8)' :
      'rgba(255, 0, 0, 0.8)'
    };
    animation: ${props => props.active ?
      css`${energyRipple} 2s infinite, ${plasmaWave} 4s infinite` :
      'none'
    };
    transform-style: preserve-3d;
    filter: blur(1px);
  }

  &::after {
    content: '';
    position: absolute;
    top: -18px;
    left: -18px;
    right: -18px;
    bottom: -18px;
    border-radius: 50%;
    background: ${props => props.active ?
      `radial-gradient(circle at center,
        rgba(0, 255, 0, 0.4) 0%,
        rgba(0, 255, 0, 0.2) 40%,
        rgba(0, 255, 0, 0.1) 70%,
        transparent 100%)`
      :
      `radial-gradient(circle at center,
        rgba(255, 0, 0, 0.4) 0%,
        rgba(255, 0, 0, 0.2) 40%,
        rgba(255, 0, 0, 0.1) 70%,
        transparent 100%)`
    };
    animation: ${props => {
      if (!props.active) return 'none';
      switch (props.effect) {
        case 'burst': return css`${shockwave} 2s infinite, ${plasmaField} 4s infinite`;
        case 'alert': return css`${dataBurst} 1s infinite, ${energyBurst} 2s infinite`;
        case 'energyBurst': return css`${superBurst} 3s infinite, ${quantumBurst} 4s infinite`;
        default: return css`${dataBurst} 3s infinite, ${plasmaWave} 5s infinite`;
      }
    }};
    transform-origin: center;
    transform-style: preserve-3d;
    mix-blend-mode: screen;
  }

  &:hover {
    transform: scale(1.1) translateZ(10px);
    box-shadow: ${props => props.active ?
      `0 0 30px rgba(0, 255, 0, 0.8),
       0 0 50px rgba(0, 255, 0, 0.5),
       0 0 70px rgba(0, 255, 0, 0.3),
       inset 0 0 20px rgba(0, 255, 0, 0.9)`
      :
      `0 0 30px rgba(255, 0, 0, 0.8),
       0 0 50px rgba(255, 0, 0, 0.5),
       0 0 70px rgba(255, 0, 0, 0.3),
       inset 0 0 20px rgba(255, 0, 0, 0.9)`
    };
  }
`;

const PlasmaOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    linear-gradient(
      45deg,
      rgba(0, 255, 0, 0.1) 0%,
      transparent 20%,
      rgba(0, 255, 0, 0.15) 40%,
      transparent 60%,
      rgba(0, 255, 0, 0.1) 80%,
      transparent 100%
    ),
    radial-gradient(
      circle at 50% 50%,
      rgba(0, 255, 0, 0.2) 0%,
      rgba(0, 255, 0, 0.1) 30%,
      transparent 70%
    ),
    conic-gradient(
      from 0deg at 50% 50%,
      transparent 0%,
      rgba(0, 255, 0, 0.1) 25%,
      rgba(0, 255, 0, 0.2) 50%,
      rgba(0, 255, 0, 0.1) 75%,
      transparent 100%
    );
  background-size: 400% 400%, 200% 200%, 100% 100%;
  animation:
    ${plasmaField} 15s linear infinite,
    ${plasmaWave} 20s ease-in-out infinite;
  pointer-events: none;
  z-index: 1;
  mix-blend-mode: screen;
  filter: blur(1px) brightness(1.2);
  transform-style: preserve-3d;
  perspective: 1000px;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background:
      repeating-linear-gradient(
        45deg,
        rgba(0, 255, 0, 0.05) 0px,
        rgba(0, 255, 0, 0.1) 10px,
        rgba(0, 255, 0, 0.05) 20px
      ),
      repeating-linear-gradient(
        -45deg,
        rgba(0, 255, 0, 0.07) 0px,
        rgba(0, 255, 0, 0.12) 10px,
        rgba(0, 255, 0, 0.07) 20px
      );
    animation: ${energyRipple} 10s linear infinite;
    opacity: 0.5;
  }

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(
      circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
      rgba(0, 255, 0, 0.2) 0%,
      rgba(0, 255, 0, 0.1) 20%,
      transparent 50%
    );
    animation: ${superBurst} 8s infinite;
    mix-blend-mode: screen;
    filter: blur(2px);
  }
`;

const SectionsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const Section = styled.div`
  margin: 20px 0;
  padding: 20px;
  background: linear-gradient(
    135deg,
    rgba(42, 42, 42, 0.9) 0%,
    rgba(32, 32, 32, 0.95) 50%,
    rgba(42, 42, 42, 0.9) 100%
  );
  border-radius: 8px;
  border: 2px solid ${props => props.highlight ? 'rgba(0, 255, 0, 0.8)' : 'rgba(51, 51, 51, 0.8)'};
  animation: ${props => {
    if (!props.highlight) return 'none';
    switch (props.effect) {
      case 'burst': return css`
        ${quantumBurst} 3s infinite,
        ${plasmaWave} 4s infinite ease-in-out
      `;
      case 'alert': return css`
        ${energyBurst} 2s infinite,
        ${plasmaWave} 3s infinite,
        ${shockwave} 2.5s infinite
      `;
      case 'energyBurst': return css`
        ${quantumBurst} 3s infinite,
        ${shockwave} 3s infinite,
        ${superBurst} 4s infinite
      `;
      default: return css`
        ${energyBurst} 3s infinite,
        ${plasmaField} 5s infinite
      `;
    }
  }};
  position: relative;
  overflow: hidden;
  transform-style: preserve-3d;
  perspective: 1000px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 20px rgba(0, 255, 0, 0.2),
              inset 0 0 15px rgba(0, 255, 0, 0.1);

  &:hover {
    transform: translateZ(40px) scale(1.02) rotateX(2deg);
    box-shadow: 0 0 40px rgba(0, 255, 0, 0.5),
                0 0 60px rgba(0, 255, 0, 0.3),
                0 0 80px rgba(0, 255, 0, 0.1),
                inset 0 0 25px rgba(0, 255, 0, 0.2);
    border-color: rgba(0, 255, 0, 1);
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: ${props => props.highlight ? `
      radial-gradient(
        circle at 50% 50%,
        rgba(0, 255, 0, 0.15) 0%,
        rgba(0, 255, 0, 0.1) 30%,
        rgba(0, 255, 0, 0.05) 60%,
        transparent 80%
      )
    ` : 'none'};
    animation: ${props => props.highlight ? css`${plasmaField} 8s infinite` : 'none'};
    pointer-events: none;
    mix-blend-mode: screen;
  }

  &::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    right: -50%;
    bottom: -50%;
    background: ${props => props.highlight ? `
      conic-gradient(
        from 0deg at 50% 50%,
        transparent 0%,
        rgba(0, 255, 0, 0.1) 25%,
        rgba(0, 255, 0, 0.15) 50%,
        rgba(0, 255, 0, 0.1) 75%,
        transparent 100%
      )
    ` : 'none'};
    animation: ${props => props.highlight ? css`${superBurst} 10s infinite` : 'none'};
    pointer-events: none;
    mix-blend-mode: screen;
    filter: blur(2px);
  }
`;

const PriorityBadge = styled.span`
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  margin-left: 12px;
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: ${props => {
    const colors = {
      high: 'linear-gradient(135deg, #ff4444 0%, #ff6666 50%, #ff4444 100%)',
      medium: 'linear-gradient(135deg, #ffbb33 0%, #ffcc44 50%, #ffbb33 100%)',
      low: 'linear-gradient(135deg, #00C851 0%, #00E676 50%, #00C851 100%)',
      default: 'linear-gradient(135deg, #333333 0%, #444444 50%, #333333 100%)'
    };
    return colors[props.level] || colors.default;
  }};
  animation: ${props => {
    switch (props.level) {
      case 'high': return css`
        ${alertAnimation} 1s infinite,
        ${shockwave} 2s infinite,
        ${energyBurst} 3s infinite
      `;
      case 'medium': return css`
        ${priorityPulse} 2s infinite,
        ${plasmaWave} 4s infinite
      `;
      case 'low': return css`
        ${glowAnimation} 3s infinite,
        ${energyRipple} 5s infinite
      `;
      default: return 'none';
    }
  }};
  box-shadow: ${props => {
    const color = {
      high: 'rgba(255, 68, 68, ',
      medium: 'rgba(255, 187, 51, ',
      low: 'rgba(0, 200, 81, ',
      default: 'rgba(51, 51, 51, '
    }[props.level || 'default'];
    return `0 0 15px ${color}0.6),
            0 0 30px ${color}0.4),
            0 0 45px ${color}0.2),
            inset 0 0 10px ${color}0.5)`;
  }};
  transform-style: preserve-3d;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
  letter-spacing: 0.5px;

  &::before {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    border-radius: 22px;
    background: ${props => {
      const color = {
        high: 'rgba(255, 68, 68, ',
        medium: 'rgba(255, 187, 51, ',
        low: 'rgba(0, 200, 81, ',
        default: 'rgba(51, 51, 51, '
      }[props.level || 'default'];
      return `linear-gradient(135deg,
        ${color}0.5) 0%,
        ${color}0.2) 50%,
        transparent 100%
      )`;
    }};
    animation: ${props => props.level === 'high' ? css`${superBurst} 3s infinite` : 'none'};
    filter: blur(2px);
    z-index: -1;
  }

  &:hover {
    transform: translateZ(10px) scale(1.1) rotateX(5deg);
    box-shadow: ${props => {
      const color = {
        high: 'rgba(255, 68, 68, ',
        medium: 'rgba(255, 187, 51, ',
        low: 'rgba(0, 200, 81, ',
        default: 'rgba(51, 51, 51, '
      }[props.level || 'default'];
      return `0 0 25px ${color}0.8),
              0 0 50px ${color}0.6),
              0 0 75px ${color}0.4),
              inset 0 0 15px ${color}0.7)`;
    }};
    letter-spacing: 1px;

    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      border-radius: 20px;
      background: ${props => {
        const color = {
          high: 'rgba(255, 68, 68, ',
          medium: 'rgba(255, 187, 51, ',
          low: 'rgba(0, 200, 81, ',
          default: 'rgba(51, 51, 51, '
        }[props.level || 'default'];
        return `radial-gradient(circle at center,
          ${color}0.3) 0%,
          transparent 70%
        )`;
      }};
      animation: ${plasmaField} 2s infinite;
      mix-blend-mode: screen;
    }
  }
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin: 20px 0;
  transform-style: preserve-3d;
  perspective: 1000px;
  position: relative;

  &::after {
    content: '';
    position: absolute;
    top: -10px;
    left: -10px;
    right: -10px;
    bottom: -10px;
    background: ${props => props.alert ?
      'radial-gradient(circle at center, rgba(255, 68, 68, 0.1) 0%, transparent 70%)' :
      'radial-gradient(circle at center, rgba(0, 255, 0, 0.1) 0%, transparent 70%)'
    };
    animation: ${plasmaField} 10s infinite linear;
    pointer-events: none;
    z-index: -1;
  }
`;

const MetricBox = styled.div`
  padding: 15px;
  background: linear-gradient(
    135deg,
    ${props => props.alert ?
      'rgba(68, 34, 34, 0.9) 0%, rgba(51, 51, 51, 0.95) 100%' :
      'rgba(34, 68, 34, 0.9) 0%, rgba(51, 51, 51, 0.95) 100%'
    }
  );
  border-radius: 8px;
  text-align: center;
  font-size: 13px;
  position: relative;
  overflow: hidden;
  transform-style: preserve-3d;
  perspective: 1000px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 15px ${props => props.alert ?
    'rgba(255, 68, 68, 0.3)' :
    'rgba(0, 255, 0, 0.3)'
  };
  border: 1px solid ${props => props.alert ?
    'rgba(255, 68, 68, 0.3)' :
    'rgba(0, 255, 0, 0.3)'
  };

  .value {
    font-size: 18px;
    font-weight: bold;
    margin: 8px 0;
    color: ${props => props.alert ? '#ff4444' : '#00ff00'};
    text-shadow: 0 0 10px ${props => props.alert ?
      'rgba(255, 68, 68, 0.8)' :
      'rgba(0, 255, 0, 0.8)'
    };
    position: relative;
    z-index: 2;
  }

  &::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    right: -50%;
    bottom: -50%;
    background: ${props => props.alert ?
      'conic-gradient(from 0deg at 50% 50%, transparent 0%, rgba(255, 68, 68, 0.1) 50%, transparent 100%)' :
      'conic-gradient(from 0deg at 50% 50%, transparent 0%, rgba(0, 255, 0, 0.1) 50%, transparent 100%)'
    };
    animation: ${props => props.effect === 'energyBurst' ?
      css`${superBurst} 3s infinite` :
      css`${plasmaField} 5s infinite`
    };
    z-index: 1;
  }

  &:hover {
    transform: translateZ(30px) scale(1.1) rotateX(10deg);
    box-shadow: 0 0 30px ${props => props.alert ?
      'rgba(255, 68, 68, 0.7)' :
      'rgba(0, 255, 0, 0.7)'
    },
    0 0 50px ${props => props.alert ?
      'rgba(255, 68, 68, 0.4)' :
      'rgba(0, 255, 0, 0.4)'
    },
    0 0 70px ${props => props.alert ?
      'rgba(255, 68, 68, 0.2)' :
      'rgba(0, 255, 0, 0.2)'
    };
    border-color: ${props => props.alert ?
      'rgba(255, 68, 68, 0.8)' :
      'rgba(0, 255, 0, 0.8)'
    };
    animation: ${props => props.alert ?
      css`
        ${quantumBurst} 2s infinite,
        ${shockwave} 3s infinite,
        ${plasmaWave} 4s infinite
      ` :
      css`
        ${energyBurst} 2s infinite,
        ${plasmaField} 3s infinite,
        ${superBurst} 4s infinite
      `
    };

    .value {
      animation: ${props => props.alert ?
        css`${alertAnimation} 1s infinite` :
        css`${glowAnimation} 2s infinite`
      };
    }

    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: ${props => props.alert ?
        'radial-gradient(circle at center, rgba(255, 68, 68, 0.2) 0%, transparent 70%)' :
        'radial-gradient(circle at center, rgba(0, 255, 0, 0.2) 0%, transparent 70%)'
      };
      animation: ${plasmaWave} 2s infinite;
      mix-blend-mode: screen;
    }
  }
`;

const MessageInput = styled.textarea`
  width: 100%;
  height: 80px;
  padding: 15px;
  margin: 15px 0;
  background: linear-gradient(
    135deg,
    rgba(26, 26, 26, 0.95) 0%,
    rgba(34, 34, 34, 0.9) 100%
  );
  border: 2px solid rgba(0, 255, 0, 0.3);
  border-radius: 8px;
  color: #00ff00;
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  resize: none;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 15px rgba(0, 255, 0, 0.1),
              inset 0 0 10px rgba(0, 255, 0, 0.1);
  transform-style: preserve-3d;
  perspective: 1000px;

  &:focus {
    outline: none;
    border-color: rgba(0, 255, 0, 0.8);
    box-shadow: 0 0 25px rgba(0, 255, 0, 0.3),
                0 0 50px rgba(0, 255, 0, 0.1),
                inset 0 0 20px rgba(0, 255, 0, 0.2);
    animation: ${inputGlow} 2s infinite;
    transform: translateZ(10px);
    background: linear-gradient(
      135deg,
      rgba(26, 26, 26, 0.98) 0%,
      rgba(34, 34, 34, 0.95) 100%
    );

    &::placeholder {
      color: rgba(0, 255, 0, 0.4);
      text-shadow: 0 0 5px rgba(0, 255, 0, 0.2);
    }
  }

  &::placeholder {
    color: rgba(0, 255, 0, 0.3);
    transition: color 0.3s ease;
  }

  &:hover {
    border-color: rgba(0, 255, 0, 0.5);
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.2),
                inset 0 0 15px rgba(0, 255, 0, 0.15);
    transform: translateZ(5px);
  }
`;

const ActionButton = styled.button`
  padding: 10px 20px;
  background: linear-gradient(
    135deg,
    rgba(0, 68, 0, 0.9) 0%,
    rgba(0, 102, 0, 0.8) 100%
  );
  border: 2px solid rgba(0, 255, 0, 0.5);
  border-radius: 8px;
  color: #00ff00;
  cursor: pointer;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  font-weight: bold;
  margin-right: 12px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform-style: preserve-3d;
  perspective: 1000px;
  text-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
  letter-spacing: 0.5px;

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
      rgba(0, 255, 0, 0.1) 50%,
      transparent 100%
    );
    animation: ${plasmaField} 5s linear infinite;
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  &:hover {
    background: linear-gradient(
      135deg,
      rgba(0, 102, 0, 0.9) 0%,
      rgba(0, 136, 0, 0.8) 100%
    );
    border-color: rgba(0, 255, 0, 0.8);
    animation: ${energyBurst} 2s infinite;
    transform: scale(1.05) translateZ(20px);
    box-shadow: 0 0 30px rgba(0, 255, 0, 0.5),
                0 0 50px rgba(0, 255, 0, 0.3),
                0 0 70px rgba(0, 255, 0, 0.1);
    letter-spacing: 1px;

    &::before {
      opacity: 1;
    }

    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: radial-gradient(
        circle at center,
        rgba(0, 255, 0, 0.2) 0%,
        transparent 70%
      );
      animation: ${plasmaWave} 2s infinite;
      mix-blend-mode: screen;
    }
  }

  &:active {
    transform: scale(0.95) translateZ(-10px);
    animation: ${buttonGlow} 0.3s ease-out;
    box-shadow: 0 0 15px rgba(0, 255, 0, 0.3),
                0 0 30px rgba(0, 255, 0, 0.2),
                inset 0 0 10px rgba(0, 255, 0, 0.2);
    border-color: rgba(0, 255, 0, 0.6);
    letter-spacing: 0.5px;
  }
`;

const LogWindow = styled.div`
  margin-top: 20px;
  padding: 15px;
  background: linear-gradient(
    135deg,
    rgba(0, 0, 0, 0.95) 0%,
    rgba(10, 10, 10, 0.9) 100%
  );
  border: 2px solid rgba(0, 255, 0, 0.3);
  border-radius: 8px;
  height: 180px;
  overflow-y: auto;
  font-size: 13px;
  position: relative;
  box-shadow: 0 0 30px rgba(0, 255, 0, 0.1),
              inset 0 0 20px rgba(0, 255, 0, 0.1);
  transform-style: preserve-3d;
  perspective: 1000px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &::-webkit-scrollbar {
    width: 8px;
    background: rgba(26, 26, 26, 0.8);
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb {
    background: linear-gradient(
      to bottom,
      rgba(0, 255, 0, 0.8),
      rgba(0, 255, 0, 0.4)
    );
    border-radius: 4px;
    box-shadow: 0 0 15px rgba(0, 255, 0, 0.5),
                inset 0 0 5px rgba(0, 255, 0, 0.3);
  }

  &::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 4px;
    box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 30px;
    background: linear-gradient(
      to bottom,
      rgba(0, 0, 0, 0.8) 0%,
      transparent 100%
    );
    pointer-events: none;
    z-index: 1;
  }

  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 30px;
    background: linear-gradient(
      to top,
      rgba(0, 0, 0, 0.8) 0%,
      transparent 100%
    );
    pointer-events: none;
    z-index: 1;
  }

  .log-entry {
    margin: 8px 0;
    padding: 8px;
    border-bottom: 1px solid rgba(34, 34, 34, 0.8);
    position: relative;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: ${logEntryAnimation} 0.5s ease-out;
    transform-style: preserve-3d;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 4px;

    &:hover {
      background: rgba(0, 255, 0, 0.1);
      transform: translateX(10px) translateZ(10px) rotateX(2deg);
      box-shadow: -5px 0 20px rgba(0, 255, 0, 0.2),
                  0 0 30px rgba(0, 255, 0, 0.1);
      border-bottom-color: rgba(0, 255, 0, 0.3);

      .timestamp {
        color: rgba(0, 255, 0, 0.8);
        text-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
      }

      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: -10px;
        width: 4px;
        height: 100%;
        background: rgba(0, 255, 0, 0.5);
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
        animation: ${glowAnimation} 2s infinite;
      }

      &::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(
          circle at left center,
          rgba(0, 255, 0, 0.1) 0%,
          transparent 70%
        );
        animation: ${plasmaField} 2s infinite;
        pointer-events: none;
        mix-blend-mode: screen;
      }
    }
  }

  .timestamp {
    color: rgba(102, 102, 102, 0.8);
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    margin-right: 10px;
    transition: all 0.3s ease;
  }

  &:hover {
    border-color: rgba(0, 255, 0, 0.5);
    box-shadow: 0 0 40px rgba(0, 255, 0, 0.15),
                inset 0 0 25px rgba(0, 255, 0, 0.1);
    transform: translateZ(5px);
  }
`;

const ChaseCommsPanel = () => {
  const [active, setActive] = useState(false);
  const [currentEffect, setCurrentEffect] = useState('none');
  const [lastMessage, setLastMessage] = useState(null);
  const [metrics, setMetrics] = useState({
    performance: { cpu: 0, memory: 0 },
    errorRate: 0,
    latency: 0,
    kafka: { healthy: false, channels: 0, messagesPerSec: 0, memoryUsage: 0 },
    redis: { healthy: false },
    rabbitmq: { healthy: false },
    postgresql: { healthy: false }
  });
  const [logs, setLogs] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [metricsExpanded, setMetricsExpanded] = useState(true);
  const [systemExpanded, setSystemExpanded] = useState(true);
  const [logsExpanded, setLogsExpanded] = useState(true);
  const logWindowRef = useRef(null);

  useEffect(() => {
    const commsSub = chaseCommsService.subscribe((type, data) => {
      if (type === 'message') {
        setLastMessage(data);
        addLog(`Received message: ${data.type}`);
        handleVisualEffect(data);
      } else if (type === 'alert') {
        handleAlert(data);
      } else if (type === 'burst') {
        handleBurst(data);
      }
    });

    const monitoringSub = monitoringService.subscribe((type, data) => {
      if (type === 'kafka' || type === 'performance') {
        setMetrics(prev => {
          const newMetrics = { ...prev };
          if (type === 'performance') {
            newMetrics.performance = { ...prev.performance, ...data };
          } else {
            Object.assign(newMetrics, data);
          }
          return newMetrics;
        });
      }
    });

    return () => {
      commsSub();
      monitoringSub();
    };
  }, []);

  const handleVisualEffect = (message) => {
    setActive(true);
    setCurrentEffect(message.visualEffect);

    switch (message.visualEffect) {
      case 'pulse':
        setTimeout(() => {
          setActive(false);
          setCurrentEffect('none');
        }, 2000);
        break;
      case 'glow':
        setTimeout(() => {
          setActive(false);
          setCurrentEffect('none');
        }, 3000);
        break;
      case 'burst':
        const metricsSection = document.querySelector('.metrics-section');
        if (metricsSection) {
          metricsSection.style.animation = 'none';
          void metricsSection.offsetHeight;
          metricsSection.style.animation = `${superBurst} 3s`;
        }
        setTimeout(() => {
          setActive(false);
          setCurrentEffect('none');
        }, 3000);
        break;
      case 'alert':
        const alertSequence = [
          { active: false, effect: 'alert', delay: 100 },
          { active: true, effect: 'alert', delay: 500 },
          { active: false, effect: 'alert', delay: 1000 },
          { active: true, effect: 'alert', delay: 2000 },
          { active: false, effect: 'none', delay: 4000 }
        ];

        alertSequence.forEach(({ active, effect, delay }) => {
          setTimeout(() => {
            setActive(active);
            setCurrentEffect(effect);
          }, delay);
        });
        break;
      case 'energyBurst':
        Array.from({ length: 3 }).forEach((_, i) => {
          setTimeout(() => {
            setActive(true);
            setCurrentEffect('energyBurst');
            const metricsSection = document.querySelector('.metrics-section');
            if (metricsSection) {
              metricsSection.style.animation = 'none';
              void metricsSection.offsetHeight;
              metricsSection.style.animation = `${superBurst} 2s, ${shockwave} 2s`;
            }
          }, i * 1000);
        });
        setTimeout(() => {
          setActive(false);
          setCurrentEffect('none');
        }, 4000);
        break;
      default:
        setTimeout(() => {
          setActive(false);
          setCurrentEffect('none');
        }, 2000);
    }
  };

  const handleAlert = (data) => {
    addLog(`ALERT from ${data.source}: ${data.alert}`);
    handleVisualEffect({ visualEffect: 'alert' });
  };

  const handleBurst = (data) => {
    addLog(`BURST on ${data.target}: ${data.burst} (Intensity: ${data.intensity})`);
    handleVisualEffect({ visualEffect: 'energyBurst' });
  };

  useEffect(() => {
    if (logWindowRef.current) {
      logWindowRef.current.scrollTop = logWindowRef.current.scrollHeight;
    }
  }, [logs]);

  const addLog = (message) => {
    setLogs(prev => [...prev, {
      timestamp: new Date().toISOString(),
      message
    }].slice(-50));
  };

  const getPriorityLevel = () => {
    const performanceMetrics = metrics.performance || {};
    const cpu = performanceMetrics.cpu || 0;
    const memory = performanceMetrics.memory || 0;

    if (cpu > 80 || memory > 80) {
      return 'high';
    }
    if (cpu > 60 || memory > 60) {
      return 'medium';
    }
    return 'low';
  };

  const handleMessage = (type) => {
    const message = {
      type: `chase.comms.${type}`,
      timestamp: Date.now(),
      content: inputMessage,
      priority: getPriorityLevel()
    };

    setActive(true);
    setTimeout(() => setActive(false), 3000);

    const metricsSection = document.querySelector('.metrics-section');
    if (metricsSection) {
      metricsSection.style.animation = 'none';
      void metricsSection.offsetHeight;
      metricsSection.style.animation = `${energyBurst} 3s`;
    }

    chaseCommsService.sendResponse(message);
    addLog(`Sent message: ${message.type}`);
    setInputMessage('');
  };

  return (
    <PanelContainer>
      <MatrixBackground delay="0s" />
      <MatrixBackground delay="2s" />
      <MatrixBackground delay="4s" />
      <PlasmaOverlay />

      <StatusLights statuses={[
        { color: '#00ff00', active: metrics.kafka?.healthy, tooltip: 'Kafka Broker Status' },
        { color: '#00ffff', active: metrics.redis?.healthy, tooltip: 'Redis Connection' },
        { color: '#ffff00', active: metrics.rabbitmq?.healthy, tooltip: 'RabbitMQ Status' },
        { color: '#ff00ff', active: metrics.postgresql?.healthy, tooltip: 'PostgreSQL Status' },
        { color: '#ff8800', active: metrics.performance?.healthy, tooltip: 'System Performance' },
        { color: '#00ff88', active: metrics.memory < 80, tooltip: 'Memory Usage' },
        { color: '#88ff00', active: metrics.cpu < 80, tooltip: 'CPU Usage' },
        { color: '#0088ff', active: metrics.latency < 200, tooltip: 'Network Latency' }
      ]} />

      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px',
        position: 'relative',
        zIndex: 2,
        perspective: '1000px',
        transformStyle: 'preserve-3d',
        animation: active ? `${plasmaWave} 3s infinite` : 'none'
      }}>
        <h2 style={{
          position: 'relative',
          zIndex: 2,
          textShadow: `0 0 10px #00ff00,
                       0 0 20px #00ff00,
                       0 0 30px #00ff00`,
          animation: `${glowAnimation} 2s infinite`,
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          transform: 'translateZ(20px)'
        }}>
          <span style={{
            display: 'inline-block',
            animation: active ? `${quantumBurst} 2s infinite` : 'none',
            transformStyle: 'preserve-3d',
            filter: 'brightness(1.5) contrast(1.2)'
          }}>Chase</span>
          <span style={{
            display: 'inline-block',
            animation: active ? `${energyBurst} 2s infinite` : 'none',
            transformStyle: 'preserve-3d',
            filter: 'brightness(1.5) contrast(1.2)'
          }}>Comms</span>
        </h2>
        <StatusIndicator active={active} effect={currentEffect} />
      </div>

      <SectionsContainer style={{
        position: 'relative',
        zIndex: 1,
        transformStyle: 'preserve-3d',
        animation: active ? `${plasmaWave} 5s infinite ease-in-out` : 'none'
      }}>
        <Section>
          <h3 style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            cursor: 'pointer'
          }} onClick={() => setMetricsExpanded(!metricsExpanded)}>
            <span>Kafka Status</span>
            <span style={{ color: metrics.kafka?.healthy ? '#00ff00' : '#ff4444' }}>
              {metricsExpanded ? '▼' : '▶'}
            </span>
          </h3>
          {metricsExpanded && (
            <div style={{
              padding: '10px',
              background: 'rgba(0, 0, 0, 0.3)',
              borderRadius: '4px',
              marginTop: '10px'
            }}>
              <div>Active Channels: {metrics.kafka?.channels || 0}</div>
              <div>Messages/sec: {metrics.kafka?.messagesPerSec || '0'}/s</div>
              <div>Memory Usage: {metrics.kafka?.memoryUsage || 0}%</div>
            </div>
          )}
        </Section>

        <Section>
          <h3 style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            cursor: 'pointer'
          }} onClick={() => setSystemExpanded(!systemExpanded)}>
            <div>
              System Status
              <PriorityBadge level={getPriorityLevel()}>
                {getPriorityLevel().toUpperCase()}
              </PriorityBadge>
            </div>
            <span>{systemExpanded ? '▼' : '▶'}</span>
          </h3>

          {systemExpanded && (
            <div>
              <MetricsGrid>
                <MetricBox alert={metrics.cpu > 80} effect={currentEffect}>
                  <div>CPU Usage</div>
                  <div className="value">{metrics.cpu || 0}%</div>
                </MetricBox>
                <MetricBox alert={metrics.memory > 80} effect={currentEffect}>
                  <div>Memory</div>
                  <div className="value">{metrics.memory || 0}%</div>
                </MetricBox>
                <MetricBox alert={metrics.errorRate > 0.5} effect={currentEffect}>
                  <div>Error Rate</div>
                  <div className="value">{metrics.errorRate || 0}%</div>
                </MetricBox>
                <MetricBox alert={metrics.latency > 200} effect={currentEffect}>
                  <div>Latency</div>
                  <div className="value">{metrics.latency || 0}ms</div>
                </MetricBox>
              </MetricsGrid>

              <MessageInput
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Enter message..."
              />

              <div>
                <ActionButton
                  type="status"
                  onClick={() => handleMessage('status')}
                  title="Check system status"
                >
                  Status
                </ActionButton>
                <ActionButton
                  type="update"
                  onClick={() => handleMessage('update')}
                  title="Send system update"
                >
                  Update
                </ActionButton>
                <ActionButton
                  type="priority"
                  onClick={() => handleMessage('priority')}
                  title="Send priority message"
                >
                  Priority
                </ActionButton>
              </div>
            </div>
          )}
        </Section>

        <Section>
          <h3 style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            cursor: 'pointer'
          }} onClick={() => setLogsExpanded(!logsExpanded)}>
            <span>Message Log</span>
            <span>{logsExpanded ? '▼' : '▶'}</span>
          </h3>
          {logsExpanded && (
            <LogWindow ref={logWindowRef}>
              {logs.map((log, index) => (
                <div key={index} className="log-entry">
                  <span className="timestamp">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  {log.message}
                </div>
              ))}
            </LogWindow>
          )}
        </Section>

        {lastMessage && (
          <Section
            highlight={true}
            effect={currentEffect}
            style={{
              animation: `${superBurst} 2s, ${shockwave} 2s`,
              transformStyle: 'preserve-3d'
            }}
          >
            <h3 style={{
              position: 'relative',
              zIndex: 2,
              textShadow: '0 0 10px #00ff00',
              animation: `${glowAnimation} 2s infinite`
            }}>Last Message</h3>
            <pre style={{
              fontSize: '12px',
              overflow: 'auto',
              padding: '10px',
              background: 'rgba(0, 0, 0, 0.3)',
              borderRadius: '3px',
              border: '1px solid rgba(0, 255, 0, 0.2)',
              boxShadow: 'inset 0 0 10px rgba(0, 255, 0, 0.1)',
              position: 'relative',
              transformStyle: 'preserve-3d',
              transform: 'translateZ(5px)'
            }}>
              {JSON.stringify(lastMessage, null, 2)}
            </pre>
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'radial-gradient(circle at center, rgba(0, 255, 0, 0.1) 0%, transparent 70%)',
              animation: `${plasmaField} 10s linear infinite`,
              pointerEvents: 'none',
              zIndex: 1
            }} />
          </Section>
        )}
      </SectionsContainer>
    </PanelContainer>
  );
};

export default ChaseCommsPanel;