import { shaderMaterial } from '@react-three/drei';
import { extend } from '@react-three/fiber';

// Force Field Shader
const ForceFieldMaterial = shaderMaterial(
  {
    time: 0,
    color: new THREE.Color(0.0, 0.5, 1.0),
    intensity: 1.0,
    pulseSpeed: 1.0,
    hexScale: 10.0,
  },
  // Vertex Shader with distortion
  `
    varying vec3 vPosition;
    varying vec3 vNormal;
    varying vec2 vUv;
    uniform float time;
    
    void main() {
      vPosition = position;
      
      // Add wave distortion
      vec3 distortedPosition = position;
      distortedPosition.x += sin(position.y * 10.0 + time) * 0.1;
      distortedPosition.y += cos(position.x * 10.0 + time) * 0.1;
      distortedPosition.z += sin(position.x * 10.0 + cos(position.y * 10.0 + time)) * 0.1;
      
      vNormal = normal;
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(distortedPosition, 1.0);
    }
  `,
  // Fragment Shader with extra effects
  `
    uniform float time;
    uniform vec3 color;
    uniform float intensity;
    uniform float pulseSpeed;
    uniform float hexScale;
    
    varying vec3 vPosition;
    varying vec3 vNormal;
    varying vec2 vUv;
    
    // Hexagonal pattern
    vec2 hexCoords(vec2 uv) {
      vec2 r = vec2(1.0, sqrt(3.0));
      vec2 h = r * 0.5;
      vec2 a = mod(uv, r) - h;
      vec2 b = mod(uv + h, r) - h;
      return dot(a, a) < dot(b, b) ? a : b;
    }
    
    // Electric noise
    float noise(vec2 p) {
      return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
    }
    
    void main() {
      // Hexagonal force field pattern
      vec2 hex = hexCoords(vUv * hexScale);
      float hexPattern = smoothstep(0.1, 0.2, length(hex));
      
      // Multiple pulse layers
      float pulse1 = sin(time * pulseSpeed) * 0.5 + 0.5;
      float pulse2 = sin(time * pulseSpeed * 1.3 + 1.0) * 0.5 + 0.5;
      float pulse3 = sin(time * pulseSpeed * 0.7 + 2.0) * 0.5 + 0.5;
      float combinedPulse = (pulse1 + pulse2 + pulse3) / 3.0;
      
      // Edge glow
      float edgeGlow = pow(1.0 - abs(dot(vNormal, vec3(0.0, 0.0, 1.0))), 2.0);
      
      // Electric noise effect
      float electric = noise(vUv * 10.0 + time) * 0.1;
      
      // Energy ripples
      float ripples = sin((vUv.x * 20.0 + time) * 3.0) * sin((vUv.y * 20.0 + time) * 3.0) * 0.1;
      
      // Combine all effects
      float alpha = (
        hexPattern * 0.5 + 
        edgeGlow + 
        combinedPulse * 0.2 +
        electric +
        ripples
      ) * intensity;
      
      // Color variations
      vec3 finalColor = mix(
        color,
        vec3(1.0),
        edgeGlow * 0.5 + electric * 2.0 + ripples
      );
      
      // Add subtle rainbow effect
      finalColor += vec3(
        sin(time + vUv.x) * 0.1,
        cos(time + vUv.y) * 0.1,
        sin(time * 0.5) * 0.1
      );
      
      gl_FragColor = vec4(finalColor, alpha);
    }
  `
);

extend({ ForceFieldMaterial });

export const ForceField: React.FC<{ 
  radius: number; 
  color?: THREE.Color;
  intensity?: number;
  pulseSpeed?: number;
}> = ({ 
  radius = 50,
  color = new THREE.Color(0.0, 0.5, 1.0),
  intensity = 1.0,
  pulseSpeed = 1.0
}) => {
  const materialRef = useRef();
  const meshRef = useRef();
  
  useFrame((state) => {
    if (materialRef.current) {
      materialRef.current.time = state.clock.getElapsedTime();
      materialRef.current.intensity = intensity * (0.5 + Math.sin(state.clock.getElapsedTime()) * 0.2);
    }
    
    // Add subtle mesh deformation
    if (meshRef.current) {
      meshRef.current.rotation.x = Math.sin(state.clock.getElapsedTime() * 0.2) * 0.1;
      meshRef.current.rotation.y = Math.cos(state.clock.getElapsedTime() * 0.2) * 0.1;
    }
  });
  
  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[radius, 64, 64]} />
      <forceFieldMaterial 
        ref={materialRef} 
        transparent
        depthWrite={false}
        color={color}
        intensity={intensity}
        pulseSpeed={pulseSpeed}
        hexScale={10.0}
        blending={THREE.AdditiveBlending}
      />
    </mesh>
  );
};