import { cn } from '../../utils/cn';
import type { AlertLevel } from '../../types';

interface SectionBadgeProps {
  count: number | null;
  alertLevel: AlertLevel;
}

export function SectionBadge({ count, alertLevel }: SectionBadgeProps) {
  if (count === null || count === undefined) {
    return null;
  }

  const alertStyles: Record<AlertLevel, string> = {
    none: 'bg-frost text-text-secondary',
    info: 'bg-glacier-blue/10 text-glacier-blue',
    warning: 'bg-warning/10 text-warning',
    critical: 'bg-critical/10 text-critical',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 rounded text-[11px] font-medium',
        alertStyles[alertLevel]
      )}
    >
      {count}
    </span>
  );
}
