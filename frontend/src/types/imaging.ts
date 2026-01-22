// Imaging Study Types

export type ImagingModality = 'CT' | 'MRI' | 'XR' | 'US' | 'NM' | 'PET' | 'FLUORO' | 'MAMMO';
export type ReportStatus = 'final' | 'preliminary' | 'pending' | 'addendum';

export const MODALITY_NAMES: Record<ImagingModality, string> = {
  CT: 'Computed Tomography',
  MRI: 'Magnetic Resonance Imaging',
  XR: 'X-Ray',
  US: 'Ultrasound',
  NM: 'Nuclear Medicine',
  PET: 'Positron Emission Tomography',
  FLUORO: 'Fluoroscopy',
  MAMMO: 'Mammography',
};

export interface ComparisonStudy {
  studyId: string;
  date: string; // ISO date string
  modality: ImagingModality;
  bodyPart: string;
}

export interface RadiologyReport {
  clinicalIndication: string;
  technique: string;
  findings: string;
  impression: string;
  comparisonStudies: ComparisonStudy[];
  criticalFinding: boolean;
  addendum?: string | null;
}

export interface ImagingStudy {
  id: string;
  patientId: string;
  accessionNumber?: string | null;
  modality: ImagingModality;
  modalityName: string;
  bodyPart: string;
  studyDate: string; // ISO date string
  facility: string;
  orderingProvider: string;
  readingRadiologist?: string | null;
  indication: string;
  seriesCount: number;
  imageCount: number;
  hasImages: boolean;
  reportStatus: ReportStatus;
  report?: RadiologyReport | null;
}

export interface ImagingStudiesResponse {
  studies: ImagingStudy[];
  totalCount: number;
}

// Filter types
export type ImagingTimeRange = '30' | '90' | '365' | '730' | 'all';
export type ImagingGroupBy = 'modality' | 'chronological';
