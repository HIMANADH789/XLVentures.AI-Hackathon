"use client";

import * as React from "react";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X, Settings2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface EditIcpFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialValues?: {
    industry?: string;
    min_employees?: number;
    max_employees?: number;
    qualification_threshold?: number;
  };
  onSubmit: (criteria: {
    industry: string;
    min_employees: number;
    max_employees: number;
    qualification_threshold: number;
  }) => Promise<void>;
}

export function EditIcpForm({ open, onOpenChange, initialValues, onSubmit }: EditIcpFormProps) {
  const [industry, setIndustry] = React.useState(initialValues?.industry || "Software / AI / SaaS / Tech");
  const [minEmployees, setMinEmployees] = React.useState(initialValues?.min_employees || 10);
  const [maxEmployees, setMaxEmployees] = React.useState(initialValues?.max_employees || 0);
  const [threshold, setThreshold] = React.useState(initialValues?.qualification_threshold || 60);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  React.useEffect(() => {
    if (open) {
      setIndustry(initialValues?.industry || "Software / AI / SaaS / Tech");
      setMinEmployees(initialValues?.min_employees || 10);
      setMaxEmployees(initialValues?.max_employees || 0);
      setThreshold(initialValues?.qualification_threshold || 60);
    }
  }, [open, initialValues]);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      await onSubmit({
        industry: industry.trim(),
        min_employees: minEmployees,
        max_employees: maxEmployees,
        qualification_threshold: threshold,
      });
      onOpenChange(false);
    } catch {
      // Error handled upstream
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <DialogPrimitive.Root open={open} onOpenChange={onOpenChange}>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=open]:fade-in-0 data-[state=closed]:fade-out-0" />
        <DialogPrimitive.Content className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 gap-4 border border-border bg-background p-6 shadow-2xl rounded-xl data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=open]:fade-in-0 data-[state=closed]:fade-out-0 data-[state=open]:zoom-in-95 data-[state=closed]:zoom-out-95 data-[state=open]:slide-in-from-top-2 data-[state=closed]:slide-out-to-top-2 duration-200">
          <DialogPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-hidden focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none cursor-pointer">
            <X className="h-4 w-4" />
            <span className="sr-only">Close</span>
          </DialogPrimitive.Close>

          <div className="flex items-center gap-3 mb-1">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-500 border border-indigo-500/20">
              <Settings2 className="h-4.5 w-4.5" />
            </div>
            <div>
              <DialogPrimitive.Title className="text-base font-bold tracking-tight text-foreground">
                Edit ICP Criteria
              </DialogPrimitive.Title>
              <DialogPrimitive.Description className="text-xs text-muted-foreground mt-0.5">
                Adjust the qualification criteria and re-score this prospect.
              </DialogPrimitive.Description>
            </div>
          </div>

          <div className="space-y-4 mt-5">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Target Industry
              </label>
              <Input
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                placeholder="e.g. AI / SaaS / Tech"
                disabled={isSubmitting}
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Min Employees
                </label>
                <Input
                  type="number"
                  min={0}
                  value={minEmployees}
                  onChange={(e) => setMinEmployees(Number(e.target.value))}
                  disabled={isSubmitting}
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Max Employees
                </label>
                <Input
                  type="number"
                  min={0}
                  value={maxEmployees}
                  onChange={(e) => setMaxEmployees(Number(e.target.value))}
                  placeholder="0 = no limit"
                  disabled={isSubmitting}
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Qualification Threshold
              </label>
              <Input
                type="number"
                min={0}
                max={100}
                value={threshold}
                onChange={(e) => setThreshold(Number(e.target.value))}
                disabled={isSubmitting}
              />
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 mt-6 pt-4 border-t border-border">
            <DialogPrimitive.Close asChild>
              <Button variant="outline" size="sm" className="h-9 text-xs cursor-pointer" disabled={isSubmitting}>
                Cancel
              </Button>
            </DialogPrimitive.Close>
            <Button
              onClick={handleSubmit}
              size="sm"
              className="h-9 text-xs cursor-pointer"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Re-scoring..." : "Apply & Re-score"}
            </Button>
          </div>
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
}
