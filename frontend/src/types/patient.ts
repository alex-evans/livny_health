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
  recentLabs?: RecentLabs;
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

// Lab Results Types
export type LabResultStatus = 'normal' | 'abnormal' | 'critical' | 'pending' | 'in_progress';

export interface PreviousLabValue {
  value: string;
  collectionDate: string; // ISO date string
}

export interface LabResult {
  id: string;
  testName: string;
  value: string;
  unit: string;
  referenceRange: string;
  status: LabResultStatus;
  collectionDate: string; // ISO date string
  performingLab?: string; // Lab organization name
  previousValue?: PreviousLabValue; // Most recent previous result (same test within last year)
  // Data completeness fields
  lastUpdated?: string; // ISO date string - when the result was last updated in the system
  acknowledged?: boolean; // Whether a provider has acknowledged this result
  acknowledgedBy?: string | null; // Provider ID who acknowledged
  acknowledgedAt?: string | null; // ISO date string - when it was acknowledged
}

export interface LabPanel {
  id: string;
  panelName: string;
  collectionDate: string; // ISO date string
  results: LabResult[];
  performingLab?: string; // Lab organization name (applies to all results in panel)
  lastUpdated?: string; // ISO date string - when the panel was last updated
}

export interface RecentLabs {
  panels: LabPanel[];
  ungroupedResults: LabResult[];
}

// Lab History Types
export interface LabHistoryEntry {
  id: string;
  value: string;
  unit: string;
  status: LabResultStatus;
  collectionDate: string; // ISO date string
  referenceRange: string;
  performingLab?: string;
  // Data completeness fields
  lastUpdated?: string | null; // ISO date string - when the result was last updated
  acknowledged?: boolean; // Whether a provider has acknowledged this result
  acknowledgedBy?: string | null; // Provider ID who acknowledged
  acknowledgedAt?: string | null; // ISO date string - when it was acknowledged
}

export interface TrendAnalysis {
  direction: 'increasing' | 'decreasing' | 'stable';
  percentChange: number;
  absoluteChange: number;
  firstValue: number;
  lastValue: number;
  dataPoints: number;
}

export interface LabHistoryResponse {
  testName: string;
  unit: string;
  referenceRange: string;
  history: LabHistoryEntry[];
  trendAnalysis: TrendAnalysis | null;
}

// Lab Filtering and Sorting Types
export type LabSortOption = 'date' | 'name' | 'abnormal';
export type LabFilterPanel = 'all' | 'BMP' | 'Lipid' | 'CBC' | 'ungrouped';
export type LabFilterStatus = 'all' | 'abnormal' | 'critical';
