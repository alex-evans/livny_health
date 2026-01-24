import { useState } from 'react';
import { cn } from '../../utils/cn';
import type { ChartSection, ChartSectionId } from '../../types';
import { ChartNavigationItem } from './ChartNavigationItem';
import { KeyboardShortcutsHelp } from './KeyboardShortcutsHelp';

interface ChartNavigationProps {
  sections: ChartSection[];
  activeSection: ChartSectionId;
  onNavigate: (sectionId: ChartSectionId) => void;
  isLoading?: boolean;
  onPrescribeClick?: () => void;
  prescriptionCount?: number;
  isPrescribeActive?: boolean;
}

export function ChartNavigation({
  sections,
  activeSection,
  onNavigate,
  isLoading = false,
  onPrescribeClick,
  prescriptionCount = 0,
  isPrescribeActive = false,
}: ChartNavigationProps) {
  const [showHelp, setShowHelp] = useState(false);

  if (isLoading) {
    return (
      <div className="space-y-tight">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
          <div
            key={i}
            className="h-12 bg-frost rounded-lg animate-pulse"
          />
        ))}
      </div>
    );
  }

  return (
    <>
      <nav className="space-y-tight">
        {sections.map((section) => (
          <ChartNavigationItem
            key={section.id}
            section={section}
            isActive={activeSection === section.id}
            onClick={onNavigate}
          />
        ))}

        {/* Prescribe Action */}
        {onPrescribeClick && (
          <button
            onClick={onPrescribeClick}
            className={cn(
              'w-full text-left rounded-lg shadow-card p-normal transition-all hover:shadow-card-hover',
              isPrescribeActive ? 'bg-glacier-blue text-white' : 'bg-white'
            )}
          >
            <div className="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className={cn('h-5 w-5', isPrescribeActive ? 'text-white' : 'text-glacier-blue')}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span className={cn('text-[15px] font-medium', isPrescribeActive ? 'text-white' : 'text-glacier-blue')}>
                Prescribe
              </span>
            </div>
            {prescriptionCount > 0 && (
              <p className={cn('text-[13px] mt-1', isPrescribeActive ? 'text-white/80' : 'text-text-secondary')}>
                {prescriptionCount} pending
              </p>
            )}
          </button>
        )}

        {/* Keyboard shortcuts help */}
        <button
          onClick={() => setShowHelp(true)}
          className={cn(
            'w-full flex items-center gap-2 px-normal py-2 rounded-lg transition-all',
            'text-[13px] text-text-tertiary hover:text-text-secondary hover:bg-frost'
          )}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Keyboard shortcuts</span>
        </button>
      </nav>

      {showHelp && (
        <KeyboardShortcutsHelp
          sections={sections}
          onClose={() => setShowHelp(false)}
        />
      )}
    </>
  );
}
