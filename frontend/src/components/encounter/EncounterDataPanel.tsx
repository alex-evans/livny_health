import { useState } from 'react';
import { cn } from '../../utils/cn';
import type { EncounterContext } from '../../types';

interface EncounterDataPanelProps {
  context: EncounterContext;
  className?: string;
}

interface CollapsibleSectionProps {
  title: string;
  count?: number;
  defaultExpanded?: boolean;
  children: React.ReactNode;
}

function CollapsibleSection({
  title,
  count,
  defaultExpanded = true,
  children,
}: CollapsibleSectionProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className="border-b border-frost last:border-b-0">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between py-normal px-comfortable hover:bg-frost/30 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="text-[15px] font-medium text-text-primary">
            {title}
          </span>
          {count !== undefined && (
            <span className="text-[12px] text-text-tertiary bg-frost px-2 py-0.5 rounded-full">
              {count}
            </span>
          )}
        </div>
        <ChevronIcon
          className={cn(
            'w-4 h-4 text-text-tertiary transition-transform',
            isExpanded ? 'rotate-180' : ''
          )}
        />
      </button>
      {isExpanded && (
        <div className="px-comfortable pb-normal">{children}</div>
      )}
    </div>
  );
}

function VitalsDisplay({ vitals }: { vitals: EncounterContext['vitals'] }) {
  if (vitals.length === 0) {
    return (
      <p className="text-[13px] text-text-tertiary">No recent vitals recorded</p>
    );
  }

  // Group vitals by type and show most recent
  const latestVitals = new Map<string, EncounterContext['vitals'][0]>();
  for (const vital of vitals) {
    if (!latestVitals.has(vital.vitalType)) {
      latestVitals.set(vital.vitalType, vital);
    }
  }

  return (
    <div className="grid grid-cols-2 gap-3">
      {Array.from(latestVitals.values()).map((vital) => (
        <div key={vital.id} className="bg-frost/30 rounded-lg p-3">
          <div className="text-[12px] text-text-tertiary mb-1">
            {vital.displayName || vital.vitalType}
          </div>
          <div
            className={cn(
              'text-[15px] font-medium',
              vital.status === 'normal'
                ? 'text-text-primary'
                : vital.status === 'critical'
                ? 'text-status-critical'
                : 'text-status-abnormal'
            )}
          >
            {vital.displayValue || `${vital.value} ${vital.unit}`}
          </div>
        </div>
      ))}
    </div>
  );
}

function MedicationsDisplay({
  medications,
}: {
  medications: EncounterContext['medications'];
}) {
  if (medications.length === 0) {
    return (
      <p className="text-[13px] text-text-tertiary">No active medications</p>
    );
  }

  return (
    <div className="space-y-2">
      {medications.slice(0, 5).map((med) => (
        <div key={med.id} className="flex justify-between items-start">
          <div>
            <div className="text-[14px] text-text-primary">{med.name}</div>
            <div className="text-[12px] text-text-secondary">
              {med.dosage} - {med.frequency}
            </div>
          </div>
        </div>
      ))}
      {medications.length > 5 && (
        <p className="text-[12px] text-glacier-blue">
          +{medications.length - 5} more medications
        </p>
      )}
    </div>
  );
}

