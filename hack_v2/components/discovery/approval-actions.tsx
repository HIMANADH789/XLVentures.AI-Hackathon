"use client";

import * as React from "react";
import { ThumbsUp, ThumbsDown, Settings2, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ApprovalActionsProps {
  companyId: string;
  isLoading: boolean;
  onApprove: () => void;
  onReject: () => void;
  onEditIcp: () => void;
}

export function ApprovalActions({ companyId, isLoading, onApprove, onReject, onEditIcp }: ApprovalActionsProps) {
  return (
    <div className="flex items-center gap-2">
      <Button
        onClick={onApprove}
        size="sm"
        className="h-8 gap-1.5 text-xs bg-emerald-600 hover:bg-emerald-500 text-white cursor-pointer"
        disabled={isLoading}
      >
        {isLoading ? (
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
        ) : (
          <ThumbsUp className="h-3.5 w-3.5" />
        )}
        Approve & Enrich
      </Button>
      <Button
        onClick={onReject}
        variant="outline"
        size="sm"
        className="h-8 gap-1.5 text-xs border-red-500/20 text-red-500 hover:bg-red-500/5 hover:border-red-500/30 cursor-pointer"
        disabled={isLoading}
      >
        <ThumbsDown className="h-3.5 w-3.5" />
        Reject
      </Button>
      <Button
        onClick={onEditIcp}
        variant="outline"
        size="sm"
        className="h-8 gap-1.5 text-xs cursor-pointer"
        disabled={isLoading}
      >
        <Settings2 className="h-3.5 w-3.5" />
        Edit ICP
      </Button>
    </div>
  );
}
