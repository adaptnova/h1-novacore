import React, { useEffect, useRef, useState } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import { Canvas, useFrame } from '@react-three/fiber';
import { EffectComposer, Bloom, ChromaticAberration } from '@react-three/postprocessing';
import { Vector3 } from 'three';
import { useSpring, animated } from 'react-spring';
import { useDrag } from 'react-use-gesture';

// Types for our nodes and links
interface Node {
  id: string;
  name: string;
  val: number;
  color: string;
  status: 'active' | 'warning' | 'error' | 'normal';
  type: 'sphere' | 'pyramid' | 'diamond';
  particleCount: number;
}

interface Link {
  source: string;
  target: string;
  strength: number;
  color: string;
  type: 'energy' | 'rainbow' | 'plasma';
}

// Custom node geometries
const NODE_TYPES = {
  sphere: new THREE.SphereGeometry(1, 32, 32),
  pyramid: new THREE.ConeGeometry(1, 2, 4),
  diamond: new THREE.OctahedronGeometry(1),
};

// Particle system for node effects
const createParticleSystem = (count: number, color: string) => {
  const particles = new THREE.BufferGeometry();
  const positions = new Float32Array(count * 3);
  const velocities = new Float32Array(count * 3);
  
  for (let i = 0; i < count; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 2;
    positions[i * 3 + 1] = (Math.random() - 0.5) * 2;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 2;
    
    velocities[i * 3] = (Math.random() - 0.5) * 0.1;
    velocities[i * 3 + 1] = (Math.random() - 0.5) * 0.1;
    velocities[i * 3 + 2] = (Math.random() - 0.5) * 0.1;
  }
  
  particles.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  particles.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));
  
  const material = new THREE.PointsMaterial({
    color,
    size: 0.1,
    transparent: true,
    blending: THREE.AdditiveBlending,
  });
  
  return new THREE.Points(particles, material);
};

// Custom link material for energy beams
const createEnergyBeam = (color: string) => {
  return new THREE.LineBasicMaterial({
    color,
    transparent: true,
    opacity: 0.8,
    linewidth: 2,
  });
};

