"use client";

import * as React from "react";
import { Loader2, CheckCircle, XCircle, X, Globe } from "lucide-react";
import { cn } from "@/lib/utils";
import { PipelineVisualizer } from "@/components/discovery/pipeline-visualizer";

interface PipelineStatusBarProps {
  pipelineId: string | null;
  onDismiss?: () => void;
  onComplete?: () => void;
}

export function PipelineStatusBar({ pipelineId, onDismiss, onComplete }: PipelineStatusBarProps) {
  const [completed, setCompleted] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [url, setUrl] = React.useState<string>("");

  // Auto-dismiss 3s after completion
  React.useEffect(() => {
    if (!completed) return;
    const timer = setTimeout(() => onDismiss?.(), 3000);
    return () => clearTimeout(timer);
  }, [completed, onDismiss]);

  const handleStatusChange = React.useCallback(
    (data: { completed: boolean; error?: string | null; url?: string }) => {
      if (data.completed) {
        setCompleted(true);
        if (data.error) setError(data.error);
        onComplete?.();
      }
      if (data.url) setUrl(data.url);
    },
    [onComplete],
  );

  if (!pipelineId) return null;

  return (
    <div
      className={cn(
        "rounded-xl border shadow-xs transition-all duration-300",
        completed && !error
          ? "border-emerald-500/20 bg-emerald-500/5"
          : error
            ? "border-rose-500/20 bg-rose-500/5"
            : "border-indigo-500/20 bg-indigo-500/5",
      )}
    >
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-inherit/50">
        <div className="flex items-center gap-2.5">
          <div
            className={cn(
              "flex h-7 w-7 items-center justify-center rounded-lg",
              completed && !error && "bg-emerald-500/10 text-emerald-500",
              error && "bg-rose-500/10 text-rose-500",
              !completed && !error && "bg-indigo-500/10 text-indigo-500",
            )}
          >
            {completed && !error ? (
              <CheckCircle className="h-4 w-4" />
            ) : error ? (
              <XCircle className="h-4 w-4" />
            ) : (
              <Loader2 className="h-4 w-4 animate-spin" />
            )}
          </div>
          <div>
            <h4 className="text-sm font-semibold text-foreground">
              {completed && !error
                ? "Discovery Complete"
                : error
                  ? "Discovery Failed"
                  : "Discovery Pipeline Running"}
            </h4>
            {url && (
              <p className="text-[11px] text-muted-foreground truncate max-w-[300px]">{url}</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {completed && (
            <span className="text-[10px] font-semibold text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-full">
              DONE
            </span>
          )}
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="flex h-6 w-6 items-center justify-center rounded-md text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors cursor-pointer"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Pipeline stages (compact) */}
      <div className="px-4 py-3">
        <PipelineVisualizer pipelineId={pipelineId} compact onStatusChange={handleStatusChange} />
      </div>
    </div>
  );
}
