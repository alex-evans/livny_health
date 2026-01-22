import type { CurrentVital, BMIResponse, VitalType } from '../../types';
import { VITAL_DISPLAY_CONFIG } from '../../types/vitals';
import { cn } from '../../utils/cn';
import { VitalSparkline } from './VitalSparkline';
import { VitalTrendIndicator } from './VitalTrendIndicator';

interface CurrentVitalsProps {
  vitals: CurrentVital[];
  bmi: BMIResponse | null;
  onVitalClick: (vitalType: VitalType) => void;
  className?: string;
}

function getStatusBadgeClass(status: 'normal' | 'abnormal' | 'critical'): string {
  switch (status) {
    case 'critical':
      return 'bg-status-critical/10 text-status-critical';
    case 'abnormal':
      return 'bg-status-warning/10 text-status-warning';
    default:
      return 'bg-status-success/10 text-status-success';
  }
}

function getBmiCategoryClass(category: string): string {
  switch (category.toLowerCase()) {
    case 'underweight':
      return 'bg-status-warning/10 text-status-warning';
    case 'normal':
      return 'bg-status-success/10 text-status-success';
    case 'overweight':
      return 'bg-status-warning/10 text-status-warning';
    case 'obese':
      return 'bg-status-critical/10 text-status-critical';
    default:
      return 'bg-frost/50 text-text-secondary';
  }
}

interface VitalCardProps {
  vital: CurrentVital;
  onClick: () => void;
}

function VitalCard({ vital, onClick }: VitalCardProps) {
  const config = VITAL_DISPLAY_CONFIG[vital.vitalType];

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'flex flex-col p-4 rounded-lg bg-white shadow-card',
        'hover:shadow-card-hover transition-shadow',
        'text-left w-full overflow-hidden'
      )}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <span className="text-[13px] text-text-secondary font-medium">
          {config.label}
        </span>
        <span
          className={cn(
            'text-[11px] px-1.5 py-0.5 rounded font-medium capitalize',
            getStatusBadgeClass(vital.status)
          )}
        >
          {vital.status}
        </span>
      </div>

      <div className="flex items-baseline gap-1 mb-3">
        <span className="text-[24px] font-semibold text-text-primary">
          {vital.value}
        </span>
        <span className="text-[15px] text-text-secondary">{vital.unit}</span>
      </div>

      {vital.sparklineData.length >= 2 && (
        <VitalSparkline data={vital.sparklineData} width={100} height={28} />
      )}

      <div className="mt-2 flex items-center justify-between">
        <span className="text-[11px] text-text-tertiary">
          Ref: {vital.referenceRange}
        </span>
        <VitalTrendIndicator trend={vital.trend} />
      </div>
    </button>
  );
}

interface BloodPressureCardProps {
  systolic: CurrentVital;
  diastolic: CurrentVital;
  onClick: () => void;
}

function BloodPressureCard({
  systolic,
  diastolic,
  onClick,
}: BloodPressureCardProps) {
  // Use the worse status of the two
  const status =
    systolic.status === 'critical' || diastolic.status === 'critical'
      ? 'critical'
      : systolic.status === 'abnormal' || diastolic.status === 'abnormal'
      ? 'abnormal'
      : 'normal';

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'flex flex-col p-4 rounded-lg bg-white shadow-card',
        'hover:shadow-card-hover transition-shadow',
        'text-left w-full overflow-hidden'
      )}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <span className="text-[13px] text-text-secondary font-medium">
          Blood Pressure
        </span>
        <span
          className={cn(
            'text-[11px] px-1.5 py-0.5 rounded font-medium capitalize',
            getStatusBadgeClass(status)
          )}
        >
          {status}
        </span>
      </div>

      <div className="flex items-baseline gap-1 mb-3">
        <span className="text-[24px] font-semibold text-text-primary">
          {systolic.value}/{diastolic.value}
        </span>
        <span className="text-[15px] text-text-secondary">mmHg</span>
      </div>

      {systolic.sparklineData.length >= 2 && (
        <VitalSparkline
          data={systolic.sparklineData}
          width={100}
          height={28}
        />
      )}

      <div className="mt-2 flex items-center justify-between">
        <span className="text-[11px] text-text-tertiary">
          Ref: {systolic.referenceRange.replace(' mmHg', '')}/
          {diastolic.referenceRange.replace(' mmHg', '')} mmHg
        </span>
        <VitalTrendIndicator trend={systolic.trend} />
      </div>
    </button>
  );
}

interface BMICardProps {
  bmi: BMIResponse;
}

function BMICard({ bmi }: BMICardProps) {
  return (
    <div
      className={cn(
        'flex flex-col p-4 rounded-lg bg-white shadow-card',
        'text-left w-full'
      )}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <span className="text-[13px] text-text-secondary font-medium">BMI</span>
        <span
          className={cn(
            'text-[11px] px-1.5 py-0.5 rounded font-medium',
            getBmiCategoryClass(bmi.category)
          )}
        >
          {bmi.category}
        </span>
      </div>

      <div className="flex items-baseline gap-1 mb-3">
        <span className="text-[24px] font-semibold text-text-primary">
          {bmi.value.toFixed(1)}
        </span>
        <span className="text-[15px] text-text-secondary">kg/m²</span>
      </div>

      <div className="text-[13px] text-text-tertiary">
        {bmi.heightValue} {bmi.heightUnit}, {bmi.weightValue} {bmi.weightUnit}
      </div>
    </div>
  );
}

export function CurrentVitals({
  vitals,
  bmi,
  onVitalClick,
  className,
}: CurrentVitalsProps) {
  // Find blood pressure vitals
  const systolicVital = vitals.find(
    (v) => v.vitalType === 'blood_pressure_systolic'
  );
  const diastolicVital = vitals.find(
    (v) => v.vitalType === 'blood_pressure_diastolic'
  );
  const hasBloodPressure = systolicVital && diastolicVital;

  // Other vitals (excluding BP and height which is rarely displayed alone)
  const otherVitals = vitals.filter(
    (v) =>
      v.vitalType !== 'blood_pressure_systolic' &&
      v.vitalType !== 'blood_pressure_diastolic' &&
      v.vitalType !== 'height'
  );

  if (vitals.length === 0) {
    return (
      <div className={cn('text-text-tertiary text-[15px]', className)}>
        No vital signs recorded
      </div>
    );
  }

  return (
    <div
      className={cn(
        'grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4',
        className
      )}
    >
      {/* Blood Pressure card (combined) */}
      {hasBloodPressure && (
        <BloodPressureCard
          systolic={systolicVital}
          diastolic={diastolicVital}
          onClick={() => onVitalClick('blood_pressure_systolic')}
        />
      )}

      {/* Other vitals */}
      {otherVitals.map((vital) => (
        <VitalCard
          key={vital.vitalType}
          vital={vital}
          onClick={() => onVitalClick(vital.vitalType)}
        />
      ))}

      {/* BMI card */}
      {bmi && <BMICard bmi={bmi} />}
    </div>
  );
}
