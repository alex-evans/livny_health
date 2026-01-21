import { useEffect, useCallback } from 'react';
import type {
  Problem,
  ProblemDetailResponse,
  ProblemHistoryEntry,
  ProblemTreatmentOutcome,
} from '../../types';
import { Button, Card, CardContent } from '../ui';
import { cn } from '../../utils/cn';

interface ProblemDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  problem: Problem | null;
  problemDetail: ProblemDetailResponse | null;
  isLoading: boolean;
  error: string | null;
  onVisitClick?: (visitId: string) => void;
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function getEntryTypeIcon(entryType: ProblemHistoryEntry['type']) {
  switch (entryType) {
    case 'onset':
      return (
        <div className="w-8 h-8 rounded-full bg-glacier-blue/10 flex items-center justify-center">
          <svg className="w-4 h-4 text-glacier-blue" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 6v6l4 2" />
          </svg>
        </div>
      );
    case 'visit':
      return (
        <div className="w-8 h-8 rounded-full bg-deep-ice/10 flex items-center justify-center">
          <svg className="w-4 h-4 text-deep-ice" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        </div>
      );
    case 'treatment':
      return (
        <div className="w-8 h-8 rounded-full bg-success/10 flex items-center justify-center">
          <svg className="w-4 h-4 text-success" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
          </svg>
        </div>
      );
    case 'status_change':
      return (
        <div className="w-8 h-8 rounded-full bg-warning/10 flex items-center justify-center">
          <svg className="w-4 h-4 text-warning" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
            <path d="M12 9v4" />
            <path d="M12 17h.01" />
          </svg>
        </div>
      );
    case 'progression':
      return (
        <div className="w-8 h-8 rounded-full bg-frost flex items-center justify-center">
          <svg className="w-4 h-4 text-text-secondary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
          </svg>
        </div>
      );
    default:
      return (
        <div className="w-8 h-8 rounded-full bg-frost flex items-center justify-center">
          <svg className="w-4 h-4 text-text-tertiary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
          </svg>
        </div>
      );
  }
}

function getOutcomeBadge(outcome: ProblemTreatmentOutcome['outcome']) {
  const styles: Record<ProblemTreatmentOutcome['outcome'], string> = {
    effective: 'bg-success/10 text-success',
    partially_effective: 'bg-warning/10 text-warning',
    ineffective: 'bg-critical/10 text-critical',
    ongoing: 'bg-glacier-blue/10 text-glacier-blue',
  };

  const labels: Record<ProblemTreatmentOutcome['outcome'], string> = {
    effective: 'Effective',
    partially_effective: 'Partially Effective',
    ineffective: 'Ineffective',
    ongoing: 'Ongoing',
  };

  return (
    <span
      className={cn(
        'px-2 py-0.5 rounded text-[11px] font-medium uppercase',
        styles[outcome]
      )}
    >
      {labels[outcome]}
    </span>
  );
}

