import { useEffect, useCallback } from 'react';
import type { ImagingStudy } from '../../types/imaging';
import { Button, Card, CardContent } from '../ui';

interface DicomViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  study: ImagingStudy | null;
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

export function DicomViewerModal({
  isOpen,
  onClose,
  study,
}: DicomViewerModalProps) {
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

  if (!isOpen || !study) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="dicom-viewer-title"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-hidden animate-in fade-in-0 zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-frost">
          <div>
            <h2
              id="dicom-viewer-title"
              className="text-[18px] font-semibold text-text-primary"
            >
              DICOM Viewer
            </h2>
            <p className="text-[13px] text-text-tertiary mt-0.5">
              {study.modalityName} - {study.bodyPart}
            </p>
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
          {/* Study Information Card */}
          <Card className="mb-normal">
            <CardContent>
              <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-normal">
                Study Information
              </h3>
              <div className="grid grid-cols-2 gap-normal">
                <div>
                  <p className="text-[13px] text-text-tertiary">Study Date</p>
                  <p className="text-[15px] text-text-primary">{formatDate(study.studyDate)}</p>
                </div>
                <div>
                  <p className="text-[13px] text-text-tertiary">Accession #</p>
                  <p className="text-[15px] text-text-primary">{study.accessionNumber || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-[13px] text-text-tertiary">Modality</p>
                  <p className="text-[15px] text-text-primary">{study.modalityName}</p>
                </div>
                <div>
                  <p className="text-[13px] text-text-tertiary">Body Part</p>
                  <p className="text-[15px] text-text-primary">{study.bodyPart}</p>
                </div>
                <div>
                  <p className="text-[13px] text-text-tertiary">Series Count</p>
                  <p className="text-[15px] text-text-primary">{study.seriesCount}</p>
                </div>
                <div>
                  <p className="text-[13px] text-text-tertiary">Image Count</p>
                  <p className="text-[15px] text-text-primary">{study.imageCount}</p>
                </div>
                <div>
                  <p className="text-[13px] text-text-tertiary">Ordering Provider</p>
                  <p className="text-[15px] text-text-primary">{study.orderingProvider}</p>
                </div>
                <div>
                  <p className="text-[13px] text-text-tertiary">Facility</p>
                  <p className="text-[15px] text-text-primary">{study.facility}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Placeholder Viewer Area */}
          <Card className="mb-normal">
            <CardContent>
              <div className="bg-text-primary rounded-lg p-generous flex flex-col items-center justify-center min-h-[300px]">
                {/* Placeholder Icon */}
                <svg
                  className="w-16 h-16 text-text-tertiary/50 mb-normal"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                >
                  <rect x="2" y="2" width="20" height="20" rx="2" />
                  <circle cx="8" cy="8" r="2" />
                  <path d="M21 15l-5-5L5 21" />
                </svg>

                <h3 className="text-[18px] font-medium text-white mb-tight">
                  OHIF DICOM Viewer Integration
                </h3>

                <p className="text-[15px] text-text-tertiary text-center max-w-md">
                  In a production environment, this area would display an integrated DICOM viewer
                  (such as OHIF Viewer) allowing you to view and manipulate medical imaging data.
                </p>

                <div className="mt-normal flex flex-wrap gap-tight justify-center">
                  <span className="px-3 py-1.5 bg-white/10 rounded-md text-[13px] text-white/80">
                    Windowing/Leveling
                  </span>
                  <span className="px-3 py-1.5 bg-white/10 rounded-md text-[13px] text-white/80">
                    Pan/Zoom
                  </span>
                  <span className="px-3 py-1.5 bg-white/10 rounded-md text-[13px] text-white/80">
                    Measurements
                  </span>
                  <span className="px-3 py-1.5 bg-white/10 rounded-md text-[13px] text-white/80">
                    3D MPR
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <div className="flex flex-wrap gap-tight justify-center">
            <Button variant="secondary" disabled>
              <svg className="w-4 h-4 mr-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" />
              </svg>
              Export Images
            </Button>
            <Button variant="secondary" disabled>
              <svg className="w-4 h-4 mr-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" />
              </svg>
              Share Study
            </Button>
            <Button variant="secondary" disabled>
              <svg className="w-4 h-4 mr-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <path d="M3 9h18M9 21V9" />
              </svg>
              Compare Studies
            </Button>
          </div>
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
