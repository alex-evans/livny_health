import { useState, useEffect } from 'react';
import type {
  ImagingStudy,
  ImagingModality,
  ReportStatus,
  ImagingTimeRange,
  ImagingGroupBy,
  RadiologyReport,
} from '../../types/imaging';
import { MODALITY_NAMES } from '../../types/imaging';
import { getImagingStudies } from '../../api/imagingApi';
import { DicomViewerModal } from './DicomViewerModal';
import { Card, CardContent, Button } from '../ui';
import { cn } from '../../utils/cn';

interface ImagingSectionProps {
  patientId: string;
}

// Status badge configuration
const reportStatusConfig: Record<ReportStatus, { label: string; badgeClass: string }> = {
  final: { label: 'Final', badgeClass: 'bg-frost text-text-primary' },
  preliminary: { label: 'Preliminary', badgeClass: 'bg-warning/20 text-warning' },
  pending: { label: 'Pending', badgeClass: 'bg-deep-ice/20 text-deep-ice' },
  addendum: { label: 'Addendum', badgeClass: 'bg-glacier-blue/20 text-glacier-blue' },
};

// Modality icons
function getModalityIcon(modality: ImagingModality): React.ReactNode {
  const iconClass = 'w-5 h-5';
  switch (modality) {
    case 'CT':
      return (
        <svg className={iconClass} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <circle cx="12" cy="12" r="4" />
          <line x1="4.93" y1="4.93" x2="9.17" y2="9.17" />
          <line x1="14.83" y1="14.83" x2="19.07" y2="19.07" />
        </svg>
      );
    case 'MRI':
      return (
        <svg className={iconClass} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="2" y="6" width="20" height="12" rx="2" />
          <line x1="6" y1="6" x2="6" y2="18" />
          <line x1="18" y1="6" x2="18" y2="18" />
          <ellipse cx="12" cy="12" rx="3" ry="4" />
        </svg>
      );
    case 'XR':
      return (
        <svg className={iconClass} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="4" y="2" width="16" height="20" rx="2" />
          <circle cx="12" cy="9" r="3" />
          <path d="M9 16h6" />
          <path d="M12 13v5" />
        </svg>
      );
    case 'US':
      return (
        <svg className={iconClass} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2a10 10 0 0110 10c0 4.42-10 12-10 12S2 16.42 2 12A10 10 0 0112 2z" />
          <circle cx="12" cy="10" r="3" />
        </svg>
      );
    case 'MAMMO':
      return (
        <svg className={iconClass} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 4h16v16H4z" />
          <circle cx="9" cy="12" r="4" />
          <circle cx="15" cy="12" r="4" />
        </svg>
      );
    default:
      return (
        <svg className={iconClass} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <path d="M21 15l-5-5L5 21" />
        </svg>
      );
  }
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
  return `${Math.floor(diffDays / 365)} years ago`;
}

// Time range filter options
const timeRangeOptions: { value: ImagingTimeRange; label: string }[] = [
  { value: '30', label: '30 Days' },
  { value: '90', label: '90 Days' },
  { value: '365', label: '1 Year' },
  { value: '730', label: '2 Years' },
  { value: 'all', label: 'All Time' },
];

