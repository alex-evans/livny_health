import { useState, useEffect } from 'react';
import type { SocialFamilyHistoryResponse } from '../../types';
import { getSocialFamilyHistory } from '../../api/socialFamilyHistoryApi';
import { cn } from '../../utils/cn';
import { SocialHistoryDisplay } from './SocialHistoryDisplay';
import { FamilyHistoryDisplay } from './FamilyHistoryDisplay';
import { RiskAssessmentDisplay } from './RiskAssessmentDisplay';

interface SocialFamilyHistorySectionProps {
  patientId: string;
  className?: string;
}

type TabType = 'social' | 'family' | 'risks';

function formatDate(dateString: string | null): string {
  if (!dateString) return 'Not reviewed';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

export function SocialFamilyHistorySection({
  patientId,
  className,
}: SocialFamilyHistorySectionProps) {
  const [data, setData] = useState<SocialFamilyHistoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('social');

  useEffect(() => {
    if (!patientId) return;

    setLoading(true);
    setError(null);

    getSocialFamilyHistory(patientId, { includeRiskAssessments: true })
      .then((response) => {
        setData(response);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load social/family history');
      })
      .finally(() => {
        setLoading(false);
      });
  }, [patientId]);

  const tabs: { id: TabType; label: string; count?: number }[] = [
    { id: 'social', label: 'Social History' },
    { id: 'family', label: 'Family History' },
    {
      id: 'risks',
      label: 'Risk Assessments',
      count: data?.riskAssessments?.length ?? 0,
    },
  ];

  const highRiskCount =
    data?.riskAssessments?.filter((r) => r.riskLevel === 'high').length ?? 0;

  return (
    <section className={cn('', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h2 className="text-[18px] font-semibold text-text-primary">
            Social & Family History
          </h2>
          {highRiskCount > 0 && (
            <span className="px-2 py-0.5 text-[12px] font-medium bg-status-critical/10 text-status-critical rounded-full">
              {highRiskCount} High Risk
            </span>
          )}
        </div>
        {data?.lastReviewed && (
          <span className="text-[13px] text-text-tertiary">
            Last reviewed: {formatDate(data.lastReviewed)}
          </span>
        )}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="text-text-tertiary text-[15px]">
            Loading history...
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="flex items-center justify-center py-8">
          <div className="text-status-critical text-[15px]">{error}</div>
        </div>
      )}

      {/* Content */}
      {!loading && !error && data && (
        <>
          {/* Tab Navigation */}
          <div className="flex gap-1 mb-6 border-b border-frost">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  'px-4 py-2 text-[15px] font-medium transition-colors relative',
                  'hover:text-glacier-blue',
                  activeTab === tab.id
                    ? 'text-glacier-blue'
                    : 'text-text-secondary'
                )}
              >
                <span className="flex items-center gap-2">
                  {tab.label}
                  {tab.count !== undefined && tab.count > 0 && (
                    <span
                      className={cn(
                        'px-1.5 py-0.5 text-[11px] rounded-full',
                        tab.id === 'risks' && highRiskCount > 0
                          ? 'bg-status-critical/10 text-status-critical'
                          : 'bg-frost text-text-secondary'
                      )}
                    >
                      {tab.count}
                    </span>
                  )}
                </span>
                {activeTab === tab.id && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-glacier-blue" />
                )}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="min-h-[300px]">
            {activeTab === 'social' && (
              <SocialHistoryDisplay socialHistory={data.socialHistory} />
            )}
            {activeTab === 'family' && (
              <FamilyHistoryDisplay familyHistory={data.familyHistory} />
            )}
            {activeTab === 'risks' && (
              <RiskAssessmentDisplay riskAssessments={data.riskAssessments} />
            )}
          </div>
        </>
      )}

      {/* Empty State */}
      {!loading &&
        !error &&
        (!data || (!data.socialHistory && !data.familyHistory)) && (
          <div className="text-text-tertiary text-[15px] py-8 text-center">
            No social or family history documented
          </div>
        )}
    </section>
  );
}
