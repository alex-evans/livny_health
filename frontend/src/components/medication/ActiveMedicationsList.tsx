import type { ActiveMedication } from '../../types';
import { Card, CardContent } from '../ui';

interface ActiveMedicationsListProps {
  medications: ActiveMedication[];
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

export function ActiveMedicationsList({ medications }: ActiveMedicationsListProps) {
  if (medications.length === 0) {
    return null;
  }

  return (
    <Card className="mb-comfortable">
      <CardContent>
        <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-normal">
          Active Medications ({medications.length})
        </h3>
        <div className="flex flex-col gap-tight">
          {medications.map((medication) => (
            <div
              key={medication.id}
              className="flex items-center justify-between py-2 border-b border-frost last:border-b-0"
            >
              <div>
                <span className="text-[15px] font-medium text-text-primary">
                  {medication.name}
                </span>
                <span className="text-[15px] text-text-secondary ml-2">
                  {medication.dosage} {medication.frequency}
                </span>
              </div>
              <span className="text-[13px] text-text-tertiary">
                Started {formatDate(medication.started)}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
