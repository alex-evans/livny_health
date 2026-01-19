import type { LabSortOption, LabFilterPanel, LabFilterStatus } from '../../types';
import { cn } from '../../utils/cn';

interface LabFiltersProps {
  sortBy: LabSortOption;
  onSortChange: (sort: LabSortOption) => void;
  filterPanel: LabFilterPanel;
  onFilterPanelChange: (panel: LabFilterPanel) => void;
  filterStatus: LabFilterStatus;
  onFilterStatusChange: (status: LabFilterStatus) => void;
  className?: string;
}

const sortOptions: { value: LabSortOption; label: string }[] = [
  { value: 'date', label: 'Date' },
  { value: 'name', label: 'Name' },
  { value: 'abnormal', label: 'Abnormal First' },
];

const panelOptions: { value: LabFilterPanel; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'BMP', label: 'BMP' },
  { value: 'Lipid', label: 'Lipid' },
  { value: 'CBC', label: 'CBC' },
  { value: 'ungrouped', label: 'Individual' },
];

const statusOptions: { value: LabFilterStatus; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'abnormal', label: 'Abnormal' },
  { value: 'critical', label: 'Critical' },
];

export function LabFilters({
  sortBy,
  onSortChange,
  filterPanel,
  onFilterPanelChange,
  filterStatus,
  onFilterStatusChange,
  className,
}: LabFiltersProps) {
  return (
    <div className={cn('flex flex-wrap items-center gap-3', className)}>
      {/* Sort dropdown */}
      <div className="flex items-center gap-1.5">
        <label className="text-[11px] text-text-tertiary uppercase tracking-wide">
          Sort
        </label>
        <select
          value={sortBy}
          onChange={(e) => onSortChange(e.target.value as LabSortOption)}
          className={cn(
            'px-2 py-1 text-[13px] rounded border border-frost bg-white',
            'focus:outline-none focus:ring-1 focus:ring-glacier-blue focus:border-glacier-blue',
            'cursor-pointer'
          )}
        >
          {sortOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Panel filter */}
      <div className="flex items-center gap-1.5">
        <label className="text-[11px] text-text-tertiary uppercase tracking-wide">
          Panel
        </label>
        <select
          value={filterPanel}
          onChange={(e) => onFilterPanelChange(e.target.value as LabFilterPanel)}
          className={cn(
            'px-2 py-1 text-[13px] rounded border border-frost bg-white',
            'focus:outline-none focus:ring-1 focus:ring-glacier-blue focus:border-glacier-blue',
            'cursor-pointer'
          )}
        >
          {panelOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Status filter */}
      <div className="flex items-center gap-1.5">
        <label className="text-[11px] text-text-tertiary uppercase tracking-wide">
          Status
        </label>
        <select
          value={filterStatus}
          onChange={(e) => onFilterStatusChange(e.target.value as LabFilterStatus)}
          className={cn(
            'px-2 py-1 text-[13px] rounded border border-frost bg-white',
            'focus:outline-none focus:ring-1 focus:ring-glacier-blue focus:border-glacier-blue',
            'cursor-pointer',
            filterStatus === 'critical' && 'border-critical/30 bg-critical/5',
            filterStatus === 'abnormal' && 'border-warning/30 bg-warning/5'
          )}
        >
          {statusOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Clear filters button */}
      {(sortBy !== 'date' || filterPanel !== 'all' || filterStatus !== 'all') && (
        <button
          type="button"
          onClick={() => {
            onSortChange('date');
            onFilterPanelChange('all');
            onFilterStatusChange('all');
          }}
          className={cn(
            'px-2 py-1 text-[11px] text-text-tertiary',
            'hover:text-text-secondary transition-colors'
          )}
        >
          Clear filters
        </button>
      )}
    </div>
  );
}
