/**
 * Clinical Alerts API Client
 *
 * Functions for fetching and managing clinical alerts.
 */

import type { AlertsResponse, AlertSummary, ClinicalAlert, AlertStatus } from '../types';

const BFF_URL = 'http://localhost:8000';

export interface GetAlertsParams {
  status?: AlertStatus | 'all';
}

/**
 * Get clinical alerts for a patient.
 *
 * @param patientId - The patient ID
 * @param params - Optional parameters (status filter)
 * @returns AlertsResponse with alerts and summary
 */
export async function getPatientAlerts(
  patientId: string,
  params: GetAlertsParams = {}
): Promise<AlertsResponse> {
  const queryParams = new URLSearchParams();

  if (params.status !== undefined) {
    queryParams.set('status', params.status);
  }

  const queryString = queryParams.toString();
  const url = `${BFF_URL}/patients/${patientId}/alerts${queryString ? `?${queryString}` : ''}`;

  const response = await fetch(url);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Patient not found');
    }
    if (response.status === 400) {
      const data = await response.json();
      throw new Error(data.detail || 'Invalid request');
    }
    throw new Error('Failed to fetch patient alerts');
  }

  return response.json();
}

/**
 * Get summary counts of active alerts for a patient.
 *
 * @param patientId - The patient ID
 * @returns AlertSummary with counts by severity
 */
export async function getAlertSummary(patientId: string): Promise<AlertSummary> {
  const response = await fetch(`${BFF_URL}/patients/${patientId}/alerts/summary`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Patient not found');
    }
    throw new Error('Failed to fetch alert summary');
  }

  return response.json();
}

export interface AcknowledgeAlertParams {
  by: string;
  note?: string;
}

/**
 * Acknowledge a clinical alert.
 *
 * @param patientId - The patient ID
 * @param alertId - The alert ID
 * @param params - Acknowledgment parameters
 * @returns The updated ClinicalAlert
 */
export async function acknowledgeAlert(
  patientId: string,
  alertId: string,
  params: AcknowledgeAlertParams
): Promise<ClinicalAlert> {
  const response = await fetch(
    `${BFF_URL}/patients/${patientId}/alerts/${alertId}/acknowledge`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    }
  );

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Alert not found');
    }
    throw new Error('Failed to acknowledge alert');
  }

  return response.json();
}

export interface DismissAlertParams {
  by: string;
  reason?: string;
}

/**
 * Dismiss a clinical alert.
 *
 * @param patientId - The patient ID
 * @param alertId - The alert ID
 * @param params - Dismissal parameters
 * @returns The updated ClinicalAlert
 */
export async function dismissAlert(
  patientId: string,
  alertId: string,
  params: DismissAlertParams
): Promise<ClinicalAlert> {
  const response = await fetch(
    `${BFF_URL}/patients/${patientId}/alerts/${alertId}/dismiss`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    }
  );

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Alert not found');
    }
    throw new Error('Failed to dismiss alert');
  }

  return response.json();
}
