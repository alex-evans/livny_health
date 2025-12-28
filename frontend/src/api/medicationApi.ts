import type { MedicationSearchResult } from '../types';
import { mockMedications } from './mockData';

// Simulates network delay for realistic UX testing
const simulateDelay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export async function searchMedications(query: string): Promise<MedicationSearchResult[]> {
  // Simulate API latency
  await simulateDelay(150);

  if (query.length < 3) {
    return [];
  }

  const lowerQuery = query.toLowerCase();

  return mockMedications.filter(med =>
    med.name.toLowerCase().includes(lowerQuery)
  );
}
