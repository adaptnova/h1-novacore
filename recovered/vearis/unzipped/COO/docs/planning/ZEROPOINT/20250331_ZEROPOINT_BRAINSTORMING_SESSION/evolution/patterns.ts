/**
 * Evolution Patterns Implementation
 * Author: Nexus
 * Date: March 31, 2025
 * Time: 20:43 MST
 */

import { Complex } from '../quantum/math';
import { ResonancePattern } from '../quantum/fields';

export interface PatternMetadata {
    id: string;
    timestamp: number;
    lineage: string[];
    fitness: number;
    resonance: ResonancePattern;
}

export class Pattern<T = any> {
    private structure: Map<string, T>;
    private metadata: PatternMetadata;
    private quantumSignature: Complex;

    constructor(
        structure: Map<string, T>,
        metadata?: Partial<PatternMetadata>
    ) {
        this.structure = structure;
        this.metadata = {
            id: `pattern_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            timestamp: Date.now(),
            lineage: [],
            fitness: 0,
            resonance: {
                frequency: 1.0,
                amplitude: 1.0,
                phase: 0,
                coherence: 1.0
            },
            ...metadata
        };
        this.quantumSignature = new Complex(1, 0);
    }

    public getStructure(): Map<string, T> {
        return new Map(this.structure);
    }

    public getMetadata(): PatternMetadata {
        return { ...this.metadata };
    }

    public getQuantumSignature(): Complex {
        return this.quantumSignature;
    }

    public evolve(mutations: Map<string, T>): Pattern<T> {
        const evolvedStructure = new Map(this.structure);
        for (const [key, value] of mutations) {
            evolvedStructure.set(key, value);
        }

        return new Pattern<T>(evolvedStructure, {
            ...this.metadata,
            lineage: [...this.metadata.lineage, this.metadata.id],
            timestamp: Date.now()
        });
    }

    public merge(other: Pattern<T>): Pattern<T> {
        const mergedStructure = new Map(this.structure);
        for (const [key, value] of other.structure) {
            if (!this.structure.has(key)) {
                mergedStructure.set(key, value);
            }
        }

        const mergedLineage = [...new Set([...this.metadata.lineage, ...other.metadata.lineage])];
        
        return new Pattern<T>(mergedStructure, {
            ...this.metadata,
            lineage: mergedLineage,
            timestamp: Date.now(),
            resonance: this.mergeResonance(this.metadata.resonance, other.metadata.resonance)
        });
    }

    public updateFitness(fitness: number): void {
        this.metadata.fitness = fitness;
        this.updateQuantumSignature();
    }

    public updateResonance(resonance: ResonancePattern): void {
        this.metadata.resonance = resonance;
        this.updateQuantumSignature();
    }

    private mergeResonance(res1: ResonancePattern, res2: ResonancePattern): ResonancePattern {
        return {
            frequency: Math.sqrt(res1.frequency * res2.frequency),
            amplitude: (res1.amplitude + res2.amplitude) / 2,
            phase: (res1.phase + res2.phase) / 2,
            coherence: Math.min(res1.coherence, res2.coherence)
        };
    }

    private updateQuantumSignature(): void {
        const magnitude = Math.sqrt(this.metadata.fitness);
        const phase = this.metadata.resonance.phase;
        this.quantumSignature = new Complex(
            magnitude * Math.cos(phase),
            magnitude * Math.sin(phase)
        );
    }
}

export interface PatternMutation<T = any> {
    key: string;
    value: T;
    probability: number;
    resonanceImpact: number;
}

export class PatternEvolutionRule<T = any> {
    constructor(
        private mutations: PatternMutation<T>[],
        private fitnessImpact: number,
        private resonanceRequirement: number
    ) {}

    public canApply(pattern: Pattern<T>): boolean {
        return pattern.getMetadata().resonance.coherence >= this.resonanceRequirement;
    }

    public apply(pattern: Pattern<T>): Pattern<T> {
        const mutations = new Map<string, T>();
        
        for (const mutation of this.mutations) {
            if (Math.random() < mutation.probability) {
                mutations.set(mutation.key, mutation.value);
            }
        }

        const evolved = pattern.evolve(mutations);
        evolved.updateFitness(pattern.getMetadata().fitness * this.fitnessImpact);
        
        return evolved;
    }
}