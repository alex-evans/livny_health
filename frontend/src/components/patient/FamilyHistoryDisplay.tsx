import { useState } from 'react';
import type { FamilyHistory, FamilyMember, RelativeDegree } from '../../types';
import { RELATIVE_TYPE_LABELS } from '../../types';
import { cn } from '../../utils/cn';

interface FamilyHistoryDisplayProps {
  familyHistory: FamilyHistory | null;
}

function FamilyMemberCard({
  member,
  isExpanded,
  onToggle,
}: {
  member: FamilyMember;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const hasConditions = member.conditions.length > 0;

  return (
    <div
      className={cn(
        'bg-white rounded-lg shadow-card hover:shadow-card-hover transition-shadow',
        hasConditions ? 'cursor-pointer' : ''
      )}
      onClick={hasConditions ? onToggle : undefined}
    >
      <div className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className={cn(
                'w-8 h-8 rounded-full flex items-center justify-center text-[13px] font-medium',
                member.isLiving
                  ? 'bg-arctic text-glacier-blue'
                  : 'bg-frost text-text-secondary'
              )}
            >
              {RELATIVE_TYPE_LABELS[member.relativeType]?.charAt(0) || '?'}
            </div>
            <div>
              <p className="text-[15px] font-medium text-text-primary">
                {RELATIVE_TYPE_LABELS[member.relativeType] || member.relativeType}
              </p>
              <p className="text-[13px] text-text-tertiary">
                {member.isLiving ? 'Living' : `Deceased (age ${member.ageAtDeath})`}
              </p>
            </div>
          </div>
          {hasConditions && (
            <div className="flex items-center gap-2">
              <span className="text-[13px] text-text-secondary">
                {member.conditions.length} condition
                {member.conditions.length !== 1 ? 's' : ''}
              </span>
              <svg
                className={cn(
                  'w-4 h-4 text-text-tertiary transition-transform',
                  isExpanded ? 'rotate-180' : ''
                )}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </div>
          )}
        </div>

        {!member.isLiving && member.causeOfDeath && (
          <p className="text-[13px] text-text-secondary mt-2 ml-11">
            Cause of death: {member.causeOfDeath}
          </p>
        )}
      </div>

      {/* Expanded Conditions */}
      {isExpanded && hasConditions && (
        <div className="border-t border-frost px-4 py-3 bg-snow/50">
          <p className="text-[11px] font-medium text-text-tertiary uppercase tracking-wide mb-2">
            Conditions
          </p>
          <ul className="space-y-2">
            {member.conditions.map((condition, idx) => (
              <li key={idx} className="text-[13px]">
                <div className="flex items-start justify-between">
                  <span className="text-text-primary font-medium">
                    {condition.conditionName}
                  </span>
                  {condition.icd10Code && (
                    <span className="text-text-tertiary text-[12px]">
                      {condition.icd10Code}
                    </span>
                  )}
                </div>
                {condition.ageAtOnset && (
                  <p className="text-text-secondary text-[12px] mt-0.5">
                    Age at onset: {condition.ageAtOnset}
                  </p>
                )}
                {condition.notes && (
                  <p className="text-text-tertiary text-[12px] mt-0.5 italic">
                    {condition.notes}
                  </p>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function DegreeSection({
  degree,
  label,
  members,
  expandedIds,
  onToggle,
}: {
  degree: RelativeDegree;
  label: string;
  members: FamilyMember[];
  expandedIds: Set<string>;
  onToggle: (id: string) => void;
}) {
  const degreeMembers = members.filter((m) => m.degree === degree);

  if (degreeMembers.length === 0) return null;

  return (
    <div className="mb-6">
      <h4 className="text-[13px] font-medium text-text-tertiary uppercase tracking-wide mb-3">
        {label}
      </h4>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {degreeMembers.map((member) => (
          <FamilyMemberCard
            key={member.id}
            member={member}
            isExpanded={expandedIds.has(member.id)}
            onToggle={() => onToggle(member.id)}
          />
        ))}
      </div>
    </div>
  );
}

export function FamilyHistoryDisplay({
  familyHistory,
}: FamilyHistoryDisplayProps) {
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  const handleToggle = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  if (!familyHistory) {
    return (
      <div className="text-text-tertiary text-[15px] py-8 text-center">
        Family history not documented
      </div>
    );
  }

  const hasMembers = familyHistory.familyMembers.length > 0;
  const hasSignificantConditions = familyHistory.significantConditions.length > 0;
  const hasSyndromes = familyHistory.hereditarySyndromes.length > 0;
  const isAdopted = familyHistory.adoptionStatus !== 'not_adopted';

  return (
    <div>
      {/* Adoption Status Banner */}
      {isAdopted && (
        <div className="bg-arctic border-l-4 border-glacier-blue p-4 rounded-r-lg mb-6">
          <p className="text-[15px] text-deep-ice font-medium">
            {familyHistory.adoptionStatus === 'adopted_known_history'
              ? 'Patient is adopted - biological family history is known'
              : 'Patient is adopted - biological family history unknown'}
          </p>
        </div>
      )}

      {/* Hereditary Syndromes */}
      {hasSyndromes && (
        <div className="bg-status-warning/10 border-l-4 border-status-warning p-4 rounded-r-lg mb-6">
          <p className="text-[13px] font-medium text-text-tertiary uppercase tracking-wide mb-2">
            Hereditary Syndromes
          </p>
          <ul className="space-y-1">
            {familyHistory.hereditarySyndromes.map((syndrome, idx) => (
              <li key={idx} className="text-[15px] text-text-primary font-medium">
                {syndrome}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Significant Conditions Summary */}
      {hasSignificantConditions && (
        <div className="bg-white rounded-lg shadow-card p-4 mb-6">
          <h4 className="text-[13px] font-medium text-text-tertiary uppercase tracking-wide mb-3">
            Significant Family Conditions
          </h4>
          <div className="space-y-3">
            {familyHistory.significantConditions.map((condition, idx) => (
              <div key={idx} className="flex items-start justify-between">
                <div>
                  <p className="text-[15px] text-text-primary font-medium">
                    {condition.conditionName}
                  </p>
                  <p className="text-[13px] text-text-secondary">
                    Affected: {condition.affectedRelatives.join(', ')}
                  </p>
                  {condition.notes && (
                    <p className="text-[13px] text-text-tertiary italic mt-1">
                      {condition.notes}
                    </p>
                  )}
                </div>
                {condition.icd10Code && (
                  <span className="text-[12px] text-text-tertiary">
                    {condition.icd10Code}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Family Members by Degree */}
      {hasMembers && (
        <>
          <DegreeSection
            degree="first"
            label="First-Degree Relatives"
            members={familyHistory.familyMembers}
            expandedIds={expandedIds}
            onToggle={handleToggle}
          />
          <DegreeSection
            degree="second"
            label="Second-Degree Relatives"
            members={familyHistory.familyMembers}
            expandedIds={expandedIds}
            onToggle={handleToggle}
          />
          <DegreeSection
            degree="third"
            label="Third-Degree Relatives"
            members={familyHistory.familyMembers}
            expandedIds={expandedIds}
            onToggle={handleToggle}
          />
        </>
      )}

      {!hasMembers && !hasSignificantConditions && !hasSyndromes && !isAdopted && (
        <div className="text-text-tertiary text-[15px] py-8 text-center">
          No family members documented
        </div>
      )}
    </div>
  );
}
