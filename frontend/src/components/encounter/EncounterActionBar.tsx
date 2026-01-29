import { cn } from '../../utils/cn';
import type { EncounterStatus } from '../../types';

interface EncounterActionBarProps {
  status: EncounterStatus;
  onComplete?: () => void;
  onSign?: () => void;
  onReopen?: () => void;
  onAddAddendum?: () => void;
  isLoading?: boolean;
  className?: string;
}

export function EncounterActionBar({
  status,
  onComplete,
  onSign,
  onReopen,
  onAddAddendum,
  isLoading = false,
  className,
}: EncounterActionBarProps) {
  const isInProgress = status === 'in_progress';
  const isCompleted = status === 'completed';
  const isSigned = status === 'signed';

  // Scheduled encounters show "Start Visit" which is handled elsewhere
  if (status === 'scheduled') {
    return null;
  }

  return (
    <div
      className={cn(
        'flex items-center justify-end gap-2 px-comfortable py-tight',
        'border-t border-frost bg-white',
        className
      )}
    >
      {isInProgress && (
        <>
          <button
            onClick={onComplete}
            disabled={isLoading}
            className={cn(
              'px-4 py-2 text-[13px] font-medium rounded-md transition-colors',
              'border border-arctic text-text-primary',
              'hover:bg-frost',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            Complete Encounter
          </button>
          <button
            onClick={onSign}
            disabled={isLoading}
            className={cn(
              'px-4 py-2 text-[13px] font-medium rounded-md transition-colors',
              'bg-glacier-blue text-white',
              'hover:bg-deep-ice',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            Sign Note
          </button>
        </>
      )}
      {isCompleted && (
        <>
          <button
            onClick={onReopen}
            disabled={isLoading}
            className={cn(
              'px-4 py-2 text-[13px] font-medium rounded-md transition-colors',
              'border border-arctic text-text-primary',
              'hover:bg-frost',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            Reopen Encounter
          </button>
          <button
            onClick={onSign}
            disabled={isLoading}
            className={cn(
              'px-4 py-2 text-[13px] font-medium rounded-md transition-colors',
              'bg-glacier-blue text-white',
              'hover:bg-deep-ice',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            Sign Note
          </button>
        </>
      )}
      {isSigned && (
        <button
          onClick={onAddAddendum}
          disabled={isLoading}
          className={cn(
            'px-4 py-2 text-[13px] font-medium rounded-md transition-colors',
            'bg-glacier-blue text-white',
            'hover:bg-deep-ice',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        >
          Add Addendum
        </button>
      )}
    </div>
  );
}
