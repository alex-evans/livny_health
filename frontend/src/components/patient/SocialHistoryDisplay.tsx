import { useState } from 'react';
import type {
  SocialHistory,
  StatusDisplayConfig,
  SmokingStatus,
  AlcoholUse,
  SubstanceUseLevel,
  ExerciseLevel,
} from '../../types';
import {
  SMOKING_STATUS_CONFIG,
  ALCOHOL_USE_CONFIG,
  SUBSTANCE_USE_CONFIG,
  EXERCISE_LEVEL_CONFIG,
  MARITAL_STATUS_LABELS,
  DIET_TYPE_LABELS,
} from '../../types';
import { cn } from '../../utils/cn';

interface SocialHistoryDisplayProps {
  socialHistory: SocialHistory | null;
}

function StatusIndicator({ config }: { config: StatusDisplayConfig }) {
  const colorClasses = {
    green: 'bg-status-success',
    yellow: 'bg-status-warning',
    red: 'bg-status-critical',
    gray: 'bg-text-tertiary',
  };

  return (
    <span
      className={cn(
        'inline-block w-2 h-2 rounded-full mr-2',
        colorClasses[config.color]
      )}
    />
  );
}

function InfoCard({
  title,
  children,
  className,
}: {
  title: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        'bg-white rounded-lg shadow-card p-4 hover:shadow-card-hover transition-shadow',
        className
      )}
    >
      <h4 className="text-[13px] font-medium text-text-tertiary uppercase tracking-wide mb-3">
        {title}
      </h4>
      {children}
    </div>
  );
}

// Cessation resources based on smoking status
const CESSATION_RESOURCES: Record<SmokingStatus, { title: string; resources: string[] }> = {
  current_daily: {
    title: 'Smoking Cessation Resources',
    resources: [
      'National Quitline: 1-800-QUIT-NOW',
      'Nicotine Replacement Therapy (NRT) options available',
      'Prescription medications: Varenicline, Bupropion',
      'Smokefree.gov - Free texting programs',
      'Consider referral to behavioral counseling',
    ],
  },
  current_occasional: {
    title: 'Smoking Cessation Resources',
    resources: [
      'National Quitline: 1-800-QUIT-NOW',
      'Nicotine replacement options for occasional use',
      'Smokefree.gov - Free support programs',
      'Identify and avoid smoking triggers',
    ],
  },
  former: {
    title: 'Relapse Prevention Resources',
    resources: [
      'Continue to avoid known triggers',
      'Support groups available if needed',
      'Quitline support: 1-800-QUIT-NOW',
      'Recognize early signs of relapse',
    ],
  },
  never: { title: '', resources: [] },
  unknown: { title: '', resources: [] },
};

