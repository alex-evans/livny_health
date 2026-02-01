import { useMemo } from 'react';
import { useDebounce } from './useDebounce';
import { getAllPromptsForEncounterType } from '../config/promptDefinitions';
import type {
  EncounterType,
  SOAPSectionKey,
  GuidanceCoverage,
  SectionCoverage,
  PromptWithStatus,
  PromptStatus,
  SectionGuidanceStatus,
  DocumentationPrompt,
} from '../types/guidance';

interface UsePromptCoverageOptions {
  content: string;
  encounterType: EncounterType;
  dismissedPrompts: Set<string>;
  debounceMs?: number;
}

interface UsePromptCoverageResult {
  coverage: GuidanceCoverage;
  isDebouncing: boolean;
}

function checkPromptCovered(content: string, keywords: string[]): boolean {
  const lowerContent = content.toLowerCase();
  return keywords.some((keyword) => lowerContent.includes(keyword.toLowerCase()));
}

function getPromptStatus(
  prompt: DocumentationPrompt,
  content: string,
  dismissedPrompts: Set<string>
): PromptStatus {
  if (dismissedPrompts.has(prompt.id)) {
    return 'dismissed';
  }
  if (checkPromptCovered(content, prompt.keywords)) {
    return 'mentioned';
  }
  return 'uncovered';
}

function getSectionStatus(prompts: PromptWithStatus[]): SectionGuidanceStatus {
  const activePrompts = prompts.filter((p) => p.status !== 'dismissed');
  if (activePrompts.length === 0) {
    return 'complete';
  }

  const coveredCount = activePrompts.filter((p) => p.status === 'mentioned').length;

  if (coveredCount === activePrompts.length) {
    return 'complete';
  }
  if (coveredCount > 0) {
    return 'partial';
  }
  return 'uncovered';
}

function calculateSectionCoverage(
  section: SOAPSectionKey,
  prompts: DocumentationPrompt[],
  content: string,
  dismissedPrompts: Set<string>
): SectionCoverage {
  const promptsWithStatus: PromptWithStatus[] = prompts.map((prompt) => ({
    ...prompt,
    status: getPromptStatus(prompt, content, dismissedPrompts),
  }));

  const activePrompts = promptsWithStatus.filter((p) => p.status !== 'dismissed');
  const coveredCount = activePrompts.filter((p) => p.status === 'mentioned').length;

  return {
    section,
    status: getSectionStatus(promptsWithStatus),
    prompts: promptsWithStatus,
    coveredCount,
    totalCount: activePrompts.length,
  };
}

export function usePromptCoverage({
  content,
  encounterType,
  dismissedPrompts,
  debounceMs = 500,
}: UsePromptCoverageOptions): UsePromptCoverageResult {
  const debouncedContent = useDebounce(content, debounceMs);
  const isDebouncing = content !== debouncedContent;

  const coverage = useMemo<GuidanceCoverage>(() => {
    const allPrompts = getAllPromptsForEncounterType(encounterType);

    return {
      subjective: calculateSectionCoverage(
        'subjective',
        allPrompts.subjective,
        debouncedContent,
        dismissedPrompts
      ),
      objective: calculateSectionCoverage(
        'objective',
        allPrompts.objective,
        debouncedContent,
        dismissedPrompts
      ),
      assessment: calculateSectionCoverage(
        'assessment',
        allPrompts.assessment,
        debouncedContent,
        dismissedPrompts
      ),
      plan: calculateSectionCoverage(
        'plan',
        allPrompts.plan,
        debouncedContent,
        dismissedPrompts
      ),
    };
  }, [debouncedContent, encounterType, dismissedPrompts]);

  return { coverage, isDebouncing };
}
