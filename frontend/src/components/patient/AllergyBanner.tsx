import type { Allergy, AllergySeverity } from '../../types';
import { cn } from '../../utils/cn';

interface AllergyBannerProps {
  allergies: Allergy[];
}

const severityConfig: Record<AllergySeverity, { label: string; className: string }> = {
  severe: {
    label: 'Severe',
    className: 'bg-critical text-white',
  },
  moderate: {
    label: 'Moderate',
    className: 'bg-warning text-white',
  },
  mild: {
    label: 'Mild',
    className: 'bg-frost text-text-primary',
  },
};

export function AllergyBanner({ allergies }: AllergyBannerProps) {
  const hasAllergies = allergies.length > 0;
  const hasSevereAllergy = allergies.some((a) => a.severity === 'severe');

  if (!hasAllergies) {
    return (
      <div
        className="px-generous py-normal bg-arctic"
        role="status"
        aria-label="No known allergies"
      >
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center gap-tight">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 text-success"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            <span className="text-[15px] font-medium text-text-primary">
              No known allergies
            </span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        'px-generous py-normal',
        hasSevereAllergy ? 'bg-[#FADBD8]' : 'bg-[#FEF5E7]'
      )}
      role="alert"
      aria-label="Patient allergies"
    >
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center gap-tight mb-tight">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className={cn('h-5 w-5', hasSevereAllergy ? 'text-critical' : 'text-warning')}
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          <span
            className={cn(
              'text-[11px] font-medium uppercase tracking-wide',
              hasSevereAllergy ? 'text-critical' : 'text-warning'
            )}
          >
            Allergies ({allergies.length})
          </span>
        </div>
        <div className="flex flex-wrap gap-tight">
          {allergies.map((allergy) => {
            const config = severityConfig[allergy.severity];
            return (
              <div
                key={allergy.id}
                className="flex items-center gap-tight bg-white rounded-md px-3 py-2 shadow-sm"
              >
                <span className="text-[15px] font-medium text-text-primary">
                  {allergy.allergen}
                </span>
                <span
                  className={cn(
                    'px-2 py-0.5 text-[11px] font-medium uppercase tracking-wide rounded',
                    config.className
                  )}
                >
                  {config.label}
                </span>
                {allergy.reaction && (
                  <span className="text-[13px] text-text-secondary">
                    ({allergy.reaction})
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
