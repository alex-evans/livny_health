import { useMemo } from 'react';
import { cn } from '../../utils/cn';
import { GuidancePromptItem } from './GuidancePromptItem';
import { SECTION_LABELS } from '../../config/promptDefinitions';
import type { SectionCoverage, SOAPSectionKey } from '../../types/guidance';

interface GuidancePanelProps {
  section: SOAPSectionKey;
  coverage: SectionCoverage;
  onDismissPrompt: (promptId: string) => void;
  onRestorePrompt: (promptId: string) => void;
  onClose: () => void;
  className?: string;
}

export function GuidancePanel({
  section,
  coverage,
  onDismissPrompt,
  onRestorePrompt,
  onClose,
  className,
}: GuidancePanelProps) {
  const sortedPrompts = useMemo(() => {
    return [...coverage.prompts].sort((a, b) => {
      const statusOrder = { uncovered: 0, mentioned: 1, dismissed: 2 };
      const orderDiff = statusOrder[a.status] - statusOrder[b.status];
      if (orderDiff !== 0) return orderDiff;

      // Within same status, required prompts first
      if (a.required && !b.required) return -1;
      if (!a.required && b.required) return 1;
      return 0;
    });
  }, [coverage.prompts]);

  const uncoveredCount = coverage.prompts.filter(
    (p) => p.status === 'uncovered'
  ).length;

  return (
    <div
      className={cn(
        'bg-snow border-b border-frost animate-in slide-in-from-top-2 duration-150',
        className
      )}
    >
      <div className="px-comfortable py-tight">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <h4 className="text-[15px] font-medium text-text-primary">
              {SECTION_LABELS[section]}
            </h4>
            <span className="text-[13px] text-text-tertiary">
              {coverage.coveredCount}/{coverage.totalCount} documented
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-[13px] text-text-secondary hover:text-text-primary transition-colors px-2 py-1 rounded hover:bg-frost/50"
          >
            Got it
          </button>
        </div>

        {uncoveredCount > 0 && (
          <p className="text-[13px] text-text-secondary mb-3">
            Document the following to complete this section:
          </p>
        )}

        <div className="space-y-1 max-h-[200px] overflow-y-auto">
          {sortedPrompts.map((prompt) => (
            <GuidancePromptItem
              key={prompt.id}
              prompt={prompt}
              onDismiss={onDismissPrompt}
              onRestore={onRestorePrompt}
            />
          ))}
        </div>

        {coverage.status === 'complete' && (
          <div className="mt-3 p-3 bg-status-success/10 rounded-md">
            <p className="text-[13px] text-status-success font-medium">
              All prompts documented for {SECTION_LABELS[section]}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
