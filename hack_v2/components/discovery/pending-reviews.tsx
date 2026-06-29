"use client";

import * as React from "react";
import { Clock, Building2, Target, Users, Sparkles, AlertCircle } from "lucide-react";
import { Company } from "@/types/company";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { ApprovalActions } from "./approval-actions";
import { EditIcpForm } from "./edit-icp-form";

interface PendingReviewsProps {
  companies: Company[];
  approvalLoading: string | null;
  onApprove: (id: string) => Promise<void>;
  onReject: (id: string) => Promise<void>;
  onRescore: (id: string, criteria: Record<string, any>) => Promise<void>;
}

export function PendingReviews({ companies, approvalLoading, onApprove, onReject, onRescore }: PendingReviewsProps) {
  const [editIcpCompany, setEditIcpCompany] = React.useState<Company | null>(null);

  if (companies.length === 0) return null;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <div className="flex h-6 w-6 items-center justify-center rounded-md bg-amber-500/10 text-amber-500 border border-amber-500/20">
          <Clock className="h-3.5 w-3.5" />
        </div>
        <h2 className="text-sm font-bold tracking-tight text-foreground">
          Pending Review ({companies.length})
        </h2>
      </div>

      <div className="grid gap-3">
        {companies.map((company) => (
          <PendingReviewCard
            key={company.id}
            company={company}
            isLoading={approvalLoading === company.id}
            onApprove={() => onApprove(company.id)}
            onReject={() => onReject(company.id)}
            onEditIcp={() => setEditIcpCompany(company)}
          />
        ))}
      </div>

      <EditIcpForm
        open={editIcpCompany !== null}
        onOpenChange={(open) => { if (!open) setEditIcpCompany(null); }}
        initialValues={{
          industry: editIcpCompany?.industry || undefined,
          min_employees: 10,
          qualification_threshold: 60,
        }}
        onSubmit={async (criteria) => {
          if (editIcpCompany) {
            await onRescore(editIcpCompany.id, criteria);
          }
        }}
      />
    </div>
  );
}

interface PendingReviewCardProps {
  company: Company;
  isLoading: boolean;
  onApprove: () => void;
  onReject: () => void;
  onEditIcp: () => void;
}

function PendingReviewCard({ company, isLoading, onApprove, onReject, onEditIcp }: PendingReviewCardProps) {
  const score = company.score;
  const triggerEvents = company.trigger_events || [];
  const hasTriggers = triggerEvents.length > 0;

  return (
    <Card className="border-amber-500/15 bg-amber-500/[0.02] hover:border-amber-500/25 transition-colors">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3 min-w-0">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-border bg-muted/40 text-muted-foreground">
              <Building2 className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="text-sm font-bold text-foreground truncate">
                  {company.company}
                </h3>
                <Badge variant="trigger" className="text-[10px] uppercase">
                  Score {score}
                </Badge>
              </div>
              {company.website && (
                <p className="text-[11px] text-muted-foreground truncate mt-0.5">
                  {company.website.replace("https://", "").replace("http://", "")}
                </p>
              )}
            </div>
          </div>

          <ApprovalActions
            companyId={company.id}
            isLoading={isLoading}
            onApprove={onApprove}
            onReject={onReject}
            onEditIcp={onEditIcp}
          />
        </div>

        {/* Score breakdown and trigger events */}
        <div className="mt-3 flex flex-wrap items-center gap-3">
          {/* Industry & employees */}
          <div className="flex items-center gap-1.5 text-[11px] font-medium text-muted-foreground bg-muted/30 border border-border px-2 py-1 rounded-md">
            <Target className="h-3 w-3" />
            <span>{company.industry}</span>
          </div>
          {company.employees && (
            <div className="flex items-center gap-1.5 text-[11px] font-medium text-muted-foreground bg-muted/30 border border-border px-2 py-1 rounded-md">
              <Users className="h-3 w-3" />
              <span>{company.employees.toLocaleString()} employees</span>
            </div>
          )}

          {/* Score breakdown */}
          <div className="flex items-center gap-1 text-[10px] font-mono text-muted-foreground">
            <span className="px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-500 font-semibold">
              T:{company.trigger_score ?? "?"}/50
            </span>
            <span className="px-1.5 py-0.5 rounded bg-green-500/10 text-green-500 font-semibold">
              I:{company.industry_score ?? "?"}/30
            </span>
            <span className="px-1.5 py-0.5 rounded bg-orange-500/10 text-orange-500 font-semibold">
              E:{company.employee_score ?? "?"}/20
            </span>
          </div>
        </div>

        {/* Trigger events */}
        {hasTriggers && (
          <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
            <Sparkles className="h-3 w-3 text-indigo-500 shrink-0" />
            {triggerEvents.map((t, i) => (
              <Badge key={i} variant="trigger" className="text-[10px] uppercase">
                {t.trigger_type}
                {t.confidence !== undefined && (
                  <span className="ml-1 opacity-60">{(t.confidence * 100).toFixed(0)}%</span>
                )}
              </Badge>
            ))}
          </div>
        )}

        {/* Error summary if score is low */}
        {!company.qualified && (
          <div className="mt-2.5 flex items-center gap-1.5 text-[11px] text-amber-500 font-medium">
            <AlertCircle className="h-3 w-3" />
            <span>Below qualification threshold — review before approving</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
