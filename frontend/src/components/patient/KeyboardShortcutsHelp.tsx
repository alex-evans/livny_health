import { useEffect, useCallback } from 'react';
import type { ChartSection } from '../../types';

interface KeyboardShortcutsHelpProps {
  sections: ChartSection[];
  onClose: () => void;
}

export function KeyboardShortcutsHelp({
  sections,
  onClose,
}: KeyboardShortcutsHelpProps) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    },
    [onClose]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-deep-ice/50 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-card-hover max-w-md w-full mx-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-frost">
          <h2 className="text-xl font-semibold text-deep-ice">Keyboard Shortcuts</h2>
          <button
            onClick={onClose}
            className="text-text-tertiary hover:text-text-primary transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="px-6 py-4">
          <p className="text-[15px] text-text-secondary mb-4">
            Use these keyboard shortcuts to quickly navigate between chart sections.
          </p>

          <div className="space-y-3">
            {sections.map((section) => (
              <div
                key={section.id}
                className="flex items-center justify-between py-2 border-b border-frost last:border-0"
              >
                <span className="text-[15px] text-text-primary">{section.name}</span>
                <kbd className="inline-flex items-center gap-1 px-2 py-1 bg-frost rounded text-[13px] font-mono text-text-secondary">
                  <span className="text-[11px]">Alt</span>
                  <span>+</span>
                  <span className="font-semibold">{section.keyboardShortcut.key}</span>
                </kbd>
              </div>
            ))}
          </div>
        </div>

        <div className="px-6 py-4 bg-arctic rounded-b-lg">
          <p className="text-[13px] text-text-tertiary">
            Press <kbd className="px-1.5 py-0.5 bg-white rounded text-[11px] font-mono">Esc</kbd> to close this dialog
          </p>
        </div>
      </div>
    </div>
  );
}
