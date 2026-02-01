import { useEffect, useCallback } from 'react';
import { cn } from '../../utils/cn';
import { GuidanceSectionIndicator } from './GuidanceSectionIndicator';
import { SECTION_LETTERS } from '../../config/promptDefinitions';
import type { SOAPSectionKey, GuidanceCoverage } from '../../types/guidance';

interface GuidanceNavigatorProps {
  coverage: GuidanceCoverage;
  activeSection: SOAPSectionKey | null;
  onSectionClick: (section: SOAPSectionKey) => void;
  className?: string;
}

const SECTIONS: SOAPSectionKey[] = ['subjective', 'objective', 'assessment', 'plan'];

export function GuidanceNavigator({
  coverage,
  activeSection,
  onSectionClick,
  className,
}: GuidanceNavigatorProps) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!event.metaKey && !event.ctrlKey) return;

      const keyMap: Record<string, SOAPSectionKey> = {
        '1': 'subjective',
        '2': 'objective',
        '3': 'assessment',
        '4': 'plan',
      };

      const section = keyMap[event.key];
      if (section) {
        event.preventDefault();
        onSectionClick(activeSection === section ? section : section);
      }
    },
    [onSectionClick, activeSection]
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return (
    <div className={cn('flex items-center gap-1', className)}>
      {SECTIONS.map((section, index) => {
        const sectionCoverage = coverage[section];
        const isActive = activeSection === section;

        return (
          <div key={section} className="flex items-center">
            {index > 0 && (
              <span className="text-text-tertiary mx-1 select-none">·</span>
            )}
            <button
              onClick={() => onSectionClick(section)}
              className={cn(
                'flex items-center gap-1.5 px-2 py-1 rounded transition-colors',
                isActive
                  ? 'bg-glacier-blue/10 text-glacier-blue'
                  : 'text-text-secondary hover:text-text-primary hover:bg-frost/50'
              )}
              title={`${SECTION_LETTERS[section]} - ${sectionCoverage.coveredCount}/${sectionCoverage.totalCount} covered (${navigator.platform.includes('Mac') ? '⌘' : 'Ctrl'}+${index + 1})`}
              aria-label={`${section} section - ${sectionCoverage.coveredCount} of ${sectionCoverage.totalCount} prompts covered`}
              aria-pressed={isActive}
            >
              <span className="text-[15px] font-medium">
                {SECTION_LETTERS[section]}
              </span>
              <GuidanceSectionIndicator status={sectionCoverage.status} />
            </button>
          </div>
        );
      })}
    </div>
  );
}
