import type { EnrichedContextVisit } from '../../types';

interface VisitsContextSectionProps {
  visits: EnrichedContextVisit[];
}

export function VisitsContextSection({ visits }: VisitsContextSectionProps) {
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
            {formatDaysAgo(visit.daysAgo)} - {visit.type}
            {visit.provider && ` - ${visit.provider}`}
          </div>
          {visit.summary && (
            <div className="text-[12px] text-text-secondary mt-1 line-clamp-2">
              {visit.summary}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function formatDaysAgo(days: number): string {
  if (days === 0) {
    return 'Today';
  }
  if (days === 1) {
    return 'Yesterday';
  }
  if (days < 7) {
    return `${days} days ago`;
  }
  if (days < 14) {
    return '1 week ago';
  }
  if (days < 30) {
    return `${Math.floor(days / 7)} weeks ago`;
  }
  if (days < 60) {
    return '1 month ago';
  }
  return `${Math.floor(days / 30)} months ago`;
}
