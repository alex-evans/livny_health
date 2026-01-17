import { useState, useRef } from 'react';
import type { ActiveMedication } from '../../types';

interface MedicationTooltipProps {
  medication: ActiveMedication;
  children: React.ReactNode;
}

export function MedicationTooltip({ medication, children }: MedicationTooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [position, setPosition] = useState<{ top: number; left: number }>({ top: 0, left: 0 });
  const triggerRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const showTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    timeoutRef.current = setTimeout(() => {
      if (triggerRef.current) {
        const rect = triggerRef.current.getBoundingClientRect();
        setPosition({
          top: rect.bottom + 8,
          left: rect.left,
        });
      }
      setIsVisible(true);
    }, 300);
  };

  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    timeoutRef.current = setTimeout(() => {
      setIsVisible(false);
    }, 100);
  };

  const keepTooltipVisible = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
  };

  const hasAdditionalContext = medication.indication || medication.prescriberNotes || medication.drugClass;

  if (!hasAdditionalContext) {
    return <>{children}</>;
  }

  return (
    <div
      ref={triggerRef}
      onMouseEnter={showTooltip}
      onMouseLeave={hideTooltip}
      className="inline"
    >
      {children}
      {isVisible && (
        <div
          className="fixed z-50 max-w-xs bg-deep-ice text-white rounded-md shadow-lg p-normal"
          style={{ top: position.top, left: position.left }}
          onMouseEnter={keepTooltipVisible}
          onMouseLeave={hideTooltip}
        >
          <div className="space-y-2">
            {medication.indication && (
              <div>
                <span className="text-[11px] font-medium uppercase tracking-wide text-white/70">
                  Indication
                </span>
                <p className="text-[13px] text-white">{medication.indication}</p>
              </div>
            )}
            {medication.drugClass && (
              <div>
                <span className="text-[11px] font-medium uppercase tracking-wide text-white/70">
                  Class
                </span>
                <p className="text-[13px] text-white">{medication.drugClass}</p>
              </div>
            )}
            {medication.prescriberNotes && (
              <div>
                <span className="text-[11px] font-medium uppercase tracking-wide text-white/70">
                  Notes
                </span>
                <p className="text-[13px] text-white italic">{medication.prescriberNotes}</p>
              </div>
            )}
          </div>
          {/* Tooltip arrow */}
          <div
            className="absolute -top-2 left-4 w-0 h-0 border-l-8 border-r-8 border-b-8 border-l-transparent border-r-transparent border-b-deep-ice"
          />
        </div>
      )}
    </div>
  );
}
