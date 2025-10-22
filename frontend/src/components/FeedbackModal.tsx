/**
 * Feedback modal for collecting user feedback with optional comment.
 */
import { useState } from 'react';
import { Modal } from './ui/Modal';
import { Button } from './ui/Button';
import { Textarea } from './ui/Textarea';
import { ThumbsUp, ThumbsDown } from 'lucide-react';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (rating: number, comment?: string) => void;
  feedbackType: 'positive' | 'negative' | null;
}

export function FeedbackModal({ isOpen, onClose, onSubmit, feedbackType }: FeedbackModalProps) {
  const [comment, setComment] = useState('');

  const handleSubmit = () => {
    const rating = feedbackType === 'positive' ? 5 : 1;
    onSubmit(rating, comment.trim() || undefined);
    setComment('');
    onClose();
  };

  const handleCancel = () => {
    setComment('');
    onClose();
  };

  if (!feedbackType) return null;

  const isPositive = feedbackType === 'positive';

  return (
    <Modal isOpen={isOpen} onClose={handleCancel} title="Provide Feedback" size="md">
      <div className="space-y-4">
        {/* Feedback Type Indicator */}
        <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200">
          {isPositive ? (
            <>
              <ThumbsUp className="w-6 h-6 text-green-600" />
              <div>
                <p className="font-medium text-gray-900">Positive Feedback</p>
                <p className="text-sm text-gray-600">This response was helpful</p>
              </div>
            </>
          ) : (
            <>
              <ThumbsDown className="w-6 h-6 text-red-600" />
              <div>
                <p className="font-medium text-gray-900">Negative Feedback</p>
                <p className="text-sm text-gray-600">This response needs improvement</p>
              </div>
            </>
          )}
        </div>

        {/* Optional Comment */}
        <div>
          <label htmlFor="feedback-comment" className="block text-sm font-medium text-gray-700 mb-2">
            Additional Comments (Optional)
          </label>
          <Textarea
            id="feedback-comment"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder={
              isPositive
                ? 'What did you like about this response?'
                : 'What could be improved?'
            }
            rows={4}
            className="resize-none"
            maxLength={1000}
          />
          <p className="mt-1 text-xs text-gray-500">{comment.length}/1000 characters</p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
          <Button variant="outline" onClick={handleCancel}>
            Cancel
          </Button>
          <Button onClick={handleSubmit}>
            Submit Feedback
          </Button>
        </div>
      </div>
    </Modal>
  );
}