export function ProblemDetailModal({
  isOpen,
  onClose,
  problem,
  problemDetail,
  isLoading,
  error,
  onVisitClick,
}: ProblemDetailModalProps) {
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    },
    [onClose]
  );

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [isOpen, handleKeyDown]);

  if (!isOpen) return null;

  const displayProblem = problemDetail?.problem || problem;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="problem-detail-title"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden animate-in fade-in-0 zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-frost">
          <div>
            <h2
              id="problem-detail-title"
              className="text-[18px] font-semibold text-text-primary"
            >
              {displayProblem?.name || 'Problem Detail'}
            </h2>
            {displayProblem && (
              <div className="flex items-center gap-2 mt-1">
                <span className="font-mono text-[13px] text-deep-ice">
                  {displayProblem.icd10Code}
                </span>
                <span
                  className={cn(
                    'px-2 py-0.5 rounded text-[11px] font-medium',
                    displayProblem.status === 'active' && 'bg-glacier-blue/10 text-glacier-blue',
                    displayProblem.status === 'resolved' && 'bg-success/10 text-success',
                    displayProblem.status === 'inactive' && 'bg-frost text-text-tertiary',
                    displayProblem.status === 'rule_out' && 'bg-amber-100 text-amber-700'
                  )}
                >
                  {displayProblem.status === 'rule_out' ? 'Rule Out' : displayProblem.status}
                </span>
                {displayProblem.isCritical && (
                  <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-critical/10 text-critical uppercase">
                    Critical
                  </span>
                )}
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-frost rounded-md transition-colors"
            aria-label="Close modal"
          >
            <svg
              className="w-5 h-5 text-text-tertiary"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-2 border-glacier-blue border-t-transparent" />
            </div>
          )}

          {error && (
            <div className="text-center py-12">
              <p className="text-critical text-[15px]">{error}</p>
              <Button variant="secondary" onClick={onClose} className="mt-4">
                Close
              </Button>
            </div>
          )}

          {!isLoading && !error && displayProblem && (
            <>
              {/* Summary Card */}
              <Card className="mb-normal">
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                        Onset Date
                      </span>
                      <p className="text-[15px] text-text-primary mt-0.5">
                        {formatDate(displayProblem.onsetDate)}
                      </p>
                    </div>
                    {problemDetail?.lastAddressed && (
                      <div>
                        <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                          Last Addressed
                        </span>
                        <p className="text-[15px] text-text-primary mt-0.5">
                          {formatDate(problemDetail.lastAddressed)}
                        </p>
                      </div>
                    )}
                    {displayProblem.documentingProvider && (
                      <div>
                        <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                          Documenting Provider
                        </span>
                        <p className="text-[15px] text-text-primary mt-0.5">
                          {displayProblem.documentingProvider}
                        </p>
                      </div>
                    )}
                    {problemDetail?.currentTreatment && (
                      <div>
                        <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                          Current Treatment
                        </span>
                        <p className="text-[15px] text-text-primary mt-0.5">
                          {problemDetail.currentTreatment}
                        </p>
                      </div>
                    )}
                    {displayProblem.severity && (
                      <div>
                        <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                          Severity
                        </span>
                        <p className="text-[15px] text-text-primary mt-0.5 capitalize">
                          {displayProblem.severity.replace('_', ' ')}
                        </p>
                      </div>
                    )}
                    {displayProblem.clinicalCategory && (
                      <div>
                        <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                          Category
                        </span>
                        <p className="text-[15px] text-text-primary mt-0.5 capitalize">
                          {displayProblem.clinicalCategory}
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Treatment History */}
              {problemDetail?.treatments && problemDetail.treatments.length > 0 && (
                <div className="mb-normal">
                  <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
                    Treatment History
                  </h3>
                  <Card>
                    <CardContent>
                      <div className="space-y-3">
                        {problemDetail.treatments.map((treatment, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between py-2 border-b border-frost/50 last:border-0"
                          >
                            <div>
                              <p className="text-[15px] font-medium text-text-primary">
                                {treatment.treatment}
                              </p>
                              <p className="text-[13px] text-text-tertiary">
                                Started {formatDate(treatment.startDate)}
                                {treatment.endDate && ` - Ended ${formatDate(treatment.endDate)}`}
                              </p>
                            </div>
                            {getOutcomeBadge(treatment.outcome)}
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}

              {/* History Timeline */}
              {problemDetail?.historyTimeline && problemDetail.historyTimeline.length > 0 && (
                <div>
                  <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
                    History Timeline
                  </h3>
                  <Card>
                    <CardContent>
                      <div className="space-y-4">
                        {problemDetail.historyTimeline.map((entry, index) => (
                          <div key={index} className="flex gap-3">
                            {getEntryTypeIcon(entry.type)}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between gap-2">
                                <p className="text-[15px] text-text-primary">
                                  {entry.description}
                                </p>
                                <span className="text-[13px] text-text-tertiary flex-shrink-0">
                                  {formatDate(entry.date)}
                                </span>
                              </div>
                              {entry.provider && (
                                <p className="text-[13px] text-text-tertiary mt-0.5">
                                  {entry.provider}
                                </p>
                              )}
                              {entry.visitId && onVisitClick && (
                                <button
                                  type="button"
                                  onClick={() => onVisitClick(entry.visitId!)}
                                  className="text-[13px] text-glacier-blue hover:text-deep-ice transition-colors mt-1"
                                >
                                  View visit details
                                </button>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}

              {/* Related Items */}
              {displayProblem.relatedMedications && displayProblem.relatedMedications.length > 0 && (
                <div className="mt-normal">
                  <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
                    Related Medications
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {displayProblem.relatedMedications.map((med) => (
                      <span
                        key={med.medicationId}
                        className="px-3 py-1.5 rounded-md bg-frost/50 text-[13px] text-text-secondary"
                      >
                        {med.name}
                        {med.dosage && <span className="text-text-tertiary ml-1">{med.dosage}</span>}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {displayProblem.relatedLabs && displayProblem.relatedLabs.length > 0 && (
                <div className="mt-normal">
                  <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
                    Related Lab Results
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {displayProblem.relatedLabs.map((lab) => (
                      <span
                        key={lab.labName}
                        className={cn(
                          'px-3 py-1.5 rounded-md text-[13px]',
                          lab.status === 'critical' && 'bg-critical/10 text-critical',
                          lab.status === 'abnormal' && 'bg-warning/10 text-warning',
                          (!lab.status || lab.status === 'normal') && 'bg-frost/50 text-text-secondary'
                        )}
                      >
                        {lab.labName}
                        {lab.mostRecentValue && (
                          <span className="ml-1 font-medium">{lab.mostRecentValue}</span>
                        )}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* No detailed history available */}
              {(!problemDetail?.historyTimeline || problemDetail.historyTimeline.length === 0) &&
                (!problemDetail?.treatments || problemDetail.treatments.length === 0) && (
                  <div className="text-center py-8 text-text-tertiary">
                    <svg
                      className="w-12 h-12 mx-auto mb-2 text-frost"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.5"
                    >
                      <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p className="text-[15px]">No detailed history available for this problem</p>
                  </div>
                )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end px-6 py-4 border-t border-frost">
          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}
