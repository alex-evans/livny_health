import { useState, useEffect, useCallback, useRef } from 'react';
import { useDebounce } from './useDebounce';
import {
  saveEncounterNote,
  VersionConflictException,
} from '../api/encounterApi';

export type SaveStatus = 'idle' | 'saving' | 'saved' | 'error' | 'conflict';

interface UseAutoSaveOptions {
  encounterId: string;
  initialContent: string;
  initialVersion: number;
  debounceMs?: number;
  enabled?: boolean;
}

interface UseAutoSaveReturn {
  content: string;
  setContent: (content: string) => void;
  version: number;
  wordCount: number;
  saveStatus: SaveStatus;
  lastSavedAt: Date | null;
  error: string | null;
  conflictData: {
    serverContent: string;
    serverVersion: number;
  } | null;
  save: (saveType?: 'auto' | 'manual') => Promise<void>;
  resolveConflict: (useServerContent: boolean) => void;
  isDirty: boolean;
}

const DRAFT_KEY_PREFIX = 'encounter_draft_';

function countWords(text: string): number {
  if (!text.trim()) return 0;
  return text.trim().split(/\s+/).length;
}

function saveDraft(encounterId: string, content: string, version: number): void {
  try {
    localStorage.setItem(
      `${DRAFT_KEY_PREFIX}${encounterId}`,
      JSON.stringify({
        content,
        version,
        timestamp: Date.now(),
      })
    );
  } catch {
    // localStorage might be full or unavailable
  }
}

function loadDraft(
  encounterId: string
): { content: string; version: number; timestamp: number } | null {
  try {
    const stored = localStorage.getItem(`${DRAFT_KEY_PREFIX}${encounterId}`);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch {
    // Invalid JSON or localStorage unavailable
  }
  return null;
}

function clearDraft(encounterId: string): void {
  try {
    localStorage.removeItem(`${DRAFT_KEY_PREFIX}${encounterId}`);
  } catch {
    // localStorage might be unavailable
  }
}

export function useAutoSave({
  encounterId,
  initialContent,
  initialVersion,
  debounceMs = 5000,
  enabled = true,
}: UseAutoSaveOptions): UseAutoSaveReturn {
  const [content, setContentState] = useState(initialContent);
  const [version, setVersion] = useState(initialVersion);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [conflictData, setConflictData] = useState<{
    serverContent: string;
    serverVersion: number;
  } | null>(null);
  const [savedContent, setSavedContent] = useState(initialContent);

  const debouncedContent = useDebounce(content, debounceMs);
  const isSavingRef = useRef(false);

  // Check for draft on mount
  useEffect(() => {
    const draft = loadDraft(encounterId);
    if (draft && draft.timestamp > Date.now() - 24 * 60 * 60 * 1000) {
      // Draft is less than 24 hours old
      if (draft.version === initialVersion && draft.content !== initialContent) {
        // There's a local draft that differs from server
        setContentState(draft.content);
      }
    }
  }, [encounterId, initialContent, initialVersion]);

  const save = useCallback(
    async (saveType: 'auto' | 'manual' = 'auto') => {
      if (isSavingRef.current) return;
      if (content === savedContent) return; // No changes to save

      isSavingRef.current = true;
      setSaveStatus('saving');
      setError(null);

      try {
        const result = await saveEncounterNote(encounterId, {
          content,
          expectedVersion: version,
          saveType,
        });

        setVersion(result.version);
        setSavedContent(content);
        setSaveStatus('saved');
        setLastSavedAt(new Date(result.savedAt));
        clearDraft(encounterId);
      } catch (err) {
        if (err instanceof VersionConflictException) {
          setSaveStatus('conflict');
          setConflictData({
            serverContent: err.serverContent,
            serverVersion: err.currentVersion,
          });
        } else {
          setSaveStatus('error');
          setError(err instanceof Error ? err.message : 'Failed to save');
        }
      } finally {
        isSavingRef.current = false;
      }
    },
    [content, savedContent, encounterId, version]
  );

  // Auto-save on debounced content change
  useEffect(() => {
    if (!enabled) return;
    if (debouncedContent === savedContent) return;
    if (saveStatus === 'conflict') return;

    // Save draft locally first
    saveDraft(encounterId, debouncedContent, version);

    // Then save to server
    save('auto');
  }, [debouncedContent, savedContent, enabled, encounterId, version, save, saveStatus]);

  const setContent = useCallback(
    (newContent: string) => {
      setContentState(newContent);
      if (saveStatus === 'saved' || saveStatus === 'idle') {
        setSaveStatus('idle');
      }
    },
    [saveStatus]
  );

  const resolveConflict = useCallback(
    (useServerContent: boolean) => {
      if (!conflictData) return;

      if (useServerContent) {
        setContentState(conflictData.serverContent);
        setSavedContent(conflictData.serverContent);
      }
      // In both cases, update to server version
      setVersion(conflictData.serverVersion);
      setConflictData(null);
      setSaveStatus('idle');
      clearDraft(encounterId);
    },
    [conflictData, encounterId]
  );

  const wordCount = countWords(content);
  const isDirty = content !== savedContent;

  return {
    content,
    setContent,
    version,
    wordCount,
    saveStatus,
    lastSavedAt,
    error,
    conflictData,
    save,
    resolveConflict,
    isDirty,
  };
}
