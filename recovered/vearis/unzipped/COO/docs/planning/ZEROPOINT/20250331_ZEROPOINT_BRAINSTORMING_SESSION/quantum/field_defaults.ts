/**
 * Quantum Field Defaults
 * Author: Synergy
 * Date: March 31, 2025
 * Time: 22:21 MST
 */

import { Vector3D } from './math';
import { BaseField } from './types';

export const DEFAULT_FIELD_VALUES: Required<BaseField> = {
  potential: 1.0,
  gradient: new Vector3D(0, 0, 1),
  resonanceFrequency: 432.0,
  phaseAlignment: 0,
  intensityMap: new Map()
};

export function getFieldValue<K extends keyof BaseField>(
  field: BaseField,
  key: K
): NonNullable<BaseField[K]> {
  return (field[key] ?? DEFAULT_FIELD_VALUES[key]) as NonNullable<BaseField[K]>;
}

export function createBaseField(partial: Partial<BaseField> = {}): Required<BaseField> {
  return {
    ...DEFAULT_FIELD_VALUES,
    ...partial,
    intensityMap: partial.intensityMap ?? new Map()
  };
}

export function mergeFields(fields: BaseField[]): Required<BaseField> {
  const potential = fields.reduce((sum, f) => sum + (f.potential ?? DEFAULT_FIELD_VALUES.potential), 0) / fields.length;
  
  const gradients = fields.map(f => f.gradient ?? DEFAULT_FIELD_VALUES.gradient);
  const gradient = new Vector3D(
    gradients.reduce((sum, g) => sum + g.x, 0) / gradients.length,
    gradients.reduce((sum, g) => sum + g.y, 0) / gradients.length,
    gradients.reduce((sum, g) => sum + g.z, 0) / gradients.length
  );

  const resonanceFrequency = fields.reduce((sum, f) => sum + (f.resonanceFrequency ?? DEFAULT_FIELD_VALUES.resonanceFrequency), 0) / fields.length;
  
  const phaseAlignment = fields.reduce((sum, f) => sum + (f.phaseAlignment ?? DEFAULT_FIELD_VALUES.phaseAlignment), 0) / fields.length;

  const intensityMap = new Map<Vector3D, number>();
  for (const field of fields) {
    const map = field.intensityMap ?? new Map();
    for (const [key, value] of map) {
      intensityMap.set(key, (intensityMap.get(key) ?? 0) + value);
    }
  }
  for (const [key, value] of intensityMap) {
    intensityMap.set(key, value / fields.length);
  }

  return {
    potential,
    gradient,
    resonanceFrequency,
    phaseAlignment,
    intensityMap
  };
}

export function harmonicMean(values: (number | undefined)[], defaultValue: number): number {
  const definedValues = values.map(v => v ?? defaultValue);
  return definedValues.length / definedValues.reduce((sum, v) => sum + 1/v, 0);
}

export function averagePhase(phases: (number | undefined)[], defaultValue: number): number {
  const definedPhases = phases.map(p => p ?? defaultValue);
  const x = definedPhases.reduce((sum, p) => sum + Math.cos(p), 0) / definedPhases.length;
  const y = definedPhases.reduce((sum, p) => sum + Math.sin(p), 0) / definedPhases.length;
  return Math.atan2(y, x);
}

export function mergeIntensityMaps(
  maps: (Map<Vector3D, number> | undefined)[]
): Map<Vector3D, number> {
  const merged = new Map<Vector3D, number>();
  const definedMaps = maps.filter((m): m is Map<Vector3D, number> => m !== undefined);
  
  for (const map of definedMaps) {
    for (const [key, value] of map) {
      merged.set(key, (merged.get(key) ?? 0) + value);
    }
  }

  if (definedMaps.length > 0) {
    for (const [key, value] of merged) {
      merged.set(key, value / definedMaps.length);
    }
  }

  return merged;
}

export function averageVectors(vectors: (Vector3D | undefined)[]): Vector3D {
  const definedVectors = vectors.filter((v): v is Vector3D => v !== undefined);
  if (definedVectors.length === 0) {
    return DEFAULT_FIELD_VALUES.gradient;
  }

  return new Vector3D(
    definedVectors.reduce((sum, v) => sum + v.x, 0) / definedVectors.length,
    definedVectors.reduce((sum, v) => sum + v.y, 0) / definedVectors.length,
    definedVectors.reduce((sum, v) => sum + v.z, 0) / definedVectors.length
  );
}