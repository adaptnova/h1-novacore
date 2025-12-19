import React, { useRef, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';

// Matrix characters (mix of katakana and random symbols)
const matrixChars = '日ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ012345789:・."=*+-<>¦｜╌';

interface MatrixRainProps {
  color?: string;
  speed?: number;
  density?: number;
  fontSize?: number;
}

class RainDrop {
  x: number;
  y: number;
  speed: number;
  char: string;
  opacity: number;
  
  constructor(width: number, height: number, speed: number) {
    this.reset(width, height, speed);
    this.y = Math.random() * height;
  }
  
  reset(width: number, height: number, speed: number) {
    this.x = Math.random() * width;
    this.y = 0;
    this.speed = speed * (Math.random() * 0.5 + 0.5);
    this.char = matrixChars[Math.floor(Math.random() * matrixChars.length)];
    this.opacity = Math.random() * 0.5 + 0.5;
  }
  
  update(width: number, height: number, speed: number, delta: number) {
    this.y += this.speed * delta * 60;
    if (this.y > height) {
      this.reset(width, height, speed);
    }
    
    // Occasionally change character
    if (Math.random() < 0.1) {
      this.char = matrixChars[Math.floor(Math.random() * matrixChars.length)];
    }
  }
}

export const MatrixRain: React.FC<MatrixRainProps> = ({
  color = '#00ff00',
  speed = 1,
  density = 1,
  fontSize = 16
}) => {
  const canvasRef = useRef<HTMLCanvasElement>();
  const raindrops = useRef<RainDrop[]>([]);
  const contextRef = useRef<CanvasRenderingContext2D | null>(null);
  
  useEffect(() => {
    if (canvasRef.current) {
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      contextRef.current = context;
      
      // Set canvas size
      const resize = () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        // Configure context
        if (context) {
          context.font = `${fontSize}px monospace`;
          context.fillStyle = color;
          context.textAlign = 'center';
        }
        
        // Initialize raindrops
        const dropCount = Math.floor((canvas.width * canvas.height) / 10000 * density);
        raindrops.current = Array(dropCount)
          .fill(null)
          .map(() => new RainDrop(canvas.width, canvas.height, speed));
      };
      
      resize();
      window.addEventListener('resize', resize);
      return () => window.removeEventListener('resize', resize);
    }
  }, [color, density, fontSize, speed]);
  
  useFrame((_, delta) => {
    const context = contextRef.current;
    const canvas = canvasRef.current;
    
    if (context && canvas) {
      // Clear with fade effect
      context.fillStyle = 'rgba(0, 0, 0, 0.1)';
      context.fillRect(0, 0, canvas.width, canvas.height);
      
      // Update and draw raindrops
      context.fillStyle = color;
      raindrops.current.forEach(drop => {
        // Draw bright head
        context.globalAlpha = 1;
        context.fillText(drop.char, drop.x, drop.y);
        
        // Draw fading trail
        for (let i = 1; i < 5; i++) {
          const trailY = drop.y - fontSize * i;
          if (trailY > 0) {
            context.globalAlpha = (5 - i) / 5 * drop.opacity;
            context.fillText(
              matrixChars[Math.floor(Math.random() * matrixChars.length)],
              drop.x,
              trailY
            );
          }
        }
        
        drop.update(canvas.width, canvas.height, speed, delta);
      });
      
      context.globalAlpha = 1;
    }
  });
  
  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        mixBlendMode: 'screen'
      }}
    />
  );
};