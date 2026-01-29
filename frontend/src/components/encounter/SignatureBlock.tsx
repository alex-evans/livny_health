import { cn } from '../../utils/cn';

interface SignatureBlockProps {
  signedByName: string;
  signedAt: string;
  npi?: string | null;
  className?: string;
}

function formatDateTime(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
}

export function SignatureBlock({
  signedByName,
  signedAt,
  npi,
  className,
}: SignatureBlockProps) {
  return (
    <div
      className={cn(
        'border-t-2 border-dashed border-frost pt-normal mt-generous',
        className
      )}
    >
      <div className="flex items-start gap-comfortable">
        {/* Signature icon */}
        <div className="w-10 h-10 rounded-full bg-success/10 flex items-center justify-center flex-shrink-0">
          <svg
            className="w-5 h-5 text-success"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>

        <div className="flex-1">
          <p className="text-[15px] font-medium text-text-primary">
            Electronically signed by {signedByName}
          </p>
          <p className="text-[13px] text-text-secondary mt-1">
            {formatDateTime(signedAt)}
          </p>
          {npi && (
            <p className="text-[13px] text-text-tertiary mt-1">
              NPI: {npi}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
