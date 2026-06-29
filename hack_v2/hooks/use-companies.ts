"use client";

import * as React from "react";
import { Company } from "@/types/company";
import { apiService } from "@/services/api";
import { useDebounce } from "@/hooks/use-debounce";

const SEARCH_DEBOUNCE_MS = 200;
const URL_SYNC_DEBOUNCE_MS = 400;

/** Read initial filter values from URL search params on mount. */
function getInitialFilters(): { q: string; industry: string; trigger: string; qualified: string; score: string } {
  if (typeof window === "undefined") {
    return { q: "", industry: "all", trigger: "all", qualified: "all", score: "all" };
  }
  const params = new URLSearchParams(window.location.search);
  return {
    q: params.get("q") || "",
    industry: params.get("industry") || "all",
    trigger: params.get("trigger") || "all",
    qualified: params.get("qualified") || "all",
    score: params.get("score") || "all",
  };
}

/** Replace current URL search params without pushing history entry. */
function syncUrlParams(params: Record<string, string | undefined>) {
  if (typeof window === "undefined") return;
  const url = new URL(window.location.href);
  url.search = "";
  for (const [key, value] of Object.entries(params)) {
    if (value && value !== "all") {
      url.searchParams.set(key, value);
    }
  }
  window.history.replaceState(null, "", url.toString());
}

