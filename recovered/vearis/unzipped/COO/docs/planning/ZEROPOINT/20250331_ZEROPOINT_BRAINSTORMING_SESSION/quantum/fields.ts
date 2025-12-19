/**
 * Quantum Field Implementation
 * Author: Nexus
 * Date: March 31, 2025
 * Time: 20:32 MST
 */

import { Complex } from './math';
import { Pattern } from '../evolution/patterns';

export interface ResonancePattern {
    frequency: number;
    amplitude: number;
    phase: number;
    coherence: number;
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

    public getFieldStrength(): number {
        return this.fieldStrength;
    }

    public getResonancePattern(id: string): ResonancePattern | undefined {
        return this.resonancePatterns.get(id);
    }

    private getStateId(state: any): string {
        // Generate unique ID for quantum state
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

    private updateCoherence(id1: string, id2: string): void {
        const pattern1 = this.resonancePatterns.get(id1);
        const pattern2 = this.resonancePatterns.get(id2);

        if (!pattern1 || !pattern2) {
            return;
        }

        const phaseDiff = Math.abs(pattern1.phase - pattern2.phase);
        const freqRatio = Math.min(pattern1.frequency, pattern2.frequency) / 
                         Math.max(pattern1.frequency, pattern2.frequency);
        
        const coherence = Math.cos(phaseDiff) * freqRatio * 
                         Math.min(pattern1.coherence, pattern2.coherence);

        this.setCoherence(id1, id2, coherence);
    }

    private getCoherence(id1: string, id2: string): number {
        const matrix1 = this.coherenceMatrix.get(id1);
        if (!matrix1) {
            return 1.0;
        }
        return matrix1.get(id2) ?? 1.0;
    }

    private setCoherence(id1: string, id2: string, value: number): void {
        let matrix1 = this.coherenceMatrix.get(id1);
        if (!matrix1) {
            matrix1 = new Map();
            this.coherenceMatrix.set(id1, matrix1);
        }
        matrix1.set(id2, value);

        let matrix2 = this.coherenceMatrix.get(id2);
        if (!matrix2) {
            matrix2 = new Map();
            this.coherenceMatrix.set(id2, matrix2);
        }
        matrix2.set(id1, value);
    }
}