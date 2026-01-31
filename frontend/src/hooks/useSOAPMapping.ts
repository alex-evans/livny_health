import { useState, useEffect, useRef, useCallback } from 'react';
import { getSOAPMapping } from '../api/encounterApi';
import type { SOAPMappingResponse, SOAPSection, SOAPCompleteness } from '../types';

interface UseSOAPMappingOptions {
  encounterId: string;
  content: string;
  enabled?: boolean;
  debounceMs?: number;
}

interface UseSOAPMappingResult {
  mapping: SOAPMappingResponse | null;
  isLoading: boolean;
  error: string | null;
}

const EMPTY_SECTION: SOAPSection = {
  content: '',
  completeness: 'empty',
  wordCount: 0,
};

const EMPTY_MAPPING: SOAPMappingResponse = {
  subjective: EMPTY_SECTION,
  objective: EMPTY_SECTION,
  assessment: EMPTY_SECTION,
  plan: EMPTY_SECTION,
  overallCompleteness: 'empty',
};

// Section markers for client-side parsing (mirrors backend)
const SECTION_MARKERS: Record<string, string[]> = {
  subjective: [
    'subjective:',
    'subjective',
    's:',
    'hpi:',
    'hpi',
    'history of present illness:',
    'chief complaint:',
    'cc:',
    'patient reports',
    'patient states',
  ],
  objective: [
    'objective:',
    'objective',
    'o:',
    'physical exam:',
    'physical exam',
    'pe:',
    'vitals:',
    'vitals',
    'on exam',
    'findings:',
  ],
  assessment: [
    'assessment:',
    'assessment',
    'a:',
    'impression:',
    'impression',
    'diagnosis:',
    'dx:',
    'differential:',
  ],
  plan: [
    'plan:',
    'plan',
    'p:',
    'recommendations:',
    'treatment plan:',
    'follow-up:',
    'orders:',
    'management:',
  ],
};

const PARTIAL_THRESHOLD = 30;

function countWords(text: string): number {
  if (!text || !text.trim()) return 0;
  return text.split(/\s+/).filter(Boolean).length;
}

function getCompleteness(wordCount: number): SOAPCompleteness {
  if (wordCount === 0) return 'empty';
  if (wordCount < PARTIAL_THRESHOLD) return 'partial';
  return 'complete';
}

function findSectionStart(text: string, markers: string[]): number | null {
  const textLower = text.toLowerCase();
  let bestPos: number | null = null;

  for (const marker of markers) {
    const pos = textLower.indexOf(marker.toLowerCase());
    if (pos !== -1) {
      let endPos = pos + marker.length;
      while (endPos < text.length && ': \t'.includes(text[endPos])) {
        endPos++;
      }
      if (bestPos === null || pos < bestPos) {
        bestPos = endPos;
      }
    }
  }

  return bestPos;
}

function extractSectionContent(
  text: string,
  sectionName: string,
  allMarkers: Record<string, string[]>
): string {
  const markers = allMarkers[sectionName];
  const start = findSectionStart(text, markers);

  if (start === null) return '';

  let end = text.length;
  for (const [otherSection, otherMarkers] of Object.entries(allMarkers)) {
    if (otherSection === sectionName) continue;
    for (const marker of otherMarkers) {
      const markerPos = text.toLowerCase().indexOf(marker.toLowerCase());
      if (markerPos !== null && markerPos > start && markerPos < end) {
        end = markerPos;
      }
    }
  }

  return text.slice(start, end).trim();
}

function parseClientSide(content: string): SOAPMappingResponse {
  if (!content || !content.trim()) {
    return EMPTY_MAPPING;
  }

  const sections: Record<string, SOAPSection> = {};
  const completenessValues: SOAPCompleteness[] = [];

  for (const sectionName of ['subjective', 'objective', 'assessment', 'plan']) {
    const sectionContent = extractSectionContent(content, sectionName, SECTION_MARKERS);
    const wordCount = countWords(sectionContent);
    const completeness = getCompleteness(wordCount);
    completenessValues.push(completeness);

    sections[sectionName] = {
      content: sectionContent,
      completeness,
      wordCount,
    };
  }

  let overallCompleteness: SOAPCompleteness;
  if (completenessValues.every((c) => c === 'complete')) {
    overallCompleteness = 'complete';
  } else if (completenessValues.every((c) => c === 'empty')) {
    overallCompleteness = 'empty';
  } else {
    overallCompleteness = 'partial';
  }

  return {
    subjective: sections.subjective,
    objective: sections.objective,
    assessment: sections.assessment,
    plan: sections.plan,
    overallCompleteness,
  };
}

export function useSOAPMapping({
  encounterId,
  content,
  enabled = true,
  debounceMs = 1000,
}: UseSOAPMappingOptions): UseSOAPMappingResult {
  const [mapping, setMapping] = useState<SOAPMappingResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const lastContentRef = useRef<string>('');

  // Immediate client-side parse for instant feedback
  useEffect(() => {
    if (!enabled) {
      setMapping(null);
      return;
    }

    const clientMapping = parseClientSide(content);
    setMapping(clientMapping);
  }, [content, enabled]);

  // Debounced server request for refined parse
  const fetchServerMapping = useCallback(async () => {
    if (!enabled || !encounterId) return;

    // Cancel any in-flight request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Don't fetch if content hasn't changed
    if (content === lastContentRef.current) return;
    lastContentRef.current = content;

    // Don't fetch for empty content
    if (!content || !content.trim()) {
      setMapping(EMPTY_MAPPING);
      setError(null);
      return;
    }

    abortControllerRef.current = new AbortController();
    setIsLoading(true);
    setError(null);

    try {
      const result = await getSOAPMapping(encounterId, content);
      setMapping(result);
    } catch (err) {
      // Don't update error state for aborted requests
      if (err instanceof Error && err.name === 'AbortError') return;
      setError(err instanceof Error ? err.message : 'Failed to parse note');
      // Keep client-side mapping on error
    } finally {
      setIsLoading(false);
    }
  }, [encounterId, content, enabled]);

  // Set up debounced server fetch
  useEffect(() => {
    if (!enabled) return;

    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      fetchServerMapping();
    }, debounceMs);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [fetchServerMapping, debounceMs, enabled]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, []);

  return { mapping, isLoading, error };
}
