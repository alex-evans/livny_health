import type { DailySchedule } from '../types';

const BFF_URL = 'http://localhost:8000';

export async function getDailySchedule(
  date: string,
  providerId: string = 'provider-001'
): Promise<DailySchedule> {
  const params = new URLSearchParams({
    date,
    provider_id: providerId,
  });

  const response = await fetch(`${BFF_URL}/schedule?${params}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Schedule not found');
    }
    throw new Error('Failed to fetch schedule');
  }

  return response.json();
}
