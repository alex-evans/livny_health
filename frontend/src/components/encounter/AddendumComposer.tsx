import { useState, useCallback } from 'react';
import { cn } from '../../utils/cn';

interface AddendumComposerProps {
  isOpen: boolean;
  onSubmit: (content: string, reason: string) => Promise<void>;
  onClose: () => void;
}

export function AddendumComposer({
  isOpen,
  onSubmit,
  onClose,
}: AddendumComposerProps) {
  const [content, setContent] = useState('');
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback(async () => {
    if (!content.trim()) {
      setError('Please enter addendum content');
      return;
    }
    if (!reason.trim()) {
      setError('Please enter a reason for the addendum');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await onSubmit(content.trim(), reason.trim());
      setContent('');
      setReason('');
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create addendum');
    } finally {
      setIsSubmitting(false);
    }
  }, [content, reason, onSubmit, onClose]);

  const handleClose = useCallback(() => {
    if (!isSubmitting) {
      setContent('');
      setReason('');
      setError(null);
      onClose();
    }
  }, [isSubmitting, onClose]);

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-deep-ice/50"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-card-hover w-full max-w-lg mx-4">
        {/* Header */}
        <div className="flex items-center justify-between px-comfortable py-normal border-b border-frost">
          <h2 className="text-[18px] font-semibold text-text-primary">
            Add Addendum
          </h2>
          <button
            onClick={handleClose}
            disabled={isSubmitting}
            className="p-2 text-text-secondary hover:text-text-primary hover:bg-frost/50 rounded transition-colors"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="px-comfortable py-normal">
          <p className="text-[13px] text-text-secondary mb-normal">
            Add additional information to this signed encounter. The original
            note will remain unchanged, and the addendum will be appended with
            your name and timestamp.
          </p>

          {/* Reason field */}
          <div className="mb-normal">
            <label
              htmlFor="addendum-reason"
              className="block text-[13px] font-medium text-text-primary mb-tight"
            >
              Reason for Addendum
            </label>
            <input
              id="addendum-reason"
              type="text"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              disabled={isSubmitting}
              placeholder="e.g., Lab results received, Patient follow-up"
              className={cn(
                'w-full px-3 py-2 text-[15px] border border-arctic rounded-md',
                'focus:outline-none focus:border-glacier-blue focus:ring-[3px] focus:ring-glacier-blue/10',
                'disabled:bg-frost disabled:cursor-not-allowed'
              )}
            />
          </div>

          {/* Content field */}
          <div className="mb-normal">
            <label
              htmlFor="addendum-content"
              className="block text-[13px] font-medium text-text-primary mb-tight"
            >
              Addendum Content
            </label>
            <textarea
              id="addendum-content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              disabled={isSubmitting}
              placeholder="Enter the addendum text..."
              rows={6}
              className={cn(
                'w-full px-3 py-2 text-[15px] border border-arctic rounded-md resize-none',
                'focus:outline-none focus:border-glacier-blue focus:ring-[3px] focus:ring-glacier-blue/10',
                'disabled:bg-frost disabled:cursor-not-allowed'
              )}
            />
          </div>

          {/* Error */}
          {error && (
            <div className="mb-normal p-3 bg-[#FADBD8] rounded-md">
              <p className="text-[13px] text-critical">{error}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 px-comfortable py-normal border-t border-frost">
          <button
            onClick={handleClose}
            disabled={isSubmitting}
            className={cn(
              'px-4 py-2 text-[13px] font-medium rounded-md transition-colors',
              'border border-arctic text-text-primary',
              'hover:bg-frost',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={isSubmitting || !content.trim() || !reason.trim()}
            className={cn(
              'px-4 py-2 text-[13px] font-medium rounded-md transition-colors',
              'bg-glacier-blue text-white',
              'hover:bg-deep-ice',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            {isSubmitting ? 'Saving...' : 'Add Addendum'}
          </button>
        </div>
      </div>
    </div>
  );
}
