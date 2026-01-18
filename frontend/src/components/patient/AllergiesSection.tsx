import { useState } from 'react';
import type { Allergy, AllergySeverity, AllergyType, AllergySource, AllergyVerificationStatus, AllergyClinicalStatus, AllergyReviewStatus } from '../../types';
import { Card, CardContent } from '../ui';
import { cn } from '../../utils/cn';

interface AllergiesSectionProps {
  /**
   * Patient's allergies array.
   * - undefined = allergy history has not been reviewed
   * - empty array = NKDA (No Known Drug Allergies)
   * - populated array = documented allergies
   */
  allergies: Allergy[] | undefined;
  /**
   * Allergy review status - when the allergy list was last reviewed.
   */
  allergyReviewStatus?: AllergyReviewStatus;
  /**
   * Callback when user wants to mark allergies as reviewed.
   */
  onMarkReviewed?: () => void;
}

const severityOrder: Record<AllergySeverity, number> = {
  severe: 0,
  moderate: 1,
  mild: 2,
  unknown: 3,
};

const severityConfig: Record<AllergySeverity, { label: string; badgeClass: string; dotClass: string }> = {
  severe: {
    label: 'Critical/Severe',
    badgeClass: 'bg-critical text-white',
    dotClass: 'bg-critical',
  },
  moderate: {
    label: 'Moderate',
    badgeClass: 'bg-warning text-white',
    dotClass: 'bg-warning',
  },
  mild: {
    label: 'Mild',
    badgeClass: 'bg-frost text-text-primary',
    dotClass: 'bg-text-tertiary',
  },
  unknown: {
    label: 'Unknown',
    badgeClass: 'bg-frost text-text-secondary',
    dotClass: 'bg-text-tertiary',
  },
};

const typeConfig: Record<AllergyType, { label: string; icon: React.ReactNode }> = {
  drug: {
    label: 'Drug',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M10.5 20.5L3.5 13.5C2.1 12.1 2.1 9.9 3.5 8.5L8.5 3.5C9.9 2.1 12.1 2.1 13.5 3.5L20.5 10.5C21.9 11.9 21.9 14.1 20.5 15.5L15.5 20.5C14.1 21.9 11.9 21.9 10.5 20.5Z" />
        <path d="M8.5 8.5L15.5 15.5" />
      </svg>
    ),
  },
  food: {
    label: 'Food',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M18 8h1a4 4 0 0 1 0 8h-1" />
        <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z" />
        <line x1="6" y1="1" x2="6" y2="4" />
        <line x1="10" y1="1" x2="10" y2="4" />
        <line x1="14" y1="1" x2="14" y2="4" />
      </svg>
    ),
  },
  environmental: {
    label: 'Environmental',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      </svg>
    ),
  },
  other: {
    label: 'Other',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
        <line x1="12" y1="17" x2="12.01" y2="17" />
      </svg>
    ),
  },
};

const sourceConfig: Record<AllergySource, string> = {
  patient_reported: 'Patient reported',
  chart_documented: 'Chart documented',
  verified_by_provider: 'Verified by provider',
};

const verificationStatusConfig: Record<AllergyVerificationStatus, { label: string; className: string }> = {
  unconfirmed: { label: 'Unconfirmed', className: 'text-warning' },
  confirmed: { label: 'Confirmed', className: 'text-success' },
  refuted: { label: 'Refuted', className: 'text-text-tertiary' },
  'entered-in-error': { label: 'Entered in Error', className: 'text-critical' },
};

const clinicalStatusConfig: Record<AllergyClinicalStatus, { label: string; badgeClass: string }> = {
  active: { label: 'Active', badgeClass: 'bg-success/20 text-success' },
  inactive: { label: 'Inactive', badgeClass: 'bg-frost text-text-tertiary' },
  resolved: { label: 'Resolved', badgeClass: 'bg-frost text-text-tertiary' },
};

type FilterType = 'all' | AllergyType;