function AllergiesDisplay({
  allergies,
}: {
  allergies: EncounterContext['allergies'];
}) {
  if (allergies.length === 0) {
    return (
      <div className="bg-status-normal/10 text-status-normal text-[13px] px-3 py-2 rounded">
        No known allergies
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {allergies.map((allergy) => (
        <div
          key={allergy.id}
          className={cn(
            'px-3 py-2 rounded',
            allergy.severity === 'severe' || allergy.isAnaphylaxis
              ? 'bg-status-critical/10 text-status-critical'
              : 'bg-status-abnormal/10 text-status-abnormal'
          )}
        >
          <div className="text-[14px] font-medium">{allergy.allergen}</div>
          <div className="text-[12px]">
            {allergy.reaction}
            {allergy.isAnaphylaxis && ' (Anaphylaxis)'}
          </div>
        </div>
      ))}
    </div>
  );
}

function ProblemsDisplay({
  problems,
}: {
  problems: EncounterContext['problems'];
}) {
  if (problems.length === 0) {
    return (
      <p className="text-[13px] text-text-tertiary">No active problems</p>
    );
  }

  const activeProblems = problems.filter((p) => p.status === 'active');

  return (
    <div className="space-y-2">
      {activeProblems.slice(0, 5).map((problem, idx) => (
        <div key={idx} className="flex items-start gap-2">
          {problem.isCritical && (
            <span className="mt-1 w-2 h-2 rounded-full bg-status-critical flex-shrink-0" />
          )}
          <div>
            <div className="text-[14px] text-text-primary">{problem.name}</div>
            <div className="text-[12px] text-text-tertiary">
              {problem.icd10Code}
            </div>
          </div>
        </div>
      ))}
      {activeProblems.length > 5 && (
        <p className="text-[12px] text-glacier-blue">
          +{activeProblems.length - 5} more problems
        </p>
      )}
    </div>
  );
}

function RecentLabsDisplay({
  labs,
}: {
  labs: EncounterContext['recentLabs'];
}) {
  if (labs.length === 0) {
    return <p className="text-[13px] text-text-tertiary">No recent labs</p>;
  }

  return (
    <div className="space-y-2">
      {labs.slice(0, 5).map((lab) => (
        <div key={lab.id} className="flex justify-between items-center">
          <span className="text-[14px] text-text-primary">{lab.testName}</span>
          <span
            className={cn(
              'text-[14px]',
              lab.status === 'normal'
                ? 'text-text-secondary'
                : lab.status === 'critical'
                ? 'text-status-critical font-medium'
                : 'text-status-abnormal'
            )}
          >
            {lab.value} {lab.unit}
          </span>
        </div>
      ))}
    </div>
  );
}

function RecentVisitsDisplay({
  visits,
}: {
  visits: EncounterContext['recentVisits'];
}) {
  if (visits.length === 0) {
    return <p className="text-[13px] text-text-tertiary">No recent visits</p>;
  }

  return (
    <div className="space-y-2">
      {visits.slice(0, 3).map((visit) => (
        <div key={visit.id} className="border-l-2 border-frost pl-3">
          <div className="text-[14px] text-text-primary">
            {visit.chiefComplaint}
          </div>
          <div className="text-[12px] text-text-tertiary">
            {new Date(visit.date).toLocaleDateString()} - {visit.visitType}
          </div>
        </div>
      ))}
    </div>
  );
}

export function EncounterDataPanel({
  context,
  className,
}: EncounterDataPanelProps) {
  return (
    <div className={cn('bg-white overflow-y-auto', className)}>
      <CollapsibleSection title="Vitals" count={context.vitals.length}>
        <VitalsDisplay vitals={context.vitals} />
      </CollapsibleSection>

      <CollapsibleSection title="Medications" count={context.medications.length}>
        <MedicationsDisplay medications={context.medications} />
      </CollapsibleSection>

      <CollapsibleSection title="Allergies" count={context.allergies.length}>
        <AllergiesDisplay allergies={context.allergies} />
      </CollapsibleSection>

      <CollapsibleSection title="Problems" count={context.problems.length}>
        <ProblemsDisplay problems={context.problems} />
      </CollapsibleSection>

      <CollapsibleSection
        title="Recent Labs"
        count={context.recentLabs.length}
        defaultExpanded={false}
      >
        <RecentLabsDisplay labs={context.recentLabs} />
      </CollapsibleSection>

      <CollapsibleSection
        title="Recent Visits"
        count={context.recentVisits.length}
        defaultExpanded={false}
      >
        <RecentVisitsDisplay visits={context.recentVisits} />
      </CollapsibleSection>
    </div>
  );
}

function ChevronIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
    </svg>
  );
}
