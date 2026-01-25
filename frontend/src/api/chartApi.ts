import type { ChartSectionsResponse } from '../types';

const BFF_URL = 'http://localhost:8000';

export async function getChartSections(
  patientId: string
): Promise<ChartSectionsResponse> {
  const response = await fetch(`${BFF_URL}/patients/${patientId}/chart/sections`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Patient not found');
    }
    throw new Error('Failed to fetch chart sections');
  }

  return response.json();
}
