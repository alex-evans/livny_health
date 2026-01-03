import { cn } from '../../utils/cn';
import { Button } from './Button';
import type { AllergyAlert } from '../../types';

interface AllergyBlockModalProps {
  alert: AllergyAlert;
  onClose: () => void;
}

export function AllergyBlockModal({ alert, onClose }: AllergyBlockModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="allergy-alert-title"
        aria-describedby="allergy-alert-message"
        className={cn(
          'relative bg-white rounded-lg shadow-xl max-w-md w-full mx-normal',
          'border-l-4 border-critical'
        )}
      >
        <div className="p-generous">
          <div className="flex items-start gap-normal">
            <div className="flex-shrink-0">
              <svg
                className="h-8 w-8 text-critical"
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
              <h2
                id="allergy-alert-title"
                className="text-xl font-semibold text-critical"
              >
                {alert.title}
              </h2>
              <p
                id="allergy-alert-message"
                className="mt-normal text-[15px] text-text-primary leading-relaxed"
              >
                {alert.message}
              </p>
              {alert.isCrossReactive && (
                <div className="mt-normal p-normal bg-critical/5 rounded-md">
                  <p className="text-[13px] text-text-secondary">
                    <span className="font-medium">Cross-reactivity detected:</span>{' '}
                    {alert.medicationName} belongs to the same drug class as {alert.allergen}.
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="mt-generous flex justify-end">
            <Button variant="secondary" onClick={onClose}>
              Select Alternative Medication
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
