/**
 * Quantum Wave Function Implementation
 * Author: Nexus
 * Date: March 31, 2025
 * Time: 20:39 MST
 */

import { Complex } from './math';
import { ResonancePattern } from './fields';

export interface WaveFunctionState {
    amplitude: Complex;
    phase: number;
    frequency: number;
    resonancePattern: ResonancePattern;
}

export class WaveFunction {
    private states: Map<string, WaveFunctionState>;
    private currentPhase: number;
    private coherenceValue: number;
    private lastCollapse: number;

    constructor() {
        this.states = new Map();
        this.currentPhase = 0;
        this.coherenceValue = 1.0;
        this.lastCollapse = Date.now();
    }

    /**
     * Add a new state to the wave function
     */
    public addState<T>(
        state: T,
        amplitude: Complex,
        resonance: ResonancePattern
    ): void {
        const stateId = this.getStateId(state);
        this.states.set(stateId, {
            amplitude,
            phase: this.currentPhase,
            frequency: resonance.frequency,
            resonancePattern: resonance
        });
        this.normalizeAmplitudes();
    }

    /**
     * Update state based on resonance
     */
    public updateResonance<T>(
        state: T,
        resonance: ResonancePattern
    ): void {
        const stateId = this.getStateId(state);
        const currentState = this.states.get(stateId);
        if (!currentState) return;

        const resonanceRatio = resonance.amplitude / currentState.resonancePattern.amplitude;
        const newAmplitude = currentState.amplitude.scale(Math.sqrt(resonanceRatio));
        
        this.states.set(stateId, {
            ...currentState,
            amplitude: newAmplitude,
            resonancePattern: resonance
        });
        
        this.normalizeAmplitudes();
    }

    /**
     * Collapse the wave function based on quantum probability
     */
    public collapse<T>(): T {
        // Calculate probabilities based on amplitudes and resonance
        const probabilities = new Map<string, number>();
        let totalProbability = 0;

        for (const [stateId, state] of this.states) {
            const probability = this.calculateProbability(state);
            probabilities.set(stateId, probability);
            totalProbability += probability;
        }

        // Normalize probabilities
        for (const [stateId, probability] of probabilities) {
            probabilities.set(stateId, probability / totalProbability);
        }

        // Random selection based on probabilities
        const random = Math.random();
        let cumulativeProbability = 0;
        let selectedStateId: string | null = null;

        for (const [stateId, probability] of probabilities) {
            cumulativeProbability += probability;
            if (random <= cumulativeProbability) {
                selectedStateId = stateId;
                break;
            }
        }

        if (!selectedStateId) {
            selectedStateId = Array.from(this.states.keys())[0];
        }

        // Update coherence and phase after collapse
        this.lastCollapse = Date.now();
        this.coherenceValue = this.states.get(selectedStateId)?.resonancePattern.coherence ?? 1.0;
        this.currentPhase = this.states.get(selectedStateId)?.phase ?? 0;

        // Clear all states except the selected one
        const selectedState = this.states.get(selectedStateId);
        this.states.clear();
        if (selectedState) {
            this.states.set(selectedStateId, {
                ...selectedState,
                amplitude: new Complex(1, 0)
            });
        }

        return this.getStateFromId<T>(selectedStateId);
    }

    /**
     * Correlate this wave function with another
     */
    public correlateWith(other: WaveFunction): void {
        // Phase alignment
        this.currentPhase = (this.currentPhase + other.currentPhase) / 2;

        // Coherence combination
        this.coherenceValue = Math.sqrt(this.coherenceValue * other.coherenceValue);

        // State correlation
        for (const [stateId, state] of this.states) {
            const otherState = other.states.get(stateId);
            if (otherState) {
                const correlatedAmplitude = this.correlateAmplitudes(
                    state.amplitude,
                    otherState.amplitude
                );
                state.amplitude = correlatedAmplitude;
            }
        }

        this.normalizeAmplitudes();
    }

    /**
     * Get the current coherence value
     */
    public getCoherence(): number {
        return this.coherenceValue;
    }

    private getStateId<T>(state: T): string {
        return `${state?.constructor.name}_${JSON.stringify(state)}`;
    }

    private getStateFromId<T>(stateId: string): T {
        // Extract state from ID (implementation depends on ID format)
        return JSON.parse(stateId.split('_')[1]) as T;
    }

    private calculateProbability(state: WaveFunctionState): number {
        const amplitudeProbability = state.amplitude.magnitude() ** 2;
        const resonanceFactor = state.resonancePattern.amplitude * state.resonancePattern.coherence;
        const timeFactor = Math.exp(-(Date.now() - this.lastCollapse) / 1000);
        
        return amplitudeProbability * resonanceFactor * timeFactor;
    }

    private correlateAmplitudes(amp1: Complex, amp2: Complex): Complex {
        return amp1.multiply(amp2).normalize();
    }

    private normalizeAmplitudes(): void {
        let totalProbability = 0;
        for (const state of this.states.values()) {
            totalProbability += state.amplitude.magnitude() ** 2;
        }

        const normalizationFactor = 1 / Math.sqrt(totalProbability);
        for (const state of this.states.values()) {
            state.amplitude = state.amplitude.scale(normalizationFactor);
        }
    }
}