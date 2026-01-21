import { useState, useMemo } from 'react';
import type {
  Problem,
  ProblemStatus,
  ProblemPriority,
  ProblemSeverity,
  ProblemComplexity,
  ClinicalCategory,
  RelatedVisit,
  RelatedMedication,
  RelatedLabResult,
  ProblemGroup,
  ProblemFilterStatus,
  ProblemSortOption,
} from '../../types';
import { Card, CardContent } from '../ui';
import { cn } from '../../utils/cn';

interface ProblemListSectionProps {
  /**
   * Patient's problem list.
   * - undefined or empty = no problems documented
   * - populated = documented problems
   */
  problemList: Problem[] | undefined;
  /**
   * Optional grouped problems by clinical category.
   * If provided, displays problems in grouped view.
   */
  groups?: ProblemGroup[];
  /**
   * Callback when a related visit is clicked.
   */
  onVisitClick?: (visitId: string) => void;
  /**
   * Callback when a related medication is clicked.
   */
  onMedicationClick?: (medicationId: string) => void;
  /**
   * Callback when a related lab is clicked.
   */
  onLabClick?: (labName: string) => void;
  /**
   * Callback when a problem is clicked for detailed view.
   */
  onProblemClick?: (problem: Problem) => void;
  /**
   * Callback when a resolved/inactive problem should be reactivated.
   * Called with the ICD-10 code of the problem.
   */
  onReactivateProblem?: (icd10Code: string) => void;
}

const priorityOrder: Record<ProblemPriority, number> = {
  acute: 0,
  chronic: 1,
  inactive: 2,
  resolved: 3,
};

/**
 * Sort problems by clinical priority:
 * 1. Critical problems first (life-threatening conditions)
 * 2. By priority: acute > chronic > inactive > resolved
 * 3. By onset date (most recent first)
 */
function sortProblemsByClinicalPriority(problems: Problem[]): Problem[] {
  return [...problems].sort((a, b) => {
    // Primary: critical problems first
    if (a.isCritical !== b.isCritical) {
      return a.isCritical ? -1 : 1;
    }
    // Secondary: by priority
    const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
    if (priorityDiff !== 0) return priorityDiff;
    // Tertiary: by onset date (most recent first)
    const dateA = new Date(a.onsetDate).getTime();
    const dateB = new Date(b.onsetDate).getTime();
    return dateB - dateA;
  });
}

/**
 * Group problems by clinical category for display.
 */
function groupProblemsByCategory(problems: Problem[]): Map<ClinicalCategory, Problem[]> {
  const groups = new Map<ClinicalCategory, Problem[]>();

  for (const problem of problems) {
    const category = problem.clinicalCategory || 'other';
    if (!groups.has(category)) {
      groups.set(category, []);
    }
    groups.get(category)!.push(problem);
  }

  return groups;
}

const statusConfig: Record<ProblemStatus, { label: string; badgeClass: string; dotClass: string }> = {
  active: {
    label: 'Active',
    badgeClass: 'bg-glacier-blue/10 text-glacier-blue',
    dotClass: 'bg-glacier-blue',
  },
  inactive: {
    label: 'Inactive',
    badgeClass: 'bg-frost text-text-tertiary',
    dotClass: 'bg-text-tertiary',
  },
  resolved: {
    label: 'Resolved',
    badgeClass: 'bg-success/10 text-success',
    dotClass: 'bg-success',
  },
  rule_out: {
    label: 'Rule Out',
    badgeClass: 'bg-amber-100 text-amber-700',
    dotClass: 'bg-amber-500',
  },
};

const priorityConfig: Record<ProblemPriority, { label: string; badgeClass: string }> = {
  acute: {
    label: 'Acute',
    badgeClass: 'bg-warning/10 text-warning',
  },
  chronic: {
    label: 'Chronic',
    badgeClass: 'bg-deep-ice/10 text-deep-ice',
  },
  inactive: {
    label: 'Inactive',
    badgeClass: 'bg-frost text-text-tertiary',
  },
  resolved: {
    label: 'Resolved',
    badgeClass: 'bg-frost text-text-tertiary',
  },
};

