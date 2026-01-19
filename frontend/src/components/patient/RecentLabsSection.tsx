import { useState, useMemo, useCallback } from 'react';
import type {
  RecentLabs,
  LabPanel,
  LabResult,
  LabResultStatus,
  PreviousLabValue,
  LabHistoryResponse,
  LabSortOption,
  LabFilterPanel,
  LabFilterStatus,
} from '../../types';
import { Card, CardContent, Tooltip } from '../ui';
import { LabFilters } from './LabFilters';
import { LabHistoryModal } from './LabHistoryModal';
import { getLabHistory } from '../../api/patientApi';
import { cn } from '../../utils/cn';

// Trend direction types
type TrendDirection = 'up' | 'down' | 'stable';
type ClinicalSignificance = 'good' | 'concerning' | 'neutral';

interface TrendInfo {
  direction: TrendDirection;
  percentChange: number;
  absoluteChange: number;
  significance: ClinicalSignificance;
}

// Tests where LOWER values are generally better
const lowerIsBetterTests = new Set([
  'HbA1c', 'A1C', 'HgbA1c', 'Hemoglobin A1C',
  'LDL', 'LDL-C', 'Low-Density Lipoprotein Cholesterol',
  'TC', 'Total Cholesterol',
  'TG', 'Trig', 'Triglycerides',
  'BUN', 'Blood Urea Nitrogen',
  'Cr', 'Creatinine',
  'ALT', 'Alanine Aminotransferase',
  'AST', 'Aspartate Aminotransferase',
  'ALP', 'Alkaline Phosphatase',
  'GGT', 'Gamma-Glutamyl Transferase',
  'T. Bili', 'Total Bilirubin',
  'D. Bili', 'Direct Bilirubin',
  'ESR', 'Erythrocyte Sedimentation Rate',
  'CRP', 'C-Reactive Protein',
  'hs-CRP', 'High-Sensitivity C-Reactive Protein',
  'PSA', 'Prostate-Specific Antigen',
  'FBG', 'Fasting Blood Glucose', 'FBS', 'Fasting Blood Sugar',
  'RBS', 'Random Blood Sugar', 'Glucose',
]);

// Tests where HIGHER values are generally better
const higherIsBetterTests = new Set([
  'HDL', 'HDL-C', 'High-Density Lipoprotein Cholesterol',
  'eGFR', 'GFR', 'Estimated Glomerular Filtration Rate', 'Glomerular Filtration Rate',
]);

// Parse numeric value from string (handles values like ">100" or "<5")
function parseNumericValue(value: string): number | null {
  const cleaned = value.replace(/[<>]/g, '').trim();
  const num = parseFloat(cleaned);
  return isNaN(num) ? null : num;
}

// Value direction types for abnormal highlighting
type ValueDirection = 'high' | 'low' | 'borderline-high' | 'borderline-low' | 'normal';

interface ReferenceRangeBounds {
  min: number | null;
  max: number | null;
}

// Parse reference range string into min/max bounds
function parseReferenceRange(range: string): ReferenceRangeBounds {
  if (!range) return { min: null, max: null };

  const cleaned = range.replace(/Normal:\s*/i, '').trim();

  const lessThanMatch = cleaned.match(/^<\s*([\d.]+)/);
  if (lessThanMatch) {
    return { min: null, max: parseFloat(lessThanMatch[1]) };
  }

  const greaterThanMatch = cleaned.match(/^>\s*([\d.]+)/);
  if (greaterThanMatch) {
    return { min: parseFloat(greaterThanMatch[1]), max: null };
  }

  const rangeMatch = cleaned.match(/([\d.]+)\s*[-–]\s*([\d.]+)/);
  if (rangeMatch) {
    return { min: parseFloat(rangeMatch[1]), max: parseFloat(rangeMatch[2]) };
  }

  return { min: null, max: null };
}

// Determine value direction (high/low/borderline) based on reference range
function getValueDirection(
  value: string,
  referenceRange: string,
  status: LabResultStatus
): ValueDirection {
  if (status === 'normal') return 'normal';

  const numericValue = parseNumericValue(value);
  if (numericValue === null) return 'normal';

  const bounds = parseReferenceRange(referenceRange);

  if (bounds.min === null && bounds.max === null) {
    return 'high';
  }

  if (bounds.max !== null && numericValue > bounds.max) {
    return 'high';
  }

  if (bounds.min !== null && numericValue < bounds.min) {
    return 'low';
  }

  if (bounds.max !== null && bounds.min !== null) {
    const rangeSize = bounds.max - bounds.min;
    const borderlineThreshold = rangeSize * 0.1;

    if (numericValue >= bounds.max - borderlineThreshold) {
      return 'borderline-high';
    }

    if (numericValue <= bounds.min + borderlineThreshold) {
      return 'borderline-low';
    }
  } else if (bounds.max !== null) {
    const borderlineThreshold = bounds.max * 0.1;
    if (numericValue >= bounds.max - borderlineThreshold) {
      return 'borderline-high';
    }
  } else if (bounds.min !== null) {
    const borderlineThreshold = bounds.min * 0.1;
    if (numericValue <= bounds.min + borderlineThreshold) {
      return 'borderline-low';
    }
  }

  return 'normal';
}

