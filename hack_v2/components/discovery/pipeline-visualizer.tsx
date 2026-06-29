"use client";

import * as React from "react";
import {
  Globe,
  Newspaper,
  Users,
  Zap,
  Target,
  Database,
  FileText,
  Lightbulb,
  Save,
  Check,
  Loader2,
  XCircle,
  Clock,
} from "lucide-react";
import { cn } from "@/lib/utils";

const STAGE_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  scraping: Globe,
  news_search: Newspaper,
  contact_finding: Users,
  trigger_extraction: Zap,
  icp_qualification: Target,
  enrichment: Database,
  summary: FileText,
  action_recommendation: Lightbulb,
  saving: Save,
  complete: Check,
};

const STAGE_LABELS: Record<string, string> = {
  scraping: "Website Scrape",
  news_search: "News Search",
  contact_finding: "Contact Finding",
  trigger_extraction: "Trigger Extraction",
  icp_qualification: "ICP Scoring",
  enrichment: "Enrichment",
  summary: "Summary",
  action_recommendation: "Action Plan",
  saving: "Saving Results",
  complete: "Complete",
};

export type StageStatus = "pending" | "running" | "completed" | "failed";

export interface StageData {
  id: string;
  label: string;
  status: StageStatus;
  duration: number | null;
  error?: string | null;
  phase?: number | null;
  icon?: React.ComponentType<{ className?: string }>;
}

export interface ActivityEntry {
  message: string;
  status: "completed" | "failed" | "running";
  timestamp: number;
}

export interface PipelineData {
  pipeline_id: string;
  url?: string;
  completed: boolean;
  error?: string | null;
  current_stage?: string | null;
  stages: StageData[];
  activities?: ActivityEntry[];
}

export interface PipelineVisualizerProps {
  pipelineId?: string | null;
  pipelineData?: PipelineData | null;
  pollingInterval?: number;
  className?: string;
  compact?: boolean;
  onStatusChange?: (data: PipelineData) => void;
}

