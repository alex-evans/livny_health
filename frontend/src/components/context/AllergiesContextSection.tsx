import { cn } from '../../utils/cn';
import type { EnrichedContextAllergy } from '../../types';

interface AllergiesContextSectionProps {
  allergies: EnrichedContextAllergy[];
}

export function AllergiesContextSection({ allergies }: AllergiesContextSectionProps) {
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
            allergy.severity === 'critical' || allergy.isAnaphylaxis
              ? 'bg-status-critical/10 text-status-critical'
              : allergy.severity === 'moderate'
                ? 'bg-status-abnormal/10 text-status-abnormal'
                : 'bg-frost text-text-primary'
          )}
        >
          <div className="flex items-center gap-2">
            <span className="text-[14px] font-medium">{allergy.allergen}</span>
            {allergy.isAnaphylaxis && (
              <span className="text-[11px] font-medium uppercase">
                Anaphylaxis
              </span>
            )}
            <SeverityBadge severity={allergy.severity} />
          </div>
          <div className="text-[12px] mt-1">
            {allergy.reaction}
          </div>
          {allergy.status !== 'confirmed' && (
            <div className="text-[11px] mt-1 opacity-75">
              Status: {allergy.status}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function SeverityBadge({ severity }: { severity: 'critical' | 'moderate' | 'mild' }) {
  const colors = {
    critical: 'bg-status-critical/20',
    moderate: 'bg-status-abnormal/20',
    mild: 'bg-frost',
  };

  return (
    <span
      className={cn(
        'text-[10px] font-medium uppercase px-1.5 py-0.5 rounded',
        colors[severity]
      )}
    >
      {severity}
    </span>
  );
}