export const NovaForceGraph: React.FC = () => {
  const fgRef = useRef();
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  
  // Physics settings
  const SPRING_LENGTH = 50;
  const SPRING_STRENGTH = 0.1;
  const CHARGE_STRENGTH = -30;
  
  useEffect(() => {
    // Generate some awesome test data
    const nodes: Node[] = Array.from({ length: 1000 }).map((_, i) => ({
      id: String(i),
      name: `Node ${i}`,
      val: Math.random() * 20 + 10,
      color: `hsl(${Math.random() * 360}, 70%, 50%)`,
      status: ['active', 'warning', 'error', 'normal'][Math.floor(Math.random() * 4)] as Node['status'],
      type: ['sphere', 'pyramid', 'diamond'][Math.floor(Math.random() * 3)] as Node['type'],
      particleCount: Math.floor(Math.random() * 100) + 50,
    }));
    
    const links: Link[] = [];
    nodes.forEach((node) => {
      const numLinks = Math.floor(Math.random() * 3) + 1;
      for (let i = 0; i < numLinks; i++) {
        const target = Math.floor(Math.random() * nodes.length);
        if (target !== parseInt(node.id)) {
          links.push({
            source: node.id,
            target: String(target),
            strength: Math.random(),
            color: `hsl(${Math.random() * 360}, 70%, 50%)`,
            type: ['energy', 'rainbow', 'plasma'][Math.floor(Math.random() * 3)] as Link['type'],
          });
        }
      }
    });
    
    setGraphData({ nodes, links });
  }, []);
  
  // Custom node rendering
  const nodeThreeObject = (node: Node) => {
    const geometry = NODE_TYPES[node.type];
    const material = new THREE.MeshPhongMaterial({
      color: node.color,
      transparent: true,
      opacity: 0.9,
      emissive: node.color,
      emissiveIntensity: node.status === 'active' ? 0.5 : 0.2,
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.scale.multiplyScalar(node.val / 10);
    
    // Add particle system
    const particles = createParticleSystem(node.particleCount, node.color);
    mesh.add(particles);
    
    return mesh;
  };
  
  // Custom link rendering
  const linkThreeObject = (link: Link) => {
    const material = createEnergyBeam(link.color);
    return new THREE.Line(undefined, material);
  };
  
  // Animation loop
  useFrame((state) => {
    const time = state.clock.getElapsedTime();
    
    // Update particles
    fgRef.current?.graphData().nodes.forEach((node: Node) => {
      const obj = fgRef.current?.nodeThreeObject(node);
      if (obj) {
        const particles = obj.children[0];
        const positions = particles.geometry.attributes.position.array;
        const velocities = particles.geometry.attributes.velocity.array;
        
        for (let i = 0; i < positions.length; i += 3) {
          positions[i] += velocities[i];
          positions[i + 1] += velocities[i + 1];
          positions[i + 2] += velocities[i + 2];
          
          // Reset particles that go too far
          if (Math.abs(positions[i]) > 2) positions[i] *= -0.9;
          if (Math.abs(positions[i + 1]) > 2) positions[i + 1] *= -0.9;
          if (Math.abs(positions[i + 2]) > 2) positions[i + 2] *= -0.9;
        }
        
        particles.geometry.attributes.position.needsUpdate = true;
      }
    });
    
    // Animate links
    fgRef.current?.graphData().links.forEach((link: Link) => {
      const obj = fgRef.current?.linkThreeObject(link);
      if (obj) {
        obj.material.opacity = 0.5 + Math.sin(time * 2) * 0.2;
        if (link.type === 'rainbow') {
          obj.material.color.setHSL((time * 0.1) % 1, 0.7, 0.5);
        }
      }
    });
  });
  
  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <Canvas camera={{ position: [0, 0, 200], fov: 60 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[100, 100, 100]} intensity={2} />
        <pointLight position={[-100, -100, -100]} intensity={5} />
        
        <EffectComposer>
          <Bloom 
            intensity={1.5}
            luminanceThreshold={0.6}
            luminanceSmoothing={0.9}
            height={300}
          />
          <ChromaticAberration offset={[0.002, 0.002]} />
        </EffectComposer>
        
        <ForceGraph3D
          ref={fgRef}
          graphData={graphData}
          nodeThreeObject={nodeThreeObject}
          linkThreeObject={linkThreeObject}
          linkWidth={2}
          linkOpacity={0.5}
          nodeRelSize={6}
          nodeResolution={32}
          warmupTicks={100}
          cooldownTicks={50}
          cooldownTime={1000}
          d3AlphaDecay={0.02}
          d3VelocityDecay={0.3}
          d3Force={
            'charge',
            () => {
              return d3.forceManyBody()
                .strength(CHARGE_STRENGTH);
            }
          }
          showNavInfo={false}
          enableNodeDrag={true}
          enableNavigationControls={true}
          nodeLabel="name"
          linkLabel={(link) => `${link.source} → ${link.target}`}
          onNodeClick={(node) => {
            // Add dramatic effects when clicking nodes
            const obj = fgRef.current?.nodeThreeObject(node);
            if (obj) {
              gsap.to(obj.scale, {
                x: obj.scale.x * 1.5,
                y: obj.scale.y * 1.5,
                z: obj.scale.z * 1.5,
                duration: 0.3,
                yoyo: true,
                repeat: 1,
                ease: 'elastic.out(1, 0.3)',
              });
              
              // Emit burst of particles
              const particles = createParticleSystem(100, node.color);
              obj.add(particles);
              setTimeout(() => obj.remove(particles), 1000);
            }
          }}
          onNodeDragEnd={(node) => {
            // Add dramatic bounce effect
            const obj = fgRef.current?.nodeThreeObject(node);
            if (obj) {
              gsap.from(obj.scale, {
                x: obj.scale.x * 0.5,
                y: obj.scale.y * 0.5,
                z: obj.scale.z * 0.5,
                duration: 1,
                ease: 'elastic.out(1, 0.3)',
              });
            }
          }}
          onLinkClick={(link) => {
            // Add energy pulse along link
            const obj = fgRef.current?.linkThreeObject(link);
            if (obj) {
              gsap.to(obj.material, {
                opacity: 1,
                duration: 0.2,
                yoyo: true,
                repeat: 1,
              });
            }
          }}
        />
      </Canvas>
      
      {/* Overlay Controls */}
      <div style={{
        position: 'absolute',
        top: 10,
        right: 10,
        background: 'rgba(0,0,0,0.7)',
        padding: 10,
        borderRadius: 5,
        color: 'white',
      }}>
        <button onClick={() => {
          // Add CHAOS MODE!
          fgRef.current?.graphData().nodes.forEach((node: Node) => {
            const force = new Vector3(
              (Math.random() - 0.5) * 100,
              (Math.random() - 0.5) * 100,
              (Math.random() - 0.5) * 100
            );
            node.__threeObj.position.add(force);
          });
        }}>
          🎲 CHAOS MODE!
        </button>
      </div>
    </div>
  );
};

export default NovaForceGraph;