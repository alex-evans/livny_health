import { useState, useCallback, useEffect, useRef } from 'react';
import { getPatient } from '../api';
import type { Patient, ActiveMedication } from '../types';

interface UseMedicationFreshnessOptions {
  /** Poll interval in milliseconds. Set to 0 to disable polling. Default: 0 (disabled) */
  pollInterval?: number;
  /** Whether polling is enabled. Default: false */
  enablePolling?: boolean;
}

interface UseMedicationFreshnessResult {
  /** The patient data including active medications */
  patient: Patient | null;
  /** Whether the initial load is in progress */
  isLoading: boolean;
  /** Whether a refetch is currently in progress */
  isRefetching: boolean;
  /** Error message if fetch failed */
  error: string | null;
  /** Timestamp of when medications were last successfully fetched */
  lastUpdated: Date | null;
  /** Manually trigger a refetch of medications */
  refetch: () => Promise<void>;
  /** Update patient data locally (for optimistic updates) */
  updatePatient: (updater: (prev: Patient | null) => Patient | null) => void;
  /** Add new medications to the list (for optimistic updates after prescription) */
  addMedications: (medications: ActiveMedication[]) => void;
  /** Remove a medication by ID (for discontinuation) */
  removeMedication: (medicationId: string) => void;
  /** Time since last update in human-readable format */
  timeSinceUpdate: string | null;
}

function formatTimeSinceUpdate(lastUpdated: Date | null): string | null {
  if (!lastUpdated) return null;

  const now = new Date();
  const diffMs = now.getTime() - lastUpdated.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);

  if (diffSeconds < 10) {
    return 'Just now';
  } else if (diffSeconds < 60) {
    return `${diffSeconds} seconds ago`;
  } else if (diffMinutes < 60) {
    return diffMinutes === 1 ? '1 minute ago' : `${diffMinutes} minutes ago`;
  } else {
    return diffHours === 1 ? '1 hour ago' : `${diffHours} hours ago`;
  }
}

export function useMedicationFreshness(
  patientId: string | undefined,
  options: UseMedicationFreshnessOptions = {}
): UseMedicationFreshnessResult {
  const { pollInterval = 0, enablePolling = false } = options;

  const [patient, setPatient] = useState<Patient | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefetching, setIsRefetching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [timeSinceUpdate, setTimeSinceUpdate] = useState<string | null>(null);

  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const timeUpdateIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Fetch patient data
  const fetchPatient = useCallback(async (isInitialLoad = false) => {
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
      const patientData = await getPatient(patientId);
      setPatient(patientData);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load patient');
    } finally {
      setIsLoading(false);
      setIsRefetching(false);
    }
  }, [patientId]);

  // Manual refetch function
  const refetch = useCallback(async () => {
    await fetchPatient(false);
  }, [fetchPatient]);

  // Update patient data locally (for optimistic updates)
  const updatePatient = useCallback((updater: (prev: Patient | null) => Patient | null) => {
    setPatient(updater);
    setLastUpdated(new Date());
  }, []);

  // Add new medications (optimistic update after prescription)
  const addMedications = useCallback((medications: ActiveMedication[]) => {
    setPatient((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        activeMedications: [...(prev.activeMedications || []), ...medications],
      };
    });
    setLastUpdated(new Date());
  }, []);

  // Remove a medication by ID (for discontinuation)
  const removeMedication = useCallback((medicationId: string) => {
    setPatient((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        activeMedications: (prev.activeMedications || []).filter(
          (med) => med.id !== medicationId
        ),
      };
    });
    setLastUpdated(new Date());
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchPatient(true);
  }, [fetchPatient]);

  // Polling interval
  useEffect(() => {
    if (enablePolling && pollInterval > 0) {
      pollIntervalRef.current = setInterval(() => {
        fetchPatient(false);
      }, pollInterval);
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    };
  }, [enablePolling, pollInterval, fetchPatient]);

  // Update "time since update" every 10 seconds
  useEffect(() => {
    const updateTimeSince = () => {
      setTimeSinceUpdate(formatTimeSinceUpdate(lastUpdated));
    };

    updateTimeSince();
    timeUpdateIntervalRef.current = setInterval(updateTimeSince, 10000);

    return () => {
      if (timeUpdateIntervalRef.current) {
        clearInterval(timeUpdateIntervalRef.current);
        timeUpdateIntervalRef.current = null;
      }
    };
  }, [lastUpdated]);

  return {
    patient,
    isLoading,
    isRefetching,
    error,
    lastUpdated,
    refetch,
    updatePatient,
    addMedications,
    removeMedication,
    timeSinceUpdate,
  };
}
