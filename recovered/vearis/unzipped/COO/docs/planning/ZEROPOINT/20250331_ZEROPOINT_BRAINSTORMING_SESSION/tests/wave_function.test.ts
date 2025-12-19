/**
 * Wave Function Tests
 * Author: Nexus
 * Date: March 31, 2025
 * Time: 20:41 MST
 */

import { Complex } from '../quantum/math';
import { WaveFunction } from '../quantum/wave_function';
import { ResonancePattern } from '../quantum/fields';

describe('Wave Function Implementation', () => {
    let waveFunction: WaveFunction;
    let defaultResonance: ResonancePattern;

    beforeEach(() => {
        waveFunction = new WaveFunction();
        defaultResonance = {
            frequency: 1.0,
            amplitude: 1.0,
            phase: 0,
            coherence: 1.0
        };
    });

    describe('State Management', () => {
        test('should add states with correct amplitudes', () => {
            waveFunction.addState('state1', new Complex(1, 0), defaultResonance);
            waveFunction.addState('state2', new Complex(1, 0), defaultResonance);

            // Test internal state through collapse probability
            let state1Count = 0;
            const trials = 1000;

            for (let i = 0; i < trials; i++) {
                const result = waveFunction.collapse<string>();
                if (result === 'state1') state1Count++;
            }

            // Should be roughly 50/50 split
            const ratio = state1Count / trials;
            expect(ratio).toBeGreaterThan(0.45);
            expect(ratio).toBeLessThan(0.55);
        });

        test('should normalize amplitudes automatically', () => {
            waveFunction.addState('state1', new Complex(2, 0), defaultResonance);
            waveFunction.addState('state2', new Complex(2, 0), defaultResonance);

            // Internal amplitudes should be normalized
            const result = waveFunction.collapse<string>();
            expect(result).toBeTruthy();
            expect(waveFunction.getCoherence()).toBe(1.0);
        });
    });

    describe('Resonance Integration', () => {
        test('should update state probabilities based on resonance', () => {
            waveFunction.addState('state1', new Complex(1, 0), defaultResonance);
            waveFunction.addState('state2', new Complex(1, 0), defaultResonance);

            // Increase resonance for state1
            waveFunction.updateResonance('state1', {
                ...defaultResonance,
                amplitude: 2.0
            });

            let state1Count = 0;
            const trials = 1000;

            for (let i = 0; i < trials; i++) {
                const result = waveFunction.collapse<string>();
                if (result === 'state1') state1Count++;
            }

            // Should favor state1 due to higher resonance
            const ratio = state1Count / trials;
            expect(ratio).toBeGreaterThan(0.6);
        });

        test('should maintain coherence during resonance updates', () => {
            waveFunction.addState('state1', new Complex(1, 0), defaultResonance);
            
            waveFunction.updateResonance('state1', {
                ...defaultResonance,
                coherence: 0.8
            });

            expect(waveFunction.getCoherence()).toBe(0.8);
        });
    });

    describe('Wave Function Collapse', () => {
        test('should collapse to single state', () => {
            waveFunction.addState('state1', new Complex(1, 0), defaultResonance);
            waveFunction.addState('state2', new Complex(1, 0), defaultResonance);

            const result = waveFunction.collapse<string>();
            expect(['state1', 'state2']).toContain(result);

            // Should maintain only the collapsed state
            let sameStateCount = 0;
            const trials = 10;

            for (let i = 0; i < trials; i++) {
                if (waveFunction.collapse<string>() === result) sameStateCount++;
            }

            expect(sameStateCount).toBe(trials);
        });

        test('should respect quantum probability', () => {
            waveFunction.addState('likely', new Complex(Math.sqrt(0.8), 0), defaultResonance);
            waveFunction.addState('unlikely', new Complex(Math.sqrt(0.2), 0), defaultResonance);

            let likelyCount = 0;
            const trials = 1000;

            for (let i = 0; i < trials; i++) {
                const result = waveFunction.collapse<string>();
                if (result === 'likely') likelyCount++;
            }

            const ratio = likelyCount / trials;
            expect(ratio).toBeGreaterThan(0.75);
            expect(ratio).toBeLessThan(0.85);
        });
    });

    describe('Wave Function Correlation', () => {
        test('should correlate wave functions', () => {
            const waveFunction2 = new WaveFunction();

            waveFunction.addState('state1', new Complex(1, 0), defaultResonance);
            waveFunction2.addState('state1', new Complex(1, 0), {
                ...defaultResonance,
                phase: Math.PI / 2
            });

            waveFunction.correlateWith(waveFunction2);

            // Phase should be averaged
            expect(waveFunction.collapse<string>()).toBe('state1');
            expect(waveFunction.getCoherence()).toBe(1.0);
        });

        test('should maintain correlation through collapse', () => {
            const waveFunction2 = new WaveFunction();

            waveFunction.addState('state1', new Complex(1, 0), defaultResonance);
            waveFunction.addState('state2', new Complex(1, 0), defaultResonance);
            waveFunction2.addState('state1', new Complex(1, 0), defaultResonance);

            waveFunction.correlateWith(waveFunction2);
            const result = waveFunction.collapse<string>();

            // Should collapse to correlated state
            expect(result).toBe('state1');
        });
    });
});