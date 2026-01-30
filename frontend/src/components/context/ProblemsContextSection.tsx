import { cn } from '../../utils/cn';
import type { EnrichedContextProblem } from '../../types';

interface ProblemsContextSectionProps {
  problems: EnrichedContextProblem[];
}

export function ProblemsContextSection({ problems }: ProblemsContextSectionProps) {
  if (problems.length === 0) {
    return (
      <p className="text-[13px] text-text-tertiary">No active problems</p>
    );
  }

  // Separate primary/critical problems from others
  const primaryProblems = problems.filter((p) => p.isPrimary);
  const otherProblems = problems.filter((p) => !p.isPrimary);

  return (
    <div className="space-y-2">
      {primaryProblems.map((problem) => (
        <ProblemItem key={problem.id} problem={problem} isPrimary />
      ))}
      {otherProblems.slice(0, 5).map((problem) => (
        <ProblemItem key={problem.id} problem={problem} />
      ))}
      {otherProblems.length > 5 && (
        <p className="text-[12px] text-glacier-blue">
          +{otherProblems.length - 5} more problems
        </p>
      )}
    </div>
  );
}

function ProblemItem({
  problem,
  isPrimary = false,
}: {
  problem: EnrichedContextProblem;
  isPrimary?: boolean;
}) {
  return (
    <div className="flex items-start gap-2">
      {isPrimary && (
        <span className="mt-1 w-2 h-2 rounded-full bg-status-critical flex-shrink-0" />
      )}
      <div className={cn(!isPrimary && 'ml-4')}>
        <div className="flex items-center gap-2">
          <span className="text-[14px] text-text-primary">{problem.description}</span>
          {problem.type === 'acute' && (
            <span className="text-[10px] font-medium uppercase px-1.5 py-0.5 rounded bg-status-abnormal/10 text-status-abnormal">
              Acute
            </span>
          )}
        </div>
        <div className="text-[12px] text-text-tertiary">
          {problem.icd10Code}
        </div>
      </div>
    </div>
  );
}
