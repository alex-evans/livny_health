import { cn } from '../../utils/cn';
import type { EnrichedContextVital } from '../../types';

interface VitalsContextSectionProps {
  vitals: Record<string, EnrichedContextVital>;
  recordedAt?: string;
}

export function VitalsContextSection({ vitals, recordedAt }: VitalsContextSectionProps) {
  const vitalsList = Object.values(vitals);

  if (vitalsList.length === 0) {
    return (
      <p className="text-[13px] text-text-tertiary">No recent vitals recorded</p>
    );
  }

  return (
    <div>
      {recordedAt && (
        <p className="text-[12px] text-text-tertiary mb-2">
          Last recorded: {new Date(recordedAt).toLocaleDateString()}
        </p>
      )}
      <div className="grid grid-cols-2 gap-3">
        {vitalsList.map((vital) => (
          <div key={vital.id} className="bg-frost/30 rounded-lg p-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[12px] text-text-tertiary">
                {vital.displayName}
              </span>
              {vital.trend && <TrendIndicator trend={vital.trend} />}
            </div>
            <div
              className={cn(
                'text-[15px] font-medium',
                vital.status === 'normal'
                  ? 'text-text-primary'
                  : vital.status === 'critical'
                    ? 'text-status-critical'
                    : 'text-status-abnormal'
              )}
            >
              {vital.displayValue}
            </div>
            {vital.previousValue !== undefined && (
              <div className="text-[11px] text-text-tertiary mt-1">
                Previous: {vital.previousValue} {vital.unit}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function TrendIndicator({ trend }: { trend: 'improving' | 'worsening' | 'stable' }) {
  if (trend === 'stable') {
    return (
      <span className="text-[11px] text-text-tertiary" title="Stable">
        —
      </span>
    );
  }

  if (trend === 'improving') {
    return (
      <span className="text-[11px] text-status-normal" title="Improving">
        ↓
      </span>
    );
  }

  return (
    <span className="text-[11px] text-status-abnormal" title="Worsening">
      ↑
    </span>
  );
}
