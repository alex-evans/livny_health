import { cn } from '../../utils/cn';
import type { SaveStatus } from '../../hooks/useAutoSave';

interface SaveIndicatorProps {
  status: SaveStatus;
  lastSavedAt: Date | null;
  wordCount: number;
  error?: string | null;
  onRetry?: () => void;
  className?: string;
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  });
}

export function SaveIndicator({
  status,
  lastSavedAt,
  wordCount,
  error,
  onRetry,
  className,
}: SaveIndicatorProps) {
  return (
    <div
      className={cn(
        'flex items-center gap-3 text-[13px]',
        className
      )}
    >
      {/* Word count */}
      <span className="text-text-tertiary">
        {wordCount} {wordCount === 1 ? 'word' : 'words'}
      </span>

      {/* Divider */}
      <span className="text-text-tertiary">|</span>

      {/* Save status */}
      <div className="flex items-center gap-2">
        {status === 'idle' && lastSavedAt && (
          <>
            <span className="w-2 h-2 rounded-full bg-text-tertiary" />
            <span className="text-text-tertiary">
              Saved at {formatTime(lastSavedAt)}
            </span>
          </>
        )}

        {status === 'idle' && !lastSavedAt && (
          <span className="text-text-tertiary">Not saved yet</span>
        )}

        {status === 'saving' && (
          <>
            <span className="w-2 h-2 rounded-full bg-glacier-blue animate-pulse" />
            <span className="text-text-secondary">Saving...</span>
          </>
        )}

        {status === 'saved' && (
          <>
            <span className="w-2 h-2 rounded-full bg-status-normal" />
            <span className="text-status-normal">Saved</span>
          </>
        )}

        {status === 'error' && (
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-status-critical" />
            <span className="text-status-critical">
              {error || 'Save failed'}
            </span>
            {onRetry && (
              <button
                onClick={onRetry}
                className="text-glacier-blue hover:underline"
              >
                Retry
              </button>
            )}
          </div>
        )}

        {status === 'conflict' && (
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-status-abnormal" />
            <span className="text-status-abnormal">Conflict detected</span>
          </div>
        )}
      </div>
    </div>
  );
}
