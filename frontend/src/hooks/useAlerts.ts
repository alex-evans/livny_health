/**
 * useAlerts Hook
 *
 * Hook for fetching and managing clinical alerts for a patient.
 */

import { useState, useEffect, useCallback } from 'react';
import { getPatientAlerts, acknowledgeAlert, dismissAlert } from '../api/alertApi';
import type { ClinicalAlert, AlertSummary, AlertStatus } from '../types';

interface UseAlertsOptions {
  patientId: string;
  status?: AlertStatus | 'all';
  autoRefresh?: boolean;
  refreshInterval?: number; // in milliseconds
}

interface UseAlertsReturn {
  alerts: ClinicalAlert[];
  summary: AlertSummary;
  isLoading: boolean;
  error: Error | null;
  acknowledge: (alertId: string, note?: string) => Promise<void>;
  dismiss: (alertId: string, reason?: string) => Promise<void>;
  refetch: () => Promise<void>;
}

const EMPTY_SUMMARY: AlertSummary = {
  criticalCount: 0,
  highCount: 0,
  mediumCount: 0,
  totalActive: 0,
};

export function useAlerts({
  patientId,
  status = 'active',
  autoRefresh = false,
  refreshInterval = 60000, // 1 minute default
}: UseAlertsOptions): UseAlertsReturn {
  const [alerts, setAlerts] = useState<ClinicalAlert[]>([]);
  const [summary, setSummary] = useState<AlertSummary>(EMPTY_SUMMARY);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchAlerts = useCallback(async () => {
    if (!patientId) {
      setAlerts([]);
      setSummary(EMPTY_SUMMARY);
      setIsLoading(false);
      return;
    }

    try {
      setError(null);
      const response = await getPatientAlerts(patientId, { status });
      setAlerts(response.alerts);
      setSummary(response.summary);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch alerts'));
      setAlerts([]);
      setSummary(EMPTY_SUMMARY);
    } finally {
      setIsLoading(false);
    }
  }, [patientId, status]);

  // Initial fetch
  useEffect(() => {
    setIsLoading(true);
    fetchAlerts();
  }, [fetchAlerts]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh || !patientId) {
      return;
    }

    const intervalId = setInterval(fetchAlerts, refreshInterval);
    return () => clearInterval(intervalId);
  }, [autoRefresh, refreshInterval, fetchAlerts, patientId]);

  const acknowledge = useCallback(
    async (alertId: string, note?: string) => {
      try {
        // Use a mock provider ID for now
        await acknowledgeAlert(patientId, alertId, {
          by: 'current-provider',
          note,
        });
        // Refetch to update the list
        await fetchAlerts();
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to acknowledge alert'));
        throw err;
      }
    },
    [patientId, fetchAlerts]
  );

  const dismiss = useCallback(
    async (alertId: string, reason?: string) => {
      try {
        // Use a mock provider ID for now
        await dismissAlert(patientId, alertId, {
          by: 'current-provider',
          reason,
        });
        // Refetch to update the list
        await fetchAlerts();
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to dismiss alert'));
        throw err;
      }
    },
    [patientId, fetchAlerts]
  );

  return {
    alerts,
    summary,
    isLoading,
    error,
    acknowledge,
    dismiss,
    refetch: fetchAlerts,
  };
}
