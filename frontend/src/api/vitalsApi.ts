import type { VitalsResponse, VitalHistoryResponse, VitalType } from '../types';

const BFF_URL = 'http://localhost:8000';

export interface GetVitalsParams {
  months?: number;
  includeTrends?: boolean;
}

export async function getPatientVitals(
  patientId: string,
  params: GetVitalsParams = {}
): Promise<VitalsResponse> {
  const queryParams = new URLSearchParams();

  if (params.months !== undefined) {
    queryParams.set('months', params.months.toString());
  }
  if (params.includeTrends !== undefined) {
    queryParams.set('include_trends', params.includeTrends.toString());
  }

  const queryString = queryParams.toString();
  const url = `${BFF_URL}/patients/${patientId}/vitals${queryString ? `?${queryString}` : ''}`;

  const response = await fetch(url);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Patient not found');
    }
    throw new Error('Failed to fetch patient vitals');
  }

  return response.json();
}

export async function getVitalHistory(
  patientId: string,
  vitalType: VitalType,
  daysBack: number = 365
): Promise<VitalHistoryResponse> {
  const response = await fetch(
    `${BFF_URL}/patients/${patientId}/vitals/${vitalType}/history?days_back=${daysBack}`
  );

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Vital history not found');
    }
    if (response.status === 400) {
      throw new Error('Invalid vital type');
    }
    throw new Error('Failed to fetch vital history');
  }

  return response.json();
}