function sortAllergiesBySeverity(allergies: Allergy[]): Allergy[] {
  return [...allergies].sort((a, b) => {
    // First sort by severity
    const severityDiff = severityOrder[a.severity] - severityOrder[b.severity];
    if (severityDiff !== 0) return severityDiff;
    // Within same severity, prioritize anaphylaxis
    if (a.isAnaphylaxis && !b.isAnaphylaxis) return -1;
    if (!a.isAnaphylaxis && b.isAnaphylaxis) return 1;
    return 0;
  });
}

export function AllergiesSection({ allergies, allergyReviewStatus, onMarkReviewed }: AllergiesSectionProps) {
  const [expandedAllergyIds, setExpandedAllergyIds] = useState<Set<string>>(new Set());
  const [filterType, setFilterType] = useState<FilterType>('all');
  const [showInactive, setShowInactive] = useState(false);

  const toggleExpanded = (id: string) => {
    setExpandedAllergyIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  // Helper to format the review date
  const formatReviewDate = (isoDate: string): string => {
    const date = new Date(isoDate);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  // Allergy history has not been reviewed
  if (allergies === undefined) {
    return (
      <Card className="mb-normal border-2 border-dashed border-frost">
        <CardContent>
          <div className="flex items-center gap-tight">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 text-text-tertiary"
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
            <span className="text-[15px] text-text-tertiary">
              No allergies documented
            </span>
          </div>
        </CardContent>
      </Card>
    );
  }

  // NKDA - No Known Drug Allergies
  if (allergies.length === 0) {
    return (
      <Card className="mb-normal bg-success/5 border border-success/20">
        <CardContent>
          <div className="flex items-center gap-tight">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 text-success"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            <span className="text-[15px] font-semibold text-success">
              NKDA
            </span>
            <span className="text-[15px] text-text-secondary">
              — No Known Drug Allergies
            </span>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Has documented allergies
  // Separate active and inactive allergies
  const activeAllergies = allergies.filter((a) => !a.clinicalStatus || a.clinicalStatus === 'active');
  const inactiveAllergies = allergies.filter((a) => a.clinicalStatus === 'inactive' || a.clinicalStatus === 'resolved');

  // Apply active/inactive filter first
  const visibleAllergies = showInactive ? allergies : activeAllergies;
  const sortedAllergies = sortAllergiesBySeverity(visibleAllergies);
  const hasSevereAllergy = activeAllergies.some((a) => a.severity === 'severe');
  const hasAnaphylaxis = activeAllergies.some((a) => a.isAnaphylaxis);

  // Apply type filter
  const filteredAllergies = filterType === 'all'
    ? sortedAllergies
    : sortedAllergies.filter((a) => a.type === filterType);

  const drugAllergies = filteredAllergies.filter((a) => a.type === 'drug');
  const otherAllergies = filteredAllergies.filter((a) => a.type !== 'drug');

  // Get counts for filter badges (based on currently visible allergies)
  const typeCounts = {
    all: visibleAllergies.length,
    drug: visibleAllergies.filter((a) => a.type === 'drug').length,
    food: visibleAllergies.filter((a) => a.type === 'food').length,
    environmental: visibleAllergies.filter((a) => a.type === 'environmental').length,
    other: visibleAllergies.filter((a) => a.type === 'other').length,
  };

  return (
    <Card
      className={cn(
        'mb-normal',
        hasSevereAllergy || hasAnaphylaxis
          ? 'bg-critical/5 border-2 border-critical/30'
          : 'bg-warning/5 border border-warning/20'
      )}
    >
      <CardContent>
        {/* Stale review warning banner */}
        {allergyReviewStatus?.isStale && (
          <div className="mb-normal p-3 bg-warning/10 border border-warning/30 rounded-md">
            <div className="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 text-warning flex-shrink-0"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
              <div className="flex-1">
                <span className="text-[15px] font-medium text-warning">
                  Allergy list review overdue
                </span>
                <span className="text-[13px] text-text-secondary ml-2">
                  Last reviewed {formatReviewDate(allergyReviewStatus.reviewedAt)}
                  {allergyReviewStatus.reviewedBy && ` by ${allergyReviewStatus.reviewedBy}`}
                </span>
              </div>
              {onMarkReviewed && (
                <button
                  type="button"
                  onClick={onMarkReviewed}
                  className="px-3 py-1.5 text-[13px] font-medium text-white bg-warning hover:bg-warning/90 rounded transition-colors"
                >
                  Mark Reviewed
                </button>
              )}
            </div>
          </div>
        )}

        {/* Header */}
        <div className="flex items-center gap-tight mb-normal">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className={cn('h-5 w-5', hasSevereAllergy || hasAnaphylaxis ? 'text-critical' : 'text-warning')}
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
            Allergies ({activeAllergies.length})
          </h3>
          {/* Anaphylaxis warning banner */}
          {hasAnaphylaxis && (
            <span className="ml-auto flex items-center gap-1 px-2 py-1 text-[11px] font-semibold text-critical bg-critical/10 rounded">
              <span aria-hidden="true">⚠️</span>
              <span>ANAPHYLAXIS RISK</span>
            </span>
          )}
        </div>

        {/* Review status display (when not stale) */}
        {allergyReviewStatus && !allergyReviewStatus.isStale && (
          <div className="mb-normal text-[13px] text-text-tertiary flex items-center gap-1">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4 text-success"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            <span>
              Reviewed {formatReviewDate(allergyReviewStatus.reviewedAt)}
              {allergyReviewStatus.reviewedBy && ` by ${allergyReviewStatus.reviewedBy}`}
            </span>
          </div>
        )}

        {/* Filter buttons and inactive toggle */}
        <div className="flex items-center justify-between gap-normal mb-normal flex-wrap">
          <div className="flex flex-wrap gap-1">
            <FilterButton
              label="All"
              count={typeCounts.all}
              isActive={filterType === 'all'}
              onClick={() => setFilterType('all')}
            />
            {typeCounts.drug > 0 && (
              <FilterButton
                label="Drug"
                count={typeCounts.drug}
                isActive={filterType === 'drug'}
                onClick={() => setFilterType('drug')}
              />
            )}
            {typeCounts.food > 0 && (
              <FilterButton
                label="Food"
                count={typeCounts.food}
                isActive={filterType === 'food'}
                onClick={() => setFilterType('food')}
              />
            )}
            {typeCounts.environmental > 0 && (
              <FilterButton
                label="Environmental"
                count={typeCounts.environmental}
                isActive={filterType === 'environmental'}
                onClick={() => setFilterType('environmental')}
              />
            )}
            {typeCounts.other > 0 && (
              <FilterButton
                label="Other"
                count={typeCounts.other}
                isActive={filterType === 'other'}
                onClick={() => setFilterType('other')}
              />
            )}
          </div>

          {/* Show inactive toggle */}
          {inactiveAllergies.length > 0 && (
            <button
              type="button"
              onClick={() => setShowInactive(!showInactive)}
              className={cn(
                'flex items-center gap-1 px-2 py-1 text-[11px] font-medium rounded transition-colors',
                showInactive
                  ? 'bg-deep-ice text-white'
                  : 'bg-frost/50 text-text-secondary hover:bg-frost'
              )}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-3.5 w-3.5"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M3 3l18 18" />
                <path d="M10.5 10.677a2 2 0 0 0 2.823 2.823" />
                <path d="M7.362 7.561C5.68 8.74 4.279 10.42 3 12c1.889 2.991 5.282 6 9 6 1.55 0 3.043-.523 4.395-1.35M12 6c3.718 0 7.111 3.009 9 6-.947 1.497-2.153 2.864-3.5 3.965" />
              </svg>
              {showInactive ? 'Hide' : 'Show'} Historical ({inactiveAllergies.length})
            </button>
          )}
        </div>

        {/* Drug Allergies Section */}
        {drugAllergies.length > 0 && (
          <div className="mb-normal">
            <div className="flex items-center gap-1 mb-tight">
              <span className="text-critical">{typeConfig.drug.icon}</span>
              <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                Drug Allergies
              </span>
            </div>
            <div className="flex flex-wrap gap-tight">
              {drugAllergies.map((allergy) => (
                <AllergyCard
                  key={allergy.id}
                  allergy={allergy}
                  isDrug
                  isExpanded={expandedAllergyIds.has(allergy.id)}
                  onToggleExpand={() => toggleExpanded(allergy.id)}
                />
              ))}
            </div>
          </div>
        )}

        {/* Other Allergies Section (Food & Environmental) */}
        {otherAllergies.length > 0 && (
          <div>
            {drugAllergies.length > 0 && filterType === 'all' && (
              <div className="flex items-center gap-1 mb-tight">
                <span className="text-text-tertiary">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10" />
                  </svg>
                </span>
                <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                  Other Allergies
                </span>
              </div>
            )}
            <div className="flex flex-wrap gap-tight">
              {otherAllergies.map((allergy) => (
                <AllergyCard
                  key={allergy.id}
                  allergy={allergy}
                  isDrug={false}
                  isExpanded={expandedAllergyIds.has(allergy.id)}
                  onToggleExpand={() => toggleExpanded(allergy.id)}
                />
              ))}
            </div>
          </div>
        )}

        {/* No results after filtering */}
        {filteredAllergies.length === 0 && (
          <div className="text-center py-normal text-text-tertiary text-[15px]">
            No {filterType} allergies documented
          </div>
        )}
      </CardContent>
    </Card>
  );
}

interface FilterButtonProps {
  label: string;
  count: number;
  isActive: boolean;
  onClick: () => void;
}

function FilterButton({ label, count, isActive, onClick }: FilterButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'px-2 py-1 text-[11px] font-medium rounded transition-colors',
        isActive
          ? 'bg-deep-ice text-white'
          : 'bg-frost/50 text-text-secondary hover:bg-frost'
      )}
    >
      {label} ({count})
    </button>
  );
}

interface AllergyCardProps {
  allergy: Allergy;
  isDrug: boolean;
  isExpanded: boolean;
  onToggleExpand: () => void;
}

function AllergyCard({ allergy, isDrug, isExpanded, onToggleExpand }: AllergyCardProps) {
  const [showTooltip, setShowTooltip] = useState(false);
  const severity = severityConfig[allergy.severity] || severityConfig.unknown;
  const type = typeConfig[allergy.type] || typeConfig.other;
  const isAnaphylaxis = allergy.isAnaphylaxis;
  const hasMultipleReactions = (allergy.reactions?.length ?? 0) > 1;
  const verificationStatus = allergy.verificationStatus
    ? verificationStatusConfig[allergy.verificationStatus]
    : null;
  const isInactive = allergy.clinicalStatus === 'inactive' || allergy.clinicalStatus === 'resolved';
  const clinicalStatus = allergy.clinicalStatus && allergy.clinicalStatus !== 'active'
    ? clinicalStatusConfig[allergy.clinicalStatus]
    : null;

  return (
    <div
      className={cn(
        'rounded-md px-3 py-2 shadow-sm cursor-pointer transition-all relative',
        isDrug ? 'bg-white border border-critical/10' : 'bg-white/80',
        isAnaphylaxis && !isInactive && 'ring-2 ring-critical/30',
        isExpanded && 'ring-2 ring-deep-ice/50',
        isInactive && 'opacity-60 border-dashed'
      )}
      onClick={onToggleExpand}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
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
      {/* Tooltip on hover */}
      {showTooltip && !isExpanded && (verificationStatus || allergy.lastUpdated) && (
        <div className="absolute bottom-full left-0 mb-1 z-10 bg-text-primary text-white text-[11px] px-2 py-1 rounded shadow-lg whitespace-nowrap">
          {verificationStatus && (
            <span className={verificationStatus.className}>
              {verificationStatus.label}
            </span>
          )}
          {verificationStatus && allergy.lastUpdated && <span className="mx-1">·</span>}
          {allergy.lastUpdated && (
            <span>Updated: {allergy.lastUpdated}</span>
          )}
        </div>
      )}

      {/* Top row: severity dot, name, anaphylaxis indicator, type badge, severity badge, expand icon */}
      <div className="flex items-center gap-2 flex-wrap">
        {/* Severity indicator dot */}
        <span className={cn('w-2 h-2 rounded-full flex-shrink-0', severity.dotClass)} />

        {/* Allergen name */}
        <span className="text-[15px] font-medium text-text-primary">
          {allergy.allergen}
        </span>

        {/* Anaphylaxis indicator */}
        {isAnaphylaxis && (
          <span
            className="flex items-center gap-1 px-1.5 py-0.5 text-[11px] font-semibold text-critical bg-critical/10 rounded"
            title="Anaphylaxis risk"
          >
            <span aria-hidden="true">⚠️</span>
            <span>Anaphylaxis</span>
          </span>
        )}

        {/* Type badge */}
        <span className="flex items-center gap-1 px-1.5 py-0.5 text-[11px] text-text-tertiary bg-frost/50 rounded">
          {type.icon}
          <span>{type.label}</span>
        </span>

        {/* Severity badge */}
        <span
          className={cn(
            'px-2 py-0.5 text-[11px] font-medium uppercase tracking-wide rounded',
            severity.badgeClass
          )}
        >
          {severity.label}
        </span>

        {/* Clinical status badge for inactive/resolved */}
        {clinicalStatus && (
          <span
            className={cn(
              'px-2 py-0.5 text-[11px] font-medium uppercase tracking-wide rounded',
              clinicalStatus.badgeClass
            )}
          >
            {clinicalStatus.label}
          </span>
        )}

        {/* Expand/collapse indicator for multiple reactions */}
        {hasMultipleReactions && (
          <span className="ml-auto text-text-tertiary">
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
          </span>
        )}
      </div>

      {/* Details row: reaction, documented date, source */}
      <div className="mt-1 ml-4 flex items-center gap-2 flex-wrap text-[13px] text-text-secondary">
        {/* Reaction */}
        {allergy.reaction && (
          <span>Reaction: {allergy.reaction}</span>
        )}

        {/* Documented date */}
        {allergy.documented && (
          <>
            {allergy.reaction && <span className="text-text-tertiary">·</span>}
            <span>Documented: {allergy.documented}</span>
          </>
        )}

        {/* Source */}
        {allergy.source && (
          <>
            <span className="text-text-tertiary">·</span>
            <span>{sourceConfig[allergy.source]}</span>
          </>
        )}
      </div>

      {/* Expanded details */}
      {isExpanded && (
        <div className="mt-normal pt-normal border-t border-frost">
          {/* Provider and verification info */}
          <div className="flex flex-wrap gap-2 text-[13px] text-text-secondary mb-tight">
            {allergy.documentingProvider && (
              <span>
                <span className="text-text-tertiary">Documented by:</span> {allergy.documentingProvider}
              </span>
            )}
            {verificationStatus && (
              <span>
                <span className="text-text-tertiary">Status:</span>{' '}
                <span className={verificationStatus.className}>{verificationStatus.label}</span>
              </span>
            )}
            {allergy.lastUpdated && (
              <span>
                <span className="text-text-tertiary">Last updated:</span> {allergy.lastUpdated}
              </span>
            )}
          </div>

          {/* Notes */}
          {allergy.notes && (
            <div className="text-[13px] text-text-secondary mb-tight">
              <span className="text-text-tertiary">Notes:</span> {allergy.notes}
            </div>
          )}

          {/* Multiple reactions list */}
          {hasMultipleReactions && (
            <div className="mt-tight">
              <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                All Reactions ({allergy.reactions?.length})
              </span>
              <div className="mt-1 space-y-1">
                {allergy.reactions?.map((reaction, index) => {
                  const reactionSeverity = severityConfig[reaction.severity] || severityConfig.unknown;
                  return (
                    <div
                      key={index}
                      className="flex items-center gap-2 text-[13px] text-text-secondary"
                    >
                      <span className={cn('w-1.5 h-1.5 rounded-full flex-shrink-0', reactionSeverity.dotClass)} />
                      <span>{reaction.manifestation}</span>
                      <span className={cn('text-[11px] px-1 py-0.5 rounded', reactionSeverity.badgeClass)}>
                        {reactionSeverity.label}
                      </span>
                      {reaction.description && (
                        <span className="text-text-tertiary">— {reaction.description}</span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
