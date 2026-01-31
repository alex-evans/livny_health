import { cn } from '../../utils/cn';

interface SOAPToggleButtonProps {
  isActive: boolean;
  onClick: () => void;
  className?: string;
}

export function SOAPToggleButton({
  isActive,
  onClick,
  className,
}: SOAPToggleButtonProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'flex items-center gap-2 px-3 py-1.5 rounded transition-colors',
        'text-[13px] font-medium',
        isActive
          ? 'bg-glacier-blue text-white'
          : 'bg-frost/50 text-text-secondary hover:bg-frost hover:text-text-primary',
        className
      )}
      aria-label={isActive ? 'Hide SOAP view' : 'Show SOAP view'}
      title="Toggle SOAP view (Cmd/Ctrl+Shift+S)"
    >
      <SOAPIcon className="w-4 h-4" />
      <span>SOAP</span>
    </button>
  );
}

function SOAPIcon({ className }: { className?: string }) {
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
        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
      />
    </svg>
  );
}
