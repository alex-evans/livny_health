import type { PatientContextData, QuickContextSummary, ContextMode } from '../types';

const BFF_URL = 'http://localhost:8000';

/**
 * Fetch comprehensive patient context data.
 *
 * @param patientId - The patient ID
 * @param encounterId - Optional encounter ID for context
 * @param mode - 'review' for full history, 'documentation' for today-focused
 */
export async function getPatientContext(
  patientId: string,
  encounterId?: string,
  mode: Exclude<ContextMode, 'expanded'> = 'review'
): Promise<PatientContextData> {
  const params = new URLSearchParams();
  if (encounterId) {
    params.set('encounter_id', encounterId);
  }
  params.set('mode', mode);

  const response = await fetch(
    `${BFF_URL}/patients/${patientId}/context?${params}`
  );

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Patient not found');
    }
    throw new Error('Failed to fetch patient context');
  }

  return response.json();
}

/**
 * Fetch quick context summary for the context bar.
 *
 * @param patientId - The patient ID
 */
export async function getQuickContextSummary(
  patientId: string
): Promise<QuickContextSummary> {
  const response = await fetch(
    `${BFF_URL}/patients/${patientId}/context/quick`
  );

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Patient not found');
    }
    throw new Error('Failed to fetch quick context summary');
  }

  return response.json();
}
