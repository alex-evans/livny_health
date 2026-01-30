import { cn } from '../../utils/cn';
import type { PatientContextData, ContextMode } from '../../types';
import { CollapsibleContextSection } from './CollapsibleContextSection';
import { QuickContextBar } from './QuickContextBar';
import { VitalsContextSection } from './VitalsContextSection';
import { MedicationsContextSection } from './MedicationsContextSection';
import { AllergiesContextSection } from './AllergiesContextSection';
import { ProblemsContextSection } from './ProblemsContextSection';
import { LabsContextSection } from './LabsContextSection';
import { VisitsContextSection } from './VisitsContextSection';

interface PatientContextContainerProps {
  context: PatientContextData | null;
  mode: ContextMode;
  isLoading: boolean;
  error: string | null;
  collapsedSections: Set<string>;
  onToggleSection: (sectionId: string) => void;
  onExpandNote?: () => void;
  onCollapseNote?: () => void;
  className?: string;
}

export function PatientContextContainer({
  context,
  mode,
  isLoading,
  error,
  collapsedSections,
  onToggleSection,
  onExpandNote,
  onCollapseNote,
  className,
}: PatientContextContainerProps) {
  // Show quick context bar in expanded note mode
  if (mode === 'expanded') {
    if (!context?.quickSummary) {
      return null;
    }
    return (
      <QuickContextBar
        summary={context.quickSummary}
        onClick={onCollapseNote}
        className={className}
      />
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div className={cn('bg-white rounded-lg shadow-card', className)}>
        <div className="px-comfortable py-normal">
          <div className="space-y-4 animate-pulse">
            <div className="h-4 bg-frost rounded w-1/3" />
            <div className="h-20 bg-frost rounded" />
            <div className="h-4 bg-frost rounded w-1/2" />
            <div className="h-16 bg-frost rounded" />
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={cn('bg-white rounded-lg shadow-card', className)}>
        <div className="px-comfortable py-normal text-center">
          <p className="text-[15px] text-status-critical">{error}</p>
        </div>
      </div>
    );
  }

  // No data state
  if (!context) {
    return null;
  }

  // Determine default expansion based on mode
  const defaultExpanded = mode === 'review';

  return (
    <div className={cn('bg-white rounded-lg shadow-card overflow-hidden', className)}>
      {/* Vitals Section - Always prominent */}
      <CollapsibleContextSection
        title="Vitals"
        count={Object.keys(context.vitals.mostRecent).length}
        isExpanded={!collapsedSections.has('vitals')}
        onToggle={() => onToggleSection('vitals')}
      >
        <VitalsContextSection
          vitals={context.vitals.mostRecent}
          recordedAt={context.vitals.recordedAt}
        />
      </CollapsibleContextSection>

      {/* Allergies Section - Important for safety */}
      <CollapsibleContextSection
        title="Allergies"
        count={context.allergies.length}
        isExpanded={!collapsedSections.has('allergies')}
        onToggle={() => onToggleSection('allergies')}
      >
        <AllergiesContextSection allergies={context.allergies} />
      </CollapsibleContextSection>

      {/* Medications Section */}
      <CollapsibleContextSection
        title="Medications"
        count={context.medications.totalActive}
        isExpanded={!collapsedSections.has('medications')}
        onToggle={() => onToggleSection('medications')}
      >
        <MedicationsContextSection
          medications={context.medications.active}
          recentlyDiscontinued={context.medications.recentlyDiscontinued}
        />
      </CollapsibleContextSection>

      {/* Problems Section */}
      <CollapsibleContextSection
        title="Problems"
        count={context.problems.totalActive}
        isExpanded={!collapsedSections.has('problems')}
        onToggle={() => onToggleSection('problems')}
      >
        <ProblemsContextSection problems={context.problems.active} />
      </CollapsibleContextSection>

      {/* Labs Section - Default collapsed in review mode */}
      <CollapsibleContextSection
        title="Recent Labs"
        count={context.recentLabs.results.length + context.recentLabs.pending.length}
        isExpanded={
          mode === 'documentation'
            ? !collapsedSections.has('labs')
            : !collapsedSections.has('labs') && defaultExpanded
        }
        onToggle={() => onToggleSection('labs')}
      >
        <LabsContextSection
          labs={context.recentLabs.results}
          pending={context.recentLabs.pending}
        />
      </CollapsibleContextSection>

      {/* Visits Section - Default collapsed */}
      <CollapsibleContextSection
        title="Recent Visits"
        count={context.recentVisits.length}
        isExpanded={!collapsedSections.has('visits') && mode === 'review'}
        onToggle={() => onToggleSection('visits')}
      >
        <VisitsContextSection visits={context.recentVisits} />
      </CollapsibleContextSection>

      {/* Expand note button in documentation mode */}
      {mode === 'documentation' && onExpandNote && (
        <div className="px-comfortable py-2 border-t border-frost">
          <button
            onClick={onExpandNote}
            className="text-[12px] text-glacier-blue hover:text-deep-ice transition-colors"
          >
            Collapse to context bar
          </button>
        </div>
      )}
    </div>
  );
}
