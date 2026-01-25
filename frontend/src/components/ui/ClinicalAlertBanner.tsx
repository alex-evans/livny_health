/**
 * ClinicalAlertBanner Component
 *
 * Displays clinical alerts at the top of the patient chart.
 * Shows severity-based styling and supports acknowledgment/dismissal.
 */

import { cn } from '../../utils/cn';
import { Button } from './Button';
import type { ClinicalAlert, AlertSeverity } from '../../types';

interface ClinicalAlertBannerProps {
  alerts: ClinicalAlert[];
  onAcknowledge: (alertId: string) => void;
  onViewDetails?: (alert: ClinicalAlert) => void;
  maxDisplayed?: number;
  className?: string;
}

function getSeverityStyles(severity: AlertSeverity) {
  switch (severity) {
    case 'critical':
      return {
        border: 'border-l-critical',
        bg: 'bg-critical/5',
        badge: 'bg-critical/15 text-critical',
        icon: 'text-critical',
        title: 'text-critical',
      };
    case 'high':
      return {
        border: 'border-l-warning',
        bg: 'bg-warning/5',
        badge: 'bg-warning/15 text-warning',
        icon: 'text-warning',
        title: 'text-[#C87B0F]',
      };
    case 'medium':
    default:
      return {
        border: 'border-l-info',
        bg: 'bg-info/5',
        badge: 'bg-info/15 text-info',
        icon: 'text-info',
        title: 'text-info',
      };
  }
}

function getSeverityIcon(severity: AlertSeverity) {
  if (severity === 'critical') {
    return (
      <svg
        className="h-5 w-5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
        />
      </svg>
    );
  }
  return (
    <svg
      className="h-5 w-5"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
  );
}

function AlertItem({
  alert,
  onAcknowledge,
  onViewDetails,
}: {
  alert: ClinicalAlert;
  onAcknowledge: (alertId: string) => void;
  onViewDetails?: (alert: ClinicalAlert) => void;
}) {
  const styles = getSeverityStyles(alert.severity);

  return (
    <div
      role="alert"
      className={cn(
        'p-normal rounded-md border-l-4',
        styles.border,
        styles.bg,
        'transition-all duration-200 hover:shadow-sm'
      )}
    >
      <div className="flex items-start gap-normal">
        <div className={cn('flex-shrink-0 mt-0.5', styles.icon)}>
          {getSeverityIcon(alert.severity)}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-tight flex-wrap">
            <span
              className={cn(
                'inline-flex items-center px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide rounded',
                styles.badge
              )}
            >
              {alert.severity}
            </span>
            <h4 className={cn('text-[15px] font-semibold', styles.title)}>
              {alert.title}
            </h4>
          </div>
          <p className="mt-1 text-[14px] text-text-secondary leading-relaxed">
            {alert.description}
          </p>
          {alert.recommendedActions.length > 0 && (
            <ul className="mt-2 space-y-0.5">
              {alert.recommendedActions.slice(0, 2).map((action, index) => (
                <li
                  key={index}
                  className="text-[13px] text-text-tertiary flex items-start gap-1"
                >
                  <span className="text-text-tertiary">•</span>
                  <span>{action}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="flex-shrink-0 flex items-center gap-2">
          {onViewDetails && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onViewDetails(alert)}
              className="text-[13px]"
            >
              View
            </Button>
          )}
          <Button
            variant="primary"
            size="sm"
            onClick={() => onAcknowledge(alert.id)}
            className="text-[13px]"
          >
            Acknowledge
          </Button>
        </div>
      </div>
    </div>
  );
}

export function ClinicalAlertBanner({
  alerts,
  onAcknowledge,
  onViewDetails,
  maxDisplayed = 3,
  className,
}: ClinicalAlertBannerProps) {
  if (alerts.length === 0) {
    return null;
  }

  const displayedAlerts = alerts.slice(0, maxDisplayed);
  const remainingCount = alerts.length - maxDisplayed;

  return (
    <div className={cn('space-y-tight', className)} role="region" aria-label="Clinical Alerts">
      {displayedAlerts.map((alert) => (
        <AlertItem
          key={alert.id}
          alert={alert}
          onAcknowledge={onAcknowledge}
          onViewDetails={onViewDetails}
        />
      ))}
      {remainingCount > 0 && (
        <div className="text-center py-tight">
          <button
            className="text-[14px] text-glacier-blue hover:text-deep-ice font-medium transition-colors"
            onClick={() => {
              // Could trigger a modal or expand the list
              console.log('Show all alerts');
            }}
          >
            +{remainingCount} more alert{remainingCount > 1 ? 's' : ''}
          </button>
        </div>
      )}
    </div>
  );
}
