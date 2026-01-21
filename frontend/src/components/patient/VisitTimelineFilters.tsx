import { useState, useMemo } from 'react';
import type { EncounterType, VisitHistoryParams, VisitProviderOption } from '../../types';
import { cn } from '../../utils/cn';
import { DateJumpPicker } from './DateJumpPicker';

interface VisitTimelineFiltersProps {
  filters: VisitHistoryParams;
  onFiltersChange: (filters: VisitHistoryParams) => void;
  providers: VisitProviderOption[];
  onJumpToDate: (date: string) => void;
  isLoading?: boolean;
}

const visitTypeOptions: { value: EncounterType | ''; label: string }[] = [
  { value: '', label: 'All Types' },
  { value: 'office_visit', label: 'Office Visit' },
  { value: 'telehealth', label: 'Telehealth' },
  { value: 'urgent_care', label: 'Urgent Care' },
  { value: 'emergency', label: 'Emergency' },
  { value: 'hospital_admission', label: 'Hospital' },
  { value: 'procedure', label: 'Procedure' },
  { value: 'lab_only', label: 'Lab Only' },
  { value: 'follow_up', label: 'Follow-Up' },
];

export function VisitTimelineFilters({
  filters,
  onFiltersChange,
  providers,
  onJumpToDate,
  isLoading,
}: VisitTimelineFiltersProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [searchValue, setSearchValue] = useState(filters.searchQuery ?? '');

  // Count active filters (excluding search which is always visible)
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.visitType) count++;
    if (filters.providerId) count++;
    if (filters.diagnosisCode) count++;
    if (filters.dateFrom || filters.dateTo) count++;
    return count;
  }, [filters]);

  const handleSearchChange = (value: string) => {
    setSearchValue(value);
    // Apply search immediately for display, but let parent debounce API call
    onFiltersChange({ ...filters, searchQuery: value || undefined });
  };

  const handleVisitTypeChange = (value: string) => {
    onFiltersChange({
      ...filters,
      visitType: value ? (value as EncounterType) : undefined,
      offset: 0, // Reset pagination
    });
  };

  const handleProviderChange = (value: string) => {
    onFiltersChange({
      ...filters,
      providerId: value || undefined,
      offset: 0, // Reset pagination
    });
  };

  const handleDiagnosisChange = (value: string) => {
    onFiltersChange({
      ...filters,
      diagnosisCode: value || undefined,
      offset: 0, // Reset pagination
    });
  };

  const handleDateFromChange = (value: string) => {
    onFiltersChange({
      ...filters,
      dateFrom: value || undefined,
      offset: 0, // Reset pagination
    });
  };

  const handleDateToChange = (value: string) => {
    onFiltersChange({
      ...filters,
      dateTo: value || undefined,
      offset: 0, // Reset pagination
    });
  };

  const handleClearAll = () => {
    setSearchValue('');
    onFiltersChange({
      ...filters,
      searchQuery: undefined,
      visitType: undefined,
      providerId: undefined,
      diagnosisCode: undefined,
      dateFrom: undefined,
      dateTo: undefined,
      offset: 0,
    });
  };

  const hasAnyFilter = Boolean(
    filters.searchQuery ||
    filters.visitType ||
    filters.providerId ||
    filters.diagnosisCode ||
    filters.dateFrom ||
    filters.dateTo
  );

  return (
    <div className="mb-normal">
      {/* Search Bar + Filter Toggle */}
      <div className="flex items-center gap-2">
        {/* Search Input */}
        <div className="flex-1 relative">
          <SearchIcon className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary" />
          <input
            type="text"
            placeholder="Search visits..."
            value={searchValue}
            onChange={(e) => handleSearchChange(e.target.value)}
            disabled={isLoading}
            className={cn(
              'w-full pl-8 pr-3 py-2 text-[15px] rounded-md border border-frost',
              'focus:outline-none focus:ring-1 focus:ring-glacier-blue focus:border-glacier-blue',
              'placeholder:text-text-tertiary',
              isLoading && 'opacity-60'
            )}
          />
          {searchValue && (
            <button
              type="button"
              onClick={() => handleSearchChange('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 p-0.5 hover:bg-frost rounded"
            >
              <CloseIcon className="h-3.5 w-3.5 text-text-tertiary" />
            </button>
          )}
        </div>

        {/* Filters Toggle Button */}
        <button
          type="button"
          onClick={() => setIsExpanded(!isExpanded)}
          className={cn(
            'flex items-center gap-1.5 px-3 py-2 text-[13px] font-medium rounded-md',
            'transition-colors border',
            isExpanded || activeFilterCount > 0
              ? 'bg-glacier-blue/10 text-glacier-blue border-glacier-blue/30'
              : 'bg-frost/50 text-text-secondary border-transparent hover:bg-frost'
          )}
        >
          <FilterIcon className="h-4 w-4" />
          <span>Filters</span>
          {activeFilterCount > 0 && (
            <span className="ml-0.5 px-1.5 py-0.5 text-[11px] font-semibold bg-glacier-blue text-white rounded-full">
              {activeFilterCount}
            </span>
          )}
        </button>

        {/* Jump to Date */}
        <DateJumpPicker onDateSelect={onJumpToDate} />
      </div>

      {/* Expanded Filters */}
      {isExpanded && (
        <div className="mt-3 p-3 bg-frost/30 rounded-md border border-frost">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {/* Visit Type Filter */}
            <div>
              <label className="block text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-1">
                Visit Type
              </label>
              <select
                value={filters.visitType ?? ''}
                onChange={(e) => handleVisitTypeChange(e.target.value)}
                disabled={isLoading}
                className={cn(
                  'w-full px-2.5 py-1.5 text-[13px] rounded border border-frost bg-white',
                  'focus:outline-none focus:ring-1 focus:ring-glacier-blue focus:border-glacier-blue',
                  isLoading && 'opacity-60'
                )}
              >
                {visitTypeOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Provider Filter */}
            <div>
              <label className="block text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-1">
                Provider
              </label>
              <select
                value={filters.providerId ?? ''}
                onChange={(e) => handleProviderChange(e.target.value)}
                disabled={isLoading}
                className={cn(
                  'w-full px-2.5 py-1.5 text-[13px] rounded border border-frost bg-white',
                  'focus:outline-none focus:ring-1 focus:ring-glacier-blue focus:border-glacier-blue',
                  isLoading && 'opacity-60'
                )}
              >
                <option value="">All Providers</option>
                {providers.map((provider) => (
                  <option key={provider.id} value={provider.id}>
                    {provider.name}
                    {provider.specialty && ` (${provider.specialty})`}
                  </option>
                ))}
              </select>
            </div>

            {/* Diagnosis/Problem Filter */}
            <div>
              <label className="block text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-1">
                Problem/ICD-10
              </label>
              <input
                type="text"
                placeholder="e.g., E11 or diabetes"
                value={filters.diagnosisCode ?? ''}
                onChange={(e) => handleDiagnosisChange(e.target.value)}
                disabled={isLoading}
                className={cn(
                  'w-full px-2.5 py-1.5 text-[13px] rounded border border-frost',
                  'focus:outline-none focus:ring-1 focus:ring-glacier-blue focus:border-glacier-blue',
                  'placeholder:text-text-tertiary',
                  isLoading && 'opacity-60'
                )}
              />
            </div>

            {/* Date Range */}
            <div>
              <label className="block text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-1">
                Date Range
              </label>
              <div className="flex items-center gap-1">
                <input
                  type="date"
                  value={filters.dateFrom ?? ''}
                  onChange={(e) => handleDateFromChange(e.target.value)}
                  max={filters.dateTo || new Date().toISOString().split('T')[0]}
                  disabled={isLoading}
                  className={cn(
                    'flex-1 px-1.5 py-1.5 text-[13px] rounded border border-frost',
                    'focus:outline-none focus:ring-1 focus:ring-glacier-blue focus:border-glacier-blue',
                    isLoading && 'opacity-60'
                  )}
                />
                <span className="text-text-tertiary text-[13px]">-</span>
                <input
                  type="date"
                  value={filters.dateTo ?? ''}
                  onChange={(e) => handleDateToChange(e.target.value)}
                  min={filters.dateFrom}
                  max={new Date().toISOString().split('T')[0]}
                  disabled={isLoading}
                  className={cn(
                    'flex-1 px-1.5 py-1.5 text-[13px] rounded border border-frost',
                    'focus:outline-none focus:ring-1 focus:ring-glacier-blue focus:border-glacier-blue',
                    isLoading && 'opacity-60'
                  )}
                />
              </div>
            </div>
          </div>

          {/* Clear All Button */}
          {hasAnyFilter && (
            <div className="mt-3 pt-3 border-t border-frost flex justify-end">
              <button
                type="button"
                onClick={handleClearAll}
                disabled={isLoading}
                className={cn(
                  'flex items-center gap-1.5 px-2.5 py-1.5 text-[13px] font-medium rounded',
                  'text-text-secondary hover:text-critical hover:bg-critical/10',
                  'transition-colors',
                  isLoading && 'opacity-60'
                )}
              >
                <CloseIcon className="h-3.5 w-3.5" />
                Clear All Filters
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function SearchIcon({ className }: { className?: string }) {
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
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  );
}

function FilterIcon({ className }: { className?: string }) {
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
      <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
    </svg>
  );
}

function CloseIcon({ className }: { className?: string }) {
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
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}
