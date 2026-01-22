import type { VitalTrendAnalysis, ClinicalSignificance } from '../../types';
import { cn } from '../../utils/cn';

interface VitalTrendIndicatorProps {
  trend: VitalTrendAnalysis | null;
  showDetails?: boolean;
  className?: string;
}

function getSignificanceColor(significance: ClinicalSignificance): string {
  switch (significance) {
    case 'good':
      return 'text-status-success';
    case 'concerning':
      return 'text-status-critical';
    default:
      return 'text-text-tertiary';
  }
}

function getSignificanceBgColor(significance: ClinicalSignificance): string {
  switch (significance) {
    case 'good':
      return 'bg-status-success/10';
    case 'concerning':
      return 'bg-status-critical/10';
    default:
      return 'bg-frost/50';
  }
}

function TrendArrow({
  direction,
  className,
}: {
  direction: 'increasing' | 'decreasing' | 'stable';
  className?: string;
}) {
  if (direction === 'stable') {
    return (
      <svg
        className={cn('w-4 h-4', className)}
        viewBox="0 0 16 16"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      >
        <path d="M3 8h10" />
      </svg>
    );
  }

  if (direction === 'increasing') {
    return (
      <svg
        className={cn('w-4 h-4', className)}
        viewBox="0 0 16 16"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M8 12V4" />
        <path d="M4 8l4-4 4 4" />
      </svg>
    );
  }

  return (
    <svg
      className={cn('w-4 h-4', className)}
      viewBox="0 0 16 16"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M8 4v8" />
      <path d="M4 8l4 4 4-4" />
    </svg>
  );
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
}

export function VitalTrendIndicator({
  trend,
  showDetails = false,
  className,
}: VitalTrendIndicatorProps) {
  if (!trend) {
    return null;
  }

  const { direction, percentChange, absoluteChange, previousValue, previousDate, clinicalSignificance } = trend;

  const signClass = percentChange >= 0 ? '+' : '';
  const colorClass = getSignificanceColor(clinicalSignificance);
  const bgClass = getSignificanceBgColor(clinicalSignificance);

  if (!showDetails) {
    // Compact view - just arrow and percentage
    return (
      <div
        className={cn(
          'inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[13px]',
          bgClass,
          colorClass,
          className
        )}
        title={`${signClass}${percentChange.toFixed(1)}% from ${previousValue} on ${formatDate(previousDate)}`}
      >
        <TrendArrow direction={direction} />
        <span>{signClass}{percentChange.toFixed(1)}%</span>
      </div>
    );
  }

  // Detailed view
  return (
    <div className={cn('flex flex-col gap-1', className)}>
      <div
        className={cn(
          'inline-flex items-center gap-1 px-2 py-1 rounded',
          bgClass,
          colorClass
        )}
      >
        <TrendArrow direction={direction} />
        <span className="text-[15px] font-medium">
          {signClass}{percentChange.toFixed(1)}%
        </span>
        <span className="text-text-tertiary text-[13px]">
          ({signClass}{absoluteChange.toFixed(1)})
        </span>
      </div>
      <div className="text-[13px] text-text-tertiary">
        Previous: {previousValue} on {formatDate(previousDate)}
      </div>
    </div>
  );
}
