import React, { useRef, useMemo } from 'react';
import { Vector3 } from 'three';
import { useFrame } from '@react-three/fiber';

interface LightningBoltProps {
  start: Vector3;
  end: Vector3;
  segments?: number;
  color?: string;
  thickness?: number;
  chaos?: number;
  lifetime?: number;
  branchChance?: number;
}

const generateLightningPoints = (
  start: Vector3,
  end: Vector3,
  segments: number,
  chaos: number,
  branchChance: number
): Vector3[][] => {
  const mainBolt: Vector3[] = [];
  const branches: Vector3[][] = [];
  
  // Generate main bolt
  const direction = end.clone().sub(start);
  const segmentLength = direction.length() / segments;
  const segmentDirection = direction.normalize();
  
  mainBolt.push(start.clone());
  
  for (let i = 1; i < segments; i++) {
    const lastPoint = mainBolt[i - 1];
    const idealPoint = start.clone().add(segmentDirection.multiplyScalar(segmentLength * i));
    
    // Add random displacement
    const displacement = new Vector3(
      (Math.random() - 0.5) * chaos,
      (Math.random() - 0.5) * chaos,
      (Math.random() - 0.5) * chaos
    );
    
    const newPoint = idealPoint.add(displacement);
    mainBolt.push(newPoint);
    
    // Possibly create a branch
    if (Math.random() < branchChance) {
      const branchLength = Math.random() * 0.5 + 0.5; // 50-100% of remaining length
      const branchEnd = newPoint.clone().add(
        new Vector3(
          (Math.random() - 0.5) * segmentLength * branchLength,
          (Math.random() - 0.5) * segmentLength * branchLength,
          (Math.random() - 0.5) * segmentLength * branchLength
        )
      );
      
      const branchPoints = generateLightningPoints(
        newPoint,
        branchEnd,
        Math.floor(segments * branchLength),
        chaos * 0.5,
        0 // No more sub-branches
      )[0];
      
      branches.push(branchPoints);
    }
  }
  
  mainBolt.push(end.clone());
  return [mainBolt, ...branches];
};

export const LightningBolt: React.FC<LightningBoltProps> = ({
  start,
  end,
  segments = 12,
  color = '#00ffff',
  thickness = 2,
  chaos = 2,
  lifetime = 1000,
  branchChance = 0.3
}) => {
  const boltRef = useRef<THREE.Group>();
  const timeRef = useRef(0);
  
  const [mainPoints, ...branchPoints] = useMemo(
    () => generateLightningPoints(start, end, segments, chaos, branchChance),
    [start, end, segments, chaos, branchChance]
  );
  
  useFrame((state, delta) => {
    if (boltRef.current) {
      timeRef.current += delta;
      
      // Fade out effect
      const life = (timeRef.current % lifetime) / lifetime;
      const opacity = 1 - life;
      
      boltRef.current.children.forEach((child: THREE.Line) => {
        const material = child.material as THREE.LineBasicMaterial;
        material.opacity = opacity * (Math.random() * 0.3 + 0.7); // Flicker effect
      });
      
      // Regenerate bolt occasionally
      if (timeRef.current >= lifetime) {
        const newBolt = generateLightningPoints(start, end, segments, chaos, branchChance);
        // Update geometry
        boltRef.current.children.forEach((child: THREE.Line, index) => {
          const points = index === 0 ? newBolt[0] : newBolt[index];
          const geometry = child.geometry as THREE.BufferGeometry;
          geometry.setFromPoints(points);
        });
      }
    }
  });
  
  return (
    <group ref={boltRef}>
      {/* Main bolt */}
      <line>
        <bufferGeometry attach="geometry" setFromPoints={mainPoints} />
        <lineBasicMaterial
          attach="material"
          color={color}
          linewidth={thickness}
          opacity={1}
          transparent
          blending={THREE.AdditiveBlending}
        />
      </line>
      
      {/* Branches */}
      {branchPoints.map((branch, index) => (
        <line key={index}>
          <bufferGeometry attach="geometry" setFromPoints={branch} />
          <lineBasicMaterial
            attach="material"
            color={color}
            linewidth={thickness * 0.7}
            opacity={0.7}
            transparent
            blending={THREE.AdditiveBlending}
          />
        </line>
      ))}
      
      {/* Glow effect */}
      <mesh position={start.clone().add(end).multiplyScalar(0.5)}>
        <sphereGeometry args={[0.5, 16, 16]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.2}
          blending={THREE.AdditiveBlending}
        />
      </mesh>
    </group>
  );
};