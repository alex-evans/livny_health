import { useEffect, useCallback } from 'react';
import type { LabHistoryResponse, LabHistoryEntry } from '../../types';
import { LabTrendChart } from './LabTrendChart';
import { Button, Card, CardContent } from '../ui';
import { cn } from '../../utils/cn';

interface LabHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  labHistory: LabHistoryResponse | null;
  isLoading: boolean;
  error: string | null;
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function getStatusBadge(status: LabHistoryEntry['status']) {
  const styles: Record<LabHistoryEntry['status'], string> = {
    normal: 'bg-success/10 text-success',
    abnormal: 'bg-warning/10 text-warning',
    critical: 'bg-critical/10 text-critical',
    pending: 'bg-frost/50 text-text-tertiary',
    in_progress: 'bg-glacier-blue/10 text-glacier-blue',
  };

  const labels: Record<LabHistoryEntry['status'], string> = {
    normal: 'normal',
    abnormal: 'abnormal',
    critical: 'critical',
    pending: 'pending',
    in_progress: 'in progress',
  };

  return (
    <span
      className={cn(
        'px-2 py-0.5 rounded text-[11px] font-medium uppercase',
        styles[status]
      )}
    >
      {labels[status]}
    </span>
  );
}

function getTrendIcon(direction: 'increasing' | 'decreasing' | 'stable') {
  switch (direction) {
    case 'increasing':
      return (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M7 17l5-5 5 5M7 7l5-5 5 5" />
        </svg>
      );
    case 'decreasing':
      return (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M7 7l5 5 5-5M7 17l5 5 5-5" />
        </svg>
      );
    default:
      return (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M5 12h14" />
        </svg>
      );
  }
}

export function LabHistoryModal({
  isOpen,
  onClose,
  labHistory,
  isLoading,
  error,
}: LabHistoryModalProps) {
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

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="lab-history-title"
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
              id="lab-history-title"
              className="text-[18px] font-semibold text-text-primary"
            >
              {labHistory?.testName || 'Lab History'}
            </h2>
            {labHistory && (
              <p className="text-[13px] text-text-tertiary mt-0.5">
                Reference range: {labHistory.referenceRange} {labHistory.unit}
              </p>
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

          {!isLoading && !error && labHistory && (
            <>
              {/* Trend Analysis Summary */}
              {labHistory.trendAnalysis && (
                <Card className="mb-normal">
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span
                          className={cn(
                            'p-2 rounded-full',
                            labHistory.trendAnalysis.direction === 'increasing' &&
                              'bg-warning/10 text-warning',
                            labHistory.trendAnalysis.direction === 'decreasing' &&
                              'bg-success/10 text-success',
                            labHistory.trendAnalysis.direction === 'stable' &&
                              'bg-frost text-text-secondary'
                          )}
                        >
                          {getTrendIcon(labHistory.trendAnalysis.direction)}
                        </span>
                        <div>
                          <p className="text-[15px] font-medium text-text-primary capitalize">
                            {labHistory.trendAnalysis.direction} Trend
                          </p>
                          <p className="text-[13px] text-text-tertiary">
                            {Math.abs(labHistory.trendAnalysis.percentChange).toFixed(1)}% change
                            over {labHistory.trendAnalysis.dataPoints} results
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-[13px] text-text-tertiary">
                          First: {labHistory.trendAnalysis.firstValue} {labHistory.unit}
                        </p>
                        <p className="text-[15px] font-medium text-text-primary">
                          Latest: {labHistory.trendAnalysis.lastValue} {labHistory.unit}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Trend Chart */}
              <div className="mb-normal">
                <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
                  Trend Chart
                </h3>
                <Card>
                  <CardContent className="flex justify-center py-4">
                    <LabTrendChart
                      history={labHistory.history}
                      referenceRange={labHistory.referenceRange}
                      unit={labHistory.unit}
                      width={500}
                      height={220}
                    />
                  </CardContent>
                </Card>
              </div>

              {/* History List */}
              <div>
                <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
                  Historical Results ({labHistory.history.length})
                </h3>
                <div className="space-y-1">
                  {labHistory.history.map((entry) => (
                    <div
                      key={entry.id}
                      className={cn(
                        'flex items-center justify-between px-3 py-2 rounded-md',
                        'hover:bg-frost/50 transition-colors'
                      )}
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-[13px] text-text-tertiary w-24">
                          {formatDate(entry.collectionDate)}
                        </span>
                        <span className="text-[15px] font-medium text-text-primary">
                          {entry.value} {entry.unit}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        {getStatusBadge(entry.status)}
                        {entry.performingLab && (
                          <span className="text-[11px] text-text-tertiary">
                            {entry.performingLab}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
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