export function PipelineVisualizer({
  pipelineId,
  pipelineData: initialData,
  pollingInterval = 800,
  className,
  compact,
  onStatusChange,
}: PipelineVisualizerProps) {
  const [pipeline, setPipeline] = React.useState<PipelineData | null>(
    initialData ?? null
  );
  const [error, setError] = React.useState<string | null>(null);

  const pollRef = React.useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchPipeline = React.useCallback(async () => {
    if (!pipelineId) return;
    try {
      const baseUrl =
        process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${baseUrl}/discover/pipeline/${pipelineId}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: PipelineData = await res.json();
      setPipeline(data);
      setError(null);
      onStatusChange?.(data);
      if (data.completed) {
        if (pollRef.current) clearInterval(pollRef.current);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to fetch pipeline");
    }
  }, [pipelineId]);

  React.useEffect(() => {
    if (!pipelineId || initialData?.completed) return;
    fetchPipeline();
    pollRef.current = setInterval(fetchPipeline, pollingInterval);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [pipelineId, fetchPipeline, pollingInterval, initialData?.completed]);

  if (!pipeline && !error) {
    return (
      <div className="flex items-center justify-center py-8 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin mr-2" />
        <span className="text-sm">Loading pipeline...</span>
      </div>
    );
  }

  if (error && !pipeline) {
    return (
      <div className="flex items-center justify-center py-8 text-rose-500 text-sm">
        <XCircle className="h-4 w-4 mr-2" />
        Failed to load pipeline: {error}
      </div>
    );
  }

  if (!pipeline) return null;

  const stages = pipeline.stages ?? [];
  const isRunning = !pipeline.completed && !pipeline.error;
  const currentStage = pipeline.current_stage;

  if (stages.length === 0) {
    return (
      <div className="flex items-center justify-center py-8 text-muted-foreground text-sm">
        No pipeline data available
      </div>
    );
  }

  if (compact) {
    const activities = pipeline.activities ?? [];
    const showRunning = isRunning && currentStage;
    const currentLabel = currentStage
      ? (STAGE_LABELS[currentStage] || currentStage)
      : "";
    return (
      <div className={cn("space-y-1.5", className)}>
        {/* Completed activities */}
        {activities.map((act, i) => (
          <div key={i} className="flex items-center gap-2 text-xs">
            {act.status === "completed" ? (
              <Check className="h-3.5 w-3.5 shrink-0 text-emerald-500" />
            ) : act.status === "failed" ? (
              <XCircle className="h-3.5 w-3.5 shrink-0 text-rose-500" />
            ) : (
              <Loader2 className="h-3.5 w-3.5 shrink-0 animate-spin text-indigo-500" />
            )}
            <span className="text-foreground">{act.message}</span>
          </div>
        ))}

        {/* Current running stage */}
        {showRunning && (
          <div className="flex items-center gap-2 text-xs">
            <Loader2 className="h-3.5 w-3.5 shrink-0 animate-spin text-indigo-500" />
            <span className="text-indigo-500 font-medium">{currentLabel}...</span>
          </div>
        )}

        {pipeline.error && (
          <div className="flex items-center gap-2 text-xs text-rose-500">
            <XCircle className="h-3.5 w-3.5 shrink-0" />
            {pipeline.error}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={cn("space-y-0", className)}>
      {pipeline.url && (
        <div className="text-xs text-muted-foreground mb-3 truncate">
          {pipeline.url}
        </div>
      )}
      <div className="relative">
        {/* Vertical connector line */}
        <div className="absolute left-[17px] top-4 bottom-4 w-px bg-border" />

        <div className="space-y-0">
          {stages.map((stage, index) => {
            const Icon = STAGE_ICONS[stage.id] || Clock;
            const isActive = stage.id === currentStage || stage.status === "running";
            const isLast = index === stages.length - 1;

            return (
              <div key={stage.id} className="relative flex items-start gap-3 pb-6 last:pb-0">
                {/* Icon circle */}
                <div
                  className={cn(
                    "relative z-10 flex h-[34px] w-[34px] shrink-0 items-center justify-center rounded-full border-2 transition-all duration-300",
                    stage.status === "completed" &&
                      "border-emerald-500 bg-emerald-500/10 text-emerald-500",
                    stage.status === "running" &&
                      "border-indigo-500 bg-indigo-500/10 text-indigo-500 shadow-[0_0_12px_rgba(99,102,241,0.3)]",
                    stage.status === "failed" &&
                      "border-rose-500 bg-rose-500/10 text-rose-500",
                    stage.status === "pending" &&
                      "border-border bg-muted text-muted-foreground"
                  )}
                >
                  {stage.status === "completed" ? (
                    <Check className="h-3.5 w-3.5" />
                  ) : stage.status === "running" ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : stage.status === "failed" ? (
                    <XCircle className="h-3.5 w-3.5" />
                  ) : (
                    <Icon className="h-3.5 w-3.5" />
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0 pt-1.5">
                  <div className="flex items-center gap-2">
                    <span
                      className={cn(
                        "text-sm font-semibold",
                        stage.status === "pending" && "text-muted-foreground",
                        stage.status === "running" && "text-indigo-500",
                        stage.status === "completed" && "text-emerald-600 dark:text-emerald-400",
                        stage.status === "failed" && "text-rose-500"
                      )}
                    >
                      {STAGE_LABELS[stage.id] || stage.label}
                    </span>
                    {stage.duration != null && (
                      <span className="text-[11px] tabular-nums text-muted-foreground">
                        {stage.duration.toFixed(1)}s
                      </span>
                    )}
                    {isActive && (
                      <span className="text-[10px] font-semibold text-indigo-500 bg-indigo-500/10 px-1.5 py-0.5 rounded-full">
                        IN PROGRESS
                      </span>
                    )}
                  </div>
                  {stage.error && (
                    <div className="text-xs text-rose-500 mt-0.5">{stage.error}</div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {pipeline.error && (
        <div className="mt-3 p-2 rounded-lg bg-rose-500/5 border border-rose-500/20 text-xs text-rose-500">
          Pipeline failed: {pipeline.error}
        </div>
      )}
    </div>
  );
}

function StageDot({
  status,
  size = "sm",
}: {
  status: StageStatus;
  size?: "sm" | "md";
}) {
  const sizeClass = size === "sm" ? "h-2 w-2" : "h-3 w-3";
  return (
    <span
      className={cn(
        "rounded-full shrink-0 transition-colors duration-300",
        sizeClass,
        status === "completed" && "bg-emerald-500",
        status === "running" && "bg-indigo-500 animate-pulse",
        status === "failed" && "bg-rose-500",
        status === "pending" && "bg-muted-foreground/30"
      )}
    />
  );
}
