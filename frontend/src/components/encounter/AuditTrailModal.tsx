import { cn } from '../../utils/cn';
import type { StatusAuditEntry, EncounterStatus } from '../../types';

interface AuditTrailModalProps {
  isOpen: boolean;
  entries: StatusAuditEntry[];
  isLoading?: boolean;
  onClose: () => void;
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

function getStatusLabel(status: EncounterStatus | null): string {
  if (!status) return 'Created';
  const labels: Record<EncounterStatus, string> = {
    scheduled: 'Scheduled',
    in_progress: 'In Progress',
    completed: 'Completed',
    signed: 'Signed',
  };
  return labels[status] || status;
}

function getStatusColor(status: EncounterStatus | null): string {
  if (!status) return 'bg-frost text-text-secondary';
  const colors: Record<EncounterStatus, string> = {
    scheduled: 'bg-arctic text-deep-ice',
    in_progress: 'bg-glacier-blue/10 text-glacier-blue',
    completed: 'bg-[#FEF5E7] text-warning',
    signed: 'bg-[#E8F6EF] text-success',
  };
  return colors[status] || 'bg-frost text-text-secondary';
}

export function AuditTrailModal({
  isOpen,
  entries,
  isLoading = false,
  onClose,
}: AuditTrailModalProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-deep-ice/50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-card-hover w-full max-w-lg mx-4 max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-comfortable py-normal border-b border-frost flex-shrink-0">
          <h2 className="text-[18px] font-semibold text-text-primary">
            Audit Trail
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-text-secondary hover:text-text-primary hover:bg-frost/50 rounded transition-colors"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-comfortable py-normal">
          {isLoading ? (
            <div className="flex items-center justify-center py-generous">
              <div className="w-6 h-6 border-2 border-glacier-blue border-t-transparent rounded-full animate-spin" />
            </div>
          ) : entries.length === 0 ? (
            <div className="text-center py-generous">
              <p className="text-[15px] text-text-secondary">
                No status changes recorded
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {entries.map((entry, index) => (
                <div
                  key={entry.id}
                  className={cn(
                    'relative pl-6',
                    index !== entries.length - 1 &&
                      'pb-4 border-l-2 border-frost ml-2'
                  )}
                >
                  {/* Timeline dot */}
                  <div className="absolute left-0 top-0 w-4 h-4 rounded-full bg-white border-2 border-glacier-blue -translate-x-[7px]" />

                  {/* Entry content */}
                  <div className="ml-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      {entry.fromStatus && (
                        <>
                          <span
                            className={cn(
                              'px-2 py-0.5 rounded text-[12px] font-medium',
                              getStatusColor(entry.fromStatus)
                            )}
                          >
                            {getStatusLabel(entry.fromStatus)}
                          </span>
                          <svg
                            className="w-4 h-4 text-text-tertiary"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                            strokeWidth={2}
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              d="M13 7l5 5m0 0l-5 5m5-5H6"
                            />
                          </svg>
                        </>
                      )}
                      <span
                        className={cn(
                          'px-2 py-0.5 rounded text-[12px] font-medium',
                          getStatusColor(entry.toStatus)
                        )}
                      >
                        {getStatusLabel(entry.toStatus)}
                      </span>
                    </div>

                    <p className="text-[13px] text-text-secondary mt-1">
                      {entry.changedByName || 'System'}
                    </p>
                    <p className="text-[12px] text-text-tertiary">
                      {formatDateTime(entry.changedAt)}
                    </p>

                    {entry.reason && (
                      <p className="text-[13px] text-text-secondary mt-2 italic">
                        "{entry.reason}"
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end px-comfortable py-normal border-t border-frost flex-shrink-0">
          <button
            onClick={onClose}
            className={cn(
              'px-4 py-2 text-[13px] font-medium rounded-md transition-colors',
              'border border-arctic text-text-primary',
              'hover:bg-frost'
            )}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
