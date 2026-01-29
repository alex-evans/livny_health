import { useEffect, useCallback } from 'react';
import type { RefObject } from 'react';

interface UseEncounterKeyboardShortcutsOptions {
  noteTextareaRef: RefObject<HTMLTextAreaElement | null>;
  onExpand?: () => void;
  onCollapse?: () => void;
  onSave?: () => void;
  enabled?: boolean;
}

export function useEncounterKeyboardShortcuts({
  noteTextareaRef,
  onExpand,
  onCollapse,
  onSave,
  enabled = true,
}: UseEncounterKeyboardShortcutsOptions): void {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
      const isCtrlOrCmd = isMac ? event.metaKey : event.ctrlKey;

      // Ctrl/Cmd+N: Focus note textarea
      if (isCtrlOrCmd && event.key.toLowerCase() === 'n') {
        event.preventDefault();
        noteTextareaRef.current?.focus();
        return;
      }

      // Ctrl/Cmd+S: Manual save
      if (isCtrlOrCmd && event.key.toLowerCase() === 's') {
        event.preventDefault();
        onSave?.();
        return;
      }

      // Ctrl/Cmd+Up Arrow: Expand note area
      if (isCtrlOrCmd && event.key === 'ArrowUp') {
        event.preventDefault();
        onExpand?.();
        return;
      }

      // Ctrl/Cmd+Down Arrow: Collapse note area
      if (isCtrlOrCmd && event.key === 'ArrowDown') {
        event.preventDefault();
        onCollapse?.();
        return;
      }

      // Escape: Unfocus note
      if (event.key === 'Escape') {
        if (document.activeElement === noteTextareaRef.current) {
          event.preventDefault();
          noteTextareaRef.current?.blur();
        }
        return;
      }
    },
    [enabled, noteTextareaRef, onExpand, onCollapse, onSave]
  );

  useEffect(() => {
    if (!enabled) return;

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [enabled, handleKeyDown]);
}
