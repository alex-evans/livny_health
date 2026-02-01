import { cn } from '../../utils/cn';
import type { SectionGuidanceStatus } from '../../types/guidance';

interface GuidanceSectionIndicatorProps {
  status: SectionGuidanceStatus;
  className?: string;
}

export function GuidanceSectionIndicator({
  status,
  className,
}: GuidanceSectionIndicatorProps) {
  if (status === 'complete') {
    return (
      <svg
        className={cn('w-4 h-4 text-status-success', className)}
        viewBox="0 0 16 16"
        fill="none"
        aria-label="Complete"
      >
        <circle cx="8" cy="8" r="7" fill="currentColor" />
        <path
          d="M5 8L7 10L11 6"
          stroke="white"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    );
  }

  if (status === 'partial') {
    return (
      <svg
        className={cn('w-4 h-4 text-status-warning', className)}
        viewBox="0 0 16 16"
        fill="none"
        aria-label="Partial"
      >
        <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5" />
        <path
          d="M8 1A7 7 0 0 1 8 15"
          fill="currentColor"
        />
      </svg>
    );
  }

  return (
    <svg
      className={cn('w-4 h-4 text-text-tertiary', className)}
      viewBox="0 0 16 16"
      fill="none"
      aria-label="Uncovered"
    >
      <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}
