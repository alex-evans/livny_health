/**
 * Clinical Alert Types
 *
 * Types for clinical alerts that flag critical patient information
 * such as abnormal labs, critical vitals, overdue screenings, and drug interactions.
 */

export type AlertType =
  | 'critical_lab'
  | 'critical_vital'
  | 'critical_imaging'
  | 'drug_interaction'
  | 'overdue_screening'
  | 'chronic_disease';

export type AlertSeverity = 'critical' | 'high' | 'medium';

export type AlertStatus = 'active' | 'acknowledged' | 'dismissed';

export interface AlertAcknowledgment {
  acknowledgedBy: string;
  acknowledgedAt: string; // ISO date string
  note: string | null;
}

export interface ClinicalAlert {
  id: string;
  patientId: string;
  alertType: AlertType;
  severity: AlertSeverity;
  status: AlertStatus;
  title: string;
  description: string;
  generatedAt: string; // ISO date string
  source: string;
  sourceId: string;
  sourceLink: string | null;
  context: Record<string, unknown>;
  recommendedActions: string[];
  acknowledgment: AlertAcknowledgment | null;
  dismissedAt: string | null;
  dismissedBy: string | null;
  dismissedReason: string | null;
}

export interface AlertSummary {
  criticalCount: number;
  highCount: number;
  mediumCount: number;
  totalActive: number;
}

export interface AlertsResponse {
  alerts: ClinicalAlert[];
  summary: AlertSummary;
}

// Display configuration for alert types
export interface AlertDisplayConfig {
  label: string;
  icon: string;
  description: string;
}

export const ALERT_TYPE_CONFIG: Record<AlertType, AlertDisplayConfig> = {
  critical_lab: {
    label: 'Critical Lab',
    icon: '🔬',
    description: 'Critical laboratory value requiring immediate attention',
  },
  critical_vital: {
    label: 'Critical Vital',
    icon: '💓',
    description: 'Critical vital sign measurement',
  },
  critical_imaging: {
    label: 'Critical Imaging',
    icon: '🩻',
    description: 'Critical finding on imaging study',
  },
  drug_interaction: {
    label: 'Drug Interaction',
    icon: '💊',
    description: 'Potential drug-drug interaction',
  },
  overdue_screening: {
    label: 'Overdue Screening',
    icon: '📋',
    description: 'Preventive screening is overdue',
  },
  chronic_disease: {
    label: 'Chronic Disease',
    icon: '⚕️',
    description: 'Chronic disease management concern',
  },
};

// Severity display configuration
export interface SeverityDisplayConfig {
  label: string;
  bgColor: string;
  borderColor: string;
  textColor: string;
  iconColor: string;
}

export const SEVERITY_CONFIG: Record<AlertSeverity, SeverityDisplayConfig> = {
  critical: {
    label: 'Critical',
    bgColor: 'bg-red-50',
    borderColor: 'border-l-red-500',
    textColor: 'text-red-800',
    iconColor: 'text-red-500',
  },
  high: {
    label: 'High',
    bgColor: 'bg-orange-50',
    borderColor: 'border-l-orange-500',
    textColor: 'text-orange-800',
    iconColor: 'text-orange-500',
  },
  medium: {
    label: 'Medium',
    bgColor: 'bg-blue-50',
    borderColor: 'border-l-blue-500',
    textColor: 'text-blue-800',
    iconColor: 'text-blue-500',
  },
};