export function useCompanies() {
  const [companies, setCompanies] = React.useState<Company[]>([]);
  const [pendingReviews, setPendingReviews] = React.useState<Company[]>([]);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<string | null>(null);

  // AbortController for cancelling in-flight requests on unmount
  const abortRef = React.useRef<AbortController | null>(null);

  // Filter state — initialized from URL params
  const [searchInput, setSearchInput] = React.useState<string>(getInitialFilters().q);
  const [selectedIndustry, setSelectedIndustry] = React.useState<string>(getInitialFilters().industry);
  const [selectedTrigger, setSelectedTrigger] = React.useState<string>(getInitialFilters().trigger);
  const [selectedQualified, setSelectedQualified] = React.useState<string>(getInitialFilters().qualified);
  const [selectedScore, setSelectedScore] = React.useState<string>(getInitialFilters().score);

  // Debounced search query (used for filtering, not for input binding)
  const searchQuery = useDebounce(searchInput, SEARCH_DEBOUNCE_MS);
  const debouncedUrlParams = useDebounce(
    { q: searchInput, industry: selectedIndustry, trigger: selectedTrigger, qualified: selectedQualified, score: selectedScore },
    URL_SYNC_DEBOUNCE_MS,
  );

  // Sync filters to URL on change (debounced)
  React.useEffect(() => {
    syncUrlParams(debouncedUrlParams);
  }, [debouncedUrlParams]);

  // Discovery state
  const [isDiscovering, setIsDiscovering] = React.useState<boolean>(false);
  const [approvalLoading, setApprovalLoading] = React.useState<string | null>(null);
  const [activePipelineId, setActivePipelineId] = React.useState<string | null>(null);

  const fetchCompanies = React.useCallback(async () => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setIsLoading(true);
    setError(null);
    try {
      const [enriched, pending] = await Promise.all([
        apiService.getCompanies("enriched,rejected,new,updated,discovered", undefined, controller.signal),
        apiService.getCompanies(undefined, "pending", controller.signal),
      ]);
      if (!controller.signal.aborted) {
        setCompanies(enriched);
        setPendingReviews(pending);
      }
    } catch (err: any) {
      if (err?.name === "CanceledError" || err?.code === "ERR_CANCELED") return;
      console.error("Error loading companies from FastAPI:", err);
      setError(
        err?.response?.data?.detail ||
        err?.message ||
        "Failed to load company records from server",
      );
    } finally {
      if (!controller.signal.aborted) {
        setIsLoading(false);
      }
    }
  }, []);

  // Initial fetch on mount
  React.useEffect(() => {
    fetchCompanies();
    return () => {
      abortRef.current?.abort();
    };
  }, [fetchCompanies]);

  // Client-side filtering
  const filteredCompanies = React.useMemo(() => {
    return companies.filter((company) => {
      const matchesSearch =
        company.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
        company.industry.toLowerCase().includes(searchQuery.toLowerCase()) ||
        company.trigger.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesIndustry =
        selectedIndustry === "all" ||
        company.industry.toLowerCase() === selectedIndustry.toLowerCase();

      const matchesTrigger =
        selectedTrigger === "all" ||
        company.trigger.toLowerCase() === selectedTrigger.toLowerCase();

      const matchesQualified =
        selectedQualified === "all" ||
        (selectedQualified === "qualified" && company.qualified === true) ||
        (selectedQualified === "unqualified" && company.qualified === false);

      const matchesScore =
        selectedScore === "all" ||
        (selectedScore === "high" && company.score >= 85) ||
        (selectedScore === "medium" && company.score >= 70 && company.score < 85) ||
        (selectedScore === "low" && company.score < 70);

      return matchesSearch && matchesIndustry && matchesTrigger && matchesQualified && matchesScore;
    });
  }, [companies, searchQuery, selectedIndustry, selectedTrigger, selectedQualified, selectedScore]);

  const uniqueIndustries = React.useMemo(() => {
    const set = new Set(companies.map((c) => c.industry).filter(Boolean));
    return Array.from(set);
  }, [companies]);

  const uniqueTriggers = React.useMemo(() => {
    const set = new Set(companies.map((c) => c.trigger).filter(Boolean));
    return Array.from(set);
  }, [companies]);

  const runDiscovery = async (urls: string | string[]) => {
    const urlList = Array.isArray(urls) ? urls : [urls];
    setIsDiscovering(true);
    // Generate pipeline_id BEFORE the API call so polling starts immediately
    const pipelineId = crypto.randomUUID();
    setActivePipelineId(pipelineId);
    try {
      const result = await apiService.runDiscovery(urlList, false, pipelineId);
      // Merge backend data (in case backend modified it) — keep our ID
      if (result?._pipeline_id) {
        // Pipeline already created under our ID
      }
      await fetchCompanies();
      return result;
    } catch (err: any) {
      console.error("Error running discovery on FastAPI:", err);
      setActivePipelineId(null);
      throw err;
    } finally {
      setIsDiscovering(false);
    }
  };

  const approveCompany = async (companyId: string) => {
    setApprovalLoading(companyId);
    try {
      await apiService.approveCompany(companyId);
      await fetchCompanies();
    } catch (err: any) {
      console.error("Error approving company:", err);
      throw err;
    } finally {
      setApprovalLoading(null);
    }
  };

  const rejectCompany = async (companyId: string) => {
    setApprovalLoading(companyId);
    try {
      await apiService.rejectCompany(companyId);
      await fetchCompanies();
    } catch (err: any) {
      console.error("Error rejecting company:", err);
      throw err;
    } finally {
      setApprovalLoading(null);
    }
  };

  const rescoreCompany = async (companyId: string, icpCriteria: Record<string, any>) => {
    setApprovalLoading(companyId);
    try {
      const result = await apiService.rescoreCompany(companyId, icpCriteria);
      await fetchCompanies();
      return result;
    } catch (err: any) {
      console.error("Error rescoring company:", err);
      throw err;
    } finally {
      setApprovalLoading(null);
    }
  };

  const resetFilters = () => {
    setSearchInput("");
    setSelectedIndustry("all");
    setSelectedTrigger("all");
    setSelectedQualified("all");
    setSelectedScore("all");
  };

  return {
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
    clearActivePipeline: () => setActivePipelineId(null),
    runDiscovery,
    approveCompany,
    rejectCompany,
    rescoreCompany,
    resetFilters,
    refetch: fetchCompanies,
  };
}
