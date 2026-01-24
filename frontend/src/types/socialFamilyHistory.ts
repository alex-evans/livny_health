// Status and level types
export type SmokingStatus =
  | 'current_daily'
  | 'current_occasional'
  | 'former'
  | 'never'
  | 'unknown';

export type AlcoholUse =
  | 'none'
  | 'occasional'
  | 'moderate'
  | 'heavy'
  | 'in_recovery'
  | 'unknown';

export type SubstanceUseLevel =
  | 'none'
  | 'past'
  | 'current'
  | 'in_recovery'
  | 'unknown';

export type ExerciseLevel =
  | 'sedentary'
  | 'light'
  | 'moderate'
  | 'active'
  | 'very_active'
  | 'unknown';

export type DietType =
  | 'regular'
  | 'vegetarian'
  | 'vegan'
  | 'low_sodium'
  | 'low_carb'
  | 'diabetic'
  | 'heart_healthy'
  | 'other'
  | 'unknown';

export type MaritalStatus =
  | 'single'
  | 'married'
  | 'partnered'
  | 'divorced'
  | 'widowed'
  | 'separated'
  | 'unknown';

export type RelativeDegree = 'first' | 'second' | 'third';

export type RelativeType =
  | 'mother'
  | 'father'
  | 'sister'
  | 'brother'
  | 'daughter'
  | 'son'
  | 'maternal_grandmother'
  | 'maternal_grandfather'
  | 'paternal_grandmother'
  | 'paternal_grandfather'
  | 'maternal_aunt'
  | 'maternal_uncle'
  | 'paternal_aunt'
  | 'paternal_uncle'
  | 'niece'
  | 'nephew'
  | 'cousin'
  | 'half_sibling'
  | 'other';

export type RiskLevel = 'low' | 'moderate' | 'high';

export type AdoptionStatus =
  | 'not_adopted'
  | 'adopted_known_history'
  | 'adopted_unknown_history'
  | 'unknown';

// History component interfaces
export interface SmokingHistory {
  status: SmokingStatus;
  packYears: number | null;
  quitDate: string | null; // ISO date string
  notes: string | null;
}

export interface AlcoholHistory {
  useLevel: AlcoholUse;
  drinksPerWeek: number | null;
  historyOfAbuse: boolean;
  notes: string | null;
}

export interface SubstanceUseHistory {
  level: SubstanceUseLevel;
  substances: string[];
  ivDrugUse: boolean;
  notes: string | null;
}

export interface SocialHistory {
  smoking: SmokingHistory;
  alcohol: AlcoholHistory;
  substanceUse: SubstanceUseHistory;
  occupation: string | null;
  occupationHazards: string[];
  livingSituation: string | null;
  maritalStatus: MaritalStatus;
  exercise: ExerciseLevel;
  diet: DietType;
  dietNotes: string | null;
  lastReviewed: string | null; // ISO date string
  reviewedBy: string | null;
}

export interface FamilyMemberCondition {
  conditionName: string;
  icd10Code: string | null;
  ageAtOnset: number | null;
  notes: string | null;
}

export interface FamilyMember {
  id: string;
  relativeType: RelativeType;
  degree: RelativeDegree;
  isLiving: boolean;
  ageAtDeath: number | null;
  causeOfDeath: string | null;
  conditions: FamilyMemberCondition[];
}

export interface SignificantCondition {
  conditionName: string;
  icd10Code: string | null;
  affectedRelatives: string[];
  notes: string | null;
}

export interface FamilyHistory {
  familyMembers: FamilyMember[];
  significantConditions: SignificantCondition[];
  hereditarySyndromes: string[];
  adoptionStatus: AdoptionStatus;
  lastReviewed: string | null; // ISO date string
  reviewedBy: string | null;
}

export interface RiskAssessment {
  riskType: string;
  riskLevel: RiskLevel;
  contributingFactors: string[];
  recommendations: string[];
  screeningDue: string | null; // ISO date string
  calculatedAt: string; // ISO date string
  notes: string | null;
}

export interface SocialFamilyHistoryResponse {
  socialHistory: SocialHistory | null;
  familyHistory: FamilyHistory | null;
  riskAssessments: RiskAssessment[];
  lastReviewed: string | null; // ISO date string
  hasHighRisk: boolean;
}

// Display configuration types
export interface StatusDisplayConfig {
  label: string;
  color: 'green' | 'yellow' | 'red' | 'gray';
  description?: string;
}

export const SMOKING_STATUS_CONFIG: Record<SmokingStatus, StatusDisplayConfig> = {
  never: { label: 'Never smoker', color: 'green' },
  former: { label: 'Former smoker', color: 'yellow' },
  current_occasional: { label: 'Current (occasional)', color: 'red' },
  current_daily: { label: 'Current (daily)', color: 'red' },
  unknown: { label: 'Unknown', color: 'gray' },
};

export const ALCOHOL_USE_CONFIG: Record<AlcoholUse, StatusDisplayConfig> = {
  none: { label: 'None', color: 'green' },
  occasional: { label: 'Occasional', color: 'green' },
  moderate: { label: 'Moderate', color: 'yellow' },
  heavy: { label: 'Heavy', color: 'red' },
  in_recovery: { label: 'In recovery', color: 'yellow' },
  unknown: { label: 'Unknown', color: 'gray' },
};

export const SUBSTANCE_USE_CONFIG: Record<SubstanceUseLevel, StatusDisplayConfig> = {
  none: { label: 'None', color: 'green' },
  past: { label: 'Past use', color: 'yellow' },
  current: { label: 'Current use', color: 'red' },
  in_recovery: { label: 'In recovery', color: 'yellow' },
  unknown: { label: 'Unknown', color: 'gray' },
};

export const EXERCISE_LEVEL_CONFIG: Record<ExerciseLevel, StatusDisplayConfig> = {
  very_active: { label: 'Very active', color: 'green', description: '5+ days/week, vigorous' },
  active: { label: 'Active', color: 'green', description: '3-4 days/week' },
  moderate: { label: 'Moderate', color: 'yellow', description: '1-2 days/week' },
  light: { label: 'Light', color: 'yellow', description: 'Occasional' },
  sedentary: { label: 'Sedentary', color: 'red', description: 'Little to no exercise' },
  unknown: { label: 'Unknown', color: 'gray' },
};

export const RISK_LEVEL_CONFIG: Record<RiskLevel, StatusDisplayConfig> = {
  low: { label: 'Low Risk', color: 'green' },
  moderate: { label: 'Moderate Risk', color: 'yellow' },
  high: { label: 'High Risk', color: 'red' },
};

export const RELATIVE_TYPE_LABELS: Record<RelativeType, string> = {
  mother: 'Mother',
  father: 'Father',
  sister: 'Sister',
  brother: 'Brother',
  daughter: 'Daughter',
  son: 'Son',
  maternal_grandmother: 'Maternal Grandmother',
  maternal_grandfather: 'Maternal Grandfather',
  paternal_grandmother: 'Paternal Grandmother',
  paternal_grandfather: 'Paternal Grandfather',
  maternal_aunt: 'Maternal Aunt',
  maternal_uncle: 'Maternal Uncle',
  paternal_aunt: 'Paternal Aunt',
  paternal_uncle: 'Paternal Uncle',
  niece: 'Niece',
  nephew: 'Nephew',
  cousin: 'Cousin',
  half_sibling: 'Half-Sibling',
  other: 'Other',
};

export const MARITAL_STATUS_LABELS: Record<MaritalStatus, string> = {
  single: 'Single',
  married: 'Married',
  partnered: 'Partnered',
  divorced: 'Divorced',
  widowed: 'Widowed',
  separated: 'Separated',
  unknown: 'Unknown',
};

export const DIET_TYPE_LABELS: Record<DietType, string> = {
  regular: 'Regular',
  vegetarian: 'Vegetarian',
  vegan: 'Vegan',
  low_sodium: 'Low Sodium',
  low_carb: 'Low Carb',
  diabetic: 'Diabetic',
  heart_healthy: 'Heart Healthy',
  other: 'Other',
  unknown: 'Unknown',
};
