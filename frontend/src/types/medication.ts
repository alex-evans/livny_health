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
}
