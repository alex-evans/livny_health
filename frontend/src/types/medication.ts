export interface Medication {
  id: string;
  name: string;
  genericName: string;
  strength: string;
  form: 'tablet' | 'capsule' | 'liquid' | 'injection' | 'topical' | 'inhaler';
  commonDosing: string[];
  isControlled: boolean;
  drugClass?: string;
}

export interface MedicationSearchResult {
  id: string;
  name: string;
  strength: string;
  form: string;
  commonDosing: string[];
  isControlled: boolean;
}

export interface AllergyOverride {
  allergen: string;
  severity: string;
  justification: string;
  acknowledgedAt: string;
}

export interface InteractionOverride {
  interactions: { interactingDrug: string; severity: string; description: string }[];
  justification: string;
  acknowledgedAt: string;
}

export interface SelectedMedication extends MedicationSearchResult {
  selectedDosing?: string;
  dosageAmount?: string;
  frequency?: string;
  durationDays?: number;
  calculatedQuantity?: number;
  quantityUnit?: string;
  isQuantityEstimate?: boolean;
  imperialEquivalent?: { value: number; unit: string; formatted: string };
  instructions?: string;
  allergyOverride?: AllergyOverride;
  interactionOverride?: InteractionOverride;
}

export interface ActiveMedication {
  id: string;
  name: string;
  brandName?: string | null;
  strength?: string | null;
  form?: string | null;
  dosage: string | null;
  frequency: string | null;
  route?: string | null;
  started: string;
  prescriber?: string | null;
  status?: string;
}