// Calculate trend information between current and previous value
function calculateTrend(
  currentValue: string,
  previousValue: PreviousLabValue | undefined,
  testName: string
): TrendInfo | null {
  if (!previousValue) return null;

  const current = parseNumericValue(currentValue);
  const previous = parseNumericValue(previousValue.value);

  if (current === null || previous === null) return null;
  if (previous === 0) return null;

  const absoluteChange = current - previous;
  const percentChange = ((current - previous) / Math.abs(previous)) * 100;

  let direction: TrendDirection;
  if (Math.abs(percentChange) <= 5) {
    direction = 'stable';
  } else if (absoluteChange > 0) {
    direction = 'up';
  } else {
    direction = 'down';
  }

  let significance: ClinicalSignificance = 'neutral';

  if (direction !== 'stable') {
    const standardName = getStandardTestName(testName);

    if (lowerIsBetterTests.has(testName) || lowerIsBetterTests.has(standardName)) {
      significance = direction === 'down' ? 'good' : 'concerning';
    } else if (higherIsBetterTests.has(testName) || higherIsBetterTests.has(standardName)) {
      significance = direction === 'up' ? 'good' : 'concerning';
    }
  }

  return {
    direction,
    percentChange: Math.abs(percentChange),
    absoluteChange: Math.abs(absoluteChange),
    significance,
  };
}

interface RecentLabsSectionProps {
  recentLabs: RecentLabs | undefined;
  patientId: string;
}

type TimeRangeOption = '90days' | '6months' | '1year' | 'all';

const timeRangeOptions: { value: TimeRangeOption; label: string }[] = [
  { value: '90days', label: '90 Days' },
  { value: '6months', label: '6 Months' },
  { value: '1year', label: '1 Year' },
  { value: 'all', label: 'All Results' },
];

const statusConfig: Record<LabResultStatus, { label: string; className: string; dotClass: string }> = {
  normal: {
    label: 'Normal',
    className: 'text-success',
    dotClass: 'bg-success',
  },
  abnormal: {
    label: 'Abnormal',
    className: 'text-warning',
    dotClass: 'bg-warning',
  },
  critical: {
    label: 'Critical',
    className: 'text-critical',
    dotClass: 'bg-critical',
  },
  pending: {
    label: 'Pending',
    className: 'text-text-tertiary',
    dotClass: 'bg-frost animate-pulse',
  },
  in_progress: {
    label: 'In Progress',
    className: 'text-glacier-blue',
    dotClass: 'bg-glacier-blue animate-pulse',
  },
};

function getTimeRangeDays(range: TimeRangeOption): number | null {
  switch (range) {
    case '90days':
      return 90;
    case '6months':
      return 180;
    case '1year':
      return 365;
    case 'all':
      return null;
  }
}

function isWithinTimeRange(dateString: string, days: number | null): boolean {
  if (days === null) return true;
  const date = new Date(dateString);
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - days);
  return date >= cutoff;
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const year = date.getFullYear();
  return `${month}/${day}/${year}`;
}

// Format relative time for last updated
function formatRelativeTime(dateString: string | undefined): string {
  if (!dateString) return '';
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins} min ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays === 1) return 'yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  return formatDate(dateString);
}

// Check if a result is pending (pending or in_progress status)
function isPendingResult(result: LabResult): boolean {
  return result.status === 'pending' || result.status === 'in_progress';
}

// Check if a result is critical and unacknowledged
function isUnacknowledgedCritical(result: LabResult): boolean {
  return result.status === 'critical' && result.acknowledged === false;
}

// Count unacknowledged critical results
function countUnacknowledgedCritical(labs: RecentLabs | undefined): number {
  if (!labs) return 0;
  let count = 0;

  for (const panel of labs.panels) {
    count += panel.results.filter(isUnacknowledgedCritical).length;
  }
  count += labs.ungroupedResults.filter(isUnacknowledgedCritical).length;

  return count;
}

// Count pending results
function countPendingResults(labs: RecentLabs | undefined): number {
  if (!labs) return 0;
  let count = 0;

  for (const panel of labs.panels) {
    count += panel.results.filter(isPendingResult).length;
  }
  count += labs.ungroupedResults.filter(isPendingResult).length;

  return count;
}

// Get unacknowledged critical results
function getUnacknowledgedCriticalResults(labs: RecentLabs | undefined): LabResult[] {
  if (!labs) return [];
  const results: LabResult[] = [];

  for (const panel of labs.panels) {
    results.push(...panel.results.filter(isUnacknowledgedCritical));
  }
  results.push(...labs.ungroupedResults.filter(isUnacknowledgedCritical));

  return results;
}

