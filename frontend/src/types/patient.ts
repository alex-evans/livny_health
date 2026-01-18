import type { ActiveMedication } from './medication';

export type AllergySeverity = 'mild' | 'moderate' | 'severe' | 'unknown';
export type AllergyType = 'drug' | 'food' | 'environmental' | 'other';
export type AllergySource = 'patient_reported' | 'chart_documented' | 'verified_by_provider';
export type AllergyVerificationStatus = 'unconfirmed' | 'confirmed' | 'refuted' | 'entered-in-error';
export type AllergyClinicalStatus = 'active' | 'inactive' | 'resolved';

export interface AllergyReaction {
  manifestation: string;
  severity: AllergySeverity;
  description?: string | null;
}

export interface Allergy {
  id: string;
  allergen: string;
  type: AllergyType;
  reaction: string;
  severity: AllergySeverity;
  isAnaphylaxis: boolean;
  documented: string;
  source?: AllergySource;
  clinicalStatus?: AllergyClinicalStatus;
  verificationStatus?: AllergyVerificationStatus;
  lastUpdated?: string | null;
  documentingProvider?: string | null;
  notes?: string | null;
  reactions?: AllergyReaction[];
}

export interface NextAppointment {
  date: string;
  time: string;
  reason: string;
}

export interface Problem {
  name: string;
  diagnosedYear: number;
}

export interface RecentVitals {
  date: string;
  bloodPressure: string;
  weight: string;
  temperature: string;
}

export interface Insurance {
  provider: string;
  memberId: string;
}

export interface AllergyReviewStatus {
  reviewedAt: string;
  reviewedBy: string | null;
  isStale: boolean;
}

export interface Patient {
  id: string;
  name: string;
  dateOfBirth: string;
  gender: string;
  mrn: string;
  phone?: string;
  insurance?: Insurance;
  allergies?: Allergy[];
  activeMedications?: ActiveMedication[];
  nextAppointment?: NextAppointment;
  problemList?: Problem[];
  recentVitals?: RecentVitals;
  allergyReviewStatus?: AllergyReviewStatus;
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
