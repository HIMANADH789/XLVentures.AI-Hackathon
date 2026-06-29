"use client";

import * as React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("[ErrorBoundary]", error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex flex-col items-center justify-center rounded-xl border border-rose-500/20 bg-rose-500/5 p-12 text-center shadow-xs">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-rose-500/10 text-rose-500 mb-4">
            <AlertTriangle className="h-6 w-6 stroke-[1.5]" />
          </div>
          <h3 className="font-semibold text-base text-foreground mb-1">Something went wrong</h3>
          <p className="max-w-xs text-xs text-muted-foreground leading-normal mb-5">
            {this.state.error?.message || "An unexpected error occurred. Please try again."}
          </p>
          <Button
            onClick={this.handleRetry}
            variant="outline"
            size="sm"
            className="h-8 rounded-lg text-xs gap-1.5 border-rose-500/20 hover:bg-rose-500/10 hover:text-rose-600 dark:hover:text-rose-400 cursor-pointer"
          >
            <RefreshCw className="h-3 w-3" />
            <span>Retry</span>
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}