// Standard terminology mapping for common lab test abbreviations
const standardTerminologyMap: Record<string, string> = {
  'HbA1c': 'Hemoglobin A1C',
  'A1C': 'Hemoglobin A1C',
  'HgbA1c': 'Hemoglobin A1C',
  'Hgb': 'Hemoglobin',
  'Hb': 'Hemoglobin',
  'LDL': 'Low-Density Lipoprotein Cholesterol',
  'LDL-C': 'Low-Density Lipoprotein Cholesterol',
  'HDL': 'High-Density Lipoprotein Cholesterol',
  'HDL-C': 'High-Density Lipoprotein Cholesterol',
  'TC': 'Total Cholesterol',
  'TG': 'Triglycerides',
  'Trig': 'Triglycerides',
  'BUN': 'Blood Urea Nitrogen',
  'Cr': 'Creatinine',
  'eGFR': 'Estimated Glomerular Filtration Rate',
  'GFR': 'Glomerular Filtration Rate',
  'ALT': 'Alanine Aminotransferase',
  'AST': 'Aspartate Aminotransferase',
  'ALP': 'Alkaline Phosphatase',
  'GGT': 'Gamma-Glutamyl Transferase',
  'T. Bili': 'Total Bilirubin',
  'D. Bili': 'Direct Bilirubin',
  'WBC': 'White Blood Cell Count',
  'RBC': 'Red Blood Cell Count',
  'Hct': 'Hematocrit',
  'MCV': 'Mean Corpuscular Volume',
  'MCH': 'Mean Corpuscular Hemoglobin',
  'MCHC': 'Mean Corpuscular Hemoglobin Concentration',
  'RDW': 'Red Cell Distribution Width',
  'Plt': 'Platelet Count',
  'MPV': 'Mean Platelet Volume',
  'Na': 'Sodium',
  'K': 'Potassium',
  'Cl': 'Chloride',
  'CO2': 'Carbon Dioxide',
  'Ca': 'Calcium',
  'Mg': 'Magnesium',
  'Phos': 'Phosphorus',
  'TSH': 'Thyroid Stimulating Hormone',
  'T3': 'Triiodothyronine',
  'T4': 'Thyroxine',
  'FT3': 'Free Triiodothyronine',
  'FT4': 'Free Thyroxine',
  'ESR': 'Erythrocyte Sedimentation Rate',
  'CRP': 'C-Reactive Protein',
  'hs-CRP': 'High-Sensitivity C-Reactive Protein',
  'PSA': 'Prostate-Specific Antigen',
  'INR': 'International Normalized Ratio',
  'PT': 'Prothrombin Time',
  'PTT': 'Partial Thromboplastin Time',
  'aPTT': 'Activated Partial Thromboplastin Time',
  'FBG': 'Fasting Blood Glucose',
  'FBS': 'Fasting Blood Sugar',
  'RBS': 'Random Blood Sugar',
  'UA': 'Urinalysis',
};

function getStandardTestName(testName: string): string {
  return standardTerminologyMap[testName] || testName;
}

function formatReferenceRange(range: string, unit: string): string {
  if (!range) return '';
  if (range.toLowerCase().startsWith('normal')) return range;
  return `Normal: ${range}${unit ? '' : ''}`;
}

// Map panel names to filter options
function getPanelFilterKey(panelName: string): LabFilterPanel {
  const name = panelName.toLowerCase();
  if (name.includes('basic metabolic') || name.includes('bmp')) return 'BMP';
  if (name.includes('lipid')) return 'Lipid';
  if (name.includes('complete blood') || name.includes('cbc')) return 'CBC';
  return 'all';
}

