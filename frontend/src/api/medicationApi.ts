import type { MedicationSearchResult } from '../types';

const BFF_URL = 'http://localhost:8000';
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

interface CacheEntry {
  results: MedicationSearchResult[];
  timestamp: number;
}

const searchCache = new Map<string, CacheEntry>();

function getCached(query: string): MedicationSearchResult[] | null {
  const entry = searchCache.get(query.toLowerCase());
  if (!entry) return null;

  if (Date.now() - entry.timestamp > CACHE_TTL_MS) {
    searchCache.delete(query.toLowerCase());
    return null;
  }

  return entry.results;
}

function setCache(query: string, results: MedicationSearchResult[]): void {
  searchCache.set(query.toLowerCase(), {
    results,
    timestamp: Date.now(),
  });
}

export async function searchMedications(query: string): Promise<MedicationSearchResult[]> {
  if (query.length < 3) {
    return [];
  }

  const cached = getCached(query);
  if (cached) {
    return cached;
  }

  const response = await fetch(`${BFF_URL}/medications/search?q=${encodeURIComponent(query)}`);
  if (!response.ok) {
    throw new Error('Failed to search medications');
  }

  const results = await response.json();
  setCache(query, results);
  return results;
}
