"use client";

import * as React from "react";
import { Navbar } from "@/components/layout/navbar";
import { StatsCards } from "@/components/dashboard/stats-cards";
import { LeadTable } from "@/components/table/lead-table";
import { CompanyDrawer } from "@/components/company/company-drawer";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { ErrorBoundary } from "@/components/ui/error-boundary";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useCompanies } from "@/hooks/use-companies";
import { Company } from "@/types/company";
import { apiService } from "@/services/api";
import { Search, SlidersHorizontal, RefreshCw, X } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { DiscoveryDialog } from "@/components/ui/discovery-dialog";
import { PipelineStatusBar } from "@/components/discovery/pipeline-status-bar";
import { PendingReviews } from "@/components/discovery/pending-reviews";
import { IcpSettingsPanel } from "@/components/settings/icp-settings-panel";

export default function DashboardPage() {
  const {
    companies,
    pendingReviews,
    filteredCompanies,
    uniqueIndustries,
    uniqueTriggers,
    isLoading,
    error,
    searchInput,
    setSearchInput,
    searchQuery,
    selectedIndustry,
    setSelectedIndustry,
    selectedTrigger,
    setSelectedTrigger,
    selectedQualified,
    setSelectedQualified,
    selectedScore,
    setSelectedScore,
    isDiscovering,
    approvalLoading,
    activePipelineId,
    clearActivePipeline,
    runDiscovery,
    approveCompany,
    rejectCompany,
    rescoreCompany,
    resetFilters,
    refetch
  } = useCompanies();

  // Focus reference for search input (global search command hotkey)
  const localSearchInputRef = React.useRef<HTMLInputElement>(null);
  
  // Selected company details state
  const [selectedCompany, setSelectedCompany] = React.useState<Company | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = React.useState<boolean>(false);
  const [isLoadingDetails, setIsLoadingDetails] = React.useState<boolean>(false);
  const [toast, setToast] = React.useState<{ message: string; type: "success" | "error" } | null>(null);
  
  // Discovery dialog state
  const [isDiscoveryOpen, setIsDiscoveryOpen] = React.useState<boolean>(false);
  const [isSettingsOpen, setIsSettingsOpen] = React.useState<boolean>(false);

  React.useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  // Focus search input when ⌘K or Ctrl+K is pressed
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        localSearchInputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Fetch full details (including contacts) on demand when clicking View
  const handleViewCompany = async (company: Company) => {
    setSelectedCompany(company);
    setIsDrawerOpen(true);
    setIsLoadingDetails(true);
    try {
      const details = await apiService.getCompanyById(company.id);
      setSelectedCompany(details);
    } catch (err) {
      console.error("Failed to load company details and contacts:", err);
      // Keep basic data on failure, contacts list will display empty/fallback
    } finally {
      setIsLoadingDetails(false);
    }
  };

  const handleGlobalSearchClick = () => {
    localSearchInputRef.current?.focus();
    localSearchInputRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  };

  const handleNavbarRunDiscovery = () => {
    setIsDiscoveryOpen(true);
  };

  const handleDiscoverySubmit = async (urls: string[]) => {
    setIsDiscoveryOpen(false);
    try {
      await runDiscovery(urls);
    } catch (err: any) {
      console.error("Discovery run error:", err);
      const errMsg = err?.response?.data?.detail || err?.message || "Unknown error occurred";
      setToast({ message: `Discovery failed: ${errMsg}`, type: "error" });
    }
  };

  const handlePipelineDismiss = () => {
    clearActivePipeline();
  };

  const handlePipelineComplete = () => {
    refetch();
    setToast({ message: "Discovery completed successfully.", type: "success" });
  };

  const hasActiveFilters = searchInput !== "" || selectedIndustry !== "all" || selectedTrigger !== "all" || selectedQualified !== "all" || selectedScore !== "all";

  return (
    <div className="flex-1 flex flex-col min-h-screen relative">
      {/* Toast Notification Alert Banner */}
      {toast && (
        <div
          className={`fixed top-4 right-4 z-50 flex items-center gap-3 p-4 rounded-xl border shadow-xl transition-all duration-300 animate-in slide-in-from-top-4 ${
            toast.type === "success"
              ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-500"
              : "bg-red-500/10 border-red-500/20 text-red-500"
          }`}
        >
          <span className="text-xs font-semibold">{toast.message}</span>
          <button
            onClick={() => setToast(null)}
            className="p-0.5 rounded-full hover:bg-muted/10 cursor-pointer"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      )}
      {/* Brand Header */}
      <Navbar
        onSearchClick={handleGlobalSearchClick}
        onRunDiscovery={handleNavbarRunDiscovery}
        onSettingsClick={() => setIsSettingsOpen(true)}
        isDiscovering={isDiscovering}
      />

      {/* Main Content Pane */}
      <main className="flex-1 mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8">
        
        {/* Dashboard Title Banner */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-1">
            <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl flex items-center gap-2">
              Prospect Discovery
              <Badge variant="trigger" className="h-5 rounded-md px-2 font-bold font-mono uppercase bg-indigo-500/20 text-indigo-400">
                Live API
              </Badge>
            </h1>
            <p className="text-xs text-muted-foreground font-medium">
              Analyze real-time buying triggers, employee growth tiers, and qualifying intents.
            </p>
          </div>
          
          <Button
            onClick={refetch}
            disabled={isLoading}
            variant="outline"
            size="sm"
            className="h-9 gap-1.5 self-start sm:self-auto text-xs rounded-lg border-border bg-background cursor-pointer"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
            <span>Sync Leads</span>
          </Button>
        </div>

        {/* Pipeline Status Bar — inline during discovery */}
        {activePipelineId && (
          <PipelineStatusBar
            pipelineId={activePipelineId}
            onDismiss={handlePipelineDismiss}
            onComplete={handlePipelineComplete}
          />
        )}

        <ErrorBoundary>
          {/* Aggregated Metrics Section */}
          {isLoading ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="rounded-xl border border-border bg-card p-6 shadow-xs space-y-4">
                  <div className="flex items-center justify-between">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-4 w-4 rounded-full" />
                  </div>
                  <div className="space-y-2">
                    <Skeleton className="h-7 w-12" />
                    <Skeleton className="h-3.5 w-32" />
                  </div>
                </div>
              ))}
            </div>
          ) : error ? (
            <div className="rounded-xl border border-destructive/20 bg-destructive/5 p-6 text-center text-xs text-destructive">
              Could not calculate business metrics due to connection error.
            </div>
          ) : (
            <StatsCards companies={filteredCompanies} />
          )}
        </ErrorBoundary>

        {/* Pending Reviews Section */}
        {!isLoading && !error && pendingReviews.length > 0 && (
          <PendingReviews
            companies={pendingReviews}
            approvalLoading={approvalLoading}
            onApprove={approveCompany}
            onReject={rejectCompany}
            onRescore={rescoreCompany}
          />
        )}

        {/* Search, Filter Bar and Query Controls */}
        <div className="flex flex-col gap-4">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            {/* Search Input Box */}
            <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  ref={localSearchInputRef}
                  type="text"
                  placeholder="Search by company, industry, or trigger..."
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  className="pl-9 pr-8 h-9 rounded-lg border-input placeholder:text-muted-foreground/70"
                />
                {searchInput && (
                  <button
                    onClick={() => setSearchInput("")}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 p-0.5 rounded-full hover:bg-muted text-muted-foreground hover:text-foreground cursor-pointer"
                  >
                    <X className="h-3 w-3" />
                  </button>
                )}
              </div>

            {/* Quick Filters Group */}
            <div className="flex flex-wrap items-center gap-2">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground mr-1">
                <SlidersHorizontal className="h-3.5 w-3.5" />
                <span className="max-sm:hidden">Filters:</span>
              </div>

              {/* Industry Selection Dropdown */}
              <select
                value={selectedIndustry}
                onChange={(e) => setSelectedIndustry(e.target.value)}
                className="h-9 rounded-lg border border-input bg-background px-3 py-1 text-xs shadow-xs focus:outline-hidden focus:ring-1 focus:ring-ring cursor-pointer text-muted-foreground hover:text-foreground font-medium"
              >
                <option value="all">All Industries</option>
                {uniqueIndustries.map((ind) => (
                  <option key={ind} value={ind.toLowerCase()}>
                    {ind}
                  </option>
                ))}
              </select>

              {/* Trigger Qualification Selector */}
              <select
                value={selectedTrigger}
                onChange={(e) => setSelectedTrigger(e.target.value)}
                className="h-9 rounded-lg border border-input bg-background px-3 py-1 text-xs shadow-xs focus:outline-hidden focus:ring-1 focus:ring-ring cursor-pointer text-muted-foreground hover:text-foreground font-medium text-ellipsis overflow-hidden"
              >
                <option value="all">All Triggers</option>
                {uniqueTriggers.map((trig) => (
                  <option key={trig} value={trig.toLowerCase()}>
                    {trig}
                  </option>
                ))}
              </select>

              {/* Qualification Status Selector */}
              <select
                value={selectedQualified}
                onChange={(e) => setSelectedQualified(e.target.value)}
                className="h-9 rounded-lg border border-input bg-background px-3 py-1 text-xs shadow-xs focus:outline-hidden focus:ring-1 focus:ring-ring cursor-pointer text-muted-foreground hover:text-foreground font-medium"
              >
                <option value="all">All Statuses</option>
                <option value="qualified">Qualified</option>
                <option value="unqualified">Unqualified</option>
              </select>

              {/* Score Selector */}
              <select
                value={selectedScore}
                onChange={(e) => setSelectedScore(e.target.value)}
                className="h-9 rounded-lg border border-input bg-background px-3 py-1 text-xs shadow-xs focus:outline-hidden focus:ring-1 focus:ring-ring cursor-pointer text-muted-foreground hover:text-foreground font-medium"
              >
                <option value="all">All Scores</option>
                <option value="high">High (85+)</option>
                <option value="medium">Medium (70-84)</option>
                <option value="low">Low (&lt;70)</option>
              </select>

              {/* Active Filter Clear button */}
              {hasActiveFilters && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={resetFilters}
                  className="h-9 text-xs rounded-lg text-indigo-500 hover:text-indigo-600 hover:bg-indigo-500/5 px-2.5 font-semibold cursor-pointer"
                >
                  Reset
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Lead Table / States Section */}
        <ErrorBoundary>
          {isLoading || isDiscovering ? (
            <div className="rounded-xl border border-border bg-card shadow-xs overflow-hidden">
              <div className="border-b border-border bg-muted/40 px-6 py-4 flex items-center justify-between">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Skeleton key={i} className={`h-4.5 ${i === 0 ? "w-28" : i === 1 ? "w-20" : i === 2 ? "w-32" : "w-16"}`} />
                ))}
              </div>
              <div className="divide-y divide-border px-6">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="py-4.5 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Skeleton className="h-8 w-8 rounded-full" />
                      <div className="space-y-1.5">
                        <Skeleton className="h-4 w-32" />
                        <Skeleton className="h-3 w-20" />
                      </div>
                    </div>
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-5 w-32 rounded-full" />
                    <Skeleton className="h-4 w-12" />
                    <Skeleton className="h-5 w-10 rounded-full" />
                  </div>
                ))}
              </div>
            </div>
          ) : error ? (
            <ErrorState onRetry={refetch} description={error} />
          ) : filteredCompanies.length === 0 ? (
            <EmptyState onAction={resetFilters} />
          ) : (
            <LeadTable
              data={filteredCompanies}
              onViewCompany={handleViewCompany}
            />
          )}
        </ErrorBoundary>
      </main>

      {/* Slide-out details drawer */}
      <CompanyDrawer
        company={selectedCompany}
        open={isDrawerOpen}
        onOpenChange={setIsDrawerOpen}
        isLoadingDetails={isLoadingDetails}
      />

      {/* Discovery modal dialog */}
      <DiscoveryDialog
        open={isDiscoveryOpen}
        onOpenChange={setIsDiscoveryOpen}
        onSubmit={handleDiscoverySubmit}
        isDiscovering={isDiscovering}
      />

      {/* Settings panel */}
      <IcpSettingsPanel
        open={isSettingsOpen}
        onOpenChange={setIsSettingsOpen}
      />
    </div>
  );
}
