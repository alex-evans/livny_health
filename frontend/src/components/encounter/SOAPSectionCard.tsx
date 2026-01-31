import { useState } from 'react';
import { cn } from '../../utils/cn';
import type { SOAPSection, SOAPCompleteness } from '../../types';

interface SOAPSectionCardProps {
  title: string;
  section: SOAPSection;
  defaultExpanded?: boolean;
  className?: string;
}

const COMPLETENESS_STYLES: Record<SOAPCompleteness, { bg: string; text: string; label: string }> = {
  empty: {
    bg: 'bg-frost/50',
    text: 'text-text-tertiary',
    label: 'Not started',
  },
  partial: {
    bg: 'bg-status-abnormal/10',
    text: 'text-status-abnormal',
    label: 'In progress',
  },
  complete: {
    bg: 'bg-status-normal/10',
    text: 'text-status-normal',
    label: 'Complete',
  },
};

export function SOAPSectionCard({
  title,
  section,
  defaultExpanded = true,
  className,
}: SOAPSectionCardProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const styles = COMPLETENESS_STYLES[section.completeness];

  return (
    <div
      className={cn(
        'border border-frost rounded-lg overflow-hidden',
        className
      )}
    >
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between py-3 px-4 hover:bg-frost/30 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-[15px] font-medium text-text-primary">
            {title}
          </span>
          <span
            className={cn(
              'text-[12px] px-2 py-0.5 rounded-full',
              styles.bg,
              styles.text
            )}
          >
            {styles.label}
          </span>
        </div>
        <div className="flex items-center gap-2">
          {section.wordCount > 0 && (
            <span className="text-[12px] text-text-tertiary">
              {section.wordCount} words
            </span>
          )}
          <ChevronIcon
            className={cn(
              'w-4 h-4 text-text-tertiary transition-transform',
              isExpanded ? 'rotate-180' : ''
            )}
          />
        </div>
      </button>
      {isExpanded && (
        <div className="px-4 pb-4 pt-1">
          {section.content ? (
            <p className="text-[15px] text-text-primary leading-relaxed whitespace-pre-wrap">
              {section.content}
            </p>
          ) : (
            <p className="text-[14px] text-text-tertiary italic">
              No content mapped yet
            </p>
          )}
        </div>
      )}
    </div>
  );
}

function ChevronIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
    </svg>
  );
}
