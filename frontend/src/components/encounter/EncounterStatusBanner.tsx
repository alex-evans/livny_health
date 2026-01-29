import { cn } from '../../utils/cn';
import type { EncounterStatus } from '../../types';

interface EncounterStatusBannerProps {
  status: EncounterStatus;
  signedByName?: string | null;
  signedAt?: string | null;
  onReopen?: () => void;
  onSign?: () => void;
  onAddAddendum?: () => void;
  onViewAudit?: () => void;
  isLoading?: boolean;
  className?: string;
}

function formatDateTime(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
}

export function EncounterStatusBanner({
  status,
  signedByName,
  signedAt,
  onReopen,
  onSign,
  onAddAddendum,
  onViewAudit,
  isLoading = false,
  className,
}: EncounterStatusBannerProps) {
  // Don't show banner for in_progress or scheduled - those are the "normal" editing states
  if (status === 'in_progress' || status === 'scheduled') {
    return null;
  }

  const isCompleted = status === 'completed';
  const isSigned = status === 'signed';

  return (
    <div
      className={cn(
        'px-comfortable py-normal border-b',
        isCompleted && 'bg-[#FEF5E7] border-warning/30',
        isSigned && 'bg-[#E8F6EF] border-success/30',
        className
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {isCompleted && (
            <>
              <div className="w-2 h-2 rounded-full bg-warning" />
              <div>
                <p className="text-[15px] font-medium text-text-primary">
                  Encounter Completed
                </p>
                <p className="text-[13px] text-text-secondary">
                  Reopen to make changes or sign to finalize
                </p>
              </div>
            </>
          )}
          {isSigned && (
            <>
              <div className="w-2 h-2 rounded-full bg-success" />
              <div>
                <p className="text-[15px] font-medium text-text-primary">
                  This encounter is signed
                </p>
                {signedByName && signedAt && (
                  <p className="text-[13px] text-text-secondary">
                    Signed by {signedByName} on {formatDateTime(signedAt)}
                  </p>
                )}
              </div>
            </>
          )}
        </div>

        <div className="flex items-center gap-2">
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
            <>
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
              <button
                onClick={onViewAudit}
                disabled={isLoading}
                className={cn(
                  'px-4 py-2 text-[13px] font-medium rounded-md transition-colors',
                  'border border-arctic text-text-primary',
                  'hover:bg-frost',
                  'disabled:opacity-50 disabled:cursor-not-allowed'
                )}
              >
                View Audit Trail
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
