import { useState } from 'react';
import { cn } from '../../utils/cn';
import type { PromptWithStatus } from '../../types/guidance';

interface GuidancePromptItemProps {
  prompt: PromptWithStatus;
  onDismiss: (promptId: string) => void;
  onRestore: (promptId: string) => void;
}

export function GuidancePromptItem({
  prompt,
  onDismiss,
  onRestore,
}: GuidancePromptItemProps) {
  const [isHovered, setIsHovered] = useState(false);

  const statusIcon = {
    uncovered: (
      <div className="w-3 h-3 rounded-full border-2 border-text-tertiary" />
    ),
    mentioned: (
      <div className="w-3 h-3 rounded-full bg-status-success" />
    ),
    dismissed: (
      <div className="w-3 h-3 rounded-full bg-frost" />
    ),
  };

  return (
    <div
      className={cn(
        'flex items-start gap-3 py-2 px-3 rounded-md transition-colors',
        prompt.status === 'dismissed' && 'opacity-50',
        isHovered && 'bg-frost/50'
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex-shrink-0 mt-1">
        {statusIcon[prompt.status]}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span
            className={cn(
              'text-[15px] font-medium',
              prompt.status === 'mentioned' && 'text-text-primary',
              prompt.status === 'uncovered' && 'text-text-secondary',
              prompt.status === 'dismissed' && 'text-text-tertiary line-through'
            )}
          >
            {prompt.label}
          </span>
          {prompt.required && prompt.status === 'uncovered' && (
            <span className="text-[11px] font-medium uppercase tracking-wide text-status-critical bg-status-critical/10 px-1.5 py-0.5 rounded">
              Required
            </span>
          )}
        </div>
        <p
          className={cn(
            'text-[13px] mt-0.5',
            prompt.status === 'dismissed' ? 'text-text-tertiary' : 'text-text-secondary'
          )}
        >
          {prompt.description}
        </p>
      </div>

      <div className="flex-shrink-0">
        {isHovered && prompt.status === 'uncovered' && (
          <button
            onClick={() => onDismiss(prompt.id)}
            className="text-[13px] text-text-tertiary hover:text-text-secondary transition-colors"
          >
            Skip
          </button>
        )}
        {prompt.status === 'dismissed' && (
          <button
            onClick={() => onRestore(prompt.id)}
            className="text-[13px] text-glacier-blue hover:text-deep-ice transition-colors"
          >
            Restore
          </button>
        )}
      </div>
    </div>
  );
}
