/**
 * Quantum State Implementation Tests
 * Author: Nexus
 * Date: March 31, 2025
 * Time: 20:34 MST
 */

import { Complex } from '../quantum/math';
import { ResonanceField } from '../quantum/fields';
import { Pattern, PatternEvolutionRule } from '../evolution/patterns';
import { QuantumState } from '../20250331_2029_Nexus_Quantum_State_Implementation';

describe('Quantum State Implementation', () => {
    describe('Basic Quantum Operations', () => {
        let state: QuantumState<string>;

        beforeEach(() => {
            state = new QuantumState<string>('initial');
        });

        test('should initialize with single state in superposition', () => {
            const superposition = state['superposition'];
            expect(superposition.size).toBe(1);
            expect(superposition.get('initial')?.magnitude()).toBe(1);
        });

        test('should add states to superposition', () => {
            state.addState('second', new Complex(1/Math.sqrt(2), 0));
            const superposition = state['superposition'];
            expect(superposition.size).toBe(2);
        });

        test('should maintain normalized superposition', () => {
            state.addState('second', new Complex(1/Math.sqrt(2), 0));
            state.addState('third', new Complex(1/Math.sqrt(2), 0));
            
            let totalProbability = 0;
            for (const amplitude of state['superposition'].values()) {
                totalProbability += amplitude.magnitude() ** 2;
            }
            expect(Math.abs(totalProbability - 1)).toBeLessThan(1e-10);
        });
    });

    describe('Entanglement Operations', () => {
        let stateA: QuantumState<string>;
        let stateB: QuantumState<string>;

        beforeEach(() => {
            stateA = new QuantumState<string>('A');
            stateB = new QuantumState<string>('B');
        });

        test('should establish entanglement between states', () => {
            stateA.entangleWith(stateB);
            expect(stateA['entanglements'].has(stateB)).toBe(true);
            expect(stateB['entanglements'].has(stateA)).toBe(true);
        });

        test('should propagate collapse through entanglement', () => {
            stateA.entangleWith(stateB);
            stateA.addState('A2', new Complex(1/Math.sqrt(2), 0));
            stateB.addState('B2', new Complex(1/Math.sqrt(2), 0));

            const resultA = stateA.measure();
            const resultB = stateB.measure();
            
            // Entangled states should collapse to correlated results
            expect(resultA.includes('A')).toBe(resultB.includes('B'));
        });
    });

    describe('Field Resonance Integration', () => {
        let state: QuantumState<Pattern>;
        let field: ResonanceField;
        let pattern: Pattern;

        beforeEach(() => {
            pattern = new Pattern(new Map([['test', 'value']]));
            state = new QuantumState<Pattern>(pattern);
            field = new ResonanceField();
        });

        test('should update resonance based on field', () => {
            const initialResonance = state['fieldResonance'];
            field.addResonancePattern(pattern.getMetadata().id, {
                frequency: 2.0,
                amplitude: 1.5,
                phase: 0,
                coherence: 0.9
            });

            state.updateResonance(field);
            expect(state['fieldResonance']).not.toBe(initialResonance);
        });

        test('should maintain coherence during evolution', () => {
            const evolvedPattern = pattern.evolve(new Map([['evolved', true]]));
            const newState = new QuantumState<Pattern>(evolvedPattern);
            
            state.entangleWith(newState);
            field.addEntanglement(
                pattern.getMetadata().id,
                evolvedPattern.getMetadata().id
            );

            state.updateResonance(field);
            newState.updateResonance(field);

            expect(state['fieldResonance']).toBeGreaterThan(0);
            expect(newState['fieldResonance']).toBeGreaterThan(0);
        });
    });

    describe('Pattern Evolution Integration', () => {
        let state: QuantumState<Pattern>;
        let pattern: Pattern;
        let evolutionRule: PatternEvolutionRule;

        beforeEach(() => {
            pattern = new Pattern(new Map([['base', 'value']]));
            state = new QuantumState<Pattern>(pattern);
            evolutionRule = new PatternEvolutionRule(
                [{
                    key: 'evolved',
                    value: true,
                    probability: 1.0,
                    resonanceImpact: 1.1
                }],
                1.2,
                0.5
            );
        });

        test('should evolve pattern maintaining quantum properties', () => {
            const initialSignature = pattern.getQuantumSignature();
            const evolved = evolutionRule.apply(pattern);
            
            expect(evolved.getStructure().get('evolved')).toBe(true);
            expect(evolved.getQuantumSignature().magnitude())
                .toBeGreaterThan(initialSignature.magnitude());
        });

        test('should maintain coherence during pattern evolution', () => {
            const evolved = evolutionRule.apply(pattern);
            const newState = new QuantumState<Pattern>(evolved);
            
            state.entangleWith(newState);
            expect(state['entanglements'].has(newState)).toBe(true);
            
            const measurement = state.measure();
            expect(measurement).toBeTruthy();
        });
    });
});