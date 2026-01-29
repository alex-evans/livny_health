import { Link } from 'react-router-dom';
import { cn } from '../../utils/cn';
import type { PatientSummary, EncounterNote, EncounterStatus } from '../../types';

interface EncounterPatientBannerProps {
  patient: PatientSummary;
  encounter: EncounterNote;
  className?: string;
}

function calculateAge(dateOfBirth: string): number {
  const dob = new Date(dateOfBirth);
  const today = new Date();
  let age = today.getFullYear() - dob.getFullYear();
  const monthDiff = today.getMonth() - dob.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
    age--;
  }
  return age;
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function formatGender(gender: string): string {
  switch (gender.toLowerCase()) {
    case 'male':
      return 'M';
    case 'female':
      return 'F';
    default:
      return gender.charAt(0).toUpperCase();
  }
}

function StatusBadge({ status }: { status: EncounterStatus }) {
  const statusConfig: Record<EncounterStatus, { label: string; className: string }> = {
    scheduled: {
      label: 'Scheduled',
      className: 'bg-arctic text-deep-ice',
    },
    in_progress: {
      label: 'In Progress',
      className: 'bg-glacier-blue/10 text-glacier-blue',
    },
    completed: {
      label: 'Completed',
      className: 'bg-[#FEF5E7] text-warning',
    },
    signed: {
      label: 'Signed',
      className: 'bg-[#E8F6EF] text-success',
    },
  };

  const config = statusConfig[status] || statusConfig.scheduled;

  return (
    <span className={cn('px-2 py-0.5 rounded text-[12px] font-medium', config.className)}>
      {config.label}
    </span>
  );
}

export function EncounterPatientBanner({
  patient,
  encounter,
  className,
}: EncounterPatientBannerProps) {
  const age = patient.dateOfBirth ? calculateAge(patient.dateOfBirth) : null;

  return (
    <div
      className={cn(
        'bg-white border-b border-frost px-comfortable py-normal',
        className
      )}
    >
      <div className="flex items-center justify-between">
        {/* Left side - Patient info */}
        <div className="flex items-center gap-comfortable">
          {/* Back link */}
          <Link
            to="/schedule"
            className="flex items-center gap-2 text-[15px] text-glacier-blue hover:underline"
          >
            <ArrowLeftIcon className="w-4 h-4" />
            Schedule
          </Link>

          {/* Divider */}
          <span className="w-px h-6 bg-frost" />

          {/* Patient name and demographics */}
          <div>
            <h1 className="text-[18px] font-semibold text-text-primary">
              {patient.name}
            </h1>
            <div className="flex items-center gap-2 text-[13px] text-text-secondary">
              {age !== null && (
                <span>
                  {age}yo {formatGender(patient.gender)}
                </span>
              )}
              {patient.dateOfBirth && (
                <>
                  <span className="text-text-tertiary">|</span>
                  <span>DOB: {formatDate(patient.dateOfBirth)}</span>
                </>
              )}
              {patient.mrn && (
                <>
                  <span className="text-text-tertiary">|</span>
                  <span>MRN: {patient.mrn}</span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Right side - Encounter info */}
        <div className="text-right">
          <div className="flex items-center gap-2">
            <StatusBadge status={encounter.status} />
            {encounter.type && (
              <span className="text-[13px] text-text-secondary">
                {encounter.type}
              </span>
            )}
          </div>
          {encounter.startTime && (
            <div className="text-[13px] text-text-tertiary mt-1">
              Started {formatDate(encounter.startTime)}
            </div>
          )}
        </div>
      </div>

      {/* Chief complaint */}
      {encounter.chiefComplaint && (
        <div className="mt-normal pt-normal border-t border-frost">
          <div className="text-[13px] text-text-tertiary mb-1">
            Chief Complaint
          </div>
          <div className="text-[15px] text-text-primary">
            {encounter.chiefComplaint}
          </div>
        </div>
      )}
    </div>
  );
}

function ArrowLeftIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M10 19l-7-7m0 0l7-7m-7 7h18"
      />
    </svg>
  );
}
