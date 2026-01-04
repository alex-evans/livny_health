import type { ActiveMedication } from './medication';

export type AllergySeverity = 'mild' | 'moderate' | 'severe';

export interface Allergy {
  id: string;
  allergen: string;
  reaction: string;
  severity: AllergySeverity;
  documented: string;
}

export interface Patient {
  id: string;
  name: string;
  dateOfBirth: string;
  mrn: string;
  allergies?: Allergy[];
  activeMedications?: ActiveMedication[];
}

export interface AllergyAlert {
  blocked: boolean;
  severity: AllergySeverity;
  title: string;
  message: string;
  allergen: string;
  reaction: string;
  medicationName: string;
  isCrossReactive: boolean;
}

export interface AllergyCheckResult {
  hasConflict: boolean;
  alert: AllergyAlert | null;
}

export type InteractionSeverity = 'minor' | 'moderate' | 'major';

export interface DrugInteraction {
  interactingDrug: string;
  severity: InteractionSeverity;
  description: string;
}

export interface DrugInteractionCheckResult {
  hasInteractions: boolean;
  interactions: DrugInteraction[];
}
