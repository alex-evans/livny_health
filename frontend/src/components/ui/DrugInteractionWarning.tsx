import { cn } from '../../utils/cn';
import { Button } from './Button';
import type { DrugInteraction, InteractionSeverity } from '../../types';

interface DrugInteractionWarningProps {
  interactions: DrugInteraction[];
  onDismiss: () => void;
  onSelectAlternative: () => void;
}

function getSeverityStyles(severity: InteractionSeverity) {
  switch (severity) {
    case 'major':
      return {
        border: 'border-critical',
        bg: 'bg-critical/10',
        badge: 'bg-critical/20 text-critical',
      };
    case 'moderate':
      return {
        border: 'border-warning',
        bg: 'bg-warning/10',
        badge: 'bg-warning/20 text-warning',
      };
    case 'minor':
    default:
      return {
        border: 'border-glacier-blue',
        bg: 'bg-glacier-blue/10',
        badge: 'bg-glacier-blue/20 text-glacier-blue',
      };
  }
}

function getHighestSeverity(interactions: DrugInteraction[]): InteractionSeverity {
  if (interactions.some((i) => i.severity === 'major')) return 'major';
  if (interactions.some((i) => i.severity === 'moderate')) return 'moderate';
  return 'minor';
}

function getSeverityPriority(severity: InteractionSeverity): number {
  switch (severity) {
    case 'major':
      return 0; // Critical - highest priority
    case 'moderate':
      return 1; // Warning
    case 'minor':
    default:
      return 2; // Info - lowest priority
  }
}

function sortBySeverity(interactions: DrugInteraction[]): DrugInteraction[] {
  return [...interactions].sort(
    (a, b) => getSeverityPriority(a.severity) - getSeverityPriority(b.severity)
  );
}

export function DrugInteractionWarning({
  interactions,
  onDismiss,
  onSelectAlternative,
}: DrugInteractionWarningProps) {
  const highestSeverity = getHighestSeverity(interactions);
  const styles = getSeverityStyles(highestSeverity);

  return (
    <div
      role="alert"
      className={cn('mt-normal p-normal rounded-md', 'border-l-4', styles.border, styles.bg)}
    >
      <div className="flex items-start gap-normal">
        <div className="flex-shrink-0">
          <svg
            className={cn(
              'h-6 w-6',
              highestSeverity === 'major' ? 'text-critical' : 'text-warning'
            )}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-[15px] font-semibold text-text-primary">
            Drug Interaction Warning
          </h3>
          <div className="mt-tight space-y-tight">
            {sortBySeverity(interactions).map((interaction, index) => {
              const interactionStyles = getSeverityStyles(interaction.severity);
              return (
                <div key={index} className="flex items-start gap-tight">
                  <span
                    className={cn(
                      'px-2 py-0.5 text-[11px] font-medium uppercase tracking-wide rounded',
                      interactionStyles.badge
                    )}
                  >
                    {interaction.severity}
                  </span>
                  <p className="text-[15px] text-text-secondary">
                    <span className="font-medium text-text-primary">
                      {interaction.interactingDrug}:
                    </span>{' '}
                    {interaction.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
        <button
          onClick={onDismiss}
          className="flex-shrink-0 text-text-tertiary hover:text-text-secondary transition-colors"
          aria-label="Dismiss warning"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
      <div className="mt-normal flex justify-end">
        <Button variant="secondary" size="sm" onClick={onSelectAlternative}>
          Select Alternative Medication
        </Button>
      </div>
    </div>
  );
}
