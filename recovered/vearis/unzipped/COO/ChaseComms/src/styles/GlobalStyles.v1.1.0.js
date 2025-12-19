import { createGlobalStyle } from 'styled-components';

// Softer color palette with pure black background
export const COLORS = {
  background: '#000000',
  surface: '#000000',
  border: '#1a1a1a',
  borderHover: '#2a2a2a',
  text: '#888888',
  textBright: '#aaaaaa',
  accent: '#00cc00',
  accentHover: '#00ff00',
  warning: '#cccc00',
  error: '#cc0000',
  success: '#00cc00',
  textDim: '#666666',
  overlay: 'rgba(0, 0, 0, 0.95)',
};

const GlobalStyles = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  html, body, #root {
    background-color: ${COLORS.background};
    color: ${COLORS.text};
    height: 100%;
    overflow: hidden;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    line-height: 1.5;
  }

  ::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }

  ::-webkit-scrollbar-track {
    background: ${COLORS.background};
  }

  ::-webkit-scrollbar-thumb {
    background: ${COLORS.border};
    border-radius: 3px;

    &:hover {
      background: ${COLORS.borderHover};
    }
  }

  .tooltip {
    z-index: 9999;
    position: absolute;
  }

  button, input, select, textarea {
    font-family: inherit;
    font-size: inherit;
    color: inherit;
    background: ${COLORS.background};
    border: 1px solid ${COLORS.border};
    transition: all 0.2s ease;

    &:hover {
      border-color: ${COLORS.borderHover};
    }

    &:focus {
      outline: none;
      border-color: ${COLORS.accent};
    }
  }

  // Panel borders
  .panel-border {
    position: relative;

    &::after {
      content: '';
      position: absolute;
      inset: 0;
      border: 1px solid ${COLORS.border};
      pointer-events: none;
      transition: border-color 0.2s ease;
    }

    &:hover::after {
      border-color: ${COLORS.borderHover};
    }
  }

  // Status indicators
  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    position: relative;
    
    &::after {
      content: '';
      position: absolute;
      inset: -2px;
      border-radius: 50%;
      border: 1px solid currentColor;
      opacity: 0.3;
    }
  }

  // Tooltips
  .tooltip-container {
    position: relative;

    .tooltip {
      position: absolute;
      bottom: 100%;
      left: 50%;
      transform: translateX(-50%);
      padding: 8px 12px;
      background: ${COLORS.overlay};
      border-radius: 4px;
      font-size: 12px;
      white-space: pre-wrap;
      pointer-events: none;
      opacity: 0;
      visibility: hidden;
      transition: all 0.2s ease;
      z-index: 9999;
      margin-bottom: 8px;

      &::after {
        content: '';
        position: absolute;
        top: 100%;
        left: 50%;
        transform: translateX(-50%);
        border: 4px solid transparent;
        border-top-color: currentColor;
      }
    }

    &:hover .tooltip {
      opacity: 1;
      visibility: visible;
    }
  }
`;

export default GlobalStyles;
