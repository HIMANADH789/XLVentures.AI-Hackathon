import * as React from "react";
import { Inbox, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  title?: string;
  description?: string;
  onAction?: () => void;
  actionText?: string;
}

export function EmptyState({
  title = "No matches found",
  description = "Try adjusting your search keywords or clearing active filters to find what you are looking for.",
  onAction,
  actionText = "Reset Filters"
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border bg-card/20 p-12 text-center shadow-xs">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted/40 text-muted-foreground mb-4">
        <Inbox className="h-6 w-6 stroke-[1.5]" />
      </div>
      <h3 className="font-semibold text-base text-foreground mb-1">{title}</h3>
      <p className="max-w-xs text-xs text-muted-foreground leading-normal mb-5">
        {description}
      </p>
      {onAction && (
        <Button
          onClick={onAction}
          variant="outline"
          size="sm"
          className="h-8 rounded-lg text-xs gap-1.5 cursor-pointer"
        >
          <RotateCcw className="h-3 w-3" />
          <span>{actionText}</span>
        </Button>
      )}
    </div>
  );
}
