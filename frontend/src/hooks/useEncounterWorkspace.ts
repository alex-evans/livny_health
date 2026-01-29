import { useState, useEffect, useCallback } from 'react';
import {
  createEncounter,
  getEncounterByAppointment,
  transitionEncounterStatus,
  createAddendum,
} from '../api/encounterApi';
import type {
  EncounterNote,
  EncounterContext,
  EncounterWorkspaceMode,
  EncounterStatus,
} from '../types';

interface UseEncounterWorkspaceOptions {
  patientId: string;
  appointmentId?: string | null;
  providerId?: string;
  providerName?: string;
}

interface UseEncounterWorkspaceReturn {
  // State
  encounter: EncounterNote | null;
  context: EncounterContext | null;
  mode: EncounterWorkspaceMode;
  isNoteEditable: boolean;
  isLoading: boolean;
  error: string | null;
  isTransitioning: boolean;

  // Actions
  startEncounter: (chiefComplaint?: string) => Promise<void>;
  completeEncounter: () => Promise<void>;
  signEncounter: () => Promise<void>;
  reopenEncounter: (reason: string) => Promise<void>;
  addAddendum: (content: string, reason: string) => Promise<void>;
  refreshEncounter: () => Promise<void>;
}

function getWorkspaceMode(status: EncounterStatus | undefined): EncounterWorkspaceMode {
  switch (status) {
    case 'in_progress':
      return 'documentation';
    case 'completed':
      return 'completed';
    case 'signed':
      return 'signed';
    case 'scheduled':
    default:
      return 'review';
  }
}

export function useEncounterWorkspace({
  patientId,
  appointmentId,
  providerId = 'provider-001',
  providerName = 'Dr. Elizabeth Frost',
}: UseEncounterWorkspaceOptions): UseEncounterWorkspaceReturn {
  const [encounter, setEncounter] = useState<EncounterNote | null>(null);
  const [context, setContext] = useState<EncounterContext | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isTransitioning, setIsTransitioning] = useState(false);

  // Compute derived state
  const mode = getWorkspaceMode(encounter?.status);
  const isNoteEditable = mode === 'documentation';

  // Fetch existing encounter for appointment
  const refreshEncounter = useCallback(async () => {
    if (!appointmentId) {
      setEncounter(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await getEncounterByAppointment(appointmentId);
      if (result.encounter) {
        setEncounter(result.encounter);
      } else {
        setEncounter(null);
      }
    } catch (err) {
      console.error('Failed to fetch encounter:', err);
      setError(err instanceof Error ? err.message : 'Failed to load encounter');
    } finally {
      setIsLoading(false);
    }
  }, [appointmentId]);

  // Load encounter on mount or when appointmentId changes
  useEffect(() => {
    refreshEncounter();
  }, [refreshEncounter]);

  // Start a new encounter (transition from scheduled to in_progress)
  const startEncounter = useCallback(
    async (chiefComplaint?: string) => {
      setIsTransitioning(true);
      setError(null);

      try {
        // If no encounter exists yet, create one
        if (!encounter) {
          const result = await createEncounter(patientId, {
            providerId,
            encounterType: 'Office Visit',
            chiefComplaint,
          });
          setEncounter(result.encounter);
          setContext(result.context);
          return;
        }

        // If encounter exists but is scheduled, transition to in_progress
        if (encounter.status === 'scheduled') {
          const result = await transitionEncounterStatus(
            encounter.id,
            'in_progress',
            undefined,
            providerId,
            providerName
          );
          setEncounter((prev) =>
            prev
              ? {
                  ...prev,
                  status: result.newStatus,
                  openedAt: result.transitionedAt,
                }
              : null
          );
        }
      } catch (err) {
        console.error('Failed to start encounter:', err);
        setError(err instanceof Error ? err.message : 'Failed to start encounter');
      } finally {
        setIsTransitioning(false);
      }
    },
    [encounter, patientId, providerId, providerName]
  );

  // Complete encounter (soft lock)
  const completeEncounter = useCallback(async () => {
    if (!encounter || encounter.status !== 'in_progress') return;

    setIsTransitioning(true);
    setError(null);

    try {
      const result = await transitionEncounterStatus(
        encounter.id,
        'completed',
        undefined,
        providerId,
        providerName
      );
      setEncounter((prev) =>
        prev
          ? {
              ...prev,
              status: result.newStatus,
              completedAt: result.transitionedAt,
            }
          : null
      );
    } catch (err) {
      console.error('Failed to complete encounter:', err);
      setError(err instanceof Error ? err.message : 'Failed to complete encounter');
    } finally {
      setIsTransitioning(false);
    }
  }, [encounter, providerId, providerName]);

  // Sign encounter (hard lock)
  const signEncounter = useCallback(async () => {
    if (!encounter || (encounter.status !== 'in_progress' && encounter.status !== 'completed')) {
      return;
    }

    setIsTransitioning(true);
    setError(null);

    try {
      const result = await transitionEncounterStatus(
        encounter.id,
        'signed',
        undefined,
        providerId,
        providerName
      );
      setEncounter((prev) =>
        prev
          ? {
              ...prev,
              status: result.newStatus,
              signedAt: result.transitionedAt,
              signedByName: result.signedByName || providerName,
            }
          : null
      );
    } catch (err) {
      console.error('Failed to sign encounter:', err);
      setError(err instanceof Error ? err.message : 'Failed to sign encounter');
    } finally {
      setIsTransitioning(false);
    }
  }, [encounter, providerId, providerName]);

  // Reopen encounter (from completed back to in_progress)
  const reopenEncounter = useCallback(
    async (reason: string) => {
      if (!encounter || encounter.status !== 'completed') return;

      setIsTransitioning(true);
      setError(null);

      try {
        const result = await transitionEncounterStatus(
          encounter.id,
          'in_progress',
          reason,
          providerId,
          providerName
        );
        setEncounter((prev) =>
          prev
            ? {
                ...prev,
                status: result.newStatus,
                reopenedAt: result.transitionedAt,
              }
            : null
        );
      } catch (err) {
        console.error('Failed to reopen encounter:', err);
        setError(err instanceof Error ? err.message : 'Failed to reopen encounter');
      } finally {
        setIsTransitioning(false);
      }
    },
    [encounter, providerId, providerName]
  );

  // Add addendum to signed encounter
  const addAddendum = useCallback(
    async (content: string, reason: string) => {
      if (!encounter || encounter.status !== 'signed') return;

      setIsTransitioning(true);
      setError(null);

      try {
        await createAddendum(encounter.id, {
          content,
          reason,
          userId: providerId,
          userName: providerName,
        });
        // Refresh to get updated encounter with addendum
        await refreshEncounter();
      } catch (err) {
        console.error('Failed to add addendum:', err);
        setError(err instanceof Error ? err.message : 'Failed to add addendum');
      } finally {
        setIsTransitioning(false);
      }
    },
    [encounter, providerId, providerName, refreshEncounter]
  );

  return {
    encounter,
    context,
    mode,
    isNoteEditable,
    isLoading,
    error,
    isTransitioning,
    startEncounter,
    completeEncounter,
    signEncounter,
    reopenEncounter,
    addAddendum,
    refreshEncounter,
  };
}
