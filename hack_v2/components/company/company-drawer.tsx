"use client";

import * as React from "react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription
} from "@/components/ui/sheet";
import { Company } from "@/types/company";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Building2,
  Users,
  Award,
  Globe,
  Mail,
  Linkedin,
  Sparkles,
  ExternalLink,
  Copy,
  Check,
  ShieldCheck
} from "lucide-react";

interface CompanyDrawerProps {
  company: Company | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  isLoadingDetails?: boolean;
}

export function CompanyDrawer({ company, open, onOpenChange, isLoadingDetails = false }: CompanyDrawerProps) {
  const [copiedEmailId, setCopiedEmailId] = React.useState<string | null>(null);

  if (!company && !isLoadingDetails) return null;

  const handleCopyEmail = (email: string, contactId: string) => {
    navigator.clipboard.writeText(email);
    setCopiedEmailId(contactId);
    setTimeout(() => setCopiedEmailId(null), 2000);
  };

  // Score Badge tier helper
  let scoreVariant: "success" | "warning" | "danger" = "success";
  if (company && company.score >= 85) scoreVariant = "success";
  else if (company && company.score >= 70) scoreVariant = "warning";
  else scoreVariant = "danger";

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="overflow-y-auto sm:max-w-md md:max-w-lg p-0">
        <div className="h-2 bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500" />
        
        {isLoadingDetails ? (
          <div className="p-6 space-y-6 animate-pulse">
            <div className="flex items-center gap-3 border-b border-border pb-5">
              <div className="h-11 w-11 rounded-xl bg-muted" />
              <div className="space-y-2 flex-1">
                <div className="h-5 w-40 bg-muted rounded" />
                <div className="h-3.5 w-24 bg-muted rounded" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="h-20 bg-muted rounded-xl" />
              <div className="h-20 bg-muted rounded-xl" />
            </div>
            <div className="space-y-2">
              <div className="h-4 w-28 bg-muted rounded" />
              <div className="h-20 bg-muted rounded-xl" />
            </div>
            <div className="border-t border-border" />
            <div className="space-y-3">
              <div className="h-4 w-24 bg-muted rounded" />
              <div className="h-24 bg-muted rounded-xl" />
              <div className="h-24 bg-muted rounded-xl" />
            </div>
          </div>
        ) : (
          company && (
            <div className="p-6 space-y-6">
              {/* Header Panel */}
              <SheetHeader className="space-y-3.5 border-b border-border pb-5">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-border bg-muted/40 text-muted-foreground shadow-xs">
                      <Building2 className="h-5 w-5" />
                    </div>
                    <div className="space-y-0.5">
                      <SheetTitle className="text-xl font-bold tracking-tight">
                        {company.company}
                      </SheetTitle>
                      {company.website ? (
                        <a
                          href={company.website.startsWith("http") ? company.website : `https://${company.website}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-xs text-indigo-500 hover:underline"
                        >
                          <Globe className="h-3 w-3" />
                          <span>{company.website.replace("https://", "").replace("http://", "")}</span>
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      ) : (
                        <span className="text-xs text-muted-foreground">No Website</span>
                      )}
                    </div>
                  </div>
                  <Badge variant={scoreVariant} className="text-sm font-mono font-bold px-3 py-1">
                    Score {company.score}
                  </Badge>
                </div>
                <SheetDescription className="hidden">
                  Detailed view for {company.company}
                </SheetDescription>
              </SheetHeader>

              {/* Quick Metrics Cards */}
              <div className="grid grid-cols-2 gap-3">
                <Card className="bg-muted/10 border-border/80">
                  <CardContent className="p-3.5 flex flex-col justify-center">
                    <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider mb-1.5 flex items-center gap-1">
                      <Users className="h-3 w-3" /> Industry & Size
                    </span>
                    <span className="text-xs font-semibold text-foreground truncate">
                      {company.industry}
                    </span>
                    <span className="text-[11px] text-muted-foreground mt-0.5 font-medium">
                      {company.employees ? company.employees.toLocaleString() : "N/A"} employees
                    </span>
                  </CardContent>
                </Card>

                <Card className="bg-muted/10 border-border/80">
                  <CardContent className="p-3.5 flex flex-col justify-center">
                    <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider mb-1.5 flex items-center gap-1">
                      <Award className="h-3 w-3" /> Qualification Event
                    </span>
                    <Badge variant="trigger" className="w-fit text-[10px] py-0 uppercase max-w-full truncate">
                      {company.trigger || "none"}
                    </Badge>
                    <span className="text-[11px] text-muted-foreground mt-1 font-medium">
                      Active buying signals
                    </span>
                  </CardContent>
                </Card>
              </div>

              {/* AI Intent Summary Insight Card */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5 select-none">
                  <Sparkles className="h-3.5 w-3.5 text-indigo-500 animate-pulse" />
                  <span>ProspectIQ AI Summary</span>
                </h4>
                <Card className="border border-indigo-500/10 bg-indigo-500/5 dark:bg-indigo-500/5">
                  <CardContent className="p-4">
                    <p className="text-xs text-muted-foreground dark:text-slate-300 leading-relaxed font-medium">
                      {company.summary || "No automated summary available."}
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Pipeline Metadata Card */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5 select-none">
                  <ShieldCheck className="h-3.5 w-3.5 text-indigo-500" />
                  <span>Pipeline Details</span>
                </h4>
                <Card className="border border-border bg-card">
                  <CardContent className="p-3 grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
                    <div>
                      <span className="text-muted-foreground block">Trigger Source</span>
                      <span className="font-semibold text-foreground capitalize">{company.trigger_source || "Manual"}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block">Trigger Confidence</span>
                      <span className="font-semibold text-foreground">
                        {company.trigger_confidence !== null && company.trigger_confidence !== undefined
                          ? `${(company.trigger_confidence * 100).toFixed(0)}%`
                          : "N/A"}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block">Discovery Status</span>
                      <span className="font-semibold text-foreground capitalize">{company.status || "N/A"}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block">Website Summary</span>
                      <span className="font-semibold text-foreground text-[10px] uppercase">
                        {company.firecrawl_used ? "Firecrawl Crawl" : "HTTP Fallback"}
                      </span>
                    </div>
                    <div className="col-span-2">
                      <span className="text-muted-foreground block">Last Updated</span>
                      <span className="font-semibold text-foreground text-[11px]">
                        {company.discovery_timestamp || company.created_at
                          ? new Date(company.discovery_timestamp || company.created_at!).toLocaleString()
                          : "N/A"}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {company.news_headlines && (
                <div className="space-y-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5 select-none">
                    <Building2 className="h-3.5 w-3.5 text-indigo-500" />
                    <span>Recent News (90 Days)</span>
                  </h4>
                  <Card className="border border-border bg-card">
                    <CardContent className="p-3.5 space-y-2">
                      {company.news_headlines.split(" | ").map((headline, idx) => (
                        <div key={idx} className="text-xs border-l-2 border-indigo-500 pl-2.5 py-0.5">
                          <p className="font-semibold text-foreground leading-normal">{headline}</p>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                </div>
              )}

              {/* Divider */}
              <div className="border-t border-border" />

              {/* Decision Makers List */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground select-none">
                  Key Contacts ({company.contacts?.length || 0})
                </h4>
                
                <div className="space-y-3">
                  {company.contacts && company.contacts.length > 0 ? (
                    company.contacts.map((contact) => (
                      <Card
                        key={contact.id}
                        className="hover:border-border/80 hover:bg-muted/10 transition-all duration-200"
                      >
                        <CardContent className="p-4 flex items-center justify-between">
                          <div className="space-y-1">
                            <span className="text-sm font-semibold text-foreground block">
                              {contact.name}
                            </span>
                            <span className="text-xs text-muted-foreground block font-medium">
                              {contact.role || "Role N/A"}
                            </span>
                            {contact.source && (
                              <span className="text-[10px] text-indigo-500 dark:text-indigo-400 font-semibold block uppercase">
                                Source: {contact.source}
                              </span>
                            )}
                            
                            {/* Interactive Email Copier */}
                            {contact.email && (
                              <div className="flex items-center gap-2 mt-2">
                                <a
                                  href={`mailto:${contact.email}`}
                                  className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-indigo-500 font-medium"
                                >
                                  <Mail className="h-3 w-3" />
                                  <span className="truncate max-w-[180px] sm:max-w-xs">{contact.email}</span>
                                </a>
                                <button
                                  onClick={() => handleCopyEmail(contact.email!, contact.id)}
                                  className="p-1 rounded-sm text-muted-foreground hover:text-foreground hover:bg-muted cursor-pointer transition-colors"
                                  title="Copy Email"
                                >
                                  {copiedEmailId === contact.id ? (
                                    <Check className="h-3 w-3 text-emerald-500" />
                                  ) : (
                                    <Copy className="h-3 w-3" />
                                  )}
                                </button>
                              </div>
                            )}
                          </div>

                          {/* LinkedIn Button Link */}
                          {contact.linkedin && (
                            <a
                              href={contact.linkedin.startsWith("http") ? contact.linkedin : `https://${contact.linkedin}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-background text-muted-foreground hover:text-[#0077B5] hover:border-[#0077B5]/30 hover:bg-[#0077B5]/5 transition-all shadow-xs cursor-pointer"
                              title="LinkedIn Profile"
                            >
                              <Linkedin className="h-4 w-4 fill-current stroke-0" />
                            </a>
                          )}
                        </CardContent>
                      </Card>
                    ))
                  ) : (
                    <div className="text-xs text-muted-foreground italic text-center p-4 border border-dashed border-border rounded-xl">
                      No verified contacts found.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )
        )}
      </SheetContent>
    </Sheet>
  );
}
