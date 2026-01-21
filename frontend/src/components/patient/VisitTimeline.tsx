import { useState, useMemo, useCallback, useEffect, useRef } from 'react';
import type { Visit, EncounterType, VisitHistoryResponse, VisitVitals, VisitMedication, VisitOrder, SOAPNote, VisitHistoryParams, VisitProviderOption } from '../../types';
import { Card, CardContent } from '../ui';
import { getVisitHistory, getVisitProviders } from '../../api';
import { cn } from '../../utils/cn';
import { useDebounce } from '../../hooks';
import { VisitTimelineFilters } from './VisitTimelineFilters';

interface VisitTimelineProps {
  patientId: string;
  activeEncounterDate?: string; // ISO date string for today's active encounter, if any
  onNavigateToSection?: (section: 'medications' | 'labs') => void; // Navigate to other chart sections
}

// Type for tracking selected visits for print/copy
type SelectedVisits = Set<string>;

type TimeRangeOption = '12months' | 'all';

const timeRangeOptions: { value: TimeRangeOption; label: string }[] = [
  { value: '12months', label: 'Last 12 Months' },
  { value: 'all', label: 'All Visits' },
];

const VISITS_PER_PAGE = 10;

// Visit type configuration with enhanced styling for significant visits
const visitTypeConfig: Record<EncounterType, { label: string; iconClass: string; bgClass: string; isSignificant?: boolean }> = {
  office_visit: {
    label: 'Office Visit',
    iconClass: 'text-glacier-blue',
    bgClass: 'bg-glacier-blue/10',
  },
  telehealth: {
    label: 'Telehealth',
    iconClass: 'text-success',
    bgClass: 'bg-success/10',
  },
  urgent_care: {
    label: 'Urgent Care',
    iconClass: 'text-warning',
    bgClass: 'bg-warning/10',
  },
  emergency: {
    label: 'Emergency',
    iconClass: 'text-critical',
    bgClass: 'bg-critical/10',
    isSignificant: true,
  },
  hospital_admission: {
    label: 'Hospital Admission',
    iconClass: 'text-critical',
    bgClass: 'bg-critical/10',
    isSignificant: true,
  },
  procedure: {
    label: 'Procedure',
    iconClass: 'text-deep-ice',
    bgClass: 'bg-deep-ice/10',
  },
  lab_only: {
    label: 'Lab Only',
    iconClass: 'text-frost',
    bgClass: 'bg-frost/30',
  },
  follow_up: {
    label: 'Follow-Up',
    iconClass: 'text-glacier-blue',
    bgClass: 'bg-glacier-blue/10',
  },
  annual_physical: {
    label: 'Annual Physical',
    iconClass: 'text-deep-ice',
    bgClass: 'bg-deep-ice/15',
    isSignificant: true,
  },
};

function formatDateShort(dateString: string): { month: string; day: string; year: string } {
  const date = new Date(dateString);
  return {
    month: date.toLocaleDateString('en-US', { month: 'short' }),
    day: String(date.getDate()),
    year: String(date.getFullYear()),
  };
}

function formatDateWithDayOfWeek(dateString: string): string {
  const date = new Date(dateString);
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const year = date.getFullYear();
  const dayOfWeek = date.toLocaleDateString('en-US', { weekday: 'long' });
  return `${month}/${day}/${year} - ${dayOfWeek}`;
}

function formatTime(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
}

function formatTimeRange(dateString: string, durationMinutes?: number): string {
  const startDate = new Date(dateString);
  const startTime = formatTime(dateString);

  if (!durationMinutes) {
    return startTime;
  }

  const endDate = new Date(startDate.getTime() + durationMinutes * 60 * 1000);
  const endTime = endDate.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });

  return `${startTime} - ${endTime}`;
}

function formatFullDate(dateString: string): string {
  const date = new Date(dateString);
  const options: Intl.DateTimeFormatOptions = {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  };
  return date.toLocaleDateString('en-US', options);
}

function isToday(dateString: string): boolean {
  const date = new Date(dateString);
  const today = new Date();
  return (
    date.getFullYear() === today.getFullYear() &&
    date.getMonth() === today.getMonth() &&
    date.getDate() === today.getDate()
  );
}

