import type { ImagingStudiesResponse, ImagingModality } from '../types/imaging';

const BFF_URL = 'http://localhost:8000';

export interface GetImagingStudiesParams {
  modality?: ImagingModality;
  daysBack?: number;
}

export async function getImagingStudies(
  patientId: string,
  params: GetImagingStudiesParams = {}
): Promise<ImagingStudiesResponse> {
  const queryParams = new URLSearchParams();

  if (params.modality) {
    queryParams.set('modality', params.modality);
  }
  if (params.daysBack !== undefined) {
    queryParams.set('days_back', params.daysBack.toString());
  }

  const queryString = queryParams.toString();
  const url = `${BFF_URL}/imaging/${patientId}/studies${queryString ? `?${queryString}` : ''}`;

  const response = await fetch(url);

  if (!response.ok) {
    if (response.status === 404) {
      // Return empty response for unknown patient
      return { studies: [], totalCount: 0 };
    }
    throw new Error('Failed to fetch imaging studies');
  }

  return response.json();
}
