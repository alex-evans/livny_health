/**
 * Unit conversion utilities for medication prescribing.
 * Supports conversion between metric and imperial units commonly used in healthcare.
 */

// Conversion constants
const ML_PER_TSP = 5;
const ML_PER_TBSP = 15;
const ML_PER_FL_OZ = 29.5735;
const LBS_PER_KG = 2.20462;
const KG_PER_LB = 0.453592;

export type VolumeUnit = 'mL' | 'tsp' | 'tbsp' | 'fl oz';
export type WeightUnit = 'kg' | 'lbs';
export type UnitSystem = 'metric' | 'imperial';

export interface ConversionResult {
  value: number;
  unit: string;
  formatted: string;
}

/**
 * Round to a sensible number of decimal places for display.
 * - Whole numbers stay whole
 * - Small decimals get 1-2 decimal places
 */
function smartRound(value: number): number {
  if (Number.isInteger(value)) return value;
  if (value >= 10) return Math.round(value * 10) / 10;
  return Math.round(value * 100) / 100;
}

/**
 * Format a number with its unit for display.
 */
function formatWithUnit(value: number, unit: string): string {
  const rounded = smartRound(value);
  return `${rounded} ${unit}`;
}

// ============ Volume Conversions ============

/**
 * Convert milliliters to teaspoons.
 * 1 tsp = 5 mL
 */
export function mlToTsp(mL: number): ConversionResult {
  const value = mL / ML_PER_TSP;
  return {
    value: smartRound(value),
    unit: 'tsp',
    formatted: formatWithUnit(value, 'tsp'),
  };
}

/**
 * Convert teaspoons to milliliters.
 * 1 tsp = 5 mL
 */
export function tspToMl(tsp: number): ConversionResult {
  const value = tsp * ML_PER_TSP;
  return {
    value: smartRound(value),
    unit: 'mL',
    formatted: formatWithUnit(value, 'mL'),
  };
}

/**
 * Convert milliliters to tablespoons.
 * 1 tbsp = 15 mL
 */
export function mlToTbsp(mL: number): ConversionResult {
  const value = mL / ML_PER_TBSP;
  return {
    value: smartRound(value),
    unit: 'tbsp',
    formatted: formatWithUnit(value, 'tbsp'),
  };
}

/**
 * Convert tablespoons to milliliters.
 * 1 tbsp = 15 mL
 */
export function tbspToMl(tbsp: number): ConversionResult {
  const value = tbsp * ML_PER_TBSP;
  return {
    value: smartRound(value),
    unit: 'mL',
    formatted: formatWithUnit(value, 'mL'),
  };
}

/**
 * Convert milliliters to fluid ounces.
 * 1 fl oz ≈ 29.5735 mL
 */
export function mlToFlOz(mL: number): ConversionResult {
  const value = mL / ML_PER_FL_OZ;
  return {
    value: smartRound(value),
    unit: 'fl oz',
    formatted: formatWithUnit(value, 'fl oz'),
  };
}

/**
 * Convert fluid ounces to milliliters.
 * 1 fl oz ≈ 29.5735 mL
 */
export function flOzToMl(flOz: number): ConversionResult {
  const value = flOz * ML_PER_FL_OZ;
  return {
    value: smartRound(value),
    unit: 'mL',
    formatted: formatWithUnit(value, 'mL'),
  };
}

// ============ Weight Conversions ============

/**
 * Convert kilograms to pounds.
 * 1 kg ≈ 2.20462 lbs
 */
export function kgToLbs(kg: number): ConversionResult {
  const value = kg * LBS_PER_KG;
  return {
    value: smartRound(value),
    unit: 'lbs',
    formatted: formatWithUnit(value, 'lbs'),
  };
}

/**
 * Convert pounds to kilograms.
 * 1 lb ≈ 0.453592 kg
 */
export function lbsToKg(lbs: number): ConversionResult {
  const value = lbs * KG_PER_LB;
  return {
    value: smartRound(value),
    unit: 'kg',
    formatted: formatWithUnit(value, 'kg'),
  };
}

// ============ Generic Conversion Utilities ============

/**
 * Convert a volume from one unit to another.
 */
export function convertVolume(value: number, from: VolumeUnit, to: VolumeUnit): ConversionResult {
  // First convert to mL as the base unit
  let mL: number;
  switch (from) {
    case 'mL':
      mL = value;
      break;
    case 'tsp':
      mL = value * ML_PER_TSP;
      break;
    case 'tbsp':
      mL = value * ML_PER_TBSP;
      break;
    case 'fl oz':
      mL = value * ML_PER_FL_OZ;
      break;
  }

  // Then convert from mL to target unit
  switch (to) {
    case 'mL':
      return { value: smartRound(mL), unit: 'mL', formatted: formatWithUnit(mL, 'mL') };
    case 'tsp':
      return mlToTsp(mL);
    case 'tbsp':
      return mlToTbsp(mL);
    case 'fl oz':
      return mlToFlOz(mL);
  }
}

/**
 * Convert a weight from one unit to another.
 */
export function convertWeight(value: number, from: WeightUnit, to: WeightUnit): ConversionResult {
  if (from === to) {
    return { value: smartRound(value), unit: to, formatted: formatWithUnit(value, to) };
  }

  if (from === 'kg' && to === 'lbs') {
    return kgToLbs(value);
  }

  return lbsToKg(value);
}

/**
 * Get the equivalent volume in the preferred unit system.
 * For metric: returns mL
 * For imperial: returns the most appropriate unit (tsp, tbsp, or fl oz)
 */
export function getVolumeInSystem(mL: number, system: UnitSystem): ConversionResult {
  if (system === 'metric') {
    return { value: smartRound(mL), unit: 'mL', formatted: formatWithUnit(mL, 'mL') };
  }

  // For imperial, choose the most readable unit based on size
  const tbsp = mL / ML_PER_TBSP;
  const flOz = mL / ML_PER_FL_OZ;

  // Use tsp for small amounts (< 3 tbsp)
  if (tbsp < 3) {
    return mlToTsp(mL);
  }

  // Use tbsp for medium amounts (< 4 fl oz)
  if (flOz < 4) {
    return mlToTbsp(mL);
  }

  // Use fl oz for larger amounts
  return mlToFlOz(mL);
}

/**
 * Get the equivalent weight in the preferred unit system.
 */
export function getWeightInSystem(kg: number, system: UnitSystem): ConversionResult {
  if (system === 'metric') {
    return { value: smartRound(kg), unit: 'kg', formatted: formatWithUnit(kg, 'kg') };
  }
  return kgToLbs(kg);
}

/**
 * Format a volume with both metric and imperial equivalents.
 * Example: "15 mL (1 tbsp)"
 */
export function formatVolumeWithEquivalent(mL: number): string {
  const imperial = getVolumeInSystem(mL, 'imperial');
  return `${smartRound(mL)} mL (${imperial.formatted})`;
}

/**
 * Format a weight with both metric and imperial equivalents.
 * Example: "70 kg (154.3 lbs)"
 */
export function formatWeightWithEquivalent(kg: number): string {
  const imperial = kgToLbs(kg);
  return `${smartRound(kg)} kg (${imperial.formatted})`;
}
