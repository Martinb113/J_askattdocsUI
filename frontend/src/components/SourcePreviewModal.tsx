/**
 * Modal for previewing source details with copy and open functionality.
 */
import { useState } from 'react';
import { Modal } from './ui/Modal';
import { Button } from './ui/Button';
import { ExternalLink, Copy, Check } from 'lucide-react';
import { toast } from 'sonner';
import type { Source } from '@/types';

interface SourcePreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  source: Source | null;
  sourceNumber?: number;
}

export function SourcePreviewModal({
  isOpen,
  onClose,
  source,
  sourceNumber,
}: SourcePreviewModalProps) {
  const [copiedUrl, setCopiedUrl] = useState(false);
  const [copiedTitle, setCopiedTitle] = useState(false);

  if (!source) return null;

  const handleCopyUrl = async () => {
    try {
      await navigator.clipboard.writeText(source.url);
      setCopiedUrl(true);
      toast.success('URL copied to clipboard');
      setTimeout(() => setCopiedUrl(false), 2000);
    } catch (error) {
      toast.error('Failed to copy URL');
    }
  };

  const handleCopyTitle = async () => {
    try {
      await navigator.clipboard.writeText(source.title);
      setCopiedTitle(true);
      toast.success('Title copied to clipboard');
      setTimeout(() => setCopiedTitle(false), 2000);
    } catch (error) {
      toast.error('Failed to copy title');
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={sourceNumber ? `Source #${sourceNumber}` : 'Source Details'}
      size="lg"
    >
      <div className="space-y-6">
        {/* Title Section */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium text-gray-700">Title</label>
            <button
              onClick={handleCopyTitle}
              className="p-1.5 text-gray-400 hover:text-gray-600 bg-white rounded shadow-sm border border-gray-200"
              title="Copy title"
            >
              {copiedTitle ? (
                <Check className="w-4 h-4 text-green-600" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </button>
          </div>
          <p className="text-base text-gray-900 bg-gray-50 p-3 rounded-lg border border-gray-200">
            {source.title}
          </p>
        </div>

        {/* URL Section */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium text-gray-700">URL</label>
            <button
              onClick={handleCopyUrl}
              className="p-1.5 text-gray-400 hover:text-gray-600 bg-white rounded shadow-sm border border-gray-200"
              title="Copy URL"
            >
              {copiedUrl ? (
                <Check className="w-4 h-4 text-green-600" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </button>
          </div>
          <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-primary-600 hover:text-primary-700 hover:underline break-all bg-gray-50 p-3 rounded-lg border border-gray-200 block"
          >
            {source.url}
          </a>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
          <Button
            onClick={() => window.open(source.url, '_blank')}
            className="flex items-center"
          >
            <ExternalLink className="w-4 h-4 mr-2" />
            Open in New Tab
          </Button>
        </div>
      </div>
    </Modal>
  );
}
