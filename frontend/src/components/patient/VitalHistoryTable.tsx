import type { VitalHistoryEntry, VitalStatus } from '../../types';
import { cn } from '../../utils/cn';

interface VitalHistoryTableProps {
  history: VitalHistoryEntry[];
  unit: string;
  className?: string;
}

function getStatusBadgeClass(status: VitalStatus): string {
  switch (status) {
    case 'critical':
      return 'bg-status-critical/10 text-status-critical';
    case 'abnormal':
      return 'bg-status-warning/10 text-status-warning';
    default:
      return 'bg-status-success/10 text-status-success';
  }
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function formatTime(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  });
}

export function VitalHistoryTable({
  history,
  unit,
  className,
}: VitalHistoryTableProps) {
  if (history.length === 0) {
    return (
      <div className="text-text-tertiary text-[15px] py-8 text-center">
        No history available
      </div>
    );
  }

  return (
    <div className={cn('overflow-x-auto', className)}>
      <table className="w-full">
        <thead>
          <tr className="border-b border-frost">
            <th className="px-4 py-3 text-left text-[13px] font-medium text-text-secondary">
              Date
            </th>
            <th className="px-4 py-3 text-left text-[13px] font-medium text-text-secondary">
              Value
            </th>
            <th className="px-4 py-3 text-left text-[13px] font-medium text-text-secondary">
              Status
            </th>
            <th className="px-4 py-3 text-left text-[13px] font-medium text-text-secondary">
              Location
            </th>
            <th className="px-4 py-3 text-left text-[13px] font-medium text-text-secondary">
              Recorded By
            </th>
          </tr>
        </thead>
        <tbody>
          {history.map((entry) => (
            <tr
              key={entry.id}
              className="border-b border-frost/50 hover:bg-frost/20 transition-colors"
            >
              <td className="px-4 py-3">
                <div className="text-[15px] text-text-primary">
                  {formatDate(entry.recordedAt)}
                </div>
                <div className="text-[13px] text-text-tertiary">
                  {formatTime(entry.recordedAt)}
                </div>
              </td>
              <td className="px-4 py-3">
                <span className="text-[15px] font-medium text-text-primary">
                  {entry.value}
                </span>
                <span className="text-[13px] text-text-secondary ml-1">
                  {unit}
                </span>
              </td>
              <td className="px-4 py-3">
                <span
                  className={cn(
                    'text-[13px] px-2 py-1 rounded font-medium capitalize',
                    getStatusBadgeClass(entry.status)
                  )}
                >
                  {entry.status}
                </span>
              </td>
              <td className="px-4 py-3 text-[15px] text-text-secondary">
                {entry.location || '—'}
              </td>
              <td className="px-4 py-3 text-[15px] text-text-secondary">
                {entry.recordedBy || '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
