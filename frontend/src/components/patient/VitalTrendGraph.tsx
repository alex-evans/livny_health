import { useMemo, useState } from 'react';
import type { VitalHistoryEntry, VitalStatus } from '../../types';
import { cn } from '../../utils/cn';

interface VitalTrendGraphProps {
  history: VitalHistoryEntry[];
  referenceRange: string;
  unit: string;
  height?: number;
  width?: number;
  className?: string;
}

interface ReferenceRangeBounds {
  min: number | null;
  max: number | null;
}

type TimeRange = '3mo' | '6mo' | '1yr' | 'all';

function parseReferenceRange(range: string): ReferenceRangeBounds {
  if (!range) return { min: null, max: null };

  const cleaned = range.trim();

  // Handle "< X" format
  const lessThanMatch = cleaned.match(/^<\s*([\d.]+)/);
  if (lessThanMatch) {
    return { min: null, max: parseFloat(lessThanMatch[1]) };
  }

  // Handle "> X" format
  const greaterThanMatch = cleaned.match(/^>\s*([\d.]+)/);
  if (greaterThanMatch) {
    return { min: parseFloat(greaterThanMatch[1]), max: null };
  }

  // Handle "X - Y" range format
  const rangeMatch = cleaned.match(/([\d.]+)\s*[-–]\s*([\d.]+)/);
  if (rangeMatch) {
    return { min: parseFloat(rangeMatch[1]), max: parseFloat(rangeMatch[2]) };
  }

  return { min: null, max: null };
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function getStatusColor(status: VitalStatus): string {
  switch (status) {
    case 'critical':
      return 'var(--color-critical)';
    case 'abnormal':
      return 'var(--color-warning)';
    default:
      return 'var(--color-success)';
  }
}

function filterByTimeRange(
  history: VitalHistoryEntry[],
  range: TimeRange
): VitalHistoryEntry[] {
  if (range === 'all') return history;

  const now = new Date();
  let cutoff: Date;

  switch (range) {
    case '3mo':
      cutoff = new Date(now.setMonth(now.getMonth() - 3));
      break;
    case '6mo':
      cutoff = new Date(now.setMonth(now.getMonth() - 6));
      break;
    case '1yr':
      cutoff = new Date(now.setFullYear(now.getFullYear() - 1));
      break;
    default:
      return history;
  }

  return history.filter((h) => new Date(h.recordedAt) >= cutoff);
}

export function VitalTrendGraph({
  history,
  referenceRange,
  unit,
  height = 200,
  width = 400,
  className,
}: VitalTrendGraphProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>('1yr');

  const filteredHistory = useMemo(
    () => filterByTimeRange(history, timeRange),
    [history, timeRange]
  );

  const chartData = useMemo(() => {
    // Sort by date (oldest first for chronological chart)
    const sorted = [...filteredHistory].sort(
      (a, b) =>
        new Date(a.recordedAt).getTime() - new Date(b.recordedAt).getTime()
    );

    if (sorted.length === 0) return null;

    // Get reference range bounds
    const refBounds = parseReferenceRange(referenceRange);

    // Calculate y-axis bounds
    const values = sorted.map((p) => p.value);
    let minY = Math.min(...values);
    let maxY = Math.max(...values);

    // Extend bounds to include reference range
    if (refBounds.min !== null) {
      minY = Math.min(minY, refBounds.min);
    }
    if (refBounds.max !== null) {
      maxY = Math.max(maxY, refBounds.max);
    }

    // Add 10% padding
    const yPadding = (maxY - minY) * 0.1 || 1;
    minY -= yPadding;
    maxY += yPadding;

    return {
      points: sorted,
      refBounds,
      minY,
      maxY,
    };
  }, [filteredHistory, referenceRange]);

  if (!chartData || chartData.points.length < 2) {
    return (
      <div className="flex flex-col items-center">
        <div className="flex gap-2 mb-4">
          {(['3mo', '6mo', '1yr', 'all'] as TimeRange[]).map((range) => (
            <button
              key={range}
              type="button"
              onClick={() => setTimeRange(range)}
              className={cn(
                'px-3 py-1 rounded text-[13px]',
                timeRange === range
                  ? 'bg-glacier-blue text-white'
                  : 'bg-frost/50 text-text-secondary hover:bg-frost'
              )}
            >
              {range === 'all' ? 'All' : range.toUpperCase()}
            </button>
          ))}
        </div>
        <div
          className={cn(
            'flex items-center justify-center text-text-tertiary text-[15px]',
            className
          )}
          style={{ height, width }}
        >
          Not enough data for trend chart
        </div>
      </div>
    );
  }

  const { points, refBounds, minY, maxY } = chartData;

  // Chart dimensions
  const padding = { top: 20, right: 50, bottom: 40, left: 50 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Scale functions
  const xScale = (index: number) =>
    padding.left + (index / (points.length - 1)) * chartWidth;
  const yScale = (value: number) =>
    padding.top + ((maxY - value) / (maxY - minY)) * chartHeight;

  // Generate path
  const linePath = points
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${xScale(i)} ${yScale(p.value)}`)
    .join(' ');

  // Y-axis ticks
  const yTickCount = 5;
  const yTicks = Array.from({ length: yTickCount }, (_, i) => {
    const value = minY + ((maxY - minY) / (yTickCount - 1)) * i;
    return { value, y: yScale(value) };
  });

  return (
    <div className="flex flex-col items-center">
      {/* Time range selector */}
      <div className="flex gap-2 mb-4">
        {(['3mo', '6mo', '1yr', 'all'] as TimeRange[]).map((range) => (
          <button
            key={range}
            type="button"
            onClick={() => setTimeRange(range)}
            className={cn(
              'px-3 py-1 rounded text-[13px]',
              timeRange === range
                ? 'bg-glacier-blue text-white'
                : 'bg-frost/50 text-text-secondary hover:bg-frost'
            )}
          >
            {range === 'all' ? 'All' : range.toUpperCase()}
          </button>
        ))}
      </div>

      <svg
        width={width}
        height={height}
        className={cn('font-sans', className)}
        role="img"
        aria-label={`Trend chart showing ${points.length} data points`}
      >
        {/* Reference range shading */}
        {(refBounds.min !== null || refBounds.max !== null) && (
          <rect
            x={padding.left}
            y={refBounds.max !== null ? yScale(refBounds.max) : padding.top}
            width={chartWidth}
            height={
              refBounds.min !== null && refBounds.max !== null
                ? yScale(refBounds.min) - yScale(refBounds.max)
                : refBounds.max !== null
                ? yScale(minY) - yScale(refBounds.max)
                : yScale(refBounds.min!) - padding.top
            }
            fill="var(--color-success)"
            opacity={0.1}
          />
        )}

        {/* Reference range lines */}
        {refBounds.max !== null && (
          <>
            <line
              x1={padding.left}
              x2={width - padding.right}
              y1={yScale(refBounds.max)}
              y2={yScale(refBounds.max)}
              stroke="var(--color-success)"
              strokeDasharray="4 2"
              strokeWidth={1}
            />
            <text
              x={width - padding.right + 4}
              y={yScale(refBounds.max)}
              fill="var(--color-text-tertiary)"
              fontSize={10}
              dominantBaseline="middle"
            >
              Max
            </text>
          </>
        )}
        {refBounds.min !== null && (
          <>
            <line
              x1={padding.left}
              x2={width - padding.right}
              y1={yScale(refBounds.min)}
              y2={yScale(refBounds.min)}
              stroke="var(--color-success)"
              strokeDasharray="4 2"
              strokeWidth={1}
            />
            <text
              x={width - padding.right + 4}
              y={yScale(refBounds.min)}
              fill="var(--color-text-tertiary)"
              fontSize={10}
              dominantBaseline="middle"
            >
              Min
            </text>
          </>
        )}

        {/* Y-axis */}
        <line
          x1={padding.left}
          x2={padding.left}
          y1={padding.top}
          y2={height - padding.bottom}
          stroke="var(--color-frost)"
          strokeWidth={1}
        />

        {/* Y-axis ticks and labels */}
        {yTicks.map(({ value, y }) => (
          <g key={value}>
            <line
              x1={padding.left - 4}
              x2={padding.left}
              y1={y}
              y2={y}
              stroke="var(--color-frost)"
              strokeWidth={1}
            />
            <text
              x={padding.left - 8}
              y={y}
              fill="var(--color-text-tertiary)"
              fontSize={10}
              textAnchor="end"
              dominantBaseline="middle"
            >
              {value.toFixed(1)}
            </text>
          </g>
        ))}

        {/* X-axis */}
        <line
          x1={padding.left}
          x2={width - padding.right}
          y1={height - padding.bottom}
          y2={height - padding.bottom}
          stroke="var(--color-frost)"
          strokeWidth={1}
        />

        {/* X-axis labels (dates) */}
        {points.map((p, i) => {
          // Show labels for first, last, and middle points
          const showLabel =
            i === 0 ||
            i === points.length - 1 ||
            (points.length > 3 && i === Math.floor(points.length / 2));
          if (!showLabel) return null;

          return (
            <text
              key={p.id}
              x={xScale(i)}
              y={height - padding.bottom + 16}
              fill="var(--color-text-tertiary)"
              fontSize={10}
              textAnchor="middle"
            >
              {formatDate(p.recordedAt)}
            </text>
          );
        })}

        {/* Trend line */}
        <path
          d={linePath}
          fill="none"
          stroke="var(--color-glacier-blue)"
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Data points */}
        {points.map((p, i) => (
          <g key={p.id}>
            <circle
              cx={xScale(i)}
              cy={yScale(p.value)}
              r={5}
              fill={getStatusColor(p.status)}
              stroke="white"
              strokeWidth={2}
            />
            {/* Hover area for tooltip */}
            <circle
              cx={xScale(i)}
              cy={yScale(p.value)}
              r={12}
              fill="transparent"
              className="cursor-pointer"
            >
              <title>{`${p.value} ${unit} (${formatDate(p.recordedAt)})`}</title>
            </circle>
          </g>
        ))}

        {/* Unit label */}
        <text
          x={padding.left - 35}
          y={height / 2}
          fill="var(--color-text-tertiary)"
          fontSize={10}
          textAnchor="middle"
          transform={`rotate(-90, ${padding.left - 35}, ${height / 2})`}
        >
          {unit}
        </text>
      </svg>
    </div>
  );
}
