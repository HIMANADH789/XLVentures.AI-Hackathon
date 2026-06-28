import * as React from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ErrorStateProps {
  title?: string;
  description?: string;
  onRetry?: () => void;
  retryText?: string;
}

export function ErrorState({
  title = "Failed to load data",
  description = "There was an error communicating with the ProspectIQ live service. Please check your network and try again.",
  onRetry,
  retryText = "Try Again"
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-rose-500/20 bg-rose-500/5 p-12 text-center shadow-xs">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-rose-500/10 text-rose-500 mb-4">
        <AlertCircle className="h-6 w-6 stroke-[1.5]" />
      </div>
      <h3 className="font-semibold text-base text-foreground mb-1">{title}</h3>
      <p className="max-w-xs text-xs text-muted-foreground leading-normal mb-5">
        {description}
      </p>
      {onRetry && (
        <Button
          onClick={onRetry}
          variant="outline"
          size="sm"
          className="h-8 rounded-lg text-xs gap-1.5 border-rose-500/20 hover:bg-rose-500/10 hover:text-rose-600 dark:hover:text-rose-400 cursor-pointer"
        >
          <RefreshCw className="h-3 w-3" />
          <span>{retryText}</span>
        </Button>
      )}
    </div>
  );
}
