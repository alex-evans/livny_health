import { cn } from '../../utils/cn';
import type { EnrichedContextLab, PendingLab } from '../../types';

interface LabsContextSectionProps {
  labs: EnrichedContextLab[];
  pending: PendingLab[];
}

export function LabsContextSection({ labs, pending }: LabsContextSectionProps) {
  if (labs.length === 0 && pending.length === 0) {
    return <p className="text-[13px] text-text-tertiary">No recent labs</p>;
  }

  return (
    <div className="space-y-3">
      {pending.length > 0 && (
        <div>
          <h4 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-2">
            Pending
          </h4>
          <div className="space-y-1">
            {pending.map((lab, idx) => (
              <div key={idx} className="text-[14px] text-text-secondary flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-warning animate-pulse" />
                {lab.name}
              </div>
            ))}
          </div>
        </div>
      )}

      {labs.length > 0 && (
        <div className="space-y-2">
          {labs.slice(0, 5).map((lab) => (
            <div key={lab.id} className="flex justify-between items-center">
              <span className="text-[14px] text-text-primary">{lab.name}</span>
              <div className="flex items-center gap-2">
                <span
                  className={cn(
                    'text-[14px]',
                    lab.status === 'normal'
                      ? 'text-text-secondary'
                      : lab.status === 'critical'
                        ? 'text-status-critical font-medium'
                        : 'text-status-abnormal'
                  )}
                >
                  {lab.value} {lab.unit}
                </span>
                {lab.status !== 'normal' && (
                  <StatusIndicator status={lab.status} />
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function StatusIndicator({ status }: { status: 'high' | 'low' | 'critical' }) {
  const labels = {
    high: 'H',
    low: 'L',
    critical: '!',
  };

  return (
    <span
      className={cn(
        'text-[10px] font-bold w-4 h-4 rounded flex items-center justify-center',
        status === 'critical'
          ? 'bg-status-critical text-white'
          : 'bg-status-abnormal/20 text-status-abnormal'
      )}
    >
      {labels[status]}
    </span>
  );
}
