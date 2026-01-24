import type { SocialFamilyHistoryResponse } from '../types';

const BFF_URL = 'http://localhost:8000';

export interface GetSocialFamilyHistoryParams {
  includeRiskAssessments?: boolean;
}

export async function getSocialFamilyHistory(
  patientId: string,
  params: GetSocialFamilyHistoryParams = {}
): Promise<SocialFamilyHistoryResponse> {
  const queryParams = new URLSearchParams();

  if (params.includeRiskAssessments !== undefined) {
    queryParams.set('include_risk_assessments', params.includeRiskAssessments.toString());
  }

  const queryString = queryParams.toString();
  const url = `${BFF_URL}/patients/${patientId}/social-family-history${queryString ? `?${queryString}` : ''}`;

  const response = await fetch(url);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Patient not found');
    }
    throw new Error('Failed to fetch social and family history');
  }

  return response.json();
}
