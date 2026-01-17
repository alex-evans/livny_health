import { useState } from 'react';
import { Button, Input } from '../ui';
import type { ActiveMedication } from '../../types';

interface MedicationDetailModalProps {
  medication: ActiveMedication;
  onClose: () => void;
  onDiscontinue?: (medicationId: string, reason?: string) => void;
  isDiscontinuing?: boolean;
}

export function MedicationDetailModal({
  medication,
  onClose,
  onDiscontinue,
  isDiscontinuing = false,
}: MedicationDetailModalProps) {
  const [showDiscontinueConfirm, setShowDiscontinueConfirm] = useState(false);
  const [discontinueReason, setDiscontinueReason] = useState('');
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="medication-detail-title"
        className="relative bg-white rounded-lg shadow-xl max-w-lg w-full mx-normal max-h-[85vh] overflow-y-auto"
      >
        <div className="p-generous">
          {/* Header */}
          <div className="flex items-start justify-between mb-comfortable">
            <div>
              <h2
                id="medication-detail-title"
                className="text-xl font-semibold text-deep-ice"
              >
                {medication.name}
              </h2>
              {medication.brandName && (
                <p className="text-[15px] text-text-secondary mt-1">
                  Brand: {medication.brandName}
                </p>
              )}
            </div>
            <button
              onClick={onClose}
              className="text-text-tertiary hover:text-text-secondary transition-colors p-1"
              aria-label="Close"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Badges */}
          <div className="flex flex-wrap gap-2 mb-comfortable">
            {medication.isPRN && (
              <span className="inline-flex items-center px-2 py-1 rounded text-[11px] font-medium bg-amber-100 text-amber-700">
                PRN (As Needed)
              </span>
            )}
            {medication.isControlled && (
              <span className="inline-flex items-center px-2 py-1 rounded text-[11px] font-medium bg-red-100 text-red-700">
                Controlled Substance
              </span>
            )}
            {medication.status && (
              <span className="inline-flex items-center px-2 py-1 rounded text-[11px] font-medium bg-glacier-blue/10 text-glacier-blue">
                {medication.status}
              </span>
            )}
          </div>

          {/* Prescription Details */}
          <div className="space-y-normal">
            <section>
              <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
                Prescription Details
              </h3>
              <div className="bg-arctic rounded-md p-normal space-y-2">
                <div className="flex justify-between">
                  <span className="text-[15px] text-text-secondary">Strength</span>
                  <span className="text-[15px] text-text-primary font-medium">{medication.strength || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[15px] text-text-secondary">Form</span>
                  <span className="text-[15px] text-text-primary font-medium capitalize">{medication.form || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[15px] text-text-secondary">Dosage</span>
                  <span className="text-[15px] text-text-primary font-medium">{medication.dosage || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[15px] text-text-secondary">Frequency</span>
                  <span className="text-[15px] text-text-primary font-medium">{medication.frequency || 'N/A'}</span>
                </div>
                {medication.route && (
                  <div className="flex justify-between">
                    <span className="text-[15px] text-text-secondary">Route</span>
                    <span className="text-[15px] text-text-primary font-medium">{medication.route}</span>
                  </div>
                )}
              </div>
            </section>

            {/* Drug Class */}
            {medication.drugClass && (
              <section>
                <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
                  Drug Class
                </h3>
                <p className="text-[15px] text-text-primary">{medication.drugClass}</p>
              </section>
            )}

            {/* Indication */}
            {medication.indication && (
              <section>
                <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
                  Indication
                </h3>
                <p className="text-[15px] text-text-primary">{medication.indication}</p>
              </section>
            )}

            {/* Prescriber Info */}
            <section>
              <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
                Prescribing Information
              </h3>
              <div className="bg-arctic rounded-md p-normal space-y-2">
                <div className="flex justify-between">
                  <span className="text-[15px] text-text-secondary">Prescriber</span>
                  <span className="text-[15px] text-text-primary font-medium">{medication.prescriber || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[15px] text-text-secondary">Start Date</span>
                  <span className="text-[15px] text-text-primary font-medium">{medication.started}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[15px] text-text-secondary">Refills Remaining</span>
                  <span className="text-[15px] text-text-primary font-medium">
                    {medication.refillsRemaining !== null && medication.refillsRemaining !== undefined
                      ? medication.refillsRemaining
                      : 'N/A'}
                  </span>
                </div>
              </div>
            </section>

            {/* Pharmacy */}
            {medication.pharmacy && (
              <section>
                <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
                  Pharmacy
                </h3>
                <p className="text-[15px] text-text-primary">{medication.pharmacy}</p>
              </section>
            )}

            {/* Prescriber Notes */}
            {medication.prescriberNotes && (
              <section>
                <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
                  Prescriber Notes
                </h3>
                <div className="bg-arctic rounded-md p-normal">
                  <p className="text-[15px] text-text-primary italic">{medication.prescriberNotes}</p>
                </div>
              </section>
            )}
          </div>

          {/* Discontinue Confirmation */}
          {showDiscontinueConfirm && (
            <div className="mt-generous p-normal bg-critical/5 border border-critical/20 rounded-md">
              <h4 className="text-[15px] font-medium text-critical mb-tight">
                Discontinue this medication?
              </h4>
              <p className="text-[13px] text-text-secondary mb-normal">
                This will remove {medication.name} from the patient's active medications.
              </p>
              <div className="mb-normal">
                <label className="block text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
                  Reason (optional)
                </label>
                <Input
                  type="text"
                  placeholder="e.g., No longer needed, Side effects, etc."
                  value={discontinueReason}
                  onChange={(e) => setDiscontinueReason(e.target.value)}
                />
              </div>
              <div className="flex gap-2">
                <Button
                  variant="danger"
                  onClick={() => onDiscontinue?.(medication.id, discontinueReason || undefined)}
                  disabled={isDiscontinuing}
                >
                  {isDiscontinuing ? 'Discontinuing...' : 'Confirm Discontinue'}
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => {
                    setShowDiscontinueConfirm(false);
                    setDiscontinueReason('');
                  }}
                  disabled={isDiscontinuing}
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}

          {/* Footer */}
          <div className="flex justify-between pt-generous mt-generous border-t border-frost">
            {onDiscontinue && !showDiscontinueConfirm && (
              <Button
                variant="danger"
                onClick={() => setShowDiscontinueConfirm(true)}
              >
                Discontinue
              </Button>
            )}
            {(!onDiscontinue || showDiscontinueConfirm) && <div />}
            <Button variant="secondary" onClick={onClose}>
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
