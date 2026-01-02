/**
 * Quantity calculator for medication prescriptions.
 * Calculates total quantity needed based on frequency, duration, and doses per administration.
 */

import { getVolumeInSystem, type ConversionResult } from './unitConversion';

export interface FrequencyOption {
  value: string;
  label: string;
  perDay: number;
}

export const FREQUENCY_OPTIONS: FrequencyOption[] = [
  { value: 'daily', label: 'Once daily', perDay: 1 },
  { value: 'BID', label: 'Twice daily (BID)', perDay: 2 },
  { value: 'TID', label: 'Three times daily (TID)', perDay: 3 },
  { value: 'QID', label: 'Four times daily (QID)', perDay: 4 },
  { value: 'q4-6h', label: 'Every 4-6 hours', perDay: 6 },
  { value: 'q6h', label: 'Every 6 hours', perDay: 4 },
  { value: 'q8h', label: 'Every 8 hours', perDay: 3 },
  { value: 'q12h', label: 'Every 12 hours', perDay: 2 },
  { value: 'weekly', label: 'Once weekly', perDay: 1 / 7 },
  { value: 'prn', label: 'As needed (PRN)', perDay: 6 }, // Max estimate for PRN
];

export type MedicationForm = 'tablet' | 'capsule' | 'liquid' | 'injection' | 'topical' | 'inhaler';

const FORM_UNITS: Record<MedicationForm, string> = {
  tablet: 'tablets',
  capsule: 'capsules',
  liquid: 'mL',
  inhaler: 'puffs',
  injection: 'doses',
  topical: 'applications',
};

/**
 * Parse the dose amount from a dosing string to extract units per administration.
 * Examples:
 *   "500mg TID" -> 1 (1 tablet/capsule per dose)
 *   "2 puffs every 4-6 hours" -> 2 (2 puffs per dose)
 *   "1-2 tablets every 4-6 hours" -> 2 (max, for quantity calculation)
 */
export function parseDosesPerAdmin(dosingString: string, form: MedicationForm): number {
  // Check for explicit number of units (e.g., "2 puffs", "1-2 tablets")
  const rangeMatch = dosingString.match(/(\d+)\s*-\s*(\d+)\s*(tablet|capsule|puff|dose)/i);
  if (rangeMatch) {
    return parseInt(rangeMatch[2], 10); // Use max of range
  }

  const singleMatch = dosingString.match(/(\d+)\s*(tablet|capsule|puff|dose)/i);
  if (singleMatch) {
    return parseInt(singleMatch[1], 10);
  }

  // For inhalers, check for puffs pattern
  if (form === 'inhaler') {
    const puffMatch = dosingString.match(/(\d+)\s*puff/i);
    if (puffMatch) {
      return parseInt(puffMatch[1], 10);
    }
    return 2; // Default for inhalers
  }

  // Default: 1 unit per administration for tablets/capsules
  return 1;
}

/**
 * Parse frequency from a common dosing string.
 * Examples:
 *   "500mg TID" -> "TID"
 *   "10mg daily" -> "daily"
 *   "every 4-6 hours PRN" -> "q4-6h"
 */
export function parseFrequencyFromDosing(dosingString: string): string | null {
  const dosing = dosingString.toUpperCase();

  if (dosing.includes('TID') || dosing.includes('THREE TIMES')) return 'TID';
  if (dosing.includes('BID') || dosing.includes('TWICE')) return 'BID';
  if (dosing.includes('QID') || dosing.includes('FOUR TIMES')) return 'QID';
  if (dosing.includes('EVERY 4-6') || dosing.includes('Q4-6')) return 'q4-6h';
  if (dosing.includes('EVERY 6') || dosing.includes('Q6H')) return 'q6h';
  if (dosing.includes('EVERY 8') || dosing.includes('Q8H')) return 'q8h';
  if (dosing.includes('EVERY 12') || dosing.includes('Q12H')) return 'q12h';
  if (dosing.includes('WEEKLY')) return 'weekly';
  if (dosing.includes('PRN') || dosing.includes('AS NEEDED')) return 'prn';
  if (dosing.includes('DAILY') || dosing.includes('ONCE')) return 'daily';

  return null;
}

/**
 * Get the frequency perDay value.
 */
export function getFrequencyPerDay(frequency: string): number {
  const option = FREQUENCY_OPTIONS.find((f) => f.value === frequency);
  return option?.perDay ?? 1;
}

/**
 * Get the unit name for a medication form.
 */
export function getUnitForForm(form: MedicationForm): string {
  return FORM_UNITS[form] || 'units';
}

export interface QuantityResult {
  quantity: number;
  unit: string;
  isEstimate: boolean; // True for PRN medications
  imperialEquivalent?: ConversionResult; // For liquid medications (mL -> tsp/tbsp/fl oz)
}

/**
 * Calculate total quantity needed for a prescription.
 *
 * @param frequency - Frequency code (e.g., "TID", "BID", "daily")
 * @param durationDays - Number of days for prescription
 * @param dosesPerAdmin - Number of units per administration (e.g., 2 for "2 puffs")
 * @param form - Medication form (tablet, capsule, liquid, etc.)
 * @returns Object with quantity, unit, and whether it's an estimate
 */
export function calculateQuantity(
  frequency: string,
  durationDays: number,
  dosesPerAdmin: number,
  form: MedicationForm
): QuantityResult {
  const perDay = getFrequencyPerDay(frequency);
  const unit = getUnitForForm(form);
  const isEstimate = frequency === 'prn' || frequency === 'q4-6h';

  // Calculate total: doses per admin × times per day × duration
  const rawQuantity = dosesPerAdmin * perDay * durationDays;

  // Round up to nearest whole number
  const quantity = Math.ceil(rawQuantity);

  // Calculate imperial equivalent for liquid medications (mL -> tsp/tbsp/fl oz)
  const imperialEquivalent = form === 'liquid' ? getVolumeInSystem(quantity, 'imperial') : undefined;

  return {
    quantity,
    unit,
    isEstimate,
    imperialEquivalent,
  };
}