export function ImagingSection({ patientId }: ImagingSectionProps) {
  const [studies, setStudies] = useState<ImagingStudy[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter state
  const [timeRange, setTimeRange] = useState<ImagingTimeRange>('730');
  const [modalityFilter, setModalityFilter] = useState<ImagingModality | 'all'>('all');
  const [groupBy, setGroupBy] = useState<ImagingGroupBy>('chronological');
  const [searchQuery, setSearchQuery] = useState('');

  // Expanded states
  const [expandedStudyIds, setExpandedStudyIds] = useState<Set<string>>(new Set());

  // Modal state
  const [selectedStudy, setSelectedStudy] = useState<ImagingStudy | null>(null);
  const [isViewerOpen, setIsViewerOpen] = useState(false);

  // Fetch studies
  useEffect(() => {
    const fetchStudies = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const daysBack = timeRange === 'all' ? undefined : parseInt(timeRange);
        const response = await getImagingStudies(patientId, { daysBack });
        setStudies(response.studies);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load imaging studies');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStudies();
  }, [patientId, timeRange]);

  // Toggle study expansion
  const toggleExpanded = (id: string) => {
    setExpandedStudyIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  // Open viewer modal
  const handleViewImages = (study: ImagingStudy) => {
    setSelectedStudy(study);
    setIsViewerOpen(true);
  };

  // Filter and search studies
  const filteredStudies = studies.filter((study) => {
    // Modality filter
    if (modalityFilter !== 'all' && study.modality !== modalityFilter) {
      return false;
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const searchText = [
        study.bodyPart,
        study.modalityName,
        study.indication,
        study.orderingProvider,
        study.facility,
        study.report?.impression,
        study.report?.findings,
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();
      if (!searchText.includes(query)) {
        return false;
      }
    }

    return true;
  });

  // Group studies if needed
  const groupedStudies = groupBy === 'modality'
    ? Object.entries(
        filteredStudies.reduce<Record<ImagingModality, ImagingStudy[]>>((acc, study) => {
          if (!acc[study.modality]) {
            acc[study.modality] = [];
          }
          acc[study.modality].push(study);
          return acc;
        }, {} as Record<ImagingModality, ImagingStudy[]>)
      ).sort((a, b) => a[0].localeCompare(b[0]))
    : null;

  // Get unique modalities for filter
  const availableModalities = Array.from(new Set(studies.map((s) => s.modality))).sort();

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-generous">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-glacier-blue border-t-transparent" />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <Card className="border-2 border-dashed border-critical/30">
        <CardContent>
          <div className="text-center py-normal">
            <svg
              className="w-8 h-8 text-critical mx-auto mb-tight"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <p className="text-[15px] text-critical">{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Empty state
  if (studies.length === 0) {
    return (
      <Card className="border-2 border-dashed border-frost">
        <CardContent>
          <div className="text-center py-generous">
            <svg
              className="w-12 h-12 text-text-tertiary mx-auto mb-normal"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
            >
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <path d="M21 15l-5-5L5 21" />
            </svg>
            <p className="text-[15px] text-text-tertiary">No imaging studies on file</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div>
      {/* Filter Bar */}
      <Card className="mb-normal">
        <CardContent>
          <div className="flex flex-wrap items-center gap-normal">
            {/* Time Range Filter */}
            <div className="flex items-center gap-tight">
              <span className="text-[13px] text-text-tertiary">Time:</span>
              <div className="flex gap-1">
                {timeRangeOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => setTimeRange(option.value)}
                    className={cn(
                      'px-2 py-1 text-[11px] font-medium rounded transition-colors',
                      timeRange === option.value
                        ? 'bg-deep-ice text-white'
                        : 'bg-frost/50 text-text-secondary hover:bg-frost'
                    )}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Modality Filter */}
            {availableModalities.length > 1 && (
              <div className="flex items-center gap-tight">
                <span className="text-[13px] text-text-tertiary">Modality:</span>
                <div className="flex gap-1">
                  <button
                    onClick={() => setModalityFilter('all')}
                    className={cn(
                      'px-2 py-1 text-[11px] font-medium rounded transition-colors',
                      modalityFilter === 'all'
                        ? 'bg-deep-ice text-white'
                        : 'bg-frost/50 text-text-secondary hover:bg-frost'
                    )}
                  >
                    All
                  </button>
                  {availableModalities.map((modality) => (
                    <button
                      key={modality}
                      onClick={() => setModalityFilter(modality)}
                      className={cn(
                        'px-2 py-1 text-[11px] font-medium rounded transition-colors',
                        modalityFilter === modality
                          ? 'bg-deep-ice text-white'
                          : 'bg-frost/50 text-text-secondary hover:bg-frost'
                      )}
                    >
                      {modality}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Group By Toggle */}
            <div className="flex items-center gap-tight">
              <span className="text-[13px] text-text-tertiary">Group:</span>
              <div className="flex gap-1">
                <button
                  onClick={() => setGroupBy('chronological')}
                  className={cn(
                    'px-2 py-1 text-[11px] font-medium rounded transition-colors',
                    groupBy === 'chronological'
                      ? 'bg-deep-ice text-white'
                      : 'bg-frost/50 text-text-secondary hover:bg-frost'
                  )}
                >
                  Date
                </button>
                <button
                  onClick={() => setGroupBy('modality')}
                  className={cn(
                    'px-2 py-1 text-[11px] font-medium rounded transition-colors',
                    groupBy === 'modality'
                      ? 'bg-deep-ice text-white'
                      : 'bg-frost/50 text-text-secondary hover:bg-frost'
                  )}
                >
                  Modality
                </button>
              </div>
            </div>

            {/* Search */}
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <svg
                  className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-text-tertiary"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
                <input
                  type="text"
                  placeholder="Search studies..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-8 pr-3 py-1.5 text-[13px] border border-frost rounded-md focus:outline-none focus:ring-2 focus:ring-glacier-blue/50"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results count */}
      <div className="flex items-center justify-between mb-tight">
        <span className="text-[13px] text-text-tertiary">
          {filteredStudies.length} {filteredStudies.length === 1 ? 'study' : 'studies'}
        </span>
      </div>

      {/* No results after filter */}
      {filteredStudies.length === 0 && (
        <Card className="border-2 border-dashed border-frost">
          <CardContent>
            <div className="text-center py-normal">
              <p className="text-[15px] text-text-tertiary">No studies match your filters</p>
              <button
                onClick={() => {
                  setModalityFilter('all');
                  setSearchQuery('');
                  setTimeRange('730');
                }}
                className="mt-tight text-[13px] text-glacier-blue hover:underline"
              >
                Clear filters
              </button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Studies List - Grouped by Modality */}
      {groupBy === 'modality' && groupedStudies && (
        <div className="space-y-normal">
          {groupedStudies.map(([modality, modalityStudies]) => (
            <div key={modality}>
              <div className="flex items-center gap-tight mb-tight">
                <span className="text-deep-ice">{getModalityIcon(modality as ImagingModality)}</span>
                <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                  {MODALITY_NAMES[modality as ImagingModality]} ({modalityStudies.length})
                </h3>
              </div>
              <div className="space-y-tight">
                {modalityStudies.map((study) => (
                  <ImagingStudyCard
                    key={study.id}
                    study={study}
                    isExpanded={expandedStudyIds.has(study.id)}
                    onToggleExpand={() => toggleExpanded(study.id)}
                    onViewImages={() => handleViewImages(study)}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Studies List - Chronological */}
      {groupBy === 'chronological' && filteredStudies.length > 0 && (
        <div className="space-y-tight">
          {filteredStudies.map((study) => (
            <ImagingStudyCard
              key={study.id}
              study={study}
              isExpanded={expandedStudyIds.has(study.id)}
              onToggleExpand={() => toggleExpanded(study.id)}
              onViewImages={() => handleViewImages(study)}
            />
          ))}
        </div>
      )}

      {/* DICOM Viewer Modal */}
      <DicomViewerModal
        isOpen={isViewerOpen}
        onClose={() => setIsViewerOpen(false)}
        study={selectedStudy}
      />
    </div>
  );
}

// Study Card Component
interface ImagingStudyCardProps {
  study: ImagingStudy;
  isExpanded: boolean;
  onToggleExpand: () => void;
  onViewImages: () => void;
}

function ImagingStudyCard({
  study,
  isExpanded,
  onToggleExpand,
  onViewImages,
}: ImagingStudyCardProps) {
  const statusConfig = reportStatusConfig[study.reportStatus];
  const hasReport = study.report && study.reportStatus !== 'pending';

  return (
    <Card
      className={cn(
        'transition-all',
        isExpanded && 'ring-2 ring-glacier-blue/30',
        study.report?.criticalFinding && 'border-l-4 border-l-critical'
      )}
    >
      <CardContent>
        {/* Header Row */}
        <div
          className="flex items-start gap-normal cursor-pointer"
          onClick={onToggleExpand}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              onToggleExpand();
            }
          }}
          aria-expanded={isExpanded}
        >
          {/* Modality Icon */}
          <div className="flex-shrink-0 p-2 bg-frost/50 rounded-md text-deep-ice">
            {getModalityIcon(study.modality)}
          </div>

          {/* Main Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-tight flex-wrap">
              <h4 className="text-[15px] font-medium text-text-primary">
                {study.bodyPart}
              </h4>
              <span className="text-[13px] text-text-tertiary">
                {study.modalityName}
              </span>
              <span className={cn('px-2 py-0.5 text-[11px] font-medium rounded', statusConfig.badgeClass)}>
                {statusConfig.label}
              </span>
              {study.report?.criticalFinding && (
                <span className="flex items-center gap-1 px-2 py-0.5 text-[11px] font-semibold text-critical bg-critical/10 rounded">
                  Critical Finding
                </span>
              )}
            </div>

            <div className="flex items-center gap-normal mt-1 text-[13px] text-text-tertiary flex-wrap">
              <span>{formatDate(study.studyDate)}</span>
              <span className="text-text-tertiary/50">({formatTimeAgo(study.studyDate)})</span>
              <span className="text-text-tertiary/50">·</span>
              <span>{study.orderingProvider}</span>
              {study.readingRadiologist && (
                <>
                  <span className="text-text-tertiary/50">·</span>
                  <span>Read by: {study.readingRadiologist}</span>
                </>
              )}
            </div>

            {/* Indication */}
            <p className="mt-1 text-[13px] text-text-secondary line-clamp-1">
              {study.indication}
            </p>

            {/* Report Preview (first 3 lines of impression) */}
            {hasReport && study.report?.impression && !isExpanded && (
              <p className="mt-tight text-[13px] text-text-secondary line-clamp-2 italic">
                {study.report.impression}
              </p>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center gap-tight flex-shrink-0">
            {study.hasImages && (
              <span onClick={(e) => e.stopPropagation()}>
                <Button
                  variant="secondary"
                  onClick={onViewImages}
                  className="text-[13px]"
                >
                  <svg
                    className="w-4 h-4 mr-1"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <rect x="3" y="3" width="18" height="18" rx="2" />
                    <circle cx="8.5" cy="8.5" r="1.5" />
                    <path d="M21 15l-5-5L5 21" />
                  </svg>
                  View Images
                </Button>
              </span>
            )}
            <button
              onClick={(e) => {
                e.stopPropagation();
                onToggleExpand();
              }}
              className="p-2 hover:bg-frost rounded-md transition-colors"
              aria-label={isExpanded ? 'Collapse' : 'Expand'}
            >
              <svg
                className={cn('w-5 h-5 text-text-tertiary transition-transform', isExpanded && 'rotate-180')}
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </button>
          </div>
        </div>

        {/* Expanded Report Content */}
        {isExpanded && hasReport && study.report && (
          <div className="mt-normal pt-normal border-t border-frost">
            <ReportSection report={study.report} />
          </div>
        )}

        {/* Expanded - Pending Report */}
        {isExpanded && study.reportStatus === 'pending' && (
          <div className="mt-normal pt-normal border-t border-frost">
            <div className="text-center py-normal">
              <svg
                className="w-8 h-8 text-text-tertiary mx-auto mb-tight"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
              <p className="text-[15px] text-text-tertiary">Report pending</p>
              <p className="text-[13px] text-text-tertiary/70 mt-1">
                This study is awaiting interpretation by a radiologist
              </p>
            </div>
          </div>
        )}

        {/* Study Details Footer */}
        {isExpanded && (
          <div className="mt-normal pt-normal border-t border-frost">
            <div className="flex flex-wrap gap-normal text-[13px] text-text-tertiary">
              <span>Facility: {study.facility}</span>
              <span className="text-text-tertiary/50">·</span>
              <span>{study.seriesCount} series, {study.imageCount} images</span>
              {study.accessionNumber && (
                <>
                  <span className="text-text-tertiary/50">·</span>
                  <span>Accession: {study.accessionNumber}</span>
                </>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Report Section Component
interface ReportSectionProps {
  report: RadiologyReport;
}

function ReportSection({ report }: ReportSectionProps) {
  return (
    <div className="space-y-normal">
      {/* Clinical Indication */}
      <div>
        <h5 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-1">
          Clinical Indication
        </h5>
        <p className="text-[13px] text-text-secondary whitespace-pre-wrap">
          {report.clinicalIndication}
        </p>
      </div>

      {/* Technique */}
      <div>
        <h5 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-1">
          Technique
        </h5>
        <p className="text-[13px] text-text-secondary whitespace-pre-wrap">
          {report.technique}
        </p>
      </div>

      {/* Comparison Studies */}
      {report.comparisonStudies && report.comparisonStudies.length > 0 && (
        <div>
          <h5 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-1">
            Comparison Studies
          </h5>
          <ul className="text-[13px] text-text-secondary">
            {report.comparisonStudies.map((comp) => (
              <li key={comp.studyId}>
                {comp.modality} {comp.bodyPart} - {formatDate(comp.date)}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Findings */}
      <div>
        <h5 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-1">
          Findings
        </h5>
        <p className="text-[13px] text-text-secondary whitespace-pre-wrap">
          {report.findings}
        </p>
      </div>

      {/* Impression */}
      <div className={cn(report.criticalFinding && 'p-3 bg-critical/5 border border-critical/20 rounded-md')}>
        <h5 className={cn(
          'text-[11px] font-medium uppercase tracking-wide mb-1',
          report.criticalFinding ? 'text-critical' : 'text-text-tertiary'
        )}>
          Impression
          {report.criticalFinding && ' (Critical Finding)'}
        </h5>
        <p className="text-[13px] text-text-secondary whitespace-pre-wrap font-medium">
          {report.impression}
        </p>
      </div>

      {/* Addendum */}
      {report.addendum && (
        <div className="p-3 bg-glacier-blue/5 border border-glacier-blue/20 rounded-md">
          <h5 className="text-[11px] font-medium uppercase tracking-wide text-glacier-blue mb-1">
            Addendum
          </h5>
          <p className="text-[13px] text-text-secondary whitespace-pre-wrap">
            {report.addendum}
          </p>
        </div>
      )}
    </div>
  );
}
