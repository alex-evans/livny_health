import { useEffect, useCallback } from 'react';
import type { ChartSectionId, KeyboardShortcut } from '../types';

interface ShortcutConfig {
  shortcut: KeyboardShortcut;
  sectionId: ChartSectionId;
}

interface UseKeyboardShortcutsOptions {
  shortcuts: ShortcutConfig[];
  onNavigate: (sectionId: ChartSectionId) => void;
  enabled?: boolean;
}

export function useKeyboardShortcuts({
  shortcuts,
  onNavigate,
  enabled = true,
}: UseKeyboardShortcutsOptions): void {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      // Skip if user is typing in an input, textarea, or contenteditable
      const target = event.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        return;
      }

      // Check if Alt key is pressed
      if (!event.altKey) return;

      // Find matching shortcut
      const pressedKey = event.key.toUpperCase();
      const matchingShortcut = shortcuts.find(
        (config) =>
          config.shortcut.key.toUpperCase() === pressedKey &&
          config.shortcut.modifier === 'Alt'
      );

      if (matchingShortcut) {
        event.preventDefault();
        onNavigate(matchingShortcut.sectionId);
      }
    },
    [shortcuts, onNavigate, enabled]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);
}
