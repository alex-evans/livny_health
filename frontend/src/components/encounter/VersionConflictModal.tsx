import { useState } from 'react';
import { cn } from '../../utils/cn';

interface VersionConflictModalProps {
  isOpen: boolean;
  myContent: string;
  serverContent: string;
  serverVersion: number;
  onUseMine: () => void;
  onUseServer: () => void;
  onClose: () => void;
}

export function VersionConflictModal({
  isOpen,
  myContent,
  serverContent,
  serverVersion,
  onUseMine,
  onUseServer,
  onClose,
}: VersionConflictModalProps) {
  const [showDiff, setShowDiff] = useState(false);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-deep-ice/50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-card max-w-2xl w-full mx-4 max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="px-comfortable py-normal border-b border-frost">
          <h2 className="text-[18px] font-semibold text-text-primary">
            Note Conflict Detected
          </h2>
          <p className="text-[14px] text-text-secondary mt-1">
            Someone else edited this note while you were working.
            Choose which version to keep.
          </p>
        </div>

        {/* Content */}
        <div className="px-comfortable py-normal max-h-[50vh] overflow-y-auto">
          {!showDiff ? (
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[14px] font-medium text-text-primary">
                    Your version
                  </span>
                  <span className="text-[12px] text-text-tertiary">
                    {countWords(myContent)} words
                  </span>
                </div>
                <div className="bg-frost/30 rounded-lg p-3 text-[14px] text-text-secondary max-h-40 overflow-y-auto">
                  {myContent || <span className="text-text-tertiary italic">Empty</span>}
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[14px] font-medium text-text-primary">
                    Server version (v{serverVersion})
                  </span>
                  <span className="text-[12px] text-text-tertiary">
                    {countWords(serverContent)} words
                  </span>
                </div>
                <div className="bg-frost/30 rounded-lg p-3 text-[14px] text-text-secondary max-h-40 overflow-y-auto">
                  {serverContent || <span className="text-text-tertiary italic">Empty</span>}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-frost/30 rounded-lg p-3">
              <DiffView myContent={myContent} serverContent={serverContent} />
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-comfortable py-normal border-t border-frost flex items-center justify-between">
          <button
            onClick={() => setShowDiff(!showDiff)}
            className="text-[14px] text-glacier-blue hover:underline"
          >
            {showDiff ? 'Hide diff' : 'View diff'}
          </button>

          <div className="flex gap-3">
            <button
              onClick={onUseServer}
              className={cn(
                'px-4 py-2 text-[14px] rounded',
                'border border-frost text-text-secondary',
                'hover:bg-frost/50 transition-colors'
              )}
            >
              Use server version
            </button>
            <button
              onClick={onUseMine}
              className={cn(
                'px-4 py-2 text-[14px] rounded',
                'bg-glacier-blue text-white',
                'hover:bg-glacier-blue/90 transition-colors'
              )}
            >
              Keep my version
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function DiffView({
  myContent,
  serverContent,
}: {
  myContent: string;
  serverContent: string;
}) {
  // Simple line-by-line diff
  const myLines = myContent.split('\n');
  const serverLines = serverContent.split('\n');
  const maxLines = Math.max(myLines.length, serverLines.length);

  return (
    <div className="text-[13px] font-mono">
      <div className="grid grid-cols-2 gap-2 mb-2">
        <div className="text-text-tertiary">Your version</div>
        <div className="text-text-tertiary">Server version</div>
      </div>
      {Array.from({ length: maxLines }).map((_, i) => {
        const myLine = myLines[i] || '';
        const serverLine = serverLines[i] || '';
        const isDifferent = myLine !== serverLine;

        return (
          <div key={i} className="grid grid-cols-2 gap-2">
            <div
              className={cn(
                'py-0.5 px-1 rounded',
                isDifferent && myLine ? 'bg-status-normal/20' : ''
              )}
            >
              {myLine || <span className="text-text-tertiary">&nbsp;</span>}
            </div>
            <div
              className={cn(
                'py-0.5 px-1 rounded',
                isDifferent && serverLine ? 'bg-status-abnormal/20' : ''
              )}
            >
              {serverLine || <span className="text-text-tertiary">&nbsp;</span>}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function countWords(text: string): number {
  if (!text.trim()) return 0;
  return text.trim().split(/\s+/).length;
}
