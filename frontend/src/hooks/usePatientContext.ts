import { useState, useCallback, useEffect, useRef } from 'react';
import { getPatientContext } from '../api';
import type { PatientContextData, QuickContextSummary, ContextMode } from '../types';

const STORAGE_KEY_PREFIX = 'livny-context-collapsed-';

interface UsePatientContextOptions {
  patientId: string;
  encounterId?: string;
  mode: ContextMode;
  /** Poll interval in milliseconds. Default: 30000 for documentation mode, 0 (disabled) for review */
  pollInterval?: number;
}

interface UsePatientContextReturn {
  context: PatientContextData | null;
  isLoading: boolean;
  isRefetching: boolean;
  error: string | null;
  refetch: () => Promise<void>;

  // Collapse state with localStorage persistence
  collapsedSections: Set<string>;
  toggleSection: (sectionId: string) => void;
  expandAll: () => void;
  collapseAll: () => void;

  // Quick summary for bar
  quickSummary: QuickContextSummary | null;
}

function getStorageKey(patientId: string): string {
  return `${STORAGE_KEY_PREFIX}${patientId}`;
}

function loadCollapsedSections(patientId: string): Set<string> {
  try {
    const stored = localStorage.getItem(getStorageKey(patientId));
    if (stored) {
      const parsed = JSON.parse(stored);
      if (Array.isArray(parsed)) {
        return new Set(parsed);
      }
    }
  } catch {
    // Ignore storage errors
  }
  return new Set();
}

function saveCollapsedSections(patientId: string, sections: Set<string>): void {
  try {
    localStorage.setItem(
      getStorageKey(patientId),
      JSON.stringify(Array.from(sections))
    );
  } catch {
    // Ignore storage errors
  }
}

export function usePatientContext({
  patientId,
  encounterId,
  mode,
  pollInterval,
}: UsePatientContextOptions): UsePatientContextReturn {
  const [context, setContext] = useState<PatientContextData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefetching, setIsRefetching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [collapsedSections, setCollapsedSections] = useState<Set<string>>(
    () => loadCollapsedSections(patientId)
  );

  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Determine actual poll interval based on mode
  const effectivePollInterval =
    pollInterval ??
    (mode === 'documentation' ? 30000 : 0);

  // Fetch context data
  const fetchContext = useCallback(
    async (isInitialLoad = false) => {
      if (!patientId) {
        setError('No patient ID provided');
        setIsLoading(false);
        return;
      }

      if (isInitialLoad) {
        setIsLoading(true);
      } else {
        setIsRefetching(true);
      }

      try {
        // Map expanded mode to documentation for API call
        const apiMode = mode === 'expanded' ? 'documentation' : mode;
        const data = await getPatientContext(patientId, encounterId, apiMode);
        setContext(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load context');
      } finally {
        setIsLoading(false);
        setIsRefetching(false);
      }
    },
    [patientId, encounterId, mode]
  );

  // Manual refetch
  const refetch = useCallback(async () => {
    await fetchContext(false);
  }, [fetchContext]);

  // Toggle a section's collapsed state
  const toggleSection = useCallback(
    (sectionId: string) => {
      setCollapsedSections((prev) => {
        const next = new Set(prev);
        if (next.has(sectionId)) {
          next.delete(sectionId);
        } else {
          next.add(sectionId);
        }
        saveCollapsedSections(patientId, next);
        return next;
      });
    },
    [patientId]
  );

  // Expand all sections
  const expandAll = useCallback(() => {
    setCollapsedSections(new Set());
    saveCollapsedSections(patientId, new Set());
  }, [patientId]);

  // Collapse all sections
  const collapseAll = useCallback(() => {
    const allSections = new Set([
      'vitals',
      'medications',
      'allergies',
      'problems',
      'labs',
      'visits',
    ]);
    setCollapsedSections(allSections);
    saveCollapsedSections(patientId, allSections);
  }, [patientId]);

  // Initial fetch
  useEffect(() => {
    fetchContext(true);
  }, [fetchContext]);

  // Polling
  useEffect(() => {
    if (effectivePollInterval > 0) {
      pollIntervalRef.current = setInterval(() => {
        fetchContext(false);
      }, effectivePollInterval);
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    };
  }, [effectivePollInterval, fetchContext]);

  // Load collapsed sections when patient changes
  useEffect(() => {
    setCollapsedSections(loadCollapsedSections(patientId));
  }, [patientId]);

  return {
    context,
    isLoading,
    isRefetching,
    error,
    refetch,
    collapsedSections,
    toggleSection,
    expandAll,
    collapseAll,
    quickSummary: context?.quickSummary ?? null,
  };
}
