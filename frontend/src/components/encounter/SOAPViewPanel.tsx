import { cn } from '../../utils/cn';
import type { SOAPMappingResponse, SOAPCompleteness } from '../../types';
import { SOAPSectionCard } from './SOAPSectionCard';

interface SOAPViewPanelProps {
  mapping: SOAPMappingResponse | null;
  isLoading?: boolean;
  error?: string | null;
  className?: string;
}

const OVERALL_COMPLETENESS_STYLES: Record<
  SOAPCompleteness,
  { bg: string; text: string; label: string }
> = {
  empty: {
    bg: 'bg-frost',
    text: 'text-text-secondary',
    label: 'Note not started',
  },
  partial: {
    bg: 'bg-status-abnormal/10',
    text: 'text-status-abnormal',
    label: 'Note in progress',
  },
  complete: {
    bg: 'bg-status-normal/10',
    text: 'text-status-normal',
    label: 'All sections complete',
  },
};

export function SOAPViewPanel({
  mapping,
  isLoading = false,
  error,
  className,
}: SOAPViewPanelProps) {
  if (!mapping) {
    return (
      <div
        className={cn(
          'bg-white rounded-lg shadow-card p-comfortable',
          className
        )}
      >
        <div className="flex items-center justify-center h-32">
          <p className="text-text-tertiary text-[15px]">
            Start typing to see SOAP mapping
          </p>
        </div>
      </div>
    );
  }

  const overallStyles = OVERALL_COMPLETENESS_STYLES[mapping.overallCompleteness];

  return (
    <div
      className={cn(
        'bg-white rounded-lg shadow-card overflow-y-auto',
        className
      )}
    >
      {/* Header */}
      <div className="sticky top-0 bg-white border-b border-frost px-comfortable py-normal z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h3 className="text-[15px] font-medium text-text-primary">
              SOAP View
            </h3>
            {isLoading && (
              <span className="text-[12px] text-text-tertiary">
                Updating...
              </span>
            )}
          </div>
          <span
            className={cn(
              'text-[12px] px-3 py-1 rounded-full',
              overallStyles.bg,
              overallStyles.text
            )}
          >
            {overallStyles.label}
          </span>
        </div>
        {error && (
          <p className="text-[13px] text-status-critical mt-2">
            {error}
          </p>
        )}
      </div>

      {/* Section Cards */}
      <div className="p-comfortable space-y-normal">
        <SOAPSectionCard
          title="Subjective"
          section={mapping.subjective}
          defaultExpanded={true}
        />
        <SOAPSectionCard
          title="Objective"
          section={mapping.objective}
          defaultExpanded={true}
        />
        <SOAPSectionCard
          title="Assessment"
          section={mapping.assessment}
          defaultExpanded={true}
        />
        <SOAPSectionCard
          title="Plan"
          section={mapping.plan}
          defaultExpanded={true}
        />
      </div>

      {/* Completeness Summary */}
      <div className="border-t border-frost px-comfortable py-normal">
        <div className="flex items-center justify-between text-[13px]">
          <span className="text-text-secondary">Section completeness</span>
          <div className="flex items-center gap-2">
            <CompleteDot
              isComplete={mapping.subjective.completeness === 'complete'}
              label="S"
            />
            <CompleteDot
              isComplete={mapping.objective.completeness === 'complete'}
              label="O"
            />
            <CompleteDot
              isComplete={mapping.assessment.completeness === 'complete'}
              label="A"
            />
            <CompleteDot
              isComplete={mapping.plan.completeness === 'complete'}
              label="P"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function CompleteDot({
  isComplete,
  label,
}: {
  isComplete: boolean;
  label: string;
}) {
  return (
    <div
      className={cn(
        'w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-medium',
        isComplete
          ? 'bg-status-normal/20 text-status-normal'
          : 'bg-frost text-text-tertiary'
      )}
      title={`${label}: ${isComplete ? 'Complete' : 'Incomplete'}`}
    >
      {label}
    </div>
  );
}
