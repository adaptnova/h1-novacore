/**
 * Quantum Rule Derivation Tests
 * Author: Nexus
 * Date: March 31, 2025
 * Time: 20:43 MST
 */

import { Complex } from '../quantum/math';
import { Pattern } from '../evolution/patterns';
import { QuantumRuleDerivationSystem } from '../evolution/quantum_rules';

describe('Quantum Rule Derivation System', () => {
    let ruleSystem: QuantumRuleDerivationSystem;
    let testPattern: Pattern;

    beforeEach(() => {
        ruleSystem = new QuantumRuleDerivationSystem();
        testPattern = new Pattern(
            new Map([
                ['test_key', 'test_value'],
                ['quantum_state', true]
            ])
        );
    });

    describe('Rule Derivation', () => {
        test('should derive rules from pattern structure', () => {
            const rules = ruleSystem.deriveRules(testPattern);
            
            expect(rules.length).toBeGreaterThan(0);
            expect(rules[0].mutations.some(m => m.key === 'test_key')).toBe(true);
        });

        test('should respect resonance requirements', () => {
            testPattern.updateResonance({
                frequency: 1.0,
                amplitude: 0.5,
                phase: 0,
                coherence: 0.3
            });

            const rules = ruleSystem.deriveRules(testPattern);
            
            for (const rule of rules) {
                expect(rule.resonanceRequirement).toBeLessThanOrEqual(0.3);
            }
        });

        test('should generate quantum property rules', () => {
            testPattern.updateFitness(1.5);
            const rules = ruleSystem.deriveRules(testPattern);
            
            expect(rules.some(r => r.id.includes('quantum_magnitude'))).toBe(true);
            expect(rules.some(r => r.id.includes('quantum_phase'))).toBe(true);
        });
    });

    describe('Context Management', () => {
        test('should update context with pattern history', () => {
            ruleSystem.updateContext(testPattern);
            const rules1 = ruleSystem.deriveRules(testPattern);

            // Create evolved pattern
            const evolvedPattern = testPattern.evolve(new Map([
                ['evolved_key', 'evolved_value']
            ]));
            ruleSystem.updateContext(evolvedPattern);
            const rules2 = ruleSystem.deriveRules(evolvedPattern);

            expect(rules2.length).toBeGreaterThanOrEqual(rules1.length);
        });

        test('should track rule success rates', () => {
            const rules = ruleSystem.deriveRules(testPattern);
            const ruleId = rules[0].id;

            ruleSystem.recordRuleResult(ruleId, true);
            ruleSystem.recordRuleResult(ruleId, true);
            ruleSystem.recordRuleResult(ruleId, false);

            const newRules = ruleSystem.deriveRules(testPattern);
            expect(newRules.some(r => r.id === ruleId)).toBe(true);
        });

        test('should adjust coherence threshold', () => {
            testPattern.updateResonance({
                frequency: 1.0,
                amplitude: 1.0,
                phase: 0,
                coherence: 0.8
            });

            ruleSystem.updateContext(testPattern);
            const rules = ruleSystem.deriveRules(testPattern);

            expect(rules.some(r => r.resonanceRequirement > 0.5)).toBe(true);
        });
    });

    describe('Rule Optimization', () => {
        test('should prioritize high-impact rules', () => {
            const pattern1 = new Pattern(new Map([['key1', 'value1']]));
            const pattern2 = new Pattern(new Map([['key2', 'value2']]));

            pattern1.updateFitness(2.0);
            pattern2.updateFitness(1.0);

            ruleSystem.updateContext(pattern1);
            ruleSystem.updateContext(pattern2);

            const rules = ruleSystem.deriveRules(pattern1);
            expect(rules[0].fitnessImpact).toBeGreaterThan(1.0);
        });

        test('should combine compatible rules', () => {
            const pattern1 = new Pattern(new Map([
                ['base_key', 'base_value'],
                ['quantum_state', true]
            ]));

            const pattern2 = pattern1.evolve(new Map([
                ['evolved_key', 'evolved_value']
            ]));

            ruleSystem.updateContext(pattern1);
            ruleSystem.updateContext(pattern2);

            const rules = ruleSystem.deriveRules(pattern2);
            
            // Should have consolidated rules for related patterns
            const baseRules = rules.filter(r => r.id.includes('base_key'));
            expect(baseRules.length).toBe(1);
        });

        test('should maintain quantum coherence in derived rules', () => {
            testPattern.updateResonance({
                frequency: 1.0,
                amplitude: 1.0,
                phase: 0,
                coherence: 0.9
            });

            const rules = ruleSystem.deriveRules(testPattern);
            
            for (const rule of rules) {
                expect(rule.coherenceImpact).toBeGreaterThanOrEqual(1.0);
            }
        });
    });

    describe('Emergent Pattern Detection', () => {
        test('should detect recurring patterns', () => {
            const patterns = [
                new Pattern(new Map([['key1', 'valueA']])),
                new Pattern(new Map([['key1', 'valueA']])),
                new Pattern(new Map([['key1', 'valueB']]))
            ];

            patterns.forEach(p => ruleSystem.updateContext(p));
            const rules = ruleSystem.deriveRules(patterns[0]);

            expect(rules.some(r => r.id.includes('emergent'))).toBe(true);
        });

        test('should adapt rules based on pattern frequency', () => {
            const pattern = new Pattern(new Map([['recurring_key', 'recurring_value']]));
            
            // Update context multiple times with same pattern
            for (let i = 0; i < 5; i++) {
                ruleSystem.updateContext(pattern);
            }

            const rules = ruleSystem.deriveRules(pattern);
            const emergentRule = rules.find(r => r.id.includes('emergent'));
            
            expect(emergentRule?.probability).toBeGreaterThan(0.8);
        });
    });
});