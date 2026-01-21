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

export type ProblemStatus = 'active' | 'inactive' | 'resolved' | 'rule_out';
export type ProblemPriority = 'chronic' | 'acute' | 'inactive' | 'resolved';
export type ProblemSeverity = 'mild' | 'moderate' | 'severe' | 'well_controlled';

export type ClinicalCategory =
  | 'cardiovascular'
  | 'endocrine'
  | 'respiratory'
  | 'musculoskeletal'
  | 'neurological'
  | 'gastrointestinal'
  | 'psychiatric'
  | 'infectious'
  | 'oncology'
  | 'renal'
  | 'dermatological'
  | 'other';

export type ProblemComplexity =
  | 'simple'
  | 'with_complications'
  | 'controlled'
  | 'uncontrolled'
  | 'progressive';

export interface RelatedVisit {
  visitId: string;
  date: string; // ISO date string
  visitType: string;
  providerName?: string | null;
}

export interface RelatedMedication {
  medicationId: string;
  name: string;
  dosage?: string | null;
}

export interface RelatedLabResult {
  labName: string;
  mostRecentValue?: string | null;
  mostRecentDate?: string | null; // ISO date string
  status?: string | null; // normal, abnormal, critical
}

export interface Problem {
  name: string;
  icd10Code: string;
  onsetDate: string; // ISO date string
  status: ProblemStatus;
  priority: ProblemPriority;
  severity?: ProblemSeverity;
  documentingProvider?: string;
  documentedDate?: string; // ISO date string
  isCritical: boolean; // Life-threatening conditions (cancer, severe heart disease, etc.)
  isNew: boolean; // Documented within last 30 days
  isRuleOut: boolean; // Under investigation / suspected diagnosis
  // Resolution tracking fields
  resolvedDate?: string; // ISO date string - when problem was marked resolved
  resolvedByProvider?: string; // Provider who marked problem as resolved
  // Clinical context fields
  clinicalCategory?: ClinicalCategory;
  complexity?: ProblemComplexity;
  parentProblemCode?: string; // ICD-10 code of parent problem (for complications)
  relatedVisits?: RelatedVisit[];
  relatedMedications?: RelatedMedication[];
  relatedLabs?: RelatedLabResult[];
}

export interface ProblemGroup {
  category: ClinicalCategory;
  categoryLabel: string;
  problems: Problem[];
}

// Problem filtering and sorting types
export type ProblemFilterStatus = 'all' | 'active' | 'chronic' | 'inactive' | 'resolved';
export type ProblemSortOption = 'onset' | 'name' | 'lastUpdated';

// Problem detail/history types
export interface ProblemHistoryEntry {
  date: string; // ISO date string
  type: 'onset' | 'progression' | 'treatment' | 'status_change' | 'visit';
  description: string;
  provider?: string | null;
  visitId?: string | null;
}

export interface ProblemTreatmentOutcome {
  treatment: string;
  startDate: string; // ISO date string
  endDate?: string | null; // ISO date string
  outcome: 'effective' | 'partially_effective' | 'ineffective' | 'ongoing';
  notes?: string | null;
}

export interface ProblemDetailResponse {
  problem: Problem;
  historyTimeline: ProblemHistoryEntry[];
  treatments: ProblemTreatmentOutcome[];
  lastAddressed?: string | null; // ISO date string
  currentTreatment?: string | null;
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

// Visit/Encounter Types
export type EncounterType =
  | 'office_visit'
  | 'telehealth'
  | 'urgent_care'
  | 'emergency'
  | 'hospital_admission'
  | 'procedure'
  | 'lab_only'
  | 'follow_up'
  | 'annual_physical';

export type VisitStatus = 'completed' | 'in_progress' | 'scheduled' | 'cancelled' | 'no_show';

export interface VisitDiagnosis {
  code: string; // ICD-10 code
  description: string;
  isPrimary: boolean;
}

export interface VisitProvider {
  id: string;
  name: string;
  role: string; // e.g., "Attending", "Resident", "NP", "PA"
  specialty?: string;
}

// SOAP Note structure for clinical documentation
export interface SOAPNote {
  subjective: string; // Patient's description of symptoms, history
  objective: string; // Physical exam findings, observations
  assessment: string; // Clinical assessment/diagnosis
  plan: string; // Treatment plan
}

// Vital signs recorded during a visit
export interface VisitVitals {
  bloodPressureSystolic?: number; // mmHg
  bloodPressureDiastolic?: number; // mmHg
  heartRate?: number; // bpm
  temperature?: number; // Fahrenheit
  temperatureUnit?: 'F' | 'C';
  weight?: number; // lbs
  weightUnit?: 'lbs' | 'kg';
  oxygenSaturation?: number; // percentage
  respiratoryRate?: number; // breaths per minute
  recordedAt?: string; // ISO date string
}

// Medication prescribed or modified during a visit
export interface VisitMedication {
  id: string;
  name: string;
  dosage: string;
  frequency: string;
  route?: string; // oral, IV, topical, etc.
  action: 'prescribed' | 'modified' | 'discontinued' | 'continued';
  instructions?: string;
}

// Order types for labs, imaging, referrals
export type OrderType = 'lab' | 'imaging' | 'referral' | 'procedure' | 'other';
export type OrderStatus = 'ordered' | 'pending' | 'in_progress' | 'completed' | 'cancelled';

// Clinical order placed during a visit
export interface VisitOrder {
  id: string;
  orderType: OrderType;
  name: string; // e.g., "CBC", "Chest X-ray", "Cardiology consult"
  status: OrderStatus;
  orderedAt: string; // ISO date string
  completedAt?: string; // ISO date string
  result?: string; // Brief result summary if available
  priority?: 'routine' | 'urgent' | 'stat';
}

export interface Visit {
  id: string;
  date: string; // ISO date string
  visitType: EncounterType;
  status: VisitStatus;
  chiefComplaint: string;
  diagnoses: VisitDiagnosis[];
  provider: VisitProvider;
  location?: string; // Facility or clinic name
  duration?: number; // Visit duration in minutes
  notes?: string; // Brief summary note (not full clinical note)
  // Extended fields for note preview and expansion
  soapNote?: SOAPNote; // Full SOAP note for expanded view
  vitals?: VisitVitals; // Vital signs from this visit
  medications?: VisitMedication[]; // Medications prescribed/modified
  orders?: VisitOrder[]; // Labs, imaging, referrals ordered
  // Timeline enhancement fields
  hasCriticalFindings?: boolean; // Flag for visits with critical findings
  criticalFindingsSummary?: string; // Brief description of critical findings
  hasFollowUpRequired?: boolean; // Flag for visits requiring follow-up action
  followUpSummary?: string; // Brief description of follow-up needed
}

export interface VisitHistoryResponse {
  visits: Visit[];
  totalCount: number;
  hasMore: boolean;
  offset: number;
  limit: number;
}

export interface VisitHistoryParams {
  daysBack?: number;
  includeAll?: boolean;
  limit?: number;
  offset?: number;
  visitType?: EncounterType;
  providerId?: string;
  diagnosisCode?: string;
  searchQuery?: string;
  dateFrom?: string; // ISO date string
  dateTo?: string; // ISO date string
}

export interface VisitProviderOption {
  id: string;
  name: string;
  role: string;
  specialty?: string;
}

export interface VisitProvidersResponse {
  providers: VisitProviderOption[];
}