export function RecentLabsSection({ recentLabs, patientId }: RecentLabsSectionProps) {
  const [timeRange, setTimeRange] = useState<TimeRangeOption>('90days');
  const [expandedPanelIds, setExpandedPanelIds] = useState<Set<string>>(new Set());

  // Filter and sort state
  const [sortBy, setSortBy] = useState<LabSortOption>('date');
  const [filterPanel, setFilterPanel] = useState<LabFilterPanel>('all');
  const [filterStatus, setFilterStatus] = useState<LabFilterStatus>('all');

  // History modal state
  const [selectedLabForHistory, setSelectedLabForHistory] = useState<LabResult | null>(null);
  const [labHistory, setLabHistory] = useState<LabHistoryResponse | null>(null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);

  const togglePanel = (id: string) => {
    setExpandedPanelIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleLabClick = useCallback(async (result: LabResult) => {
    setSelectedLabForHistory(result);
    setIsLoadingHistory(true);
    setHistoryError(null);
    setLabHistory(null);

    try {
      const history = await getLabHistory(patientId, result.testName);
      setLabHistory(history);
    } catch (err) {
      setHistoryError(err instanceof Error ? err.message : 'Failed to load lab history');
    } finally {
      setIsLoadingHistory(false);
    }
  }, [patientId]);

  const handleCloseHistory = useCallback(() => {
    setSelectedLabForHistory(null);
    setLabHistory(null);
    setHistoryError(null);
  }, []);

  const rangeDays = getTimeRangeDays(timeRange);

  // Filter and sort panels
  const filteredPanels = useMemo(() => {
    if (!recentLabs?.panels) return [];

    let panels = recentLabs.panels.filter((panel) =>
      isWithinTimeRange(panel.collectionDate, rangeDays)
    );

    // Filter by panel type
    if (filterPanel !== 'all' && filterPanel !== 'ungrouped') {
      panels = panels.filter((panel) => getPanelFilterKey(panel.panelName) === filterPanel);
    }

    // Filter by status
    if (filterStatus !== 'all') {
      panels = panels.filter((panel) =>
        panel.results.some((r) => r.status === filterStatus)
      );
    }

    // Sort panels
    if (sortBy === 'name') {
      panels.sort((a, b) => a.panelName.localeCompare(b.panelName));
    } else if (sortBy === 'abnormal') {
      panels.sort((a, b) => {
        const aHasCritical = a.results.some((r) => r.status === 'critical');
        const bHasCritical = b.results.some((r) => r.status === 'critical');
        if (aHasCritical !== bHasCritical) return aHasCritical ? -1 : 1;

        const aHasAbnormal = a.results.some((r) => r.status === 'abnormal');
        const bHasAbnormal = b.results.some((r) => r.status === 'abnormal');
        if (aHasAbnormal !== bHasAbnormal) return aHasAbnormal ? -1 : 1;

        return new Date(b.collectionDate).getTime() - new Date(a.collectionDate).getTime();
      });
    } else {
      // Default: sort by date
      panels.sort((a, b) =>
        new Date(b.collectionDate).getTime() - new Date(a.collectionDate).getTime()
      );
    }

    return panels;
  }, [recentLabs?.panels, rangeDays, filterPanel, filterStatus, sortBy]);

  // Filter and sort ungrouped results
  const filteredUngrouped = useMemo(() => {
    if (!recentLabs?.ungroupedResults) return [];
    if (filterPanel !== 'all' && filterPanel !== 'ungrouped') return [];

    let results = recentLabs.ungroupedResults.filter((result) =>
      isWithinTimeRange(result.collectionDate, rangeDays)
    );

    // Filter by status
    if (filterStatus !== 'all') {
      results = results.filter((r) => r.status === filterStatus);
    }

    // Sort results
    if (sortBy === 'name') {
      results.sort((a, b) => a.testName.localeCompare(b.testName));
    } else if (sortBy === 'abnormal') {
      results.sort((a, b) => {
        if (a.status === 'critical' && b.status !== 'critical') return -1;
        if (b.status === 'critical' && a.status !== 'critical') return 1;
        if (a.status === 'abnormal' && b.status === 'normal') return -1;
        if (b.status === 'abnormal' && a.status === 'normal') return 1;
        return new Date(b.collectionDate).getTime() - new Date(a.collectionDate).getTime();
      });
    } else {
      results.sort((a, b) =>
        new Date(b.collectionDate).getTime() - new Date(a.collectionDate).getTime()
      );
    }

    return results;
  }, [recentLabs?.ungroupedResults, rangeDays, filterPanel, filterStatus, sortBy]);

  const hasResults = filteredPanels.length > 0 || filteredUngrouped.length > 0;
  const totalResultCount = filteredPanels.reduce((acc, panel) => acc + panel.results.length, 0) + filteredUngrouped.length;

  const hasCriticalResults = filteredPanels.some((panel) =>
    panel.results.some((r) => r.status === 'critical')
  ) || filteredUngrouped.some((r) => r.status === 'critical');

  const hasAbnormalResults = filteredPanels.some((panel) =>
    panel.results.some((r) => r.status === 'abnormal')
  ) || filteredUngrouped.some((r) => r.status === 'abnormal');

  // Data completeness tracking
  const unacknowledgedCriticalCount = countUnacknowledgedCritical(recentLabs);
  const unacknowledgedCriticalResults = getUnacknowledgedCriticalResults(recentLabs);
  const pendingCount = countPendingResults(recentLabs);

  if (!recentLabs) {
    return (
      <Card className="mb-normal border-2 border-dashed border-frost">
        <CardContent>
          <div className="flex items-center gap-tight">
            <LabIcon className="h-5 w-5 text-text-tertiary" />
            <span className="text-[15px] text-text-tertiary">
              No lab results available
            </span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card
        className={cn(
          'mb-normal',
          hasCriticalResults
            ? 'bg-critical/5 border border-critical/20'
            : hasAbnormalResults
            ? 'bg-warning/5 border border-warning/20'
            : ''
        )}
      >
        <CardContent>
          {/* Header */}
          <div className="flex items-center justify-between mb-normal">
            <div className="flex items-center gap-tight">
              <LabIcon
                className={cn(
                  'h-5 w-5',
                  hasCriticalResults
                    ? 'text-critical'
                    : hasAbnormalResults
                    ? 'text-warning'
                    : 'text-glacier-blue'
                )}
              />
              <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                Recent Labs
              </h3>
              {hasResults && (
                <span className="text-[11px] text-text-tertiary">
                  ({totalResultCount} result{totalResultCount !== 1 ? 's' : ''})
                </span>
              )}
            </div>

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

          {/* Filters */}
          <div className="mb-normal">
            <LabFilters
              sortBy={sortBy}
              onSortChange={setSortBy}
              filterPanel={filterPanel}
              onFilterPanelChange={setFilterPanel}
              filterStatus={filterStatus}
              onFilterStatusChange={setFilterStatus}
            />
          </div>

          {/* Unacknowledged critical results alert */}
          {unacknowledgedCriticalCount > 0 && (
            <div className="mb-normal p-3 bg-critical/15 border-2 border-critical/50 rounded-md animate-pulse">
              <div className="flex items-start gap-2">
                <AlertBellIcon className="h-5 w-5 text-critical flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[15px] font-bold text-critical">
                      {unacknowledgedCriticalCount} Critical Result{unacknowledgedCriticalCount > 1 ? 's' : ''} Require Acknowledgment
                    </span>
                  </div>
                  <div className="mt-1 space-y-0.5">
                    {unacknowledgedCriticalResults.map((result) => (
                      <div key={result.id} className="text-[13px] text-critical/80 flex items-center gap-1">
                        <span className="font-medium">{result.testName}:</span>
                        <span>{result.value} {result.unit}</span>
                        {result.lastUpdated && (
                          <span className="text-critical/60">• Updated {formatRelativeTime(result.lastUpdated)}</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Critical results banner (for acknowledged criticals) */}
          {hasCriticalResults && unacknowledgedCriticalCount === 0 && (
            <div className="mb-normal p-3 bg-critical/10 border border-critical/30 rounded-md">
              <div className="flex items-center gap-2">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5 text-critical flex-shrink-0"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="text-[15px] font-medium text-critical">
                  Critical lab values require attention
                </span>
              </div>
            </div>
          )}

          {/* Pending labs indicator */}
          {pendingCount > 0 && (
            <div className="mb-normal p-3 bg-glacier-blue/10 border border-glacier-blue/30 rounded-md">
              <div className="flex items-center gap-2">
                <ClockIcon className="h-5 w-5 text-glacier-blue flex-shrink-0" />
                <span className="text-[15px] font-medium text-glacier-blue">
                  {pendingCount} lab{pendingCount > 1 ? 's' : ''} pending or in progress
                </span>
              </div>
            </div>
          )}

          {/* No results in selected time range */}
          {!hasResults && (
            <div className="text-center py-comfortable text-text-tertiary text-[15px]">
              No lab results match the current filters
            </div>
          )}

          {/* Lab Panels */}
          {filteredPanels.length > 0 && (
            <div className="space-y-tight">
              {filteredPanels.map((panel) => (
                <LabPanelCard
                  key={panel.id}
                  panel={panel}
                  isExpanded={expandedPanelIds.has(panel.id)}
                  onToggle={() => togglePanel(panel.id)}
                  onLabClick={handleLabClick}
                />
              ))}
            </div>
          )}

          {/* Ungrouped Results */}
          {filteredUngrouped.length > 0 && (
            <div className={cn(filteredPanels.length > 0 && 'mt-normal')}>
              <div className="flex items-center gap-1 mb-tight">
                <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                  Individual Tests
                </span>
              </div>
              <div className="space-y-1">
                {filteredUngrouped.map((result) => (
                  <LabResultRow
                    key={result.id}
                    result={result}
                    onClick={() => handleLabClick(result)}
                  />
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Lab History Modal */}
      <LabHistoryModal
        isOpen={selectedLabForHistory !== null}
        onClose={handleCloseHistory}
        labHistory={labHistory}
        isLoading={isLoadingHistory}
        error={historyError}
      />
    </>
  );
}

interface LabPanelCardProps {
  panel: LabPanel;
  isExpanded: boolean;
  onToggle: () => void;
  onLabClick: (result: LabResult) => void;
}

function LabPanelCard({ panel, isExpanded, onToggle, onLabClick }: LabPanelCardProps) {
  const hasCritical = panel.results.some((r) => r.status === 'critical');
  const hasAbnormal = panel.results.some((r) => r.status === 'abnormal');
  const hasPending = panel.results.some((r) => r.status === 'pending' || r.status === 'in_progress');
  const hasUnacknowledgedCritical = panel.results.some((r) => r.status === 'critical' && r.acknowledged === false);
  const abnormalCount = panel.results.filter((r) => r.status === 'abnormal' || r.status === 'critical').length;
  const pendingCount = panel.results.filter((r) => r.status === 'pending' || r.status === 'in_progress').length;
  const showResultPerformingLab = !panel.performingLab;

  return (
    <div
      className={cn(
        'rounded-md border bg-white transition-all',
        hasUnacknowledgedCritical
          ? 'border-critical/50 border-l-4'
          : hasCritical
          ? 'border-critical/30'
          : hasAbnormal
          ? 'border-warning/30'
          : hasPending
          ? 'border-glacier-blue/30'
          : 'border-frost'
      )}
    >
      {/* Panel Header */}
      <button
        type="button"
        onClick={onToggle}
        className="w-full px-3 py-2 flex flex-col items-start text-left hover:bg-frost/30 transition-colors rounded-md"
      >
        <div className="w-full flex items-center justify-between">
          <div className="flex items-center gap-2">
            {hasPending ? (
              <span className={cn('w-2 h-2 rounded-full', statusConfig.in_progress.dotClass)} />
            ) : hasCritical ? (
              <span className={cn('w-2 h-2 rounded-full', statusConfig.critical.dotClass)} />
            ) : hasAbnormal ? (
              <span className={cn('w-2 h-2 rounded-full', statusConfig.abnormal.dotClass)} />
            ) : (
              <span className={cn('w-2 h-2 rounded-full', statusConfig.normal.dotClass)} />
            )}

            <span className="text-[15px] font-medium text-text-primary">
              {panel.panelName}
            </span>

            <span className="text-[13px] text-text-tertiary">
              {formatDate(panel.collectionDate)}
            </span>

            {/* Pending badge */}
            {pendingCount > 0 && (
              <span className="px-1.5 py-0.5 text-[11px] font-medium rounded bg-glacier-blue/10 text-glacier-blue">
                {pendingCount} pending
              </span>
            )}

            {/* Abnormal badge */}
            {abnormalCount > 0 && (
              <span
                className={cn(
                  'px-1.5 py-0.5 text-[11px] font-medium rounded',
                  hasCritical
                    ? 'bg-critical/10 text-critical'
                    : 'bg-warning/10 text-warning'
                )}
              >
                {abnormalCount} abnormal
              </span>
            )}

            {/* Unacknowledged critical alert icon */}
            {hasUnacknowledgedCritical && (
              <Tooltip content="Contains unacknowledged critical results" position="top">
                <span className="inline-flex items-center">
                  <AlertBellIcon className="h-4 w-4 text-critical animate-pulse" />
                </span>
              </Tooltip>
            )}
          </div>

          <svg
            xmlns="http://www.w3.org/2000/svg"
            className={cn('h-4 w-4 text-text-tertiary transition-transform', isExpanded && 'rotate-180')}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </div>

        <div className="flex items-center gap-2 ml-4 mt-0.5">
          {panel.performingLab && (
            <span className="text-[11px] text-text-tertiary">
              {panel.performingLab}
            </span>
          )}
          {/* Panel last updated timestamp */}
          {panel.lastUpdated && (
            <>
              {panel.performingLab && <span className="text-[11px] text-text-tertiary">•</span>}
              <span className="text-[11px] text-text-tertiary">
                Updated: {formatRelativeTime(panel.lastUpdated)}
              </span>
            </>
          )}
        </div>
      </button>

      {/* Panel Results */}
      {isExpanded && (
        <div className="px-3 pb-3 pt-1 border-t border-frost">
          <div className="space-y-1">
            {panel.results.map((result) => (
              <LabResultRow
                key={result.id}
                result={result}
                showPerformingLab={showResultPerformingLab}
                onClick={() => onLabClick(result)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Trend Indicator Component with Tooltip
interface TrendIndicatorProps {
  trend: TrendInfo;
  unit: string;
  previousValue?: PreviousLabValue;
}

function TrendIndicator({ trend, unit, previousValue }: TrendIndicatorProps) {
  const significanceStyles: Record<ClinicalSignificance, string> = {
    good: 'text-success',
    concerning: 'text-critical',
    neutral: 'text-text-tertiary',
  };

  const arrowSymbols: Record<TrendDirection, string> = {
    up: '↗',
    down: '↘',
    stable: '—',
  };

  const colorClass = significanceStyles[trend.significance];
  const arrow = arrowSymbols[trend.direction];

  const formatChange = () => {
    if (trend.direction === 'stable') {
      return 'stable';
    }

    const percentStr = trend.percentChange.toFixed(0);
    if (trend.absoluteChange < 10 && trend.percentChange > 10) {
      return `${trend.absoluteChange.toFixed(1)} ${unit}`;
    }
    return `${percentStr}%`;
  };

  const tooltipContent = previousValue ? (
    <div className="text-[13px]">
      <div>Previous: {previousValue.value} {unit}</div>
      <div className="text-white/70">{formatDate(previousValue.collectionDate)}</div>
    </div>
  ) : null;

  const indicator = (
    <span className={cn('flex items-center gap-0.5 text-[13px] font-medium cursor-help', colorClass)}>
      <span className="text-[15px]">{arrow}</span>
      <span>{formatChange()}</span>
    </span>
  );

  if (tooltipContent) {
    return (
      <Tooltip content={tooltipContent} position="top">
        {indicator}
      </Tooltip>
    );
  }

  return indicator;
}

// Value Direction Indicator Component
interface ValueDirectionIndicatorProps {
  direction: ValueDirection;
  isCritical: boolean;
}

function ValueDirectionIndicator({ direction, isCritical }: ValueDirectionIndicatorProps) {
  if (isCritical) {
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 bg-critical/15 border border-critical/30 rounded text-[11px] font-semibold text-critical uppercase tracking-wide">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-3 w-3"
          viewBox="0 0 20 20"
          fill="currentColor"
          aria-hidden="true"
        >
          <path
            fillRule="evenodd"
            d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
            clipRule="evenodd"
          />
        </svg>
        Critical
      </span>
    );
  }

  if (direction === 'normal') return null;

  if (direction === 'high') {
    return (
      <span
        className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-[var(--color-lab-high)]/15 border border-[var(--color-lab-high)]/30 rounded text-[var(--color-lab-high)] font-semibold"
        title="High - above reference range"
      >
        <span className="text-[11px]" aria-hidden="true">▲</span>
        <span className="text-[11px]">H</span>
      </span>
    );
  }

  if (direction === 'low') {
    return (
      <span
        className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-[var(--color-lab-low)]/15 border border-[var(--color-lab-low)]/30 rounded text-[var(--color-lab-low)] font-semibold"
        title="Low - below reference range"
      >
        <span className="text-[11px]" aria-hidden="true">▼</span>
        <span className="text-[11px]">L</span>
      </span>
    );
  }

  if (direction === 'borderline-high') {
    return (
      <span
        className="inline-flex items-center gap-0.5 text-[var(--color-lab-borderline)] opacity-70"
        title="Borderline high - approaching upper limit"
      >
        <span className="text-[10px]" aria-hidden="true">▲</span>
        <span className="text-[11px] italic">near high</span>
      </span>
    );
  }

  if (direction === 'borderline-low') {
    return (
      <span
        className="inline-flex items-center gap-0.5 text-[var(--color-lab-borderline)] opacity-70"
        title="Borderline low - approaching lower limit"
      >
        <span className="text-[10px]" aria-hidden="true">▼</span>
        <span className="text-[11px] italic">near low</span>
      </span>
    );
  }

  return null;
}

function getValueStyles(direction: ValueDirection, isCritical: boolean): string {
  if (isCritical) {
    return 'text-critical font-bold';
  }

  switch (direction) {
    case 'high':
      return 'text-[var(--color-lab-high)] font-semibold';
    case 'low':
      return 'text-[var(--color-lab-low)] font-semibold';
    case 'borderline-high':
    case 'borderline-low':
      return 'text-[var(--color-lab-borderline)] font-medium';
    default:
      return 'text-success';
  }
}

function getDotStyles(direction: ValueDirection, isCritical: boolean): string {
  if (isCritical) {
    return 'bg-critical';
  }

  switch (direction) {
    case 'high':
      return 'bg-[var(--color-lab-high)]';
    case 'low':
      return 'bg-[var(--color-lab-low)]';
    case 'borderline-high':
    case 'borderline-low':
      return 'bg-[var(--color-lab-borderline)] opacity-70';
    default:
      return 'bg-success';
  }
}

interface LabResultRowProps {
  result: LabResult;
  showPerformingLab?: boolean;
  onClick?: () => void;
}

function LabResultRow({ result, showPerformingLab = true, onClick }: LabResultRowProps) {
  const displayName = getStandardTestName(result.testName);
  const formattedRange = formatReferenceRange(result.referenceRange, result.unit);
  const trend = calculateTrend(result.value, result.previousValue, result.testName);

  const isCritical = result.status === 'critical';
  const isPending = result.status === 'pending' || result.status === 'in_progress';
  const isUnacknowledgedCritical = isCritical && result.acknowledged === false;
  const valueDirection = getValueDirection(result.value, result.referenceRange, result.status);

  const valueStyles = isPending ? 'text-text-tertiary italic' : getValueStyles(valueDirection, isCritical);
  const dotStyles = statusConfig[result.status]?.dotClass || getDotStyles(valueDirection, isCritical);

  return (
    <div
      className={cn(
        'py-1.5 px-2 rounded transition-colors',
        onClick && 'cursor-pointer',
        isUnacknowledgedCritical
          ? 'bg-critical/10 hover:bg-critical/15 border-l-2 border-critical'
          : isCritical
          ? 'bg-critical/5 hover:bg-critical/10'
          : isPending
          ? 'bg-frost/20 hover:bg-frost/30'
          : 'hover:bg-frost/30'
      )}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => e.key === 'Enter' && onClick() : undefined}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={cn('w-1.5 h-1.5 rounded-full flex-shrink-0', dotStyles)} />
          <span className="text-[15px] text-text-primary">{displayName}</span>
          {onClick && !isPending && (
            <svg
              className="w-3 h-3 text-text-tertiary"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M9 5l7 7-7 7" />
            </svg>
          )}
        </div>

        <div className="flex items-center gap-2 text-[15px]">
          {/* Pending/In Progress status badge */}
          {isPending && (
            <StatusBadge status={result.status} />
          )}

          {/* Value display - show placeholder for pending */}
          {isPending ? (
            <span className="text-text-tertiary italic">
              {result.status === 'pending' ? 'Awaiting results' : 'Processing...'}
            </span>
          ) : (
            <>
              <span className={cn('font-medium', valueStyles)}>
                {result.value} {result.unit}
              </span>

              <ValueDirectionIndicator direction={valueDirection} isCritical={isCritical} />

              {/* Unacknowledged critical alert icon */}
              {isUnacknowledgedCritical && (
                <Tooltip content="Critical result not yet acknowledged" position="top">
                  <span className="inline-flex items-center">
                    <AlertBellIcon className="h-4 w-4 text-critical animate-pulse" />
                  </span>
                </Tooltip>
              )}

              {trend && (
                <TrendIndicator
                  trend={trend}
                  unit={result.unit}
                  previousValue={result.previousValue}
                />
              )}

              {formattedRange && (
                <span className="text-text-tertiary text-[13px]">
                  ({formattedRange})
                </span>
              )}
            </>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 ml-4 mt-0.5">
        <span className="text-[11px] text-text-tertiary">
          Collected: {formatDate(result.collectionDate)}
        </span>
        {/* Last updated timestamp */}
        {result.lastUpdated && (
          <>
            <span className="text-[11px] text-text-tertiary">•</span>
            <span className="text-[11px] text-text-tertiary">
              Updated: {formatRelativeTime(result.lastUpdated)}
            </span>
          </>
        )}
        {!isPending && trend && result.previousValue && (
          <>
            <span className="text-[11px] text-text-tertiary">•</span>
            <span className="text-[11px] text-text-tertiary">
              Prior: {result.previousValue.value} {result.unit} ({formatDate(result.previousValue.collectionDate)})
            </span>
          </>
        )}
        {showPerformingLab && result.performingLab && (
          <>
            <span className="text-[11px] text-text-tertiary">•</span>
            <span className="text-[11px] text-text-tertiary">
              {result.performingLab}
            </span>
          </>
        )}
      </div>
    </div>
  );
}

// Status badge for pending/in_progress labs
function StatusBadge({ status }: { status: LabResultStatus }) {
  const config = statusConfig[status];
  if (!config || (status !== 'pending' && status !== 'in_progress')) return null;

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium',
        status === 'pending'
          ? 'bg-frost/50 text-text-tertiary'
          : 'bg-glacier-blue/20 text-glacier-blue'
      )}
    >
      <span className={cn('w-1.5 h-1.5 rounded-full', config.dotClass)} />
      {config.label}
    </span>
  );
}

function LabIcon({ className }: { className?: string }) {
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
      <path d="M14.5 2v6a2 2 0 0 0 2 2h6" />
      <path d="M4 5.5V4a2 2 0 0 1 2-2h8.93a2 2 0 0 1 1.66.88l4.29 6.36a2 2 0 0 1 .31 1.06V20a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-5.5" />
      <path d="M2 10h10" />
      <path d="M7 16V10" />
    </svg>
  );
}

// Alert bell icon for unacknowledged critical results
function AlertBellIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      viewBox="0 0 24 24"
      fill="currentColor"
    >
      <path d="M5.85 3.5a.75.75 0 00-1.117-1 9.719 9.719 0 00-2.348 4.876.75.75 0 001.479.248A8.219 8.219 0 015.85 3.5zM19.267 2.5a.75.75 0 10-1.118 1 8.22 8.22 0 011.987 4.124.75.75 0 001.48-.248A9.72 9.72 0 0019.266 2.5z" />
      <path fillRule="evenodd" d="M12 2.25A6.75 6.75 0 005.25 9v.75a8.217 8.217 0 01-2.119 5.52.75.75 0 00.298 1.206c1.544.57 3.16.99 4.831 1.243a3.75 3.75 0 107.48 0 24.583 24.583 0 004.83-1.244.75.75 0 00.298-1.205 8.217 8.217 0 01-2.118-5.52V9A6.75 6.75 0 0012 2.25zM9.75 18c0-.034 0-.067.002-.1a25.05 25.05 0 004.496 0l.002.1a2.25 2.25 0 11-4.5 0z" clipRule="evenodd" />
    </svg>
  );
}

// Clock icon for pending labs
function ClockIcon({ className }: { className?: string }) {
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
