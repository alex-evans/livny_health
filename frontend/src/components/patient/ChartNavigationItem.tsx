import { cn } from '../../utils/cn';
import type { ChartSection, ChartSectionId } from '../../types';
import { SectionBadge } from './SectionBadge';

interface ChartNavigationItemProps {
  section: ChartSection;
  isActive: boolean;
  onClick: (sectionId: ChartSectionId) => void;
}

export function ChartNavigationItem({
  section,
  isActive,
  onClick,
}: ChartNavigationItemProps) {
  const shortcutKey = section.keyboardShortcut?.key;

  return (
    <button
      onClick={() => onClick(section.id)}
      title={shortcutKey ? `${section.name} (Alt+${shortcutKey})` : section.name}
      className={cn(
        'w-full text-left rounded-lg shadow-card p-normal transition-all hover:shadow-card-hover',
        isActive ? 'bg-arctic ring-2 ring-glacier-blue' : 'bg-white',
        section.alertLevel === 'critical' && !isActive && 'border-l-4 border-critical'
      )}
    >
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          <SectionIcon icon={section.icon} isActive={isActive} alertLevel={section.alertLevel} />
          <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
            {section.name}
          </span>
        </div>
        <SectionBadge count={section.badgeCount} alertLevel={section.alertLevel} />
      </div>
      {section.badgeCount !== null && section.badgeCount > 0 && (
        <p className={cn(
          'text-[13px]',
          section.alertLevel === 'critical' ? 'text-critical' : 'text-text-secondary'
        )}>
          {getSectionSummary(section)}
        </p>
      )}
    </button>
  );
}

function getSectionSummary(section: ChartSection): string {
  switch (section.id) {
    case 'visits':
      return 'Previous visits';
    case 'medications':
      return `${section.badgeCount} active`;
    case 'allergies':
      return section.alertLevel === 'critical'
        ? 'Severe allergies'
        : `${section.badgeCount} documented`;
    case 'labs':
      return section.alertLevel === 'critical'
        ? 'Critical values'
        : section.alertLevel === 'warning'
          ? 'Abnormal results'
          : 'View results';
    case 'problems':
      return `${section.badgeCount} active`;
    case 'vitals':
      return section.alertLevel === 'warning' ? 'Abnormal vitals' : 'Current vitals';
    case 'imaging':
      return 'Radiology studies';
    case 'social-family':
      return 'Social & family history';
    default:
      return '';
  }
}

interface SectionIconProps {
  icon: string;
  isActive: boolean;
  alertLevel: string;
}

function SectionIcon({ icon, alertLevel }: SectionIconProps) {
  const iconColor = alertLevel === 'critical' ? 'text-critical' : 'text-glacier-blue';

  switch (icon) {
    case 'document':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className={cn('h-4 w-4', iconColor)} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      );
    case 'pill':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className={cn('h-4 w-4', iconColor)} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
        </svg>
      );
    case 'exclamation-triangle':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className={cn('h-4 w-4', iconColor)} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      );
    case 'beaker':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className={cn('h-4 w-4', iconColor)} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
        </svg>
      );
    case 'clipboard-list':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className={cn('h-4 w-4', iconColor)} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
        </svg>
      );
    case 'heart-pulse':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className={cn('h-4 w-4', iconColor)} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      );
    case 'film':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className={cn('h-4 w-4', iconColor)} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <rect x="2" y="2" width="20" height="20" rx="2" strokeWidth={2} />
          <circle cx="8" cy="8" r="2" strokeWidth={2} />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 15l-5-5L5 21" />
        </svg>
      );
    case 'users':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className={cn('h-4 w-4', iconColor)} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      );
    default:
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className={cn('h-4 w-4', iconColor)} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      );
  }
}
