import { useMemo } from 'react';
import type { SparklinePoint, VitalStatus } from '../../types';
import { cn } from '../../utils/cn';

interface VitalSparklineProps {
  data: SparklinePoint[];
  width?: number;
  height?: number;
  className?: string;
  onClick?: () => void;
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

export function VitalSparkline({
  data,
  width = 60,
  height = 24,
  className,
  onClick,
}: VitalSparklineProps) {
  const chartData = useMemo(() => {
    if (data.length < 2) return null;

    const values = data.map((d) => d.value);
    const minVal = Math.min(...values);
    const maxVal = Math.max(...values);
    const range = maxVal - minVal || 1;

    // Add 10% padding
    const padding = range * 0.1;
    const minY = minVal - padding;
    const maxY = maxVal + padding;

    // Scale points to SVG coordinates
    const points = data.map((point, i) => ({
      x: (i / (data.length - 1)) * width,
      y: height - ((point.value - minY) / (maxY - minY)) * height,
      status: point.status,
      value: point.value,
    }));

    // Generate path
    const pathData = points
      .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`)
      .join(' ');

    // Get the status of the most recent point for line color
    const latestStatus = data[data.length - 1].status;

    return {
      points,
      pathData,
      latestStatus,
    };
  }, [data, width, height]);

  if (!chartData) {
    return (
      <div
        className={cn(
          'flex items-center justify-center text-text-tertiary text-[13px]',
          className
        )}
        style={{ width, height }}
      >
        --
      </div>
    );
  }

  const { points, pathData, latestStatus } = chartData;

  return (
    <svg
      width={width}
      height={height}
      className={cn(
        'cursor-pointer transition-opacity hover:opacity-80',
        className
      )}
      onClick={onClick}
      role="img"
      aria-label={`Sparkline chart with ${points.length} data points`}
    >
      {/* Trend line */}
      <path
        d={pathData}
        fill="none"
        stroke={getStatusColor(latestStatus)}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity={0.8}
      />

      {/* Data points - show first and last only to keep it clean */}
      {points.length > 0 && (
        <>
          <circle
            cx={points[0].x}
            cy={points[0].y}
            r={2}
            fill={getStatusColor(points[0].status)}
          />
          <circle
            cx={points[points.length - 1].x}
            cy={points[points.length - 1].y}
            r={2.5}
            fill={getStatusColor(points[points.length - 1].status)}
          />
        </>
      )}
    </svg>
  );
}
