import { useState } from 'react';
import { cn } from '../../utils/cn';
import { Button } from './Button';
import type { DrugInteraction } from '../../types';

export interface InteractionOverrideData {
  justification: string;
  acknowledgedAt: string;
}

interface DrugInteractionBlockModalProps {
  interactions: DrugInteraction[];
  medicationName: string;
  onClose: () => void;
  onOverride: (data: InteractionOverrideData) => void;
}

function getSeverityPriority(severity: string): number {
  switch (severity) {
    case 'major':
      return 0;
    case 'moderate':
      return 1;
    case 'minor':
    default:
      return 2;
  }
}

export function DrugInteractionBlockModal({
  interactions,
  medicationName,
  onClose,
  onOverride,
}: DrugInteractionBlockModalProps) {
  const [showOverrideForm, setShowOverrideForm] = useState(false);
  const [justification, setJustification] = useState('');
  const [acknowledged, setAcknowledged] = useState(false);

  const canConfirmOverride = justification.trim().length > 0 && acknowledged;

  const sortedInteractions = [...interactions].sort(
    (a, b) => getSeverityPriority(a.severity) - getSeverityPriority(b.severity)
  );

  const criticalInteractions = sortedInteractions.filter((i) => i.severity === 'major');

  const handleOverrideClick = () => {
    setShowOverrideForm(true);
  };

  const handleConfirmOverride = () => {
    if (canConfirmOverride) {
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
        aria-labelledby="interaction-alert-title"
        aria-describedby="interaction-alert-message"
        className={cn(
          'relative bg-white rounded-lg shadow-xl max-w-lg w-full mx-normal',
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
                id="interaction-alert-title"
                className="text-xl font-semibold text-critical"
              >
                Critical Drug Interaction
              </h2>
              <p
                id="interaction-alert-message"
                className="mt-normal text-[15px] text-text-primary leading-relaxed"
              >
                <span className="font-medium">{medicationName}</span> has{' '}
                {criticalInteractions.length > 1
                  ? `${criticalInteractions.length} critical interactions`
                  : 'a critical interaction'}{' '}
                with the patient's current medications.
              </p>
            </div>
          </div>

          <div className="mt-normal space-y-tight">
            {sortedInteractions.map((interaction, index) => (
              <div
                key={index}
                className={cn(
                  'p-normal rounded-md',
                  interaction.severity === 'major'
                    ? 'bg-critical/10 border border-critical/20'
                    : interaction.severity === 'moderate'
                    ? 'bg-warning/10 border border-warning/20'
                    : 'bg-glacier-blue/10 border border-glacier-blue/20'
                )}
              >
                <div className="flex items-start gap-tight">
                  <span
                    className={cn(
                      'px-2 py-0.5 text-[11px] font-medium uppercase tracking-wide rounded flex-shrink-0',
                      interaction.severity === 'major'
                        ? 'bg-critical/20 text-critical'
                        : interaction.severity === 'moderate'
                        ? 'bg-warning/20 text-warning'
                        : 'bg-glacier-blue/20 text-glacier-blue'
                    )}
                  >
                    {interaction.severity}
                  </span>
                  <div>
                    <p className="text-[15px] font-medium text-text-primary">
                      {interaction.interactingDrug}
                    </p>
                    <p className="text-[13px] text-text-secondary mt-0.5">
                      {interaction.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
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
                  htmlFor="interaction-justification"
                  className="block text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight"
                >
                  Clinical Justification <span className="text-critical">*</span>
                </label>
                <textarea
                  id="interaction-justification"
                  value={justification}
                  onChange={(e) => setJustification(e.target.value)}
                  placeholder="Enter clinical justification for prescribing despite drug interaction..."
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
                    I acknowledge the{' '}
                    <span className="font-medium text-critical">
                      {criticalInteractions.length} critical drug interaction
                      {criticalInteractions.length > 1 ? 's' : ''}
                    </span>{' '}
                    and accept responsibility for this prescription override.
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
              <Button variant="danger" onClick={handleOverrideClick}>
                Override
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