const severityConfig: Record<ProblemSeverity, { label: string; badgeClass: string }> = {
  mild: {
    label: 'Mild',
    badgeClass: 'bg-success/10 text-success',
  },
  moderate: {
    label: 'Moderate',
    badgeClass: 'bg-warning/10 text-warning',
  },
  severe: {
    label: 'Severe',
    badgeClass: 'bg-critical/10 text-critical',
  },
  well_controlled: {
    label: 'Well-controlled',
    badgeClass: 'bg-glacier-blue/10 text-glacier-blue',
  },
};

const complexityConfig: Record<ProblemComplexity, { label: string; badgeClass: string }> = {
  simple: {
    label: 'Simple',
    badgeClass: 'bg-frost text-text-tertiary',
  },
  with_complications: {
    label: 'With Complications',
    badgeClass: 'bg-warning/10 text-warning',
  },
  controlled: {
    label: 'Controlled',
    badgeClass: 'bg-success/10 text-success',
  },
  uncontrolled: {
    label: 'Uncontrolled',
    badgeClass: 'bg-critical/10 text-critical',
  },
  progressive: {
    label: 'Progressive',
    badgeClass: 'bg-critical/10 text-critical',
  },
};

const categoryConfig: Record<ClinicalCategory, { label: string; icon: string }> = {
  cardiovascular: { label: 'Cardiovascular', icon: '❤️' },
  endocrine: { label: 'Endocrine & Metabolic', icon: '🔬' },
  respiratory: { label: 'Respiratory', icon: '🫁' },
  musculoskeletal: { label: 'Musculoskeletal', icon: '🦴' },
  neurological: { label: 'Neurological', icon: '🧠' },
  gastrointestinal: { label: 'Gastrointestinal', icon: '🔘' },
  psychiatric: { label: 'Mental Health', icon: '🧘' },
  infectious: { label: 'Infectious Disease', icon: '🦠' },
  oncology: { label: 'Oncology', icon: '🎗️' },
  renal: { label: 'Renal & Urological', icon: '💧' },
  dermatological: { label: 'Dermatological', icon: '🔅' },
  other: { label: 'Other', icon: '📋' },
};

const DEFAULT_VISIBLE_COUNT = 6;

/**
 * Format onset date in MM/YYYY format by default.
 * If the date includes day information (not the 1st of the month),
 * display as MM/DD/YYYY for exact dates.
 */
function formatOnsetDate(isoDate: string): string {
  const date = new Date(isoDate);
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = date.getDate();
  const year = date.getFullYear();

  // If day is 1, assume month/year precision only
  // Otherwise show the full date
  if (day === 1) {
    return `${month}/${year}`;
  }
  return `${month}/${String(day).padStart(2, '0')}/${year}`;
}

/**
 * Format documented date in MM/DD/YYYY format.
 */
function formatDocumentedDate(isoDate: string): string {
  const date = new Date(isoDate);
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const year = date.getFullYear();
  return `${month}/${day}/${year}`;
}

/**
 * Format visit type for display.
 */
