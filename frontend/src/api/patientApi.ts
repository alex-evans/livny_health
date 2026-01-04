import type { Patient, AllergyCheckResult } from '../types';

const BFF_URL = 'http://localhost:8000';

export interface AllergyOverrideLogRequest {
  patient_id: string;
  medication_name: string;
  allergen: string;
  severity: string;
  justification: string;
  acknowledged_at: string;
  prescribed_at: string;
}

export async function logAllergyOverride(
  override: AllergyOverrideLogRequest
): Promise<{ success: boolean; logId: string }> {
  const response = await fetch(`${BFF_URL}/allergy-overrides`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(override),
  });

  if (!response.ok) {
    throw new Error('Failed to log allergy override');
  }

  return response.json();
}

export async function checkAllergyConflict(
  patientId: string,
  medicationName: string
): Promise<AllergyCheckResult> {
  const response = await fetch(`${BFF_URL}/patients/${patientId}/check-allergy`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ medication_name: medicationName }),
  });

  if (!response.ok) {
    throw new Error('Failed to check allergy');
  }

  return response.json();
}

export async function getPatients(): Promise<Patient[]> {
  const response = await fetch(`${BFF_URL}/patients`);
  if (!response.ok) {
    throw new Error('Failed to fetch patients');
  }
  return response.json();
}

export async function getPatient(patientId: string): Promise<Patient> {
  const response = await fetch(`${BFF_URL}/patients/${patientId}`);
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Patient not found');
    }
    throw new Error('Failed to fetch patient');
  }
  return response.json();
}
