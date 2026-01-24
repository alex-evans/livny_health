import { useState, useEffect, useCallback } from 'react';
import type { ChartSection, ChartSectionId } from '../types';
import { getChartSections } from '../api';

interface UseChartNavigationOptions {
  patientId: string | undefined;
  initialSection?: ChartSectionId;
}

interface UseChartNavigationReturn {
  sections: ChartSection[];
  activeSection: ChartSectionId;
  setActiveSection: (sectionId: ChartSectionId) => void;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useChartNavigation({
  patientId,
  initialSection = 'visits',
}: UseChartNavigationOptions): UseChartNavigationReturn {
  const [sections, setSections] = useState<ChartSection[]>([]);
  const [activeSection, setActiveSectionState] = useState<ChartSectionId>(initialSection);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSections = useCallback(async () => {
    if (!patientId) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await getChartSections(patientId);
      setSections(response.sections);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load chart sections');
    } finally {
      setIsLoading(false);
    }
  }, [patientId]);

  // Fetch sections on mount and when patient changes
  useEffect(() => {
    fetchSections();
  }, [fetchSections]);

  // Read initial section from URL hash on mount
  useEffect(() => {
    const hash = window.location.hash.slice(1); // Remove #
    if (hash && isValidSection(hash)) {
      setActiveSectionState(hash as ChartSectionId);
    }
  }, []);

  // Update URL hash when active section changes
  const setActiveSection = useCallback((sectionId: ChartSectionId) => {
    setActiveSectionState(sectionId);
    // Update URL hash without triggering navigation
    window.history.replaceState(null, '', `#${sectionId}`);
  }, []);

  return {
    sections,
    activeSection,
    setActiveSection,
    isLoading,
    error,
    refetch: fetchSections,
  };
}

function isValidSection(section: string): section is ChartSectionId {
  const validSections: ChartSectionId[] = [
    'visits',
    'medications',
    'allergies',
    'labs',
    'problems',
    'vitals',
    'imaging',
    'social-family',
  ];
  return validSections.includes(section as ChartSectionId);
}
