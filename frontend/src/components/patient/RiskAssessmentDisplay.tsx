import type { RiskAssessment, RiskLevel } from '../../types';
import { RISK_LEVEL_CONFIG } from '../../types';
import { cn } from '../../utils/cn';

interface RiskAssessmentDisplayProps {
  riskAssessments: RiskAssessment[];
}

function RiskCard({ assessment }: { assessment: RiskAssessment }) {
  const config = RISK_LEVEL_CONFIG[assessment.riskLevel as RiskLevel];

  const colorClasses = {
    green: {
      bg: 'bg-status-success/10',
      border: 'border-status-success',
      text: 'text-status-success',
    },
    yellow: {
      bg: 'bg-status-warning/10',
      border: 'border-status-warning',
      text: 'text-status-warning',
    },
    red: {
      bg: 'bg-status-critical/10',
      border: 'border-status-critical',
      text: 'text-status-critical',
    },
    gray: {
      bg: 'bg-frost',
      border: 'border-text-tertiary',
      text: 'text-text-tertiary',
    },
  };

  const colors = colorClasses[config.color];

  const riskTypeLabels: Record<string, string> = {
    cardiovascular: 'Cardiovascular Disease',
    cancer: 'Cancer',
    diabetes: 'Type 2 Diabetes',
  };

  const riskTypeLabel = riskTypeLabels[assessment.riskType] || assessment.riskType;

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Not scheduled';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div
      className={cn(
        'bg-white rounded-lg shadow-card overflow-hidden hover:shadow-card-hover transition-shadow'
      )}
    >
      {/* Header */}
      <div className={cn('px-4 py-3 border-l-4', colors.bg, colors.border)}>
        <div className="flex items-center justify-between">
          <h4 className="text-[15px] font-semibold text-text-primary">
            {riskTypeLabel}
          </h4>
          <span
            className={cn(
              'px-2 py-0.5 text-[12px] font-medium rounded-full',
              colors.bg,
              colors.text
            )}
          >
            {config.label}
          </span>
        </div>
      </div>

      {/* Body */}
      <div className="p-4 space-y-4">
        {/* Contributing Factors */}
        {assessment.contributingFactors.length > 0 && (
          <div>
            <p className="text-[11px] font-medium text-text-tertiary uppercase tracking-wide mb-2">
              Contributing Factors
            </p>
            <ul className="space-y-1">
              {assessment.contributingFactors.map((factor, idx) => (
                <li
                  key={idx}
                  className="text-[13px] text-text-secondary flex items-start"
                >
                  <span className="text-text-tertiary mr-2">-</span>
                  {factor}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Recommendations */}
        {assessment.recommendations.length > 0 && (
          <div>
            <p className="text-[11px] font-medium text-text-tertiary uppercase tracking-wide mb-2">
              Recommendations
            </p>
            <ul className="space-y-1">
              {assessment.recommendations.map((rec, idx) => (
                <li
                  key={idx}
                  className="text-[13px] text-text-primary flex items-start"
                >
                  <span className="text-glacier-blue mr-2">-</span>
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Screening Due */}
        <div className="pt-3 border-t border-frost">
          <div className="flex items-center justify-between">
            <span className="text-[13px] text-text-tertiary">
              Next screening due:
            </span>
            <span
              className={cn(
                'text-[13px] font-medium',
                assessment.screeningDue &&
                  new Date(assessment.screeningDue) <= new Date()
                  ? 'text-status-critical'
                  : 'text-text-primary'
              )}
            >
              {formatDate(assessment.screeningDue)}
            </span>
          </div>
        </div>

        {/* Notes */}
        {assessment.notes && (
          <p className="text-[13px] text-text-tertiary italic pt-2 border-t border-frost">
            {assessment.notes}
          </p>
        )}
      </div>
    </div>
  );
}

export function RiskAssessmentDisplay({
  riskAssessments,
}: RiskAssessmentDisplayProps) {
  if (!riskAssessments || riskAssessments.length === 0) {
    return (
      <div className="text-text-tertiary text-[15px] py-8 text-center">
        No risk assessments available
      </div>
    );
  }

  // Sort by risk level: high first, then moderate, then low
  const sortedAssessments = [...riskAssessments].sort((a, b) => {
    const order: Record<RiskLevel, number> = { high: 0, moderate: 1, low: 2 };
    return order[a.riskLevel as RiskLevel] - order[b.riskLevel as RiskLevel];
  });

  const highRiskCount = riskAssessments.filter(
    (r) => r.riskLevel === 'high'
  ).length;
  const moderateRiskCount = riskAssessments.filter(
    (r) => r.riskLevel === 'moderate'
  ).length;

  return (
    <div>
      {/* Summary Banner */}
      {(highRiskCount > 0 || moderateRiskCount > 0) && (
        <div
          className={cn(
            'p-4 rounded-lg mb-6',
            highRiskCount > 0 ? 'bg-status-critical/10' : 'bg-status-warning/10'
          )}
        >
          <p
            className={cn(
              'text-[15px] font-medium',
              highRiskCount > 0 ? 'text-status-critical' : 'text-status-warning'
            )}
          >
            {highRiskCount > 0 && (
              <>
                {highRiskCount} high risk factor{highRiskCount !== 1 ? 's' : ''}{' '}
                identified
              </>
            )}
            {highRiskCount > 0 && moderateRiskCount > 0 && ', '}
            {moderateRiskCount > 0 && (
              <>
                {moderateRiskCount} moderate risk factor
                {moderateRiskCount !== 1 ? 's' : ''}
              </>
            )}
          </p>
          <p className="text-[13px] text-text-secondary mt-1">
            Review contributing factors and recommendations below
          </p>
        </div>
      )}

      {/* Risk Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
        {sortedAssessments.map((assessment, idx) => (
          <RiskCard key={idx} assessment={assessment} />
        ))}
      </div>
    </div>
  );
}
