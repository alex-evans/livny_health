import { useState, useRef, useEffect } from 'react';
import { cn } from '../../utils/cn';

interface DateJumpPickerProps {
  onDateSelect: (date: string) => void;
}

type QuickOption = {
  label: string;
  getValue: () => string;
};

const quickOptions: QuickOption[] = [
  {
    label: '1 Month Ago',
    getValue: () => {
      const date = new Date();
      date.setMonth(date.getMonth() - 1);
      return date.toISOString().split('T')[0];
    },
  },
  {
    label: '3 Months Ago',
    getValue: () => {
      const date = new Date();
      date.setMonth(date.getMonth() - 3);
      return date.toISOString().split('T')[0];
    },
  },
  {
    label: '6 Months Ago',
    getValue: () => {
      const date = new Date();
      date.setMonth(date.getMonth() - 6);
      return date.toISOString().split('T')[0];
    },
  },
  {
    label: '1 Year Ago',
    getValue: () => {
      const date = new Date();
      date.setFullYear(date.getFullYear() - 1);
      return date.toISOString().split('T')[0];
    },
  },
];

export function DateJumpPicker({ onDateSelect }: DateJumpPickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [customDate, setCustomDate] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleQuickSelect = (option: QuickOption) => {
    onDateSelect(option.getValue());
    setIsOpen(false);
  };

  const handleCustomDateSubmit = () => {
    if (customDate) {
      onDateSelect(customDate);
      setCustomDate('');
      setIsOpen(false);
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'flex items-center gap-1.5 px-2.5 py-1.5 text-[13px] font-medium rounded-md',
          'bg-frost/50 text-text-secondary hover:bg-frost hover:text-deep-ice',
          'transition-colors border border-transparent hover:border-frost',
          isOpen && 'bg-frost text-deep-ice border-frost'
        )}
      >
        <CalendarIcon className="h-3.5 w-3.5" />
        Jump to Date
        <ChevronDownIcon className={cn('h-3 w-3 transition-transform', isOpen && 'rotate-180')} />
      </button>

      {isOpen && (
        <div className="absolute top-full right-0 mt-1 w-56 bg-white rounded-md shadow-lg border border-frost z-20">
          <div className="p-2">
            <p className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-2 px-1">
              Quick Jump
            </p>
            <div className="space-y-0.5">
              {quickOptions.map((option) => (
                <button
                  key={option.label}
                  type="button"
                  onClick={() => handleQuickSelect(option)}
                  className="w-full text-left px-2 py-1.5 text-[13px] text-text-primary hover:bg-frost/50 rounded transition-colors"
                >
                  {option.label}
                </button>
              ))}
            </div>

            <div className="border-t border-frost mt-2 pt-2">
              <p className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-2 px-1">
                Custom Date
              </p>
              <div className="flex gap-1.5">
                <input
                  type="date"
                  value={customDate}
                  onChange={(e) => setCustomDate(e.target.value)}
                  max={new Date().toISOString().split('T')[0]}
                  className={cn(
                    'flex-1 px-2 py-1.5 text-[13px] rounded border border-frost',
                    'focus:outline-none focus:ring-1 focus:ring-glacier-blue focus:border-glacier-blue'
                  )}
                />
                <button
                  type="button"
                  onClick={handleCustomDateSubmit}
                  disabled={!customDate}
                  className={cn(
                    'px-2.5 py-1.5 text-[13px] font-medium rounded',
                    'bg-glacier-blue text-white hover:bg-deep-ice',
                    'disabled:bg-frost disabled:text-text-tertiary disabled:cursor-not-allowed',
                    'transition-colors'
                  )}
                >
                  Go
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function CalendarIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  );
}

function ChevronDownIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );
}