export function SocialHistoryDisplay({
  socialHistory,
}: SocialHistoryDisplayProps) {
  const [isTobaccoExpanded, setIsTobaccoExpanded] = useState(false);

  if (!socialHistory) {
    return (
      <div className="text-text-tertiary text-[15px] py-8 text-center">
        Social history not documented
      </div>
    );
  }

  const smokingConfig =
    SMOKING_STATUS_CONFIG[socialHistory.smoking.status as SmokingStatus] ||
    SMOKING_STATUS_CONFIG.unknown;
  const alcoholConfig =
    ALCOHOL_USE_CONFIG[socialHistory.alcohol.useLevel as AlcoholUse] ||
    ALCOHOL_USE_CONFIG.unknown;
  const substanceConfig =
    SUBSTANCE_USE_CONFIG[socialHistory.substanceUse.level as SubstanceUseLevel] ||
    SUBSTANCE_USE_CONFIG.unknown;
  const exerciseConfig =
    EXERCISE_LEVEL_CONFIG[socialHistory.exercise as ExerciseLevel] ||
    EXERCISE_LEVEL_CONFIG.unknown;

  const cessationInfo = CESSATION_RESOURCES[socialHistory.smoking.status as SmokingStatus] || CESSATION_RESOURCES.unknown;
  const hasResources = cessationInfo.resources.length > 0 || socialHistory.smoking.notes;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {/* Tobacco Use - Clickable for cessation resources */}
      <div
        className={cn(
          'bg-white rounded-lg shadow-card p-4 transition-shadow',
          hasResources && 'cursor-pointer hover:shadow-card-hover'
        )}
        onClick={hasResources ? () => setIsTobaccoExpanded(!isTobaccoExpanded) : undefined}
      >
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-[13px] font-medium text-text-tertiary uppercase tracking-wide">
            Tobacco Use
          </h4>
          {hasResources && (
            <svg
              className={cn(
                'w-4 h-4 text-text-tertiary transition-transform',
                isTobaccoExpanded && 'rotate-180'
              )}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          )}
        </div>
        <div className="flex items-center mb-2">
          <StatusIndicator config={smokingConfig} />
          <span className="text-[15px] text-text-primary font-medium">
            {smokingConfig.label}
          </span>
        </div>
        {socialHistory.smoking.packYears && (
          <p className="text-[13px] text-text-secondary ml-4 mb-1">
            Pack-years: {socialHistory.smoking.packYears}
          </p>
        )}
        {socialHistory.smoking.quitDate && (
          <p className="text-[13px] text-text-secondary ml-4 mb-1">
            Quit date:{' '}
            {new Date(socialHistory.smoking.quitDate).toLocaleDateString()}
          </p>
        )}
        {hasResources && !isTobaccoExpanded && (
          <p className="text-[13px] text-glacier-blue mt-2">
            Click to view {cessationInfo.resources.length > 0 ? 'resources' : 'notes'}
          </p>
        )}

        {/* Expanded Section */}
        {isTobaccoExpanded && (
          <div className="mt-3 pt-3 border-t border-frost">
            {/* Counseling Notes */}
            {socialHistory.smoking.notes && (
              <div className="mb-3">
                <p className="text-[11px] font-medium text-text-tertiary uppercase tracking-wide mb-1">
                  Counseling Notes
                </p>
                <p className="text-[13px] text-text-primary bg-arctic p-2 rounded">
                  {socialHistory.smoking.notes}
                </p>
              </div>
            )}

            {/* Cessation Resources */}
            {cessationInfo.resources.length > 0 && (
              <div>
                <p className="text-[11px] font-medium text-text-tertiary uppercase tracking-wide mb-2">
                  {cessationInfo.title}
                </p>
                <ul className="space-y-1">
                  {cessationInfo.resources.map((resource, idx) => (
                    <li
                      key={idx}
                      className="text-[13px] text-text-secondary flex items-start"
                    >
                      <span className="text-glacier-blue mr-2">•</span>
                      {resource}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Alcohol Use */}
      <InfoCard title="Alcohol Use">
        <div className="flex items-center mb-2">
          <StatusIndicator config={alcoholConfig} />
          <span className="text-[15px] text-text-primary font-medium">
            {alcoholConfig.label}
          </span>
        </div>
        {socialHistory.alcohol.drinksPerWeek !== null && (
          <p className="text-[13px] text-text-secondary ml-4 mb-1">
            {socialHistory.alcohol.drinksPerWeek} drinks/week
          </p>
        )}
        {socialHistory.alcohol.historyOfAbuse && (
          <p className="text-[13px] text-status-warning ml-4 mb-1">
            History of alcohol abuse
          </p>
        )}
        {socialHistory.alcohol.notes && (
          <p className="text-[13px] text-text-tertiary ml-4 mt-2 italic">
            {socialHistory.alcohol.notes}
          </p>
        )}
      </InfoCard>

      {/* Substance Use */}
      <InfoCard title="Substance Use">
        <div className="flex items-center mb-2">
          <StatusIndicator config={substanceConfig} />
          <span className="text-[15px] text-text-primary font-medium">
            {substanceConfig.label}
          </span>
        </div>
        {socialHistory.substanceUse.substances.length > 0 && (
          <p className="text-[13px] text-text-secondary ml-4 mb-1">
            Substances: {socialHistory.substanceUse.substances.join(', ')}
          </p>
        )}
        {socialHistory.substanceUse.ivDrugUse && (
          <p className="text-[13px] text-status-critical ml-4 mb-1">
            IV drug use history
          </p>
        )}
        {socialHistory.substanceUse.notes && (
          <p className="text-[13px] text-text-tertiary ml-4 mt-2 italic">
            {socialHistory.substanceUse.notes}
          </p>
        )}
      </InfoCard>

      {/* Occupation */}
      <InfoCard title="Occupation">
        <p className="text-[15px] text-text-primary font-medium mb-2">
          {socialHistory.occupation || 'Not specified'}
        </p>
        {socialHistory.occupationHazards.length > 0 && (
          <div className="mt-2">
            <p className="text-[13px] text-text-tertiary mb-1">Hazards:</p>
            <ul className="text-[13px] text-text-secondary ml-4">
              {socialHistory.occupationHazards.map((hazard, i) => (
                <li key={i}>- {hazard}</li>
              ))}
            </ul>
          </div>
        )}
      </InfoCard>

      {/* Living Situation */}
      <InfoCard title="Living Situation">
        <p className="text-[15px] text-text-primary mb-2">
          {socialHistory.livingSituation || 'Not specified'}
        </p>
        <p className="text-[13px] text-text-secondary">
          Marital status:{' '}
          {MARITAL_STATUS_LABELS[socialHistory.maritalStatus] || 'Unknown'}
        </p>
      </InfoCard>

      {/* Exercise & Diet */}
      <InfoCard title="Exercise & Diet">
        <div className="mb-3">
          <p className="text-[13px] text-text-tertiary mb-1">Exercise:</p>
          <div className="flex items-center">
            <StatusIndicator config={exerciseConfig} />
            <span className="text-[15px] text-text-primary font-medium">
              {exerciseConfig.label}
            </span>
          </div>
          {exerciseConfig.description && (
            <p className="text-[13px] text-text-secondary ml-4">
              {exerciseConfig.description}
            </p>
          )}
        </div>
        <div>
          <p className="text-[13px] text-text-tertiary mb-1">Diet:</p>
          <p className="text-[15px] text-text-primary font-medium">
            {DIET_TYPE_LABELS[socialHistory.diet] || 'Not specified'}
          </p>
          {socialHistory.dietNotes && (
            <p className="text-[13px] text-text-tertiary mt-1 italic">
              {socialHistory.dietNotes}
            </p>
          )}
        </div>
      </InfoCard>
    </div>
  );
}
