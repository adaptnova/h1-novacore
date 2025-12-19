import apiClient from '../api/client';
import { INFRASTRUCTURE_CONFIG } from '../config/infrastructure';

class PatternCache {
  constructor() {
    this.cache = new Map();
    this.maxSize = 1000;
    this.ttl = 300000; // 5 minutes
  }

  generateKey(fieldData) {
    return JSON.stringify(fieldData);
  }

  async get(key) {
    const cached = this.cache.get(key);
    if (!cached) return null;

    if (Date.now() > cached.expiry) {
      this.cache.delete(key);
      return null;
    }

    return cached.data;
  }

  async set(key, data) {
    if (this.cache.size >= this.maxSize) {
      // Remove oldest entry
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }

    this.cache.set(key, {
      data,
      expiry: Date.now() + this.ttl
    });
  }

  clear() {
    this.cache.clear();
  }
}

class PatternRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.colors = {
      background: '#000000',
      grid: '#1a1a1a',
      pattern: '#00ff00',
      highlight: '#00cc00',
      warning: '#cccc00',
      error: '#cc0000'
    };
  }

  clear() {
    this.ctx.fillStyle = this.colors.background;
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }

  drawGrid() {
    this.ctx.strokeStyle = this.colors.grid;
    this.ctx.lineWidth = 0.5;

    // Draw vertical lines
    for (let x = 0; x <= this.canvas.width; x += 20) {
      this.ctx.beginPath();
      this.ctx.moveTo(x, 0);
      this.ctx.lineTo(x, this.canvas.height);
      this.ctx.stroke();
    }

    // Draw horizontal lines
    for (let y = 0; y <= this.canvas.height; y += 20) {
      this.ctx.beginPath();
      this.ctx.moveTo(0, y);
      this.ctx.lineTo(this.canvas.width, y);
      this.ctx.stroke();
    }
  }

  drawPattern(pattern, metrics) {
    this.clear();
    this.drawGrid();

    // Draw pattern points
    this.ctx.fillStyle = this.getPatternColor(metrics);
    pattern.forEach(point => {
      this.ctx.beginPath();
      this.ctx.arc(point.x, point.y, 2, 0, Math.PI * 2);
      this.ctx.fill();
    });

    // Draw connections between points
    this.ctx.strokeStyle = this.getPatternColor(metrics);
    this.ctx.lineWidth = 1;
    this.ctx.beginPath();
    pattern.forEach((point, index) => {
      if (index === 0) {
        this.ctx.moveTo(point.x, point.y);
      } else {
        this.ctx.lineTo(point.x, point.y);
      }
    });
    this.ctx.stroke();

    // Draw metrics
    this.drawMetrics(metrics);
  }

  getPatternColor(metrics) {
    if (metrics.quality < 0.5) return this.colors.error;
    if (metrics.quality < 0.8) return this.colors.warning;
    return this.colors.pattern;
  }

  drawMetrics(metrics) {
    const padding = 10;
    const fontSize = 12;
    this.ctx.font = `${fontSize}px monospace`;
    this.ctx.fillStyle = this.colors.pattern;

    const metricsText = [
      `Quality: ${(metrics.quality * 100).toFixed(1)}%`,
      `Strength: ${(metrics.strength * 100).toFixed(1)}%`,
      `Resonance: ${(metrics.resonance * 100).toFixed(1)}%`
    ];

    metricsText.forEach((text, index) => {
      this.ctx.fillText(text, padding, padding + (fontSize + 5) * index);
    });
  }

  resize(width, height) {
    this.canvas.width = width;
    this.canvas.height = height;
    this.clear();
    this.drawGrid();
  }
}

export class PatternVisualizationService {
  constructor(canvas) {
    this.cache = new PatternCache();
    this.renderer = new PatternRenderer(canvas);
    this.ws = null;
    this.onPatternUpdate = null;
  }

  async initialize() {
    // Set up WebSocket connection for real-time updates
    this.ws = await apiClient.createWebSocket(
      INFRASTRUCTURE_CONFIG.websockets.channels.novaField,
      this.handlePatternUpdate.bind(this)
    );
  }

  handlePatternUpdate(data) {
    if (this.onPatternUpdate) {
      this.onPatternUpdate(data);
    }

    if (data.pattern) {
      this.visualizePattern(data.pattern, data.metrics);
    }
  }

  async visualizePattern(fieldData, metrics = null) {
    const cacheKey = this.cache.generateKey(fieldData);
    let pattern = await this.cache.get(cacheKey);

    if (!pattern) {
      try {
        const response = await apiClient.analyzePattern(fieldData);
        pattern = response.pattern;
        await this.cache.set(cacheKey, pattern);
      } catch (error) {
        console.error('Pattern analysis failed:', error);
        return null;
      }
    }

    if (!metrics) {
      try {
        metrics = await apiClient.getFieldStrength();
      } catch (error) {
        console.error('Failed to get field metrics:', error);
        metrics = { quality: 0, strength: 0, resonance: 0 };
      }
    }

    this.renderer.drawPattern(pattern, metrics);
    return pattern;
  }

  setUpdateCallback(callback) {
    this.onPatternUpdate = callback;
  }

  resize(width, height) {
    this.renderer.resize(width, height);
  }

  cleanup() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.cache.clear();
  }
}

// Export singleton instance factory
export const createPatternVisualization = (canvas) => {
  return new PatternVisualizationService(canvas);
};
