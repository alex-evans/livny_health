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
}
