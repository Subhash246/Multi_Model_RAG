import { FileText, X } from "lucide-react";
import type { Attachment } from "../../lib/types";

interface Props {
  attachment: Attachment;
  onRemove?: () => void;
}

export function AttachmentChip({ attachment, onRemove }: Props) {
  return (
    <div
      className="flex items-center gap-1.5 rounded-lg border border-border-light dark:border-border-dark
                 bg-surface-light dark:bg-surface-dark px-2.5 py-1.5 text-xs"
    >
      <FileText size={13} className="shrink-0 text-muted-light dark:text-muted-dark" />
      <span className="max-w-[140px] truncate">{attachment.filename}</span>
      {onRemove && (
        <button
          onClick={onRemove}
          aria-label={`Remove ${attachment.filename}`}
          className="ml-0.5 text-muted-light dark:text-muted-dark hover:text-ink-light dark:hover:text-ink-dark"
        >
          <X size={12} />
        </button>
      )}
    </div>
  );
}
