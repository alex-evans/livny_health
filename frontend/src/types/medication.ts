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

export interface SelectedMedication extends MedicationSearchResult {
  selectedDosing?: string;
  dosageAmount?: string;
  frequency?: string;
  durationDays?: number;
  calculatedQuantity?: number;
  quantityUnit?: string;
  isQuantityEstimate?: boolean;
}

export interface ActiveMedication {
  id: string;
  name: string;
  dosage: string;
  frequency: string;
  started: string;
}