// Calculate time gap between two dates and return a human-readable string
function getTimeGap(date1: string, date2: string): { days: number; label: string } | null {
  const d1 = new Date(date1);
  const d2 = new Date(date2);
  const diffTime = Math.abs(d1.getTime() - d2.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  // Only show gap if it's more than 14 days
  if (diffDays <= 14) return null;

  if (diffDays >= 365) {
    const years = Math.floor(diffDays / 365);
    const months = Math.floor((diffDays % 365) / 30);
    if (months > 0) {
      return { days: diffDays, label: `${years} year${years > 1 ? 's' : ''}, ${months} month${months > 1 ? 's' : ''} gap` };
    }
    return { days: diffDays, label: `${years} year${years > 1 ? 's' : ''} gap` };
  } else if (diffDays >= 30) {
    const months = Math.floor(diffDays / 30);
    return { days: diffDays, label: `${months} month${months > 1 ? 's' : ''} gap` };
  } else if (diffDays >= 7) {
    const weeks = Math.floor(diffDays / 7);
    return { days: diffDays, label: `${weeks} week${weeks > 1 ? 's' : ''} gap` };
  }

  return { days: diffDays, label: `${diffDays} days gap` };
}

function groupVisitsByMonth(visits: Visit[]): Map<string, Visit[]> {
  const grouped = new Map<string, Visit[]>();

  for (const visit of visits) {
    const date = new Date(visit.date);
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;

    if (!grouped.has(key)) {
      grouped.set(key, []);
    }
    grouped.get(key)!.push(visit);
  }

  return grouped;
}

function getMonthLabel(key: string): string {
  const [year, month] = key.split('-');
  const date = new Date(parseInt(year), parseInt(month) - 1, 1);
  return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
}

export function VisitTimeline({ patientId, activeEncounterDate, onNavigateToSection }: VisitTimelineProps) {
  const [timeRange, setTimeRange] = useState<TimeRangeOption>('12months');
  const [visits, setVisits] = useState<Visit[]>([]);
  const [providers, setProviders] = useState<VisitProviderOption[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedVisitIds, setExpandedVisitIds] = useState<Set<string>>(new Set());
  const [totalCount, setTotalCount] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const loadMoreRef = useRef<HTMLDivElement>(null);

  // Selection state for print/copy
  const [selectedVisitIds, setSelectedVisitIds] = useState<SelectedVisits>(new Set());
  const [isSelectionMode, setIsSelectionMode] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);

  // Filter state
  const [filters, setFilters] = useState<VisitHistoryParams>({
    limit: VISITS_PER_PAGE,
    offset: 0,
    daysBack: 365,
  });

  // Debounce search query
  const debouncedSearchQuery = useDebounce(filters.searchQuery, 300);

  // Build params for API call
  const apiParams = useMemo<VisitHistoryParams>(() => ({
    ...filters,
    searchQuery: debouncedSearchQuery,
    daysBack: timeRange === 'all' ? 3650 : 365,
    includeAll: timeRange === 'all',
  }), [filters, debouncedSearchQuery, timeRange]);

  // Load providers
  useEffect(() => {
    async function loadProviders() {
      try {
        const response = await getVisitProviders(patientId);
        setProviders(response.providers);
      } catch {
        // Non-critical, ignore errors
      }
    }
    loadProviders();
  }, [patientId]);

  const loadVisits = useCallback(async (append = false) => {
    if (append) {
      setIsLoadingMore(true);
    } else {
      setIsLoading(true);
    }
    setError(null);
    try {
      const params: VisitHistoryParams = {
        ...apiParams,
        offset: append ? visits.length : 0,
      };
      const response: VisitHistoryResponse = await getVisitHistory(patientId, params);

      if (append) {
        setVisits((prev) => [...prev, ...response.visits]);
      } else {
        setVisits(response.visits);
      }
      setTotalCount(response.totalCount);
      setHasMore(response.hasMore);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load visits');
    } finally {
      setIsLoading(false);
      setIsLoadingMore(false);
    }
  }, [patientId, apiParams, visits.length]);

  // Initial load and filter changes
  useEffect(() => {
    loadVisits(false);
  }, [patientId, apiParams]); // eslint-disable-line react-hooks/exhaustive-deps

  // Infinite scroll observer
  useEffect(() => {
    if (!loadMoreRef.current || isLoading || isLoadingMore || !hasMore) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !isLoadingMore) {
          loadVisits(true);
        }
      },
      { threshold: 0.1 }
    );

    observer.observe(loadMoreRef.current);
    return () => observer.disconnect();
  }, [hasMore, isLoading, isLoadingMore, loadVisits]);

  // Filter out today's active encounter and in_progress visits
  const filteredVisits = useMemo(() => {
    let result = visits;

    // Exclude today's active encounter if provided
    if (activeEncounterDate) {
      result = result.filter((visit) => {
        const visitDate = new Date(visit.date).toDateString();
        const activeDate = new Date(activeEncounterDate).toDateString();
        return visitDate !== activeDate || visit.status === 'completed' || visit.status === 'cancelled';
      });
    }

    // Exclude any in_progress visits (these are "active encounters")
    result = result.filter((visit) => visit.status !== 'in_progress');

    return result;
  }, [visits, activeEncounterDate]);

  // Group visits by month
  const groupedVisits = useMemo(() => groupVisitsByMonth(filteredVisits), [filteredVisits]);

  // Get the primary provider (most common provider)
  const primaryProviderId = useMemo(() => {
    const providerCounts = new Map<string, number>();
    for (const visit of filteredVisits) {
      const id = visit.provider.id;
      providerCounts.set(id, (providerCounts.get(id) || 0) + 1);
    }
    let maxCount = 0;
    let primaryId = '';
    for (const [id, count] of providerCounts) {
      if (count > maxCount) {
        maxCount = count;
        primaryId = id;
      }
    }
    return primaryId;
  }, [filteredVisits]);

  const toggleVisit = (id: string) => {
    setExpandedVisitIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleFiltersChange = (newFilters: VisitHistoryParams) => {
    setFilters({
      ...newFilters,
      offset: 0, // Reset pagination on filter change
    });
  };

  const handleJumpToDate = (date: string) => {
    // Set date filter to show visits from that date onwards
    setFilters((prev) => ({
      ...prev,
      dateFrom: date,
      dateTo: undefined, // Clear end date
      offset: 0,
    }));
  };

  // Filter by diagnosis code - called when user clicks a diagnosis
  const handleFilterByDiagnosis = (diagnosisCode: string) => {
    setFilters((prev) => ({
      ...prev,
      diagnosisCode,
      offset: 0,
    }));
  };

  // Filter by provider - called when user clicks a provider name
  const handleFilterByProvider = (providerId: string) => {
    setFilters((prev) => ({
      ...prev,
      providerId,
      offset: 0,
    }));
  };

  // Toggle selection mode
  const toggleSelectionMode = () => {
    setIsSelectionMode((prev) => {
      if (prev) {
        // Exiting selection mode, clear selections
        setSelectedVisitIds(new Set());
      }
      return !prev;
    });
  };

  // Toggle visit selection
  const toggleVisitSelection = (visitId: string, event: React.MouseEvent) => {
    event.stopPropagation(); // Prevent expand/collapse
    setSelectedVisitIds((prev) => {
      const next = new Set(prev);
      if (next.has(visitId)) {
        next.delete(visitId);
      } else {
        next.add(visitId);
      }
      return next;
    });
  };

  // Select all visible visits
  const selectAllVisits = () => {
    setSelectedVisitIds(new Set(filteredVisits.map((v) => v.id)));
  };

  // Clear all selections
  const clearSelections = () => {
    setSelectedVisitIds(new Set());
  };

  // Format visit for text output (clipboard/print)
  const formatVisitForText = (visit: Visit): string => {
    const lines: string[] = [];
    const dateStr = formatDateWithDayOfWeek(visit.date);
    const config = visitTypeConfig[visit.visitType];

    lines.push(`${'='.repeat(60)}`);
    lines.push(`${config.label} - ${dateStr}`);
    lines.push(`Provider: ${visit.provider.name}${visit.provider.specialty ? ` (${visit.provider.specialty})` : ''}`);
    if (visit.location) lines.push(`Location: ${visit.location}`);
    lines.push(`${'='.repeat(60)}`);
    lines.push('');

    lines.push(`CHIEF COMPLAINT: ${visit.chiefComplaint}`);
    lines.push('');

    if (visit.diagnoses.length > 0) {
      lines.push('DIAGNOSES:');
      visit.diagnoses.forEach((dx) => {
        lines.push(`  - ${dx.description} (${dx.code})${dx.isPrimary ? ' [Primary]' : ''}`);
      });
      lines.push('');
    }

    if (visit.soapNote) {
      lines.push('SUBJECTIVE:');
      lines.push(visit.soapNote.subjective);
      lines.push('');
      lines.push('OBJECTIVE:');
      lines.push(visit.soapNote.objective);
      lines.push('');
      lines.push('ASSESSMENT:');
      lines.push(visit.soapNote.assessment);
      lines.push('');
      lines.push('PLAN:');
      lines.push(visit.soapNote.plan);
      lines.push('');
    }

    if (visit.vitals) {
      const vitals = visit.vitals;
      const vitalParts: string[] = [];
      if (vitals.bloodPressureSystolic && vitals.bloodPressureDiastolic) {
        vitalParts.push(`BP: ${vitals.bloodPressureSystolic}/${vitals.bloodPressureDiastolic} mmHg`);
      }
      if (vitals.heartRate) vitalParts.push(`HR: ${vitals.heartRate} bpm`);
      if (vitals.temperature) vitalParts.push(`Temp: ${vitals.temperature}°${vitals.temperatureUnit || 'F'}`);
      if (vitals.weight) vitalParts.push(`Weight: ${vitals.weight} ${vitals.weightUnit || 'lbs'}`);
      if (vitals.oxygenSaturation) vitalParts.push(`O2 Sat: ${vitals.oxygenSaturation}%`);
      if (vitalParts.length > 0) {
        lines.push('VITAL SIGNS:');
        lines.push(`  ${vitalParts.join(' | ')}`);
        lines.push('');
      }
    }

    if (visit.medications && visit.medications.length > 0) {
      lines.push('MEDICATIONS:');
      visit.medications.forEach((med) => {
        lines.push(`  [${med.action.toUpperCase()}] ${med.name} ${med.dosage} ${med.frequency}`);
        if (med.instructions) lines.push(`    Instructions: ${med.instructions}`);
      });
      lines.push('');
    }

    if (visit.orders && visit.orders.length > 0) {
      lines.push('ORDERS:');
      visit.orders.forEach((order) => {
        lines.push(`  [${order.orderType.toUpperCase()}] ${order.name} - ${order.status}`);
        if (order.result) lines.push(`    Result: ${order.result}`);
      });
      lines.push('');
    }

    if (visit.hasCriticalFindings && visit.criticalFindingsSummary) {
      lines.push('** CRITICAL FINDINGS **');
      lines.push(visit.criticalFindingsSummary);
      lines.push('');
    }

    if (visit.hasFollowUpRequired && visit.followUpSummary) {
      lines.push('FOLLOW-UP REQUIRED:');
      lines.push(visit.followUpSummary);
      lines.push('');
    }

    return lines.join('\n');
  };

  // Copy selected visits to clipboard
  const copyToClipboard = async (visitId?: string) => {
    const visitsToCopy = visitId
      ? filteredVisits.filter((v) => v.id === visitId)
      : filteredVisits.filter((v) => selectedVisitIds.has(v.id));

    if (visitsToCopy.length === 0) return;

    const text = visitsToCopy.map(formatVisitForText).join('\n\n');

    try {
      await navigator.clipboard.writeText(text);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  // Print selected visits
  const printVisits = (visitId?: string) => {
    const visitsToPrint = visitId
      ? filteredVisits.filter((v) => v.id === visitId)
      : filteredVisits.filter((v) => selectedVisitIds.has(v.id));

    if (visitsToPrint.length === 0) return;

    const printContent = visitsToPrint.map(formatVisitForText).join('\n\n');

    const printWindow = window.open('', '_blank');
    if (printWindow) {
      printWindow.document.write(`
        <html>
          <head>
            <title>Visit Notes</title>
            <style>
              body { font-family: 'Courier New', monospace; font-size: 12px; line-height: 1.5; padding: 20px; }
              pre { white-space: pre-wrap; word-wrap: break-word; }
            </style>
          </head>
          <body>
            <pre>${printContent}</pre>
          </body>
        </html>
      `);
      printWindow.document.close();
      printWindow.print();
    }
  };

  // Check if there's an active encounter today
  const hasActiveEncounter = activeEncounterDate && isToday(activeEncounterDate);

  // Search highlighting helper
  const searchQuery = debouncedSearchQuery?.toLowerCase() || '';

  if (isLoading) {
    return (
      <Card className="mb-normal">
        <CardContent>
          <div className="flex items-center gap-tight">
            <ChartNotesIcon className="h-5 w-5 text-text-tertiary" />
            <span className="text-[15px] text-text-tertiary">Loading visit history...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="mb-normal border-2 border-dashed border-critical/30">
        <CardContent>
          <div className="flex items-center gap-tight">
            <ChartNotesIcon className="h-5 w-5 text-critical" />
            <span className="text-[15px] text-critical">{error}</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="mb-normal">
      <CardContent className="relative">
        {/* Copy success toast notification */}
        {copySuccess && (
          <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-4 py-2 bg-success text-white text-[15px] font-medium rounded-lg shadow-lg flex items-center gap-2 animate-fade-in">
            <CheckIcon className="h-4 w-4" />
            Copied to clipboard
          </div>
        )}

        {/* Header */}
        <div className="flex items-center justify-between mb-normal">
          <div className="flex items-center gap-tight">
            <ChartNotesIcon className="h-5 w-5 text-glacier-blue" />
            <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
              Chart Notes
            </h3>
            {totalCount > 0 && (
              <span className="text-[11px] text-text-tertiary">
                ({filteredVisits.length} of {totalCount} visit{totalCount !== 1 ? 's' : ''})
              </span>
            )}
          </div>

          {/* Action buttons and time range */}
          <div className="flex items-center gap-2">
            {/* Selection mode toggle */}
            <button
              type="button"
              onClick={toggleSelectionMode}
              className={cn(
                'px-2 py-1 text-[11px] font-medium rounded transition-colors flex items-center gap-1',
                isSelectionMode
                  ? 'bg-glacier-blue text-white'
                  : 'bg-frost/50 text-text-secondary hover:bg-frost'
              )}
              title={isSelectionMode ? 'Exit selection mode' : 'Select visits to print/copy'}
            >
              <SelectIcon className="h-3 w-3" />
              {isSelectionMode ? 'Done' : 'Select'}
            </button>

            {/* Time range selector */}
            <div className="flex gap-1">
              {timeRangeOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
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
        </div>

        {/* Selection mode toolbar */}
        {isSelectionMode && (
          <div className="mb-normal p-2 bg-arctic rounded-md flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-[13px] text-text-secondary">
                {selectedVisitIds.size} selected
              </span>
              <button
                type="button"
                onClick={selectAllVisits}
                className="text-[13px] text-glacier-blue hover:text-deep-ice transition-colors"
              >
                Select All
              </button>
              {selectedVisitIds.size > 0 && (
                <button
                  type="button"
                  onClick={clearSelections}
                  className="text-[13px] text-text-tertiary hover:text-text-secondary transition-colors"
                >
                  Clear
                </button>
              )}
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => copyToClipboard()}
                disabled={selectedVisitIds.size === 0}
                className={cn(
                  'px-2 py-1 text-[11px] font-medium rounded transition-colors flex items-center gap-1',
                  selectedVisitIds.size > 0
                    ? 'bg-frost text-text-primary hover:bg-frost/70'
                    : 'bg-frost/30 text-text-tertiary cursor-not-allowed'
                )}
                title="Copy selected visits to clipboard"
              >
                <CopyIcon className="h-3 w-3" />
                Copy
              </button>
              <button
                type="button"
                onClick={() => printVisits()}
                disabled={selectedVisitIds.size === 0}
                className={cn(
                  'px-2 py-1 text-[11px] font-medium rounded transition-colors flex items-center gap-1',
                  selectedVisitIds.size > 0
                    ? 'bg-glacier-blue text-white hover:bg-deep-ice'
                    : 'bg-frost/30 text-text-tertiary cursor-not-allowed'
                )}
                title="Print selected visits"
              >
                <PrintIcon className="h-3 w-3" />
                Print
              </button>
            </div>
          </div>
        )}

        {/* Filters */}
        <VisitTimelineFilters
          filters={filters}
          onFiltersChange={handleFiltersChange}
          providers={providers}
          onJumpToDate={handleJumpToDate}
          isLoading={isLoading}
        />

        {/* Active Encounter Banner */}
        {hasActiveEncounter && (
          <div className="mb-normal p-3 bg-glacier-blue/10 border border-glacier-blue/30 rounded-md">
            <div className="flex items-center gap-2">
              <ActiveEncounterIcon className="h-5 w-5 text-glacier-blue flex-shrink-0" />
              <div>
                <span className="text-[15px] font-medium text-glacier-blue">
                  Active Encounter
                </span>
                <span className="text-[13px] text-glacier-blue/70 ml-2">
                  {formatFullDate(activeEncounterDate!)}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {filteredVisits.length === 0 && !isLoading && (
          <div className="text-center py-comfortable">
            <NoVisitsIcon className="h-12 w-12 text-frost mx-auto mb-tight" />
            <p className="text-[15px] text-text-tertiary">
              {searchQuery || filters.visitType || filters.providerId || filters.diagnosisCode
                ? 'No visits match your filters'
                : 'No previous visits'}
            </p>
            <p className="text-[13px] text-text-tertiary mt-1">
              {searchQuery || filters.visitType || filters.providerId || filters.diagnosisCode
                ? 'Try adjusting your search or filter criteria'
                : timeRange === '12months'
                  ? 'No documented encounters in the last 12 months'
                  : 'This patient has no documented encounters'}
            </p>
          </div>
        )}

        {/* Visit Timeline - Vertical Layout */}
        {filteredVisits.length > 0 && (
          <div className="space-y-comfortable">
            {Array.from(groupedVisits.entries()).map(([monthKey, monthVisits]) => (
              <div key={monthKey}>
                {/* Month Header */}
                <div className="flex items-center gap-2 mb-tight">
                  <div className="h-px flex-1 bg-frost" />
                  <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary px-2">
                    {getMonthLabel(monthKey)}
                  </span>
                  <div className="h-px flex-1 bg-frost" />
                </div>

                {/* Visits in this month with timeline */}
                <div className="relative">
                  {monthVisits.map((visit, index) => {
                    // Calculate time gap to previous visit
                    const previousVisit = index > 0 ? monthVisits[index - 1] : null;
                    const timeGap = previousVisit ? getTimeGap(previousVisit.date, visit.date) : null;

                    return (
                      <div key={visit.id}>
                        {/* Time Gap Indicator */}
                        {timeGap && (
                          <TimeGapIndicator gap={timeGap} />
                        )}

                        {/* Visit with Date Marker */}
                        <VisitWithDateMarker
                          visit={visit}
                          isExpanded={expandedVisitIds.has(visit.id)}
                          onToggle={() => toggleVisit(visit.id)}
                          searchQuery={searchQuery}
                          primaryProviderId={primaryProviderId}
                          isLastInGroup={index === monthVisits.length - 1}
                          isSelectionMode={isSelectionMode}
                          isSelected={selectedVisitIds.has(visit.id)}
                          onToggleSelection={toggleVisitSelection}
                          onFilterByDiagnosis={handleFilterByDiagnosis}
                          onFilterByProvider={handleFilterByProvider}
                          onNavigateToSection={onNavigateToSection}
                          onCopyVisit={copyToClipboard}
                          onPrintVisit={printVisits}
                        />
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}

            {/* Load More / Infinite Scroll Trigger */}
            <div ref={loadMoreRef} className="py-2">
              {isLoadingMore && (
                <div className="flex items-center justify-center gap-2 py-2">
                  <LoadingSpinner className="h-4 w-4 text-glacier-blue animate-spin" />
                  <span className="text-[13px] text-text-tertiary">Loading more visits...</span>
                </div>
              )}
              {hasMore && !isLoadingMore && (
                <button
                  type="button"
                  onClick={() => loadVisits(true)}
                  className="w-full py-2 text-[13px] font-medium text-glacier-blue hover:text-deep-ice hover:bg-frost/50 rounded transition-colors"
                >
                  Load More Visits
                </button>
              )}
              {!hasMore && filteredVisits.length > 0 && (
                <p className="text-center text-[13px] text-text-tertiary py-2">
                  All visits loaded
                </p>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Time Gap Indicator Component
interface TimeGapIndicatorProps {
  gap: { days: number; label: string };
}

function TimeGapIndicator({ gap }: TimeGapIndicatorProps) {
  // Different styling based on gap length
  const isLongGap = gap.days >= 90;

  return (
    <div className="flex items-center py-2 ml-[52px]">
      <div className="flex items-center gap-2 w-full">
        <div className={cn(
          'h-px flex-1',
          isLongGap ? 'bg-warning/40' : 'bg-frost'
        )} />
        <div className={cn(
          'flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px]',
          isLongGap
            ? 'bg-warning/10 text-warning'
            : 'bg-frost/50 text-text-tertiary'
        )}>
          <TimeGapIcon className="h-3 w-3" />
          <span>{gap.label}</span>
        </div>
        <div className={cn(
          'h-px flex-1',
          isLongGap ? 'bg-warning/40' : 'bg-frost'
        )} />
      </div>
    </div>
  );
}

// Visit with Date Marker Component (vertical timeline layout)
interface VisitWithDateMarkerProps {
  visit: Visit;
  isExpanded: boolean;
  onToggle: () => void;
  searchQuery?: string;
  primaryProviderId: string;
  isLastInGroup: boolean;
  isSelectionMode: boolean;
  isSelected: boolean;
  onToggleSelection: (visitId: string, event: React.MouseEvent) => void;
  onFilterByDiagnosis: (diagnosisCode: string) => void;
  onFilterByProvider: (providerId: string) => void;
  onNavigateToSection?: (section: 'medications' | 'labs') => void;
  onCopyVisit: (visitId: string) => void;
  onPrintVisit: (visitId: string) => void;
}

function VisitWithDateMarker({
  visit,
  isExpanded,
  onToggle,
  searchQuery,
  primaryProviderId,
  isLastInGroup,
  isSelectionMode,
  isSelected,
  onToggleSelection,
  onFilterByDiagnosis,
  onFilterByProvider,
  onNavigateToSection,
  onCopyVisit,
  onPrintVisit,
}: VisitWithDateMarkerProps) {
  const dateInfo = formatDateShort(visit.date);
  const config = visitTypeConfig[visit.visitType];
  const isSignificant = config?.isSignificant || false;
  const isSameProvider = visit.provider.id === primaryProviderId;

  return (
    <div className="flex gap-3">
      {/* Selection checkbox when in selection mode */}
      {isSelectionMode && (
        <div className="flex items-start pt-3">
          <button
            type="button"
            onClick={(e) => onToggleSelection(visit.id, e)}
            className={cn(
              'w-5 h-5 rounded border-2 flex items-center justify-center transition-colors',
              isSelected
                ? 'bg-glacier-blue border-glacier-blue'
                : 'border-frost hover:border-glacier-blue/50'
            )}
          >
            {isSelected && (
              <CheckIcon className="h-3 w-3 text-white" />
            )}
          </button>
        </div>
      )}

      {/* Date Marker on Left */}
      <div className="flex flex-col items-center w-12 flex-shrink-0">
        {/* Date */}
        <div className={cn(
          'flex flex-col items-center justify-center w-12 h-12 rounded-lg',
          isSignificant ? 'bg-deep-ice/10 border border-deep-ice/30' : 'bg-frost/50'
        )}>
          <span className={cn(
            'text-[10px] font-medium uppercase',
            isSignificant ? 'text-deep-ice' : 'text-text-tertiary'
          )}>
            {dateInfo.month}
          </span>
          <span className={cn(
            'text-[18px] font-bold leading-none',
            isSignificant ? 'text-deep-ice' : 'text-text-primary'
          )}>
            {dateInfo.day}
          </span>
        </div>

        {/* Vertical timeline connector */}
        {!isLastInGroup && (
          <div className="w-0.5 flex-1 min-h-[16px] bg-frost mt-1" />
        )}
      </div>

      {/* Visit Card on Right */}
      <div className="flex-1 pb-3">
        <VisitCard
          visit={visit}
          isExpanded={isExpanded}
          onToggle={onToggle}
          searchQuery={searchQuery}
          isSameProvider={isSameProvider}
          isSignificant={isSignificant}
          onFilterByDiagnosis={onFilterByDiagnosis}
          onFilterByProvider={onFilterByProvider}
          onNavigateToSection={onNavigateToSection}
          onCopyVisit={onCopyVisit}
          onPrintVisit={onPrintVisit}
        />
      </div>
    </div>
  );
}

interface VisitCardProps {
  visit: Visit;
  isExpanded: boolean;
  onToggle: () => void;
  searchQuery?: string;
  isSameProvider: boolean;
  isSignificant: boolean;
  onFilterByDiagnosis: (diagnosisCode: string) => void;
  onFilterByProvider: (providerId: string) => void;
  onNavigateToSection?: (section: 'medications' | 'labs') => void;
  onCopyVisit: (visitId: string) => void;
  onPrintVisit: (visitId: string) => void;
}

// Search highlighting component
function HighlightText({ text, query }: { text: string; query?: string }) {
  if (!query || !text) return <>{text}</>;

  const lowerText = text.toLowerCase();
  const lowerQuery = query.toLowerCase();
  const index = lowerText.indexOf(lowerQuery);

  if (index === -1) return <>{text}</>;

  return (
    <>
      {text.slice(0, index)}
      <mark className="bg-warning/30 text-inherit rounded px-0.5">{text.slice(index, index + query.length)}</mark>
      {text.slice(index + query.length)}
    </>
  );
}

// Helper to truncate text for preview
function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trim() + '...';
}

// Helper to get preview summary from SOAP note
function getPreviewSummary(soapNote: SOAPNote | undefined, notes: string | undefined): string | null {
  if (soapNote) {
    // Get first line or sentence of assessment
    const assessmentPreview = soapNote.assessment.split('\n')[0].replace(/^\d+\.\s*/, '');
    // Get first line or sentence of plan
    const planPreview = soapNote.plan.split('\n')[0].replace(/^\d+\.\s*/, '');
    return `${truncateText(assessmentPreview, 80)} • Plan: ${truncateText(planPreview, 60)}`;
  }
  if (notes) {
    return truncateText(notes, 150);
  }
  return null;
}

// Vitals display component
function VitalsSection({ vitals }: { vitals: VisitVitals }) {
  const items = [];

  if (vitals.bloodPressureSystolic && vitals.bloodPressureDiastolic) {
    items.push({ label: 'BP', value: `${vitals.bloodPressureSystolic}/${vitals.bloodPressureDiastolic} mmHg` });
  }
  if (vitals.heartRate) {
    items.push({ label: 'HR', value: `${vitals.heartRate} bpm` });
  }
  if (vitals.temperature) {
    items.push({ label: 'Temp', value: `${vitals.temperature}°${vitals.temperatureUnit || 'F'}` });
  }
  if (vitals.weight) {
    items.push({ label: 'Weight', value: `${vitals.weight} ${vitals.weightUnit || 'lbs'}` });
  }
  if (vitals.oxygenSaturation) {
    items.push({ label: 'O₂ Sat', value: `${vitals.oxygenSaturation}%` });
  }
  if (vitals.respiratoryRate) {
    items.push({ label: 'RR', value: `${vitals.respiratoryRate}/min` });
  }

  if (items.length === 0) return null;

  return (
    <div className="mb-tight">
      <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
        Vital Signs
      </span>
      <div className="mt-1 flex flex-wrap gap-x-4 gap-y-1">
        {items.map((item, index) => (
          <span key={index} className="text-[15px] text-text-primary">
            <span className="font-medium text-text-secondary">{item.label}:</span> {item.value}
          </span>
        ))}
      </div>
    </div>
  );
}

// Medications display component
interface MedicationsSectionProps {
  medications: VisitMedication[];
  onNavigateToSection?: (section: 'medications' | 'labs') => void;
}

function MedicationsSection({ medications, onNavigateToSection }: MedicationsSectionProps) {
  if (medications.length === 0) return null;

  const actionColors: Record<string, string> = {
    prescribed: 'bg-success/10 text-success',
    modified: 'bg-warning/10 text-warning',
    discontinued: 'bg-critical/10 text-critical',
    continued: 'bg-frost text-text-secondary',
  };

  const handleMedicationClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onNavigateToSection?.('medications');
  };

  return (
    <div className="mb-tight">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
          Medications
        </span>
        {onNavigateToSection && (
          <button
            type="button"
            onClick={handleMedicationClick}
            className="text-[11px] text-glacier-blue hover:text-deep-ice transition-colors flex items-center gap-0.5"
          >
            View all
            <JumpToIcon className="h-3 w-3" />
          </button>
        )}
      </div>
      <div className="mt-1 space-y-1">
        {medications.map((med) => (
          <div key={med.id} className="flex items-start gap-2 text-[15px]">
            <span className={cn('px-1.5 py-0.5 text-[11px] font-medium rounded capitalize', actionColors[med.action] || 'bg-frost text-text-secondary')}>
              {med.action}
            </span>
            <div>
              {onNavigateToSection ? (
                <button
                  type="button"
                  onClick={handleMedicationClick}
                  className="text-text-primary font-medium hover:text-glacier-blue transition-colors cursor-pointer text-left"
                >
                  {med.name}
                </button>
              ) : (
                <span className="text-text-primary font-medium">{med.name}</span>
              )}
              <span className="text-text-secondary"> {med.dosage} {med.frequency}</span>
              {med.route && <span className="text-text-tertiary"> ({med.route})</span>}
              {med.instructions && (
                <p className="text-[13px] text-text-tertiary mt-0.5">{med.instructions}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Orders display component
interface OrdersSectionProps {
  orders: VisitOrder[];
  onNavigateToSection?: (section: 'medications' | 'labs') => void;
}

function OrdersSection({ orders, onNavigateToSection }: OrdersSectionProps) {
  if (orders.length === 0) return null;

  const statusColors: Record<string, string> = {
    ordered: 'bg-frost text-text-secondary',
    pending: 'bg-warning/10 text-warning',
    in_progress: 'bg-glacier-blue/10 text-glacier-blue',
    completed: 'bg-success/10 text-success',
    cancelled: 'bg-critical/10 text-critical',
  };

  const typeIcons: Record<string, string> = {
    lab: '🔬',
    imaging: '📷',
    referral: '👤',
    procedure: '⚕️',
    other: '📋',
  };

  const handleLabOrderClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onNavigateToSection?.('labs');
  };

  return (
    <div className="mb-tight">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
          Orders
        </span>
        {onNavigateToSection && orders.some(o => o.orderType === 'lab') && (
          <button
            type="button"
            onClick={handleLabOrderClick}
            className="text-[11px] text-glacier-blue hover:text-deep-ice transition-colors flex items-center gap-0.5"
          >
            View labs
            <JumpToIcon className="h-3 w-3" />
          </button>
        )}
      </div>
      <div className="mt-1 space-y-1.5">
        {orders.map((order) => (
          <div key={order.id} className="flex items-start gap-2 text-[15px]">
            <span className="text-[14px]">{typeIcons[order.orderType] || '📋'}</span>
            <div className="flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                {onNavigateToSection && order.orderType === 'lab' ? (
                  <button
                    type="button"
                    onClick={handleLabOrderClick}
                    className="text-text-primary font-medium hover:text-glacier-blue transition-colors cursor-pointer text-left"
                  >
                    {order.name}
                  </button>
                ) : (
                  <span className="text-text-primary font-medium">{order.name}</span>
                )}
                <span className={cn('px-1.5 py-0.5 text-[11px] font-medium rounded capitalize', statusColors[order.status] || 'bg-frost text-text-secondary')}>
                  {order.status.replace('_', ' ')}
                </span>
                {order.priority === 'stat' && (
                  <span className="px-1.5 py-0.5 text-[11px] font-medium rounded bg-critical/10 text-critical uppercase">
                    STAT
                  </span>
                )}
                {order.priority === 'urgent' && (
                  <span className="px-1.5 py-0.5 text-[11px] font-medium rounded bg-warning/10 text-warning uppercase">
                    Urgent
                  </span>
                )}
              </div>
              {order.result && (
                <p className="text-[13px] text-text-secondary mt-0.5">Result: {order.result}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// SOAP Note display component
function SOAPNoteSection({ soapNote }: { soapNote: SOAPNote }) {
  return (
    <div className="mb-tight">
      <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
        Clinical Note (SOAP)
      </span>
      <div className="mt-2 space-y-3">
        {/* Subjective */}
        <div className="border-l-2 border-glacier-blue pl-3">
          <span className="text-[11px] font-semibold uppercase tracking-wide text-glacier-blue">
            Subjective
          </span>
          <p className="text-[15px] text-text-primary mt-1 whitespace-pre-wrap">{soapNote.subjective}</p>
        </div>

        {/* Objective */}
        <div className="border-l-2 border-deep-ice pl-3">
          <span className="text-[11px] font-semibold uppercase tracking-wide text-deep-ice">
            Objective
          </span>
          <p className="text-[15px] text-text-primary mt-1 whitespace-pre-wrap">{soapNote.objective}</p>
        </div>

        {/* Assessment */}
        <div className="border-l-2 border-warning pl-3">
          <span className="text-[11px] font-semibold uppercase tracking-wide text-warning">
            Assessment
          </span>
          <p className="text-[15px] text-text-primary mt-1 whitespace-pre-wrap">{soapNote.assessment}</p>
        </div>

        {/* Plan */}
        <div className="border-l-2 border-success pl-3">
          <span className="text-[11px] font-semibold uppercase tracking-wide text-success">
            Plan
          </span>
          <p className="text-[15px] text-text-primary mt-1 whitespace-pre-wrap">{soapNote.plan}</p>
        </div>
      </div>
    </div>
  );
}

function VisitCard({
  visit,
  isExpanded,
  onToggle,
  searchQuery,
  isSameProvider,
  isSignificant,
  onFilterByDiagnosis,
  onFilterByProvider,
  onNavigateToSection,
  onCopyVisit,
  onPrintVisit,
}: VisitCardProps) {
  const config = visitTypeConfig[visit.visitType];
  const primaryDiagnosis = visit.diagnoses.find((d) => d.isPrimary);
  const isHighPriority = visit.visitType === 'emergency' || visit.visitType === 'hospital_admission';
  const previewSummary = getPreviewSummary(visit.soapNote, visit.notes);

  const handleDiagnosisClick = (diagnosisCode: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onFilterByDiagnosis(diagnosisCode);
  };

  const handleProviderClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onFilterByProvider(visit.provider.id);
  };

  const handleCopyClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onCopyVisit(visit.id);
  };

  const handlePrintClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onPrintVisit(visit.id);
  };

  return (
    <div
      className={cn(
        'rounded-md border bg-white transition-all',
        isHighPriority && 'border-l-4 border-l-critical border-critical/30',
        isSignificant && !isHighPriority && 'border-l-4 border-l-deep-ice border-deep-ice/30',
        !isHighPriority && !isSignificant && 'border-frost'
      )}
    >
      {/* Visit Header */}
      <button
        type="button"
        onClick={onToggle}
        className="w-full px-3 py-2 flex items-start justify-between text-left hover:bg-frost/30 transition-colors rounded-md"
      >
        <div className="flex-1 min-w-0">
          {/* Time and badges row */}
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="text-[13px] text-text-secondary">
              {formatTimeRange(visit.date, visit.duration)}
            </span>

            {/* Visit type badge */}
            <span
              className={cn(
                'px-2 py-0.5 text-[11px] font-medium rounded',
                config.bgClass,
                config.iconClass
              )}
            >
              {config.label}
            </span>

            {/* High priority indicator */}
            {isHighPriority && (
              <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[11px] font-medium bg-critical/10 text-critical">
                <HighPriorityIcon className="h-3 w-3" />
              </span>
            )}

            {/* Critical Findings indicator */}
            {visit.hasCriticalFindings && (
              <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-medium bg-critical/10 text-critical">
                <CriticalFindingsIcon className="h-3 w-3" />
                <span>Critical</span>
              </span>
            )}

            {/* Follow-up Required indicator */}
            {visit.hasFollowUpRequired && (
              <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-medium bg-warning/10 text-warning">
                <FollowUpIcon className="h-3 w-3" />
                <span>Follow-up</span>
              </span>
            )}

            {/* Provider continuity indicator */}
            {!isSameProvider && (
              <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-medium bg-frost text-text-tertiary">
                <DifferentProviderIcon className="h-3 w-3" />
                <span>Different provider</span>
              </span>
            )}
          </div>

          {/* Chief Complaint */}
          <div className="mt-1">
            <span className="text-[15px] text-text-primary font-medium">
              <HighlightText text={visit.chiefComplaint} query={searchQuery} />
            </span>
          </div>

          {/* Primary Diagnosis & Provider - Summary line */}
          <div className="flex items-center gap-2 mt-1 text-[13px] text-text-secondary flex-wrap">
            {primaryDiagnosis && (
              <>
                <span
                  onClick={(e) => handleDiagnosisClick(primaryDiagnosis.code, e)}
                  className="hover:text-glacier-blue cursor-pointer transition-colors"
                  title="Click to filter by this diagnosis"
                >
                  <HighlightText text={primaryDiagnosis.description} query={searchQuery} />
                </span>
                <span
                  onClick={(e) => handleDiagnosisClick(primaryDiagnosis.code, e)}
                  className="text-text-tertiary hover:text-glacier-blue cursor-pointer transition-colors"
                  title="Click to filter by this diagnosis"
                >
                  (<HighlightText text={primaryDiagnosis.code} query={searchQuery} />)
                </span>
                <span className="text-text-tertiary">•</span>
              </>
            )}
            <span
              onClick={handleProviderClick}
              className="hover:text-glacier-blue cursor-pointer transition-colors"
              title="Click to filter by this provider"
            >
              {visit.provider.name}
            </span>
            {visit.provider.specialty && (
              <span className="text-text-tertiary">({visit.provider.specialty})</span>
            )}
          </div>

          {/* Critical findings or follow-up summary when collapsed */}
          {!isExpanded && (visit.criticalFindingsSummary || visit.followUpSummary) && (
            <div className="mt-2 space-y-1">
              {visit.criticalFindingsSummary && (
                <div className="p-2 bg-critical/5 border border-critical/20 rounded text-[13px] text-critical">
                  <span className="font-medium">Critical:</span> {visit.criticalFindingsSummary}
                </div>
              )}
              {visit.followUpSummary && (
                <div className="p-2 bg-warning/5 border border-warning/20 rounded text-[13px] text-warning">
                  <span className="font-medium">Follow-up:</span> {visit.followUpSummary}
                </div>
              )}
            </div>
          )}

          {/* Preview Summary (Assessment + Plan) - Only shown when collapsed and no critical/follow-up */}
          {!isExpanded && previewSummary && !visit.criticalFindingsSummary && !visit.followUpSummary && (
            <div className="mt-2 p-2 bg-frost/30 rounded text-[13px] text-text-secondary line-clamp-2">
              {previewSummary}
            </div>
          )}
        </div>

        <svg
          xmlns="http://www.w3.org/2000/svg"
          className={cn(
            'h-4 w-4 text-text-tertiary transition-transform flex-shrink-0 ml-2 mt-1',
            isExpanded && 'rotate-180'
          )}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="px-3 pb-3 pt-1 border-t border-frost">
          {/* Action buttons for this visit */}
          <div className="flex justify-end gap-2 mb-3">
            <button
              type="button"
              onClick={handleCopyClick}
              className="px-2 py-1 text-[11px] font-medium rounded bg-frost text-text-secondary hover:bg-frost/70 transition-colors flex items-center gap-1"
              title="Copy this visit note to clipboard"
            >
              <CopyIcon className="h-3 w-3" />
              Copy
            </button>
            <button
              type="button"
              onClick={handlePrintClick}
              className="px-2 py-1 text-[11px] font-medium rounded bg-frost text-text-secondary hover:bg-frost/70 transition-colors flex items-center gap-1"
              title="Print this visit note"
            >
              <PrintIcon className="h-3 w-3" />
              Print
            </button>
          </div>

          {/* Critical Findings Alert */}
          {visit.hasCriticalFindings && visit.criticalFindingsSummary && (
            <div className="mb-3 p-3 bg-critical/5 border border-critical/30 rounded-md">
              <div className="flex items-start gap-2">
                <CriticalFindingsIcon className="h-4 w-4 text-critical flex-shrink-0 mt-0.5" />
                <div>
                  <span className="text-[13px] font-semibold text-critical">Critical Findings</span>
                  <p className="text-[15px] text-text-primary mt-1">{visit.criticalFindingsSummary}</p>
                </div>
              </div>
            </div>
          )}

          {/* Follow-up Required Alert */}
          {visit.hasFollowUpRequired && visit.followUpSummary && (
            <div className="mb-3 p-3 bg-warning/5 border border-warning/30 rounded-md">
              <div className="flex items-start gap-2">
                <FollowUpIcon className="h-4 w-4 text-warning flex-shrink-0 mt-0.5" />
                <div>
                  <span className="text-[13px] font-semibold text-warning">Follow-up Required</span>
                  <p className="text-[15px] text-text-primary mt-1">{visit.followUpSummary}</p>
                </div>
              </div>
            </div>
          )}

          {/* SOAP Note - Full Clinical Note */}
          {visit.soapNote && (
            <SOAPNoteSection soapNote={visit.soapNote} />
          )}

          {/* Vital Signs */}
          {visit.vitals && (
            <VitalsSection vitals={visit.vitals} />
          )}

          {/* Medications prescribed/modified */}
          {visit.medications && visit.medications.length > 0 && (
            <MedicationsSection medications={visit.medications} onNavigateToSection={onNavigateToSection} />
          )}

          {/* Orders (labs, imaging, referrals) */}
          {visit.orders && visit.orders.length > 0 && (
            <OrdersSection orders={visit.orders} onNavigateToSection={onNavigateToSection} />
          )}

          {/* All Diagnoses */}
          {visit.diagnoses.length > 0 && (
            <div className="mb-tight">
              <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                Diagnoses
              </span>
              <ul className="mt-1 space-y-0.5">
                {visit.diagnoses.map((dx, index) => (
                  <li key={index} className="text-[15px] text-text-primary flex items-start gap-1">
                    <span className="text-text-tertiary">•</span>
                    <span>
                      <button
                        type="button"
                        onClick={(e) => handleDiagnosisClick(dx.code, e)}
                        className="text-left hover:text-glacier-blue transition-colors cursor-pointer"
                        title="Click to filter by this diagnosis"
                      >
                        {dx.description}
                      </button>
                      <button
                        type="button"
                        onClick={(e) => handleDiagnosisClick(dx.code, e)}
                        className="text-[13px] text-text-tertiary ml-1 hover:text-glacier-blue transition-colors cursor-pointer"
                        title="Click to filter by this diagnosis"
                      >
                        ({dx.code})
                      </button>
                      {dx.isPrimary && (
                        <span className="ml-2 px-1.5 py-0.5 text-[11px] font-medium rounded bg-glacier-blue/10 text-glacier-blue">
                          Primary
                        </span>
                      )}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Provider Details */}
          <div className="mb-tight">
            <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
              Provider
            </span>
            <p className="text-[15px] text-text-primary mt-1">
              <button
                type="button"
                onClick={handleProviderClick}
                className="hover:text-glacier-blue transition-colors cursor-pointer"
                title="Click to filter by this provider"
              >
                {visit.provider.name}
              </button>
              {visit.provider.role && (
                <span className="text-text-secondary"> · {visit.provider.role}</span>
              )}
              {visit.provider.specialty && (
                <span className="text-text-secondary"> · {visit.provider.specialty}</span>
              )}
              {!isSameProvider && (
                <span className="ml-2 px-1.5 py-0.5 text-[11px] font-medium rounded bg-frost text-text-tertiary">
                  Different from usual provider
                </span>
              )}
            </p>
          </div>

          {/* Location */}
          {visit.location && (
            <div className="mb-tight">
              <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                Location
              </span>
              <p className="text-[15px] text-text-primary mt-1">{visit.location}</p>
            </div>
          )}

          {/* Visit Time */}
          <div className="mb-tight">
            <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
              Visit Time
            </span>
            <p className="text-[15px] text-text-primary mt-1">
              {formatDateWithDayOfWeek(visit.date)} at {formatTimeRange(visit.date, visit.duration)}
              {visit.duration && (
                <span className="text-text-tertiary ml-2">({visit.duration} min)</span>
              )}
            </p>
          </div>

          {/* Notes (if no SOAP note, show notes field) */}
          {!visit.soapNote && visit.notes && (
            <div>
              <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                Notes
              </span>
              <p className="text-[15px] text-text-secondary mt-1">{visit.notes}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Icon Components

function ChartNotesIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
      <line x1="10" y1="9" x2="8" y2="9" />
    </svg>
  );
}

function ActiveEncounterIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  );
}

function NoVisitsIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="12" y1="18" x2="12" y2="12" />
      <line x1="9" y1="15" x2="15" y2="15" />
    </svg>
  );
}

function HighPriorityIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      viewBox="0 0 24 24"
      fill="currentColor"
    >
      <path
        fillRule="evenodd"
        d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
        clipRule="evenodd"
      />
    </svg>
  );
}

function LoadingSpinner({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M21 12a9 9 0 1 1-6.219-8.56" />
    </svg>
  );
}

function TimeGapIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  );
}

function CriticalFindingsIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
}

function FollowUpIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
      <polyline points="9 16 12 19 16 14" />
    </svg>
  );
}

function DifferentProviderIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}

function SelectIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" />
      <rect x="14" y="14" width="7" height="7" rx="1" />
    </svg>
  );
}

function CheckIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="3"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function CopyIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  );
}

function PrintIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polyline points="6 9 6 2 18 2 18 9" />
      <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" />
      <rect x="6" y="14" width="12" height="8" />
    </svg>
  );
}

function JumpToIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <line x1="7" y1="17" x2="17" y2="7" />
      <polyline points="7 7 17 7 17 17" />
    </svg>
  );
}
