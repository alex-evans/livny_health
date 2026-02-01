import type { EncounterType } from './patient';

export type PromptStatus = 'uncovered' | 'mentioned' | 'dismissed';
export type SOAPSectionKey = 'subjective' | 'objective' | 'assessment' | 'plan';
export type SectionGuidanceStatus = 'complete' | 'partial' | 'uncovered';

export type { EncounterType };

export interface DocumentationPrompt {
  id: string;
  label: string;
  description: string;
  keywords: string[];
  required: boolean;
  encounterTypes: EncounterType[];
}

export interface PromptWithStatus extends DocumentationPrompt {
  status: PromptStatus;
}

export interface SectionCoverage {
  section: SOAPSectionKey;
  status: SectionGuidanceStatus;
  prompts: PromptWithStatus[];
  coveredCount: number;
  totalCount: number;
}

export interface GuidanceCoverage {
  subjective: SectionCoverage;
  objective: SectionCoverage;
  assessment: SectionCoverage;
  plan: SectionCoverage;
}

export interface GuidancePreferences {
  autoShowOnNewNote: boolean;
  hideGuidanceEntirely: boolean;
  enableQuickInsert: boolean;
}
