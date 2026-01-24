/**
 * AlertBadge Component
 *
 * Displays a badge with the count of active alerts.
 * Shows severity-based styling and optional pulse animation for critical alerts.
 */

import { cn } from '../../utils/cn';
import type { AlertSummary } from '../../types';

interface AlertBadgeProps {
  summary: AlertSummary;
  onClick?: () => void;
  showPulse?: boolean;
  size?: 'sm' | 'md';
  className?: string;
}

export function AlertBadge({
  summary,
  onClick,
  showPulse = true,
  size = 'md',
  className,
}: AlertBadgeProps) {
  const { criticalCount, highCount, totalActive } = summary;

  if (totalActive === 0) {
    return null;
  }

  // Determine badge color based on highest severity present
  const getBadgeColor = () => {
    if (criticalCount > 0) {
      return 'bg-critical text-white';
    }
    if (highCount > 0) {
      return 'bg-warning text-white';
    }
    return 'bg-info text-white';
  };

  const sizes = {
    sm: 'min-w-[18px] h-[18px] text-[11px] px-1',
    md: 'min-w-[22px] h-[22px] text-[12px] px-1.5',
  };

  const hasCritical = criticalCount > 0;

  return (
    <button
      onClick={onClick}
      className={cn(
        'relative inline-flex items-center justify-center',
        'rounded-full font-semibold',
        'transition-all duration-150',
        'hover:scale-110 hover:shadow-sm',
        'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-critical/50',
        getBadgeColor(),
        sizes[size],
        className
      )}
      aria-label={`${totalActive} clinical alert${totalActive > 1 ? 's' : ''}`}
    >
      {/* Pulse animation for critical alerts */}
      {showPulse && hasCritical && (
        <span
          className={cn(
            'absolute inset-0 rounded-full',
            'bg-critical animate-ping opacity-75'
          )}
          aria-hidden="true"
        />
      )}
      <span className="relative">{totalActive}</span>
    </button>
  );
}

/**
 * AlertBadgeDetailed Component
 *
 * Shows a more detailed breakdown of alerts by severity.
 */
interface AlertBadgeDetailedProps {
  summary: AlertSummary;
  onClick?: () => void;
  className?: string;
}

export function AlertBadgeDetailed({
  summary,
  onClick,
  className,
}: AlertBadgeDetailedProps) {
  const { criticalCount, highCount, mediumCount, totalActive } = summary;

  if (totalActive === 0) {
    return null;
  }

  return (
    <button
      onClick={onClick}
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-1 rounded-md',
        'bg-frost hover:bg-arctic transition-colors',
        'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-glacier-blue/50',
        className
      )}
      aria-label={`Clinical alerts: ${criticalCount} critical, ${highCount} high, ${mediumCount} medium`}
    >
      {criticalCount > 0 && (
        <span className="inline-flex items-center justify-center min-w-[18px] h-[18px] px-1 rounded-full bg-critical text-white text-[11px] font-semibold">
          {criticalCount}
        </span>
      )}
      {highCount > 0 && (
        <span className="inline-flex items-center justify-center min-w-[18px] h-[18px] px-1 rounded-full bg-warning text-white text-[11px] font-semibold">
          {highCount}
        </span>
      )}
      {mediumCount > 0 && (
        <span className="inline-flex items-center justify-center min-w-[18px] h-[18px] px-1 rounded-full bg-info text-white text-[11px] font-semibold">
          {mediumCount}
        </span>
      )}
      <span className="text-[13px] text-text-secondary font-medium ml-0.5">
        {totalActive === 1 ? 'Alert' : 'Alerts'}
      </span>
    </button>
  );
}
