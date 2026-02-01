import { useState, useCallback, useMemo } from 'react';
import type { GuidancePreferences } from '../types/guidance';

const PREFERENCES_KEY = 'guidance_preferences';
const DISMISSED_PREFIX = 'guidance_dismissed_';

const DEFAULT_PREFERENCES: GuidancePreferences = {
  autoShowOnNewNote: true,
  hideGuidanceEntirely: false,
  enableQuickInsert: true,
};

function loadPreferences(): GuidancePreferences {
  try {
    const stored = localStorage.getItem(PREFERENCES_KEY);
    if (stored) {
      return { ...DEFAULT_PREFERENCES, ...JSON.parse(stored) };
    }
  } catch {
    // Ignore parse errors
  }
  return DEFAULT_PREFERENCES;
}

function savePreferences(preferences: GuidancePreferences): void {
  try {
    localStorage.setItem(PREFERENCES_KEY, JSON.stringify(preferences));
  } catch {
    // Ignore storage errors
  }
}

function getDismissedKey(encounterId: string): string {
  return `${DISMISSED_PREFIX}${encounterId}`;
}

function loadDismissedPrompts(encounterId: string): Set<string> {
  try {
    const key = getDismissedKey(encounterId);
    const stored = localStorage.getItem(key);
    if (stored) {
      return new Set(JSON.parse(stored));
    }
  } catch {
    // Ignore parse errors
  }
  return new Set();
}

function saveDismissedPrompts(encounterId: string, prompts: Set<string>): void {
  try {
    const key = getDismissedKey(encounterId);
    localStorage.setItem(key, JSON.stringify(Array.from(prompts)));
  } catch {
    // Ignore storage errors
  }
}

interface UseGuidancePreferencesResult {
  preferences: GuidancePreferences;
  updatePreference: <K extends keyof GuidancePreferences>(
    key: K,
    value: GuidancePreferences[K]
  ) => void;
  dismissPrompt: (promptId: string) => void;
  restorePrompt: (promptId: string) => void;
  getDismissedPrompts: () => Set<string>;
  dismissedPrompts: Set<string>;
}

export function useGuidancePreferences(
  encounterId: string
): UseGuidancePreferencesResult {
  const [preferences, setPreferences] = useState<GuidancePreferences>(loadPreferences);
  const [dismissedPrompts, setDismissedPrompts] = useState<Set<string>>(() =>
    loadDismissedPrompts(encounterId)
  );

  const updatePreference = useCallback(
    <K extends keyof GuidancePreferences>(
      key: K,
      value: GuidancePreferences[K]
    ) => {
      setPreferences((prev) => {
        const updated = { ...prev, [key]: value };
        savePreferences(updated);
        return updated;
      });
    },
    []
  );

  const dismissPrompt = useCallback(
    (promptId: string) => {
      setDismissedPrompts((prev) => {
        const updated = new Set(prev);
        updated.add(promptId);
        saveDismissedPrompts(encounterId, updated);
        return updated;
      });
    },
    [encounterId]
  );

  const restorePrompt = useCallback(
    (promptId: string) => {
      setDismissedPrompts((prev) => {
        const updated = new Set(prev);
        updated.delete(promptId);
        saveDismissedPrompts(encounterId, updated);
        return updated;
      });
    },
    [encounterId]
  );

  const getDismissedPrompts = useCallback(() => dismissedPrompts, [dismissedPrompts]);

  return useMemo(
    () => ({
      preferences,
      updatePreference,
      dismissPrompt,
      restorePrompt,
      getDismissedPrompts,
      dismissedPrompts,
    }),
    [preferences, updatePreference, dismissPrompt, restorePrompt, getDismissedPrompts, dismissedPrompts]
  );
}
