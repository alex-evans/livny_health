import { useRef, useCallback, forwardRef, useImperativeHandle } from 'react';
import { cn } from '../../utils/cn';
import { SaveIndicator } from './SaveIndicator';
import { useAutoSave } from '../../hooks/useAutoSave';
import { useEncounterKeyboardShortcuts } from '../../hooks/useEncounterKeyboardShortcuts';

interface NoteComposerProps {
  encounterId: string;
  initialContent: string;
  initialVersion: number;
  isExpanded: boolean;
  isMinimized: boolean;
  onToggleExpand: () => void;
  onToggleMinimize: () => void;
  onConflict?: (serverContent: string, serverVersion: number) => void;
  readOnly?: boolean;
  className?: string;
}

export interface NoteComposerRef {
  save: () => Promise<void>;
  getContent: () => string;
  isDirty: () => boolean;
}

export const NoteComposer = forwardRef<NoteComposerRef, NoteComposerProps>(
  function NoteComposer(
    {
      encounterId,
      initialContent,
      initialVersion,
      isExpanded,
      isMinimized,
      onToggleExpand,
      onToggleMinimize,
      onConflict,
      readOnly = false,
      className,
    },
    ref
  ) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const {
      content,
      setContent,
      version,
      wordCount,
      saveStatus,
      lastSavedAt,
      error,
      conflictData,
      save,
      isDirty,
    } = useAutoSave({
      encounterId,
      initialContent,
      initialVersion,
      debounceMs: 5000,
      enabled: !readOnly,
    });

    // Notify parent of conflict
    if (conflictData && onConflict) {
      onConflict(conflictData.serverContent, conflictData.serverVersion);
    }

    const handleExpand = useCallback(() => {
      if (isMinimized) {
        onToggleMinimize(); // Restore from minimized first
      } else if (!isExpanded) {
        onToggleExpand();
      }
    }, [isExpanded, isMinimized, onToggleExpand, onToggleMinimize]);

    const handleCollapse = useCallback(() => {
      if (isExpanded) onToggleExpand();
    }, [isExpanded, onToggleExpand]);

    const handleSave = useCallback(() => {
      save('manual');
    }, [save]);

    useEncounterKeyboardShortcuts({
      noteTextareaRef: textareaRef,
      onExpand: handleExpand,
      onCollapse: handleCollapse,
      onSave: handleSave,
      enabled: true,
    });

    // Expose methods via ref
    useImperativeHandle(ref, () => ({
      save: async () => {
        await save('manual');
      },
      getContent: () => content,
      isDirty: () => isDirty,
    }));

    const handleChange = useCallback(
      (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setContent(e.target.value);
      },
      [setContent]
    );

    const handleRetry = useCallback(() => {
      save('manual');
    }, [save]);

    return (
      <div
        className={cn(
          'bg-white border-t border-frost transition-all duration-200',
          isMinimized ? 'h-[48px]' : isExpanded ? 'h-[400px]' : 'h-[180px]',
          className
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-comfortable py-tight border-b border-frost">
          <div className="flex items-center gap-3">
            <h3 className="text-[15px] font-medium text-text-primary">
              Clinical Note
            </h3>
            <span className="text-[13px] text-text-tertiary">
              v{version}
            </span>
            {isMinimized && wordCount > 0 && (
              <span className="text-[13px] text-text-tertiary">
                {wordCount} words
              </span>
            )}
          </div>

          <div className="flex items-center gap-4">
            {!isMinimized && (
              <SaveIndicator
                status={saveStatus}
                lastSavedAt={lastSavedAt}
                wordCount={wordCount}
                error={error}
                onRetry={handleRetry}
              />
            )}

            <div className="flex items-center gap-1">
              {/* Minimize/Restore button */}
              <button
                onClick={onToggleMinimize}
                className="p-2 text-text-secondary hover:text-text-primary hover:bg-frost/50 rounded transition-colors"
                aria-label={isMinimized ? 'Restore note' : 'Minimize note'}
                title={isMinimized ? 'Restore note' : 'Minimize note'}
              >
                {isMinimized ? (
                  <RestoreIcon className="w-5 h-5" />
                ) : (
                  <MinimizeIcon className="w-5 h-5" />
                )}
              </button>

              {/* Expand/Collapse button - only show when not minimized */}
              {!isMinimized && (
                <button
                  onClick={onToggleExpand}
                  className="p-2 text-text-secondary hover:text-text-primary hover:bg-frost/50 rounded transition-colors"
                  aria-label={isExpanded ? 'Collapse note' : 'Expand note'}
                  title={isExpanded ? 'Collapse note' : 'Expand note'}
                >
                  {isExpanded ? (
                    <ChevronDownIcon className="w-5 h-5" />
                  ) : (
                    <ChevronUpIcon className="w-5 h-5" />
                  )}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Textarea - hidden when minimized */}
        {!isMinimized && (
          <div className="h-[calc(100%-48px)] p-comfortable">
            <textarea
              ref={textareaRef}
              value={content}
              onChange={handleChange}
              readOnly={readOnly}
              placeholder={readOnly ? '' : 'Document the visit here. Start with the subjective findings, then objective, assessment, and plan...'}
              className={cn(
                'w-full h-full resize-none bg-transparent',
                'text-[15px] leading-relaxed text-text-primary',
                'placeholder:text-text-tertiary',
                'focus:outline-none',
                'font-normal',
                readOnly && 'text-text-secondary cursor-default'
              )}
              aria-label="Clinical note"
            />
          </div>
        )}
      </div>
    );
  }
);

// Simple chevron icons
function ChevronUpIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 15l7-7 7 7" />
    </svg>
  );
}

function ChevronDownIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
    </svg>
  );
}

function MinimizeIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M18 12H6" />
    </svg>
  );
}

function RestoreIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
    </svg>
  );
}
