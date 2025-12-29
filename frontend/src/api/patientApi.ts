import type { Patient } from '../types';

const BFF_URL = 'http://localhost:8000';

export async function getPatients(): Promise<Patient[]> {
  const response = await fetch(`${BFF_URL}/api/patients`);
  if (!response.ok) {
    throw new Error('Failed to fetch patients');
  }
  return response.json();
}
