import { useState } from 'react';
import { cn } from '../../utils/cn';
import { Button } from './Button';
import type { AllergyAlert } from '../../types';

export interface AllergyOverrideData {
  justification: string;
  acknowledgedAt: string;
}

interface AllergyBlockModalProps {
  alert: AllergyAlert;
  onClose: () => void;
  onOverride?: (data: AllergyOverrideData) => void;
}

export function AllergyBlockModal({ alert, onClose, onOverride }: AllergyBlockModalProps) {
  const [showOverrideForm, setShowOverrideForm] = useState(false);
  const [justification, setJustification] = useState('');
  const [acknowledged, setAcknowledged] = useState(false);

  const canConfirmOverride = justification.trim().length > 0 && acknowledged;

  const handleOverrideClick = () => {
    setShowOverrideForm(true);
  };

  const handleConfirmOverride = () => {
    if (canConfirmOverride && onOverride) {
      onOverride({
        justification: justification.trim(),
        acknowledgedAt: new Date().toISOString(),
      });
    }
  };

  const handleBackToAlert = () => {
    setShowOverrideForm(false);
    setJustification('');
    setAcknowledged(false);
  };

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

          {showOverrideForm ? (
            <div className="mt-generous">
              <div className="p-normal bg-warning/10 border border-warning/20 rounded-md mb-normal">
                <p className="text-[13px] text-text-primary font-medium">
                  Override requires clinical justification
                </p>
              </div>

              <div className="mb-normal">
                <label
                  htmlFor="justification"
                  className="block text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight"
                >
                  Clinical Justification <span className="text-critical">*</span>
                </label>
                <textarea
                  id="justification"
                  value={justification}
                  onChange={(e) => setJustification(e.target.value)}
                  placeholder="Enter clinical justification for prescribing despite allergy..."
                  className={cn(
                    'w-full px-4 py-3 rounded-md border border-frost bg-white',
                    'text-[15px] text-text-primary placeholder:text-text-tertiary',
                    'focus:outline-none focus:ring-2 focus:ring-glacier-blue focus:border-transparent',
                    'resize-none'
                  )}
                  rows={3}
                />
              </div>

              <div className="mb-generous">
                <label className="flex items-start gap-tight cursor-pointer">
                  <input
                    type="checkbox"
                    checked={acknowledged}
                    onChange={(e) => setAcknowledged(e.target.checked)}
                    className="mt-1 h-4 w-4 rounded border-frost text-glacier-blue focus:ring-glacier-blue"
                  />
                  <span className="text-[15px] text-text-primary leading-snug">
                    I acknowledge the patient has a documented{' '}
                    <span className="font-medium text-critical">{alert.severity}</span> allergy to{' '}
                    <span className="font-medium">{alert.allergen}</span> and accept responsibility
                    for this prescription override.
                  </span>
                </label>
              </div>

              <div className="flex justify-between gap-normal pt-normal border-t border-frost">
                <Button variant="secondary" onClick={handleBackToAlert}>
                  Back
                </Button>
                <Button
                  variant="danger"
                  onClick={handleConfirmOverride}
                  disabled={!canConfirmOverride}
                >
                  Confirm Override
                </Button>
              </div>
            </div>
          ) : (
            <div className="mt-generous flex justify-between gap-normal">
              <Button variant="secondary" onClick={onClose}>
                Select Alternative
              </Button>
              {onOverride && (
                <Button variant="danger" onClick={handleOverrideClick}>
                  Override
                </Button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
