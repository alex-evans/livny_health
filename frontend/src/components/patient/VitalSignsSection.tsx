import { useState, useEffect } from 'react';
import type { VitalsResponse, VitalType } from '../../types';
import { getPatientVitals } from '../../api/vitalsApi';
import { cn } from '../../utils/cn';
import { CurrentVitals } from './CurrentVitals';
import { VitalHistoryModal } from './VitalHistoryModal';

interface VitalSignsSectionProps {
  patientId: string;
  className?: string;
}

function formatDate(dateString: string | null): string {
  if (!dateString) return 'No data';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

export function VitalSignsSection({
  patientId,
  className,
}: VitalSignsSectionProps) {
  const [vitalsData, setVitalsData] = useState<VitalsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedVital, setSelectedVital] = useState<VitalType | null>(null);

  useEffect(() => {
    if (!patientId) return;

    setLoading(true);
    setError(null);

    getPatientVitals(patientId, { includeTrends: true })
      .then((data) => {
        setVitalsData(data);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load vitals');
      })
      .finally(() => {
        setLoading(false);
      });
  }, [patientId]);

  const handleVitalClick = (vitalType: VitalType) => {
    setSelectedVital(vitalType);
  };

  const handleCloseModal = () => {
    setSelectedVital(null);
  };

  return (
    <section className={cn('', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h2 className="text-[18px] font-semibold text-text-primary">
            Vital Signs
          </h2>
          {vitalsData?.mostRecentDate && (
            <span className="text-[13px] text-text-tertiary">
              Most recent: {formatDate(vitalsData.mostRecentDate)}
            </span>
          )}
        </div>
      </div>

      {/* Content */}
      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="text-text-tertiary text-[15px]">
            Loading vital signs...
          </div>
        </div>
      )}

      {error && (
        <div className="flex items-center justify-center py-8">
          <div className="text-status-critical text-[15px]">{error}</div>
        </div>
      )}

      {!loading && !error && vitalsData && (
        <CurrentVitals
          vitals={vitalsData.vitals}
          bmi={vitalsData.bmi}
          onVitalClick={handleVitalClick}
        />
      )}

      {!loading && !error && (!vitalsData || vitalsData.vitals.length === 0) && (
        <div className="text-text-tertiary text-[15px] py-8 text-center">
          No vital signs recorded
        </div>
      )}

      {/* History Modal */}
      {selectedVital && (
        <VitalHistoryModal
          patientId={patientId}
          vitalType={selectedVital}
          isOpen={true}
          onClose={handleCloseModal}
        />
      )}
    </section>
  );
}
