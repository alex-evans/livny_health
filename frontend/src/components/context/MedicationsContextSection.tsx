import { cn } from '../../utils/cn';
import type { EnrichedContextMedication, DiscontinuedMedication } from '../../types';

interface MedicationsContextSectionProps {
  medications: EnrichedContextMedication[];
  recentlyDiscontinued: DiscontinuedMedication[];
}

export function MedicationsContextSection({
  medications,
  recentlyDiscontinued,
}: MedicationsContextSectionProps) {
  if (medications.length === 0 && recentlyDiscontinued.length === 0) {
    return (
      <p className="text-[13px] text-text-tertiary">No active medications</p>
    );
  }

  // Group medications by category
  const byCategory = medications.reduce(
    (acc, med) => {
      const category = med.category || 'Other';
      if (!acc[category]) {
        acc[category] = [];
      }
      acc[category].push(med);
      return acc;
    },
    {} as Record<string, EnrichedContextMedication[]>
  );

  const categories = Object.keys(byCategory).sort();

  return (
    <div className="space-y-3">
      {categories.map((category) => (
        <div key={category}>
          <h4 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-2">
            {category}
          </h4>
          <div className="space-y-2">
            {byCategory[category].map((med) => (
              <MedicationItem key={med.id} medication={med} />
            ))}
          </div>
        </div>
      ))}

      {recentlyDiscontinued.length > 0 && (
        <div>
          <h4 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-2">
            Recently Discontinued
          </h4>
          <div className="space-y-2">
            {recentlyDiscontinued.map((med) => (
              <div
                key={med.id}
                className="text-[14px] text-text-tertiary line-through"
              >
                <span>{med.name}</span>
                {med.reason && (
                  <span className="text-[12px] ml-2">({med.reason})</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {medications.length > 5 && (
        <p className="text-[12px] text-glacier-blue">
          +{medications.length - 5} more medications
        </p>
      )}
    </div>
  );
}

function MedicationItem({ medication }: { medication: EnrichedContextMedication }) {
  return (
    <div className="flex items-start justify-between">
      <div>
        <div className="flex items-center gap-2">
          <span className="text-[14px] text-text-primary">{medication.name}</span>
          {medication.isHighAlert && (
            <span
              className={cn(
                'inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-medium',
                'bg-status-critical/10 text-status-critical'
              )}
              title="High-alert medication"
            >
              HA
            </span>
          )}
          {medication.isRecentlyStarted && (
            <span
              className={cn(
                'inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-medium',
                'bg-glacier-blue/10 text-glacier-blue'
              )}
            >
              New
            </span>
          )}
        </div>
        <div className="text-[12px] text-text-secondary">
          {medication.dosage} - {medication.frequency}
        </div>
      </div>
    </div>
  );
}
