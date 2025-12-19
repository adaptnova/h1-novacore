import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';

// Create root element for React
const root = document.createElement('div');
root.id = 'root';
document.body.appendChild(root);

// Apply VSCode styling
document.body.className = 'vscode-light';

// Initialize React
ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);