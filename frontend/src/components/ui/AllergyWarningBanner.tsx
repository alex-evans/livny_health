import { cn } from '../../utils/cn';
import { Button } from './Button';
import type { AllergyAlert } from '../../types';

interface AllergyWarningBannerProps {
  alert: AllergyAlert;
  onDismiss: () => void;
  onSelectAlternative: () => void;
}

export function AllergyWarningBanner({ alert, onDismiss, onSelectAlternative }: AllergyWarningBannerProps) {
  return (
    <div
      role="alert"
      className={cn(
        'mt-normal p-normal rounded-md',
        'border-l-4 border-warning bg-warning/10'
      )}
    >
      <div className="flex items-start gap-normal">
        <div className="flex-shrink-0">
          <svg
            className="h-6 w-6 text-warning"
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
            {alert.title}
          </h3>
          <p className="mt-tight text-[15px] text-text-secondary">
            {alert.message}
          </p>
          {alert.isCrossReactive && (
            <p className="mt-tight text-[13px] text-text-tertiary">
              {alert.medicationName} belongs to the same drug class as {alert.allergen}.
            </p>
          )}
        </div>
        <button
          onClick={onDismiss}
          className="flex-shrink-0 text-text-tertiary hover:text-text-secondary transition-colors"
          aria-label="Dismiss warning"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
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
