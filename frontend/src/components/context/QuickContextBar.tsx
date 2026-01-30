import { cn } from '../../utils/cn';
import type { QuickContextSummary } from '../../types';

interface QuickContextBarProps {
  summary: QuickContextSummary;
  onClick?: () => void;
  className?: string;
}

export function QuickContextBar({ summary, onClick, className }: QuickContextBarProps) {
  const parts: string[] = [];

  // Primary vital with trend
  if (summary.primaryVital) {
    let vitalText = `${summary.primaryVital.label}: ${summary.primaryVital.value}`;
    if (summary.primaryVital.trend === 'improving') {
      vitalText += ' \u2193';
    } else if (summary.primaryVital.trend === 'worsening') {
      vitalText += ' \u2191';
    }
    parts.push(vitalText);
  }

  // Medications
  if (summary.medicationNames.length > 0) {
    const medsText = `Meds: ${summary.medicationNames.join(', ')}`;
    parts.push(medsText);
  }

  // Problems count
  if (summary.problemCount > 0) {
    parts.push(`${summary.problemCount} problems`);
  }

  // Key lab
  if (summary.keyLab) {
    parts.push(`${summary.keyLab.name}: ${summary.keyLab.value}`);
  }

  return (
    <div
      className={cn(
        'bg-white border-b border-frost px-comfortable py-2',
        onClick && 'cursor-pointer hover:bg-frost/30 transition-colors',
        className
      )}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onClick();
              }
            }
          : undefined
      }
    >
      <div className="flex items-center gap-4 text-[13px]">
        {/* Critical allergies always visible */}
        {summary.criticalAllergies.length > 0 && (
          <div className="flex items-center gap-1 text-status-critical font-medium">
            <WarningIcon className="w-4 h-4" />
            <span>{summary.criticalAllergies.join(', ')}</span>
          </div>
        )}

        {/* Other context parts */}
        {parts.map((part, idx) => (
          <span key={idx} className="text-text-secondary">
            {idx > 0 && <span className="text-text-tertiary mr-4">|</span>}
            {part}
          </span>
        ))}

        {/* Expand hint */}
        {onClick && (
          <span className="ml-auto text-[11px] text-text-tertiary">
            Click to expand
          </span>
        )}
      </div>
    </div>
  );
}

function WarningIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
      />
    </svg>
  );
}
