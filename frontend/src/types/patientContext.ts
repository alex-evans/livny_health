/**
 * Patient context types for comprehensive patient view.
 */

// Extend existing ContextVital with trends
export interface EnrichedContextVital {
  id: string;
  vitalType: string;
  displayName: string;
  value: number;
  unit: string;
  displayValue: string;
  status: 'normal' | 'abnormal' | 'critical';
  trend?: 'improving' | 'worsening' | 'stable';
  previousValue?: number;
  previousDate?: string;
  recordedAt: string;
}

// Medication with categories and flags
export interface EnrichedContextMedication {
  id: string;
  name: string;
  genericName?: string;
  dosage: string;
  frequency: string;
  route: string;
  category: string;
  isHighAlert: boolean;
  isRecentlyStarted: boolean;
  startDate?: string;
  prescriber?: string;
}

export interface DiscontinuedMedication {
  id: string;
  name: string;
  dosage: string;
  discontinuedDate: string;
  reason?: string;
}

// Allergy with full details
export interface EnrichedContextAllergy {
  id: string;
  allergen: string;
  reaction: string;
  severity: 'critical' | 'moderate' | 'mild';
  status: 'confirmed' | 'suspected' | 'reported';
  isAnaphylaxis: boolean;
  onsetDate?: string;
  notes?: string;
}

// Problem with ICD-10 and relationships
export interface EnrichedContextProblem {
  id: string;
  description: string;
  icd10Code: string;
  status: 'active' | 'inactive' | 'resolved';
  type: 'chronic' | 'acute';
  onsetDate?: string;
  isPrimary: boolean;
}

// Lab with reference ranges
export interface EnrichedContextLab {
  id: string;
  name: string;
  value: string;
  unit: string;
  referenceRange: string;
  status: 'normal' | 'high' | 'low' | 'critical';
  date: string;
  isPending: boolean;
}

export interface PendingLab {
  name: string;
  orderedDate: string;
}

// Visit with summary
export interface EnrichedContextVisit {
  id: string;
  date: string;
  type: string;
  chiefComplaint: string;
  provider: string;
  daysAgo: number;
  summary?: string;
}

// Quick Context Bar summary
export interface QuickContextSummary {
  primaryVital: { label: string; value: string; trend?: string } | null;
  medicationNames: string[];
  criticalAllergies: string[];
  keyLab: { name: string; value: string } | null;
  problemCount: number;
}

// Full context response
export interface PatientContextData {
  patientId: string;
  generatedAt: string;
  medications: {
    active: EnrichedContextMedication[];
    recentlyDiscontinued: DiscontinuedMedication[];
    totalActive: number;
  };
  allergies: EnrichedContextAllergy[];
  problems: {
    active: EnrichedContextProblem[];
    totalActive: number;
  };
  vitals: {
    mostRecent: Record<string, EnrichedContextVital>;
    recordedAt?: string;
  };
  recentVisits: EnrichedContextVisit[];
  recentLabs: {
    results: EnrichedContextLab[];
    pending: PendingLab[];
  };
  quickSummary: QuickContextSummary;
}

export type ContextMode = 'review' | 'documentation' | 'expanded';
