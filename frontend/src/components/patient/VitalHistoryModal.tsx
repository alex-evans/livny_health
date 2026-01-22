import { useState, useEffect } from 'react';
import type { VitalHistoryResponse, VitalType } from '../../types';
import { VITAL_DISPLAY_CONFIG } from '../../types/vitals';
import { getVitalHistory } from '../../api/vitalsApi';
import { cn } from '../../utils/cn';
import { VitalTrendGraph } from './VitalTrendGraph';
import { VitalHistoryTable } from './VitalHistoryTable';
import { VitalTrendIndicator } from './VitalTrendIndicator';

interface VitalHistoryModalProps {
  patientId: string;
  vitalType: VitalType;
  isOpen: boolean;
  onClose: () => void;
}

type ViewMode = 'graph' | 'table';

export function VitalHistoryModal({
  patientId,
  vitalType,
  isOpen,
  onClose,
}: VitalHistoryModalProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('graph');
  const [historyData, setHistoryData] = useState<VitalHistoryResponse | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const config = VITAL_DISPLAY_CONFIG[vitalType];

  useEffect(() => {
    if (isOpen && patientId && vitalType) {
      setLoading(true);
      setError(null);

      getVitalHistory(patientId, vitalType)
        .then((data) => {
          setHistoryData(data);
        })
        .catch((err) => {
          setError(err.message || 'Failed to load vital history');
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [isOpen, patientId, vitalType]);

  // Handle ESC key
  useEffect(() => {
    function handleEscape(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        onClose();
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleExportCSV = () => {
    if (!historyData) return;

    const headers = ['Date', 'Value', 'Unit', 'Status', 'Location', 'Recorded By'];
    const rows = historyData.history.map((entry) => [
      new Date(entry.recordedAt).toISOString(),
      entry.value.toString(),
      entry.unit,
      entry.status,
      entry.location || '',
      entry.recordedBy || '',
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.map((cell) => `"${cell}"`).join(',')),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `${vitalType}_history.csv`);
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-deep-ice/50 z-40"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <div
          className={cn(
            'bg-white rounded-xl shadow-xl',
            'w-full max-w-3xl max-h-[90vh]',
            'flex flex-col'
          )}
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-frost">
            <div>
              <h2
                id="modal-title"
                className="text-[20px] font-semibold text-text-primary"
              >
                {config.label} History
              </h2>
              {historyData?.trendAnalysis && (
                <div className="mt-2">
                  <VitalTrendIndicator
                    trend={historyData.trendAnalysis}
                    showDetails
                  />
                </div>
              )}
            </div>
            <button
              type="button"
              onClick={onClose}
              className="p-2 text-text-tertiary hover:text-text-primary hover:bg-frost/50 rounded-lg transition-colors"
              aria-label="Close modal"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Tabs and Actions */}
          <div className="flex items-center justify-between px-6 py-3 border-b border-frost">
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setViewMode('graph')}
                className={cn(
                  'px-4 py-2 rounded-lg text-[15px] font-medium transition-colors',
                  viewMode === 'graph'
                    ? 'bg-glacier-blue text-white'
                    : 'text-text-secondary hover:bg-frost/50'
                )}
              >
                Graph
              </button>
              <button
                type="button"
                onClick={() => setViewMode('table')}
                className={cn(
                  'px-4 py-2 rounded-lg text-[15px] font-medium transition-colors',
                  viewMode === 'table'
                    ? 'bg-glacier-blue text-white'
                    : 'text-text-secondary hover:bg-frost/50'
                )}
              >
                Table
              </button>
            </div>
            <button
              type="button"
              onClick={handleExportCSV}
              disabled={!historyData || historyData.history.length === 0}
              className={cn(
                'px-4 py-2 rounded-lg text-[15px] font-medium',
                'text-text-secondary hover:bg-frost/50 transition-colors',
                'disabled:opacity-50 disabled:cursor-not-allowed'
              )}
            >
              Export CSV
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-auto p-6">
            {loading && (
              <div className="flex items-center justify-center py-12">
                <div className="text-text-tertiary text-[15px]">
                  Loading history...
                </div>
              </div>
            )}

            {error && (
              <div className="flex items-center justify-center py-12">
                <div className="text-status-critical text-[15px]">{error}</div>
              </div>
            )}

            {!loading && !error && historyData && (
              <>
                {viewMode === 'graph' && (
                  <div className="flex justify-center">
                    <VitalTrendGraph
                      history={historyData.history}
                      referenceRange={historyData.referenceRange}
                      unit={historyData.unit}
                      width={600}
                      height={300}
                    />
                  </div>
                )}

                {viewMode === 'table' && (
                  <VitalHistoryTable
                    history={historyData.history}
                    unit={historyData.unit}
                  />
                )}
              </>
            )}
          </div>

          {/* Footer */}
          <div className="flex justify-end px-6 py-4 border-t border-frost">
            <button
              type="button"
              onClick={onClose}
              className={cn(
                'px-6 py-2 rounded-lg text-[15px] font-medium',
                'bg-frost/50 text-text-primary hover:bg-frost transition-colors'
              )}
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
