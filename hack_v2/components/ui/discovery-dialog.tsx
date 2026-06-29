"use client";

import * as React from "react";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X, Globe, Loader2, Plus, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

function isValidUrl(str: string): boolean {
  try {
    const url = str.startsWith("http") ? new URL(str) : new URL(`https://${str}`);
    return url.hostname.includes(".");
  } catch {
    return false;
  }
}

function normalizeUrl(str: string): string {
  if (!str) return str;
  return str.startsWith("http") ? str : `https://${str}`;
}

interface DiscoveryDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (urls: string[]) => Promise<void>;
  isDiscovering?: boolean;
}

export function DiscoveryDialog({ open, onOpenChange, onSubmit, isDiscovering }: DiscoveryDialogProps) {
  const [urls, setUrls] = React.useState<string[]>([""]);

  React.useEffect(() => {
    if (open) {
      setUrls([""]);
    }
  }, [open]);

  const updateUrl = (index: number, value: string) => {
    const next = [...urls];
    next[index] = value;
    setUrls(next);
  };

  const addUrl = () => setUrls([...urls, ""]);

  const removeUrl = (index: number) => {
    if (urls.length <= 1) return;
    setUrls(urls.filter((_, i) => i !== index));
  };

  const validUrls = urls
    .map((u) => u.trim())
    .filter((u) => u !== "" && isValidUrl(u));

  const handleSubmit = async () => {
    if (validUrls.length === 0 || isDiscovering) return;
    await onSubmit(validUrls.map(normalizeUrl));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <DialogPrimitive.Root open={open} onOpenChange={onOpenChange}>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=open]:fade-in-0 data-[state=closed]:fade-out-0" />
        <DialogPrimitive.Content className="fixed left-1/2 top-1/2 z-50 w-full max-w-lg -translate-x-1/2 -translate-y-1/2 gap-4 border border-border bg-background p-6 shadow-2xl rounded-xl data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=open]:fade-in-0 data-[state=closed]:fade-out-0 data-[state=open]:zoom-in-95 data-[state=closed]:zoom-out-95 data-[state=open]:slide-in-from-top-2 data-[state=closed]:slide-out-to-top-2 duration-200">
          <DialogPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-hidden focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none cursor-pointer">
            <X className="h-4 w-4" />
            <span className="sr-only">Close</span>
          </DialogPrimitive.Close>

          <div className="flex items-center gap-3 mb-1">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-500 border border-indigo-500/20">
              <Globe className="h-4.5 w-4.5" />
            </div>
            <div>
              <DialogPrimitive.Title className="text-base font-bold tracking-tight text-foreground">
                Discover Companies
              </DialogPrimitive.Title>
              <DialogPrimitive.Description className="text-xs text-muted-foreground mt-0.5">
                Enter company website URLs to analyze buying triggers and generate prospect profiles.
              </DialogPrimitive.Description>
            </div>
          </div>

          <div className="space-y-2.5 mt-5">
            {urls.map((url, index) => (
              <div key={index} className="flex items-center gap-2">
                <div className="relative flex-1">
                  <Input
                    value={url}
                    onChange={(e) => updateUrl(index, e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="acme.ai or https://acme.ai"
                    className={cn(
                      "h-9 pr-8",
                      url.trim() !== "" && !isValidUrl(url.trim()) &&
                        "border-red-500/50 focus-visible:ring-red-500/30"
                    )}
                    disabled={isDiscovering}
                  />
                  {url.trim() !== "" && !isValidUrl(url.trim()) && (
                    <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] text-red-500 font-medium">
                      Invalid
                    </span>
                  )}
                </div>
                {urls.length > 1 && (
                  <button
                    onClick={() => removeUrl(index)}
                    className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-background text-muted-foreground hover:text-red-500 hover:border-red-500/30 hover:bg-red-500/5 transition-all cursor-pointer shrink-0"
                    disabled={isDiscovering}
                    title="Remove URL"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                )}
              </div>
            ))}

            {!isDiscovering && (
              <button
                onClick={addUrl}
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-500 hover:text-indigo-600 transition-colors cursor-pointer mt-1"
              >
                <Plus className="h-3.5 w-3.5" />
                Add another URL
              </button>
            )}
          </div>

          <div className="flex items-center justify-between gap-3 mt-6 pt-4 border-t border-border">
            <span className="text-[10px] text-muted-foreground">
              {validUrls.length > 0
                ? `${validUrls.length} URL${validUrls.length > 1 ? "s" : ""} ready for discovery`
                : "Enter at least one valid URL"}
            </span>
            <div className="flex items-center gap-2">
              <DialogPrimitive.Close asChild>
                <Button variant="outline" size="sm" className="h-9 text-xs cursor-pointer" disabled={isDiscovering}>
                  Cancel
                </Button>
              </DialogPrimitive.Close>
              <Button
                onClick={handleSubmit}
                size="sm"
                className="h-9 text-xs gap-1.5 bg-indigo-600 hover:bg-indigo-500 text-white cursor-pointer"
                disabled={validUrls.length === 0 || isDiscovering}
              >
                {isDiscovering ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    Discovering...
                  </>
                ) : (
                  <>
                    <Globe className="h-3.5 w-3.5" />
                    Run Discovery
                  </>
                )}
              </Button>
            </div>
          </div>
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
}
