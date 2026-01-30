import { cn } from '../../utils/cn';

interface CollapsibleContextSectionProps {
  title: string;
  count?: number;
  isExpanded: boolean;
  onToggle: () => void;
  isLoading?: boolean;
  children: React.ReactNode;
}

export function CollapsibleContextSection({
  title,
  count,
  isExpanded,
  onToggle,
  isLoading = false,
  children,
}: CollapsibleContextSectionProps) {
  return (
    <div className="border-b border-frost last:border-b-0">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between py-normal px-comfortable hover:bg-frost/30 transition-colors"
        aria-expanded={isExpanded}
      >
        <div className="flex items-center gap-2">
          <span className="text-[15px] font-medium text-text-primary">
            {title}
          </span>
          {count !== undefined && (
            <span className="text-[12px] text-text-tertiary bg-frost px-2 py-0.5 rounded-full">
              {count}
            </span>
          )}
        </div>
        <ChevronIcon
          className={cn(
            'w-4 h-4 text-text-tertiary transition-transform',
            isExpanded ? 'rotate-180' : ''
          )}
        />
      </button>
      {isExpanded && (
        <div className="px-comfortable pb-normal">
          {isLoading ? <LoadingSkeleton /> : children}
        </div>
      )}
    </div>
  );
}

function ChevronIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
    </svg>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-2 animate-pulse">
      <div className="h-4 bg-frost rounded w-3/4" />
      <div className="h-4 bg-frost rounded w-1/2" />
      <div className="h-4 bg-frost rounded w-2/3" />
    </div>
  );
}
