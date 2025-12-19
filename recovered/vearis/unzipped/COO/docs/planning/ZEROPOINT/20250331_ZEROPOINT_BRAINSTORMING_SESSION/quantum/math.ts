/**
 * Quantum Mathematics Implementation
 * Author: Synergy
 * Date: March 31, 2025
 * Time: 22:12 MST
 */

export class Complex {
  constructor(
    public readonly real: number,
    public readonly imaginary: number
  ) {}

  public add(other: Complex): Complex {
    return new Complex(
      this.real + other.real,
      this.imaginary + other.imaginary
    );
  }

  public scale(factor: number): Complex {
    return new Complex(
      this.real * factor,
      this.imaginary * factor
    );
  }

  public normalize(): Complex {
    const magnitude = Math.sqrt(this.real * this.real + this.imaginary * this.imaginary);
    return this.scale(1 / magnitude);
  }

  public conjugate(): Complex {
    return new Complex(this.real, -this.imaginary);
  }

  public multiply(other: Complex): Complex {
    return new Complex(
      this.real * other.real - this.imaginary * other.imaginary,
      this.real * other.imaginary + this.imaginary * other.real
    );
  }

  public magnitude(): number {
    return Math.sqrt(this.real * this.real + this.imaginary * this.imaginary);
  }

  public phase(): number {
    return Math.atan2(this.imaginary, this.real);
  }
}

export class Vector3D {
  constructor(
    public readonly x: number,
    public readonly y: number,
    public readonly z: number
  ) {}

  public add(other: Vector3D): Vector3D {
    return new Vector3D(
      this.x + other.x,
      this.y + other.y,
      this.z + other.z
    );
  }

  public scale(factor: number): Vector3D {
    return new Vector3D(
      this.x * factor,
      this.y * factor,
      this.z * factor
    );
  }

  public normalize(): Vector3D {
    const magnitude = Math.sqrt(this.x * this.x + this.y * this.y + this.z * this.z);
    return this.scale(1 / magnitude);
  }

  public dot(other: Vector3D): number {
    return this.x * other.x + this.y * other.y + this.z * other.z;
  }

  public cross(other: Vector3D): Vector3D {
    return new Vector3D(
      this.y * other.z - this.z * other.y,
      this.z * other.x - this.x * other.z,
      this.x * other.y - this.y * other.x
    );
  }

  public magnitude(): number {
    return Math.sqrt(this.x * this.x + this.y * this.y + this.z * this.z);
  }

  public distance(other: Vector3D): number {
    const dx = this.x - other.x;
    const dy = this.y - other.y;
    const dz = this.z - other.z;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }

  public angle(other: Vector3D): number {
    const dot = this.dot(other);
    const mags = this.magnitude() * other.magnitude();
    return Math.acos(dot / mags);
  }
}

export class ResonanceField {
  private fieldStrength: number;
  private resonancePatterns: Map<string, ResonancePattern>;
  private entanglementGraph: Map<string, Set<string>>;
  private coherenceMatrix: Map<string, Map<string, number>>;

  constructor() {
    this.fieldStrength = 1.0;
    this.resonancePatterns = new Map();
    this.entanglementGraph = new Map();
    this.coherenceMatrix = new Map();
  }

  public measureResonance<T>(state: any): number {
    const stateId = this.getStateId(state);
    const pattern = this.resonancePatterns.get(stateId);
    
    if (!pattern) {
      return this.fieldStrength;
    }

    const coherence = this.calculateCoherence(stateId);
    return pattern.amplitude * coherence * this.fieldStrength;
  }

  public addResonancePattern(id: string, pattern: ResonancePattern): void {
    this.resonancePatterns.set(id, pattern);
    this.updateFieldStrength();
  }

  public addEntanglement(id1: string, id2: string): void {
    this.ensureEntanglementSet(id1).add(id2);
    this.ensureEntanglementSet(id2).add(id1);
    this.updateCoherence(id1, id2);
  }

  private getStateId(state: any): string {
    return `${state.constructor.name}_${Date.now()}`;
  }

  private ensureEntanglementSet(id: string): Set<string> {
    let set = this.entanglementGraph.get(id);
    if (!set) {
      set = new Set();
      this.entanglementGraph.set(id, set);
    }
    return set;
  }

  private updateFieldStrength(): void {
    let totalAmplitude = 0;
    for (const pattern of this.resonancePatterns.values()) {
      totalAmplitude += pattern.amplitude;
    }
    this.fieldStrength = Math.sqrt(totalAmplitude / Math.max(1, this.resonancePatterns.size));
  }

  private calculateCoherence(stateId: string): number {
    const entangled = this.entanglementGraph.get(stateId);
    if (!entangled || entangled.size === 0) {
      return 1.0;
    }

    let totalCoherence = 0;
    for (const otherId of entangled) {
      const coherence = this.getCoherence(stateId, otherId);
      totalCoherence += coherence;
    }
    return totalCoherence / entangled.size;
  }

  private getCoherence(id1: string, id2: string): number {
    const matrix1 = this.coherenceMatrix.get(id1);
    if (!matrix1) {
      return 1.0;
    }
    return matrix1.get(id2) ?? 1.0;
  }
}

interface ResonancePattern {
  frequency: number;
  amplitude: number;
  phase: number;
  coherence: number;
}