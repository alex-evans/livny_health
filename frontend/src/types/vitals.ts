export type VitalType =
  | 'blood_pressure_systolic'
  | 'blood_pressure_diastolic'
  | 'heart_rate'
  | 'temperature'
  | 'weight'
  | 'oxygen_saturation'
  | 'respiratory_rate'
  | 'height';

export type VitalStatus = 'normal' | 'abnormal' | 'critical';

export type TrendDirection = 'increasing' | 'decreasing' | 'stable';

export type ClinicalSignificance = 'good' | 'concerning' | 'neutral';

export interface VitalTrendAnalysis {
  direction: TrendDirection;
  percentChange: number;
  absoluteChange: number;
  previousValue: number;
  currentValue: number;
  previousDate: string; // ISO date string
  dataPoints: number;
  clinicalSignificance: ClinicalSignificance;
}

export interface SparklinePoint {
  value: number;
  status: VitalStatus;
  date: string; // ISO date string
}

export interface CurrentVital {
  vitalType: VitalType;
  value: number;
  unit: string;
  status: VitalStatus;
  recordedAt: string; // ISO date string
  referenceRange: string;
  recordedBy: string | null;
  location: string | null;
  trend: VitalTrendAnalysis | null;
  sparklineData: SparklinePoint[];
}

export interface BMIResponse {
  value: number;
  category: string; // "Underweight" | "Normal" | "Overweight" | "Obese"
  heightValue: number;
  heightUnit: string;
  weightValue: number;
  weightUnit: string;
  calculatedAt: string; // ISO date string
}

export interface VitalsResponse {
  vitals: CurrentVital[];
  bmi: BMIResponse | null;
  mostRecentDate: string | null; // ISO date string
}

export interface VitalHistoryEntry {
  id: string;
  value: number;
  unit: string;
  status: VitalStatus;
  recordedAt: string; // ISO date string
  referenceRange: string;
  recordedBy: string | null;
  location: string | null;
}

export interface VitalHistoryResponse {
  vitalType: VitalType;
  unit: string;
  referenceRange: string;
  history: VitalHistoryEntry[];
  trendAnalysis: VitalTrendAnalysis | null;
}

// Display configuration for vital types
export interface VitalDisplayConfig {
  label: string;
  shortLabel: string;
  icon?: string;
}

export const VITAL_DISPLAY_CONFIG: Record<VitalType, VitalDisplayConfig> = {
  blood_pressure_systolic: {
    label: 'Blood Pressure (Systolic)',
    shortLabel: 'BP Sys',
  },
  blood_pressure_diastolic: {
    label: 'Blood Pressure (Diastolic)',
    shortLabel: 'BP Dia',
  },
  heart_rate: {
    label: 'Heart Rate',
    shortLabel: 'HR',
  },
  temperature: {
    label: 'Temperature',
    shortLabel: 'Temp',
  },
  weight: {
    label: 'Weight',
    shortLabel: 'Wt',
  },
  oxygen_saturation: {
    label: 'Oxygen Saturation',
    shortLabel: 'O₂ Sat',
  },
  respiratory_rate: {
    label: 'Respiratory Rate',
    shortLabel: 'RR',
  },
  height: {
    label: 'Height',
    shortLabel: 'Ht',
  },
};
