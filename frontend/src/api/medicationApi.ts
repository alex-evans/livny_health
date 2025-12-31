import type { MedicationSearchResult } from '../types';

const BFF_URL = 'http://localhost:8000';

export async function searchMedications(query: string): Promise<MedicationSearchResult[]> {
  if (query.length < 3) {
    return [];
  }

  const response = await fetch(`${BFF_URL}/api/medications/search?q=${encodeURIComponent(query)}`);
  if (!response.ok) {
    throw new Error('Failed to search medications');
  }
  return response.json();
}