function formatVisitType(visitType: string): string {
  return visitType.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

export function ProblemListSection({
  problemList,
  groups: _groups,
  onVisitClick,
  onMedicationClick,
  onLabClick,
  onProblemClick,
  onReactivateProblem,
}: ProblemListSectionProps) {
  // Note: `_groups` is available for server-provided groupings but currently
  // we compute groups client-side from the problems' clinicalCategory field
  const [isExpanded, setIsExpanded] = useState(false);
  const [viewMode, setViewMode] = useState<'list' | 'grouped'>('list');

  // Filter, sort, and search state
  const [filterStatus, setFilterStatus] = useState<ProblemFilterStatus>('all');
  const [sortOption, setSortOption] = useState<ProblemSortOption>('onset');
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  // Filter, sort, and search problems
  const filteredAndSortedProblems = useMemo(() => {
    if (!problemList) return [];

    let filtered = [...problemList];

    // Apply filter
    switch (filterStatus) {
      case 'active':
        filtered = filtered.filter((p) => p.status === 'active');
        break;
      case 'chronic':
        filtered = filtered.filter((p) => p.priority === 'chronic' && p.status === 'active');
        break;
      case 'inactive':
        filtered = filtered.filter((p) => p.status === 'inactive');
        break;
      case 'resolved':
        filtered = filtered.filter((p) => p.status === 'resolved');
        break;
      // 'all' - no filtering
    }

    // Apply search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim();
      filtered = filtered.filter(
        (p) =>
          p.name.toLowerCase().includes(query) ||
          p.icd10Code.toLowerCase().includes(query) ||
          (p.clinicalCategory && p.clinicalCategory.toLowerCase().includes(query))
      );
    }

    // Apply sort
    switch (sortOption) {
      case 'name':
        filtered.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'lastUpdated':
        filtered.sort((a, b) => {
          const dateA = a.documentedDate ? new Date(a.documentedDate).getTime() : 0;
          const dateB = b.documentedDate ? new Date(b.documentedDate).getTime() : 0;
          return dateB - dateA;
        });
        break;
      case 'onset':
      default:
        // Sort by clinical priority first, then by onset date
        filtered = sortProblemsByClinicalPriority(filtered);
        break;
    }

    return filtered;
  }, [problemList, filterStatus, sortOption, searchQuery]);

  // No problems documented
  if (!problemList || problemList.length === 0) {
    return (
      <Card>
        <CardContent>
          <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-normal">
            Problem List
          </h3>
          <div className="flex items-center gap-tight text-success">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            <span className="text-[15px] font-medium">No active problems</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Check if any problems have clinical categories for grouping
  const hasCategories = problemList.some((p) => p.clinicalCategory);
  const categoryGroups = hasCategories ? groupProblemsByCategory(filteredAndSortedProblems) : null;

  // Count problems by category (from original list)
  const activeCount = problemList.filter((p) => p.status === 'active').length;
  const resolvedCount = problemList.filter((p) => p.status === 'resolved').length;
  const inactiveCount = problemList.filter((p) => p.status === 'inactive').length;
  const criticalCount = problemList.filter((p) => p.isCritical).length;
  const newCount = problemList.filter((p) => p.isNew).length;
  const chronicCount = problemList.filter((p) => p.priority === 'chronic' && p.status === 'active').length;

  // Determine visible problems
  const hasMore = filteredAndSortedProblems.length > DEFAULT_VISIBLE_COUNT;
  const visibleProblems = isExpanded
    ? filteredAndSortedProblems
    : filteredAndSortedProblems.slice(0, DEFAULT_VISIBLE_COUNT);

  // Check if filters are active
  const hasActiveFilters = filterStatus !== 'all' || searchQuery.trim() !== '';

  return (
    <Card>
      <CardContent>
        {/* Header */}
        <div className="flex items-center justify-between mb-tight">
          <div className="flex items-center gap-2">
            <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
              Problem List
            </h3>
            <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-frost text-text-secondary">
              {hasActiveFilters ? `${filteredAndSortedProblems.length}/${problemList.length}` : problemList.length}
            </span>
            {/* View toggle if categories available */}
            {hasCategories && (
              <div className="flex items-center gap-1 ml-2">
                <button
                  type="button"
                  onClick={() => setViewMode('list')}
                  className={cn(
                    'px-2 py-0.5 rounded text-[11px] transition-colors',
                    viewMode === 'list'
                      ? 'bg-glacier-blue/10 text-glacier-blue'
                      : 'text-text-tertiary hover:text-text-secondary'
                  )}
                >
                  List
                </button>
                <button
                  type="button"
                  onClick={() => setViewMode('grouped')}
                  className={cn(
                    'px-2 py-0.5 rounded text-[11px] transition-colors',
                    viewMode === 'grouped'
                      ? 'bg-glacier-blue/10 text-glacier-blue'
                      : 'text-text-tertiary hover:text-text-secondary'
                  )}
                >
                  Grouped
                </button>
              </div>
            )}
          </div>
          {/* Filter toggle and summary badges */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={cn(
                'flex items-center gap-1 px-2 py-1 rounded text-[13px] transition-colors',
                showFilters || hasActiveFilters
                  ? 'bg-glacier-blue/10 text-glacier-blue'
                  : 'text-text-tertiary hover:text-text-secondary hover:bg-frost/50'
              )}
              title="Toggle filters"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
              </svg>
              <span className="hidden sm:inline">Filter</span>
              {hasActiveFilters && (
                <span className="w-2 h-2 rounded-full bg-glacier-blue" />
              )}
            </button>
            <div className="hidden sm:flex items-center gap-1">
              {criticalCount > 0 && (
                <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-critical/10 text-critical">
                  {criticalCount} critical
                </span>
              )}
              {newCount > 0 && (
                <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-deep-ice/10 text-deep-ice">
                  {newCount} new
                </span>
              )}
              {activeCount > 0 && (
                <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-glacier-blue/10 text-glacier-blue">
                  {activeCount} active
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Filter/Sort/Search Controls */}
        {showFilters && (
          <div className="mb-normal pb-normal border-b border-frost/50 space-y-3">
            {/* Search input */}
            <div className="relative">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by name or ICD-10 code..."
                className="w-full pl-9 pr-3 py-2 text-[15px] bg-frost/30 border border-frost rounded-md placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-glacier-blue/30 focus:border-glacier-blue"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-text-tertiary hover:text-text-secondary"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                </button>
              )}
            </div>

            {/* Filter and Sort row */}
            <div className="flex flex-wrap items-center gap-3">
              {/* Filter by status */}
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                  Filter:
                </span>
                <div className="flex items-center gap-1 flex-wrap">
                  {[
                    { value: 'all', label: 'All', count: problemList.length },
                    { value: 'active', label: 'Active', count: activeCount },
                    { value: 'chronic', label: 'Chronic', count: chronicCount },
                    { value: 'inactive', label: 'Inactive', count: inactiveCount },
                    { value: 'resolved', label: 'Resolved', count: resolvedCount },
                  ].map(({ value, label, count }) => (
                    <button
                      key={value}
                      type="button"
                      onClick={() => setFilterStatus(value as ProblemFilterStatus)}
                      className={cn(
                        'px-2 py-1 rounded text-[13px] transition-colors',
                        filterStatus === value
                          ? 'bg-glacier-blue/10 text-glacier-blue font-medium'
                          : 'text-text-secondary hover:bg-frost/50'
                      )}
                    >
                      {label}
                      <span className="ml-1 text-[11px] text-text-tertiary">({count})</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Sort by */}
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                  Sort:
                </span>
                <div className="flex items-center gap-1">
                  {[
                    { value: 'onset', label: 'Onset Date' },
                    { value: 'name', label: 'Name' },
                    { value: 'lastUpdated', label: 'Last Updated' },
                  ].map(({ value, label }) => (
                    <button
                      key={value}
                      type="button"
                      onClick={() => setSortOption(value as ProblemSortOption)}
                      className={cn(
                        'px-2 py-1 rounded text-[13px] transition-colors',
                        sortOption === value
                          ? 'bg-glacier-blue/10 text-glacier-blue font-medium'
                          : 'text-text-secondary hover:bg-frost/50'
                      )}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Clear filters button */}
              {hasActiveFilters && (
                <button
                  type="button"
                  onClick={() => {
                    setFilterStatus('all');
                    setSearchQuery('');
                  }}
                  className="px-2 py-1 rounded text-[13px] text-glacier-blue hover:bg-glacier-blue/10 transition-colors"
                >
                  Clear filters
                </button>
              )}
            </div>
          </div>
        )}

        {/* No results message */}
        {filteredAndSortedProblems.length === 0 && hasActiveFilters && (
          <div className="py-8 text-center text-text-tertiary">
            <p className="text-[15px]">No problems match your filters</p>
            <button
              type="button"
              onClick={() => {
                setFilterStatus('all');
                setSearchQuery('');
              }}
              className="mt-2 text-[13px] text-glacier-blue hover:text-deep-ice transition-colors"
            >
              Clear filters
            </button>
          </div>
        )}

        {/* Problem list - grouped view */}
        {filteredAndSortedProblems.length > 0 && viewMode === 'grouped' && categoryGroups ? (
          <div className="space-y-4">
            {Array.from(categoryGroups.entries()).map(([category, problems]) => (
              <ProblemCategoryGroup
                key={category}
                category={category}
                problems={problems}
                onVisitClick={onVisitClick}
                onMedicationClick={onMedicationClick}
                onLabClick={onLabClick}
                onProblemClick={onProblemClick}
                onReactivateProblem={onReactivateProblem}
              />
            ))}
          </div>
        ) : filteredAndSortedProblems.length > 0 ? (
          /* Problem list - flat view */
          <>
            <ul className="space-y-2">
              {visibleProblems.map((problem, index) => (
                <ProblemItem
                  key={`${problem.icd10Code}-${index}`}
                  problem={problem}
                  onVisitClick={onVisitClick}
                  onMedicationClick={onMedicationClick}
                  onLabClick={onLabClick}
                  onProblemClick={onProblemClick}
                  onReactivateProblem={onReactivateProblem}
                />
              ))}
            </ul>

            {/* View All / Show Less button */}
            {hasMore && (
              <button
                type="button"
                onClick={() => setIsExpanded(!isExpanded)}
                className="mt-normal flex items-center gap-1 text-[13px] text-glacier-blue hover:text-deep-ice transition-colors"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className={cn('h-4 w-4 transition-transform', isExpanded && 'rotate-180')}
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polyline points="6 9 12 15 18 9" />
                </svg>
                {isExpanded
                  ? 'Show Less'
                  : `View All (${filteredAndSortedProblems.length - DEFAULT_VISIBLE_COUNT} more)`}
              </button>
            )}
          </>
        ) : null}
      </CardContent>
    </Card>
  );
}

interface ProblemCategoryGroupProps {
  category: ClinicalCategory;
  problems: Problem[];
  onVisitClick?: (visitId: string) => void;
  onMedicationClick?: (medicationId: string) => void;
  onLabClick?: (labName: string) => void;
  onProblemClick?: (problem: Problem) => void;
  onReactivateProblem?: (icd10Code: string) => void;
}

function ProblemCategoryGroup({
  category,
  problems,
  onVisitClick,
  onMedicationClick,
  onLabClick,
  onProblemClick,
  onReactivateProblem,
}: ProblemCategoryGroupProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const config = categoryConfig[category] || categoryConfig.other;

  return (
    <div className="border border-frost/50 rounded-lg overflow-hidden">
      {/* Category header */}
      <button
        type="button"
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="w-full px-3 py-2 bg-frost/30 flex items-center justify-between text-left hover:bg-frost/50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="text-[15px]">{config.icon}</span>
          <span className="text-[15px] font-medium text-text-primary">{config.label}</span>
          <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-frost text-text-secondary">
            {problems.length}
          </span>
        </div>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className={cn('h-4 w-4 text-text-tertiary transition-transform', isCollapsed && '-rotate-90')}
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

      {/* Problems in this category */}
      {!isCollapsed && (
        <ul className="p-2 space-y-2">
          {problems.map((problem, index) => (
            <ProblemItem
              key={`${problem.icd10Code}-${index}`}
              problem={problem}
              onVisitClick={onVisitClick}
              onMedicationClick={onMedicationClick}
              onLabClick={onLabClick}
              onProblemClick={onProblemClick}
              onReactivateProblem={onReactivateProblem}
              showCategory={false}
            />
          ))}
        </ul>
      )}
    </div>
  );
}

interface ProblemItemProps {
  problem: Problem;
  onVisitClick?: (visitId: string) => void;
  onMedicationClick?: (medicationId: string) => void;
  onLabClick?: (labName: string) => void;
  onProblemClick?: (problem: Problem) => void;
  onReactivateProblem?: (icd10Code: string) => void;
  showCategory?: boolean;
}

function ProblemItem({
  problem,
  onVisitClick,
  onMedicationClick,
  onLabClick,
  onProblemClick,
  onReactivateProblem,
  showCategory = true,
}: ProblemItemProps) {
  const [showContext, setShowContext] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);

  const status = statusConfig[problem.status] || statusConfig.active;
  const priority = priorityConfig[problem.priority] || priorityConfig.chronic;
  const severity = problem.severity ? severityConfig[problem.severity] : null;
  const complexity = problem.complexity ? complexityConfig[problem.complexity] : null;
  const category = problem.clinicalCategory ? categoryConfig[problem.clinicalCategory] : null;

  const isResolved = problem.status === 'resolved';
  const isInactive = problem.status === 'inactive';
  const isRuleOut = problem.isRuleOut;
  const isAcute = problem.priority === 'acute';
  const isCritical = problem.isCritical;
  const isNew = problem.isNew;

  // Check if problem has related context items for the expand/collapse button
  const hasRelatedContext =
    (problem.relatedVisits && problem.relatedVisits.length > 0) ||
    (problem.relatedMedications && problem.relatedMedications.length > 0) ||
    (problem.relatedLabs && problem.relatedLabs.length > 0);

  // Get the most recent related visit date for "last addressed"
  const lastAddressedDate = problem.relatedVisits && problem.relatedVisits.length > 0
    ? problem.relatedVisits.sort((a, b) =>
        new Date(b.date).getTime() - new Date(a.date).getTime()
      )[0]?.date
    : null;

  // Get current treatment from related medications
  const currentTreatment = problem.relatedMedications && problem.relatedMedications.length > 0
    ? problem.relatedMedications.map((m) => m.name).join(', ')
    : null;

  return (
    <li
      className={cn(
        'rounded-md px-3 py-2 bg-white shadow-sm border border-frost/50 relative',
        // Critical problems get prominent red styling
        isCritical && 'border-l-4 border-l-critical bg-critical/5',
        // Rule out problems get amber styling (only if not critical)
        isRuleOut && !isCritical && 'border-l-2 border-l-amber-500 bg-amber-50/30',
        // Acute problems get warning styling (only if not critical or rule out)
        isAcute && !isRuleOut && !isCritical && 'border-l-2 border-l-warning',
        // Resolved problems are de-emphasized
        isResolved && 'opacity-60 border-dashed',
        // Inactive problems are slightly de-emphasized
        isInactive && 'opacity-75',
        // Clickable styling
        onProblemClick && 'cursor-pointer hover:shadow-card-hover hover:border-glacier-blue/30 transition-all'
      )}
      onClick={() => onProblemClick?.(problem)}
      onMouseEnter={() => onProblemClick && setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {/* Hover tooltip - only show if there's context info */}
      {showTooltip && onProblemClick && (lastAddressedDate || currentTreatment) && (
        <div className="absolute left-0 bottom-full mb-2 z-10 w-64 p-3 bg-white rounded-lg shadow-lg border border-frost/50 text-[13px]">
          <div className="absolute left-4 bottom-0 translate-y-1/2 rotate-45 w-2 h-2 bg-white border-r border-b border-frost/50" />
          {lastAddressedDate && (
            <div className={currentTreatment ? 'mb-2' : ''}>
              <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">Last Addressed</span>
              <p className="text-text-primary">{formatDocumentedDate(lastAddressedDate)}</p>
            </div>
          )}
          {currentTreatment && (
            <div>
              <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">Current Treatment</span>
              <p className="text-text-primary">{currentTreatment}</p>
            </div>
          )}
        </div>
      )}
      {/* Top row: name with ICD-10 code and badges */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 flex-wrap min-w-0">
          {/* Status dot */}
          <span className={cn(
            'w-2 h-2 rounded-full flex-shrink-0',
            isCritical ? 'bg-critical' : status.dotClass
          )} />

          {/* Problem name with ICD-10 code in parentheses */}
          <span className={cn(
            'text-[15px] font-medium text-text-primary',
            (isResolved || isInactive) && 'line-through decoration-text-tertiary/50',
            isCritical && 'text-critical'
          )}>
            {problem.name}{' '}
            <span className="font-mono text-[13px] text-deep-ice">({problem.icd10Code})</span>
          </span>

          {/* Critical badge - highest priority indicator */}
          {isCritical && (
            <span className="px-1.5 py-0.5 text-[11px] font-bold rounded bg-critical/10 text-critical uppercase">
              Critical
            </span>
          )}

          {/* NEW badge for recently documented problems */}
          {isNew && !isResolved && (
            <span className="px-1.5 py-0.5 text-[11px] font-bold rounded bg-deep-ice/10 text-deep-ice uppercase">
              New
            </span>
          )}

          {/* Rule out indicator */}
          {isRuleOut && (
            <span className="px-1.5 py-0.5 text-[11px] font-medium rounded bg-amber-100 text-amber-700 flex items-center gap-1">
              <span className="text-amber-600">?</span> Rule Out
            </span>
          )}

          {/* Priority badge for acute problems (only if not critical) */}
          {isAcute && !isCritical && !isRuleOut && (
            <span className={cn('px-1.5 py-0.5 text-[11px] font-medium rounded', priority.badgeClass)}>
              {priority.label}
            </span>
          )}

          {/* Complexity badge (show if not simple) */}
          {complexity && problem.complexity !== 'simple' && (
            <span className={cn('px-1.5 py-0.5 text-[11px] font-medium rounded', complexity.badgeClass)}>
              {complexity.label}
            </span>
          )}

          {/* Severity badge */}
          {severity && (
            <span className={cn('px-1.5 py-0.5 text-[11px] font-medium rounded', severity.badgeClass)}>
              {severity.label}
            </span>
          )}

          {/* Category badge (optional) */}
          {showCategory && category && (
            <span className="px-1.5 py-0.5 text-[11px] font-medium rounded bg-frost text-text-tertiary">
              {category.label}
            </span>
          )}
        </div>

        {/* Status badge and context toggle */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {hasRelatedContext && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                setShowContext(!showContext);
              }}
              className={cn(
                'text-[11px] px-1.5 py-0.5 rounded transition-colors',
                showContext
                  ? 'bg-glacier-blue/10 text-glacier-blue'
                  : 'text-text-tertiary hover:text-glacier-blue hover:bg-glacier-blue/5'
              )}
              title={showContext ? 'Hide related items' : 'Show related visits, medications, and labs'}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="16" x2="12" y2="12" />
                <line x1="12" y1="8" x2="12.01" y2="8" />
              </svg>
            </button>
          )}
          <span className={cn('px-2 py-0.5 text-[11px] font-medium rounded', status.badgeClass)}>
            {status.label}
          </span>
        </div>
      </div>

      {/* Details row: onset date, documenting provider, documented date */}
      <div className="mt-1 ml-4 flex items-center flex-wrap gap-x-3 gap-y-1 text-[13px] text-text-secondary">
        {/* Onset date */}
        <span className="text-text-tertiary">
          Onset: {formatOnsetDate(problem.onsetDate)}
        </span>

        {/* Documenting provider and date */}
        {(problem.documentingProvider || problem.documentedDate) && (
          <span className="text-text-tertiary">
            {problem.documentingProvider && (
              <>Documented by {problem.documentingProvider}</>
            )}
            {problem.documentingProvider && problem.documentedDate && ' · '}
            {problem.documentedDate && formatDocumentedDate(problem.documentedDate)}
          </span>
        )}

        {/* Resolution info for resolved problems */}
        {isResolved && (problem.resolvedDate || problem.resolvedByProvider) && (
          <span className="text-success flex items-center gap-1">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-3 w-3"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            Resolved
            {problem.resolvedDate && ` ${formatDocumentedDate(problem.resolvedDate)}`}
            {problem.resolvedByProvider && ` by ${problem.resolvedByProvider}`}
          </span>
        )}

        {/* Parent problem indicator */}
        {problem.parentProblemCode && (
          <span className="text-text-tertiary italic">
            Complication of {problem.parentProblemCode}
          </span>
        )}

        {/* Reactivate button for resolved/inactive problems */}
        {(isResolved || isInactive) && onReactivateProblem && (
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onReactivateProblem(problem.icd10Code);
            }}
            className="px-2 py-0.5 rounded text-[11px] font-medium bg-glacier-blue/10 text-glacier-blue hover:bg-glacier-blue/20 transition-colors flex items-center gap-1"
            title="Reactivate this problem"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-3 w-3"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
              <path d="M21 3v5h-5" />
              <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
              <path d="M8 16H3v5" />
            </svg>
            Reactivate
          </button>
        )}
      </div>

      {/* Clinical context section */}
      {showContext && hasRelatedContext && (
        <div className="mt-3 ml-4 space-y-2 border-t border-frost/50 pt-2">
          {/* Related Visits */}
          {problem.relatedVisits && problem.relatedVisits.length > 0 && (
            <RelatedVisitsSection
              visits={problem.relatedVisits}
              onClick={onVisitClick}
            />
          )}

          {/* Related Medications */}
          {problem.relatedMedications && problem.relatedMedications.length > 0 && (
            <RelatedMedicationsSection
              medications={problem.relatedMedications}
              onClick={onMedicationClick}
            />
          )}

          {/* Related Labs */}
          {problem.relatedLabs && problem.relatedLabs.length > 0 && (
            <RelatedLabsSection
              labs={problem.relatedLabs}
              onClick={onLabClick}
            />
          )}
        </div>
      )}
    </li>
  );
}

interface RelatedVisitsSectionProps {
  visits: RelatedVisit[];
  onClick?: (visitId: string) => void;
}

function RelatedVisitsSection({ visits, onClick }: RelatedVisitsSectionProps) {
  return (
    <div className="space-y-1">
      <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
        Recent Visits
      </span>
      <div className="flex flex-wrap gap-2">
        {visits.map((visit) => (
          <button
            key={visit.visitId}
            type="button"
            onClick={() => onClick?.(visit.visitId)}
            disabled={!onClick}
            className={cn(
              'px-2 py-1 rounded text-[13px] bg-frost/50 text-text-secondary',
              onClick && 'hover:bg-glacier-blue/10 hover:text-glacier-blue cursor-pointer'
            )}
          >
            <span className="font-medium">{formatVisitType(visit.visitType)}</span>
            {visit.date && (
              <span className="text-text-tertiary ml-1">
                ({formatDocumentedDate(visit.date)})
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

interface RelatedMedicationsSectionProps {
  medications: RelatedMedication[];
  onClick?: (medicationId: string) => void;
}

function RelatedMedicationsSection({ medications, onClick }: RelatedMedicationsSectionProps) {
  return (
    <div className="space-y-1">
      <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
        Related Medications
      </span>
      <div className="flex flex-wrap gap-2">
        {medications.map((med) => (
          <button
            key={med.medicationId}
            type="button"
            onClick={() => onClick?.(med.medicationId)}
            disabled={!onClick}
            className={cn(
              'px-2 py-1 rounded text-[13px] bg-frost/50 text-text-secondary',
              onClick && 'hover:bg-glacier-blue/10 hover:text-glacier-blue cursor-pointer'
            )}
          >
            <span className="font-medium">{med.name}</span>
            {med.dosage && (
              <span className="text-text-tertiary ml-1">{med.dosage}</span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

interface RelatedLabsSectionProps {
  labs: RelatedLabResult[];
  onClick?: (labName: string) => void;
}

function RelatedLabsSection({ labs, onClick }: RelatedLabsSectionProps) {
  return (
    <div className="space-y-1">
      <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
        Related Lab Results
      </span>
      <div className="flex flex-wrap gap-2">
        {labs.map((lab) => (
          <button
            key={lab.labName}
            type="button"
            onClick={() => onClick?.(lab.labName)}
            disabled={!onClick}
            className={cn(
              'px-2 py-1 rounded text-[13px] bg-frost/50 text-text-secondary flex items-center gap-1',
              onClick && 'hover:bg-glacier-blue/10 hover:text-glacier-blue cursor-pointer'
            )}
          >
            <span className="font-medium">{lab.labName}</span>
            {lab.mostRecentValue && (
              <span className={cn(
                'text-text-tertiary',
                lab.status === 'abnormal' && 'text-warning',
                lab.status === 'critical' && 'text-critical font-medium'
              )}>
                {lab.mostRecentValue}
              </span>
            )}
            {lab.status && lab.status !== 'normal' && (
              <span className={cn(
                'w-2 h-2 rounded-full',
                lab.status === 'abnormal' && 'bg-warning',
                lab.status === 'critical' && 'bg-critical'
              )} />
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
