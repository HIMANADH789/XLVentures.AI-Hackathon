"use client";

import * as React from "react";
import { Company } from "@/types/company";
import { apiService } from "@/services/api";

export function useCompanies() {
  const [companies, setCompanies] = React.useState<Company[]>([]);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<string | null>(null);
  
  // Search & Filter state
  const [searchQuery, setSearchQuery] = React.useState<string>("");
  const [selectedIndustry, setSelectedIndustry] = React.useState<string>("all");
  const [selectedTrigger, setSelectedTrigger] = React.useState<string>("all");
  const [selectedQualified, setSelectedQualified] = React.useState<string>("all");
  const [selectedScore, setSelectedScore] = React.useState<string>("all");
  
  // Simulated Discovery state
  const [isDiscovering, setIsDiscovering] = React.useState<boolean>(false);

  const fetchCompanies = React.useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiService.getCompanies();
      setCompanies(data);
    } catch (err: any) {
      console.error("Error loading companies from FastAPI:", err);
      setError(
        err?.response?.data?.detail || 
        err?.message || 
        "Failed to load company records from server"
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchCompanies();
  }, [fetchCompanies]);

  // Client-side filtering logic
  const filteredCompanies = React.useMemo(() => {
    return companies.filter((company) => {
      // 1. Text Query matches Company Name, Industry, or Trigger
      const matchesSearch =
        company.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
        company.industry.toLowerCase().includes(searchQuery.toLowerCase()) ||
        company.trigger.toLowerCase().includes(searchQuery.toLowerCase());

      // 2. Specific Industry Dropdown filter
      const matchesIndustry =
        selectedIndustry === "all" ||
        company.industry.toLowerCase() === selectedIndustry.toLowerCase();

      // 3. Specific Trigger Dropdown filter
      const matchesTrigger =
        selectedTrigger === "all" ||
        company.trigger.toLowerCase() === selectedTrigger.toLowerCase();

      // 4. Qualified filter
      const matchesQualified =
        selectedQualified === "all" ||
        (selectedQualified === "qualified" && company.qualified === true) ||
        (selectedQualified === "unqualified" && company.qualified === false);

      // 5. Score filter
      const matchesScore =
        selectedScore === "all" ||
        (selectedScore === "high" && company.score >= 85) ||
        (selectedScore === "medium" && company.score >= 70 && company.score < 85) ||
        (selectedScore === "low" && company.score < 70);

      return matchesSearch && matchesIndustry && matchesTrigger && matchesQualified && matchesScore;
    });
  }, [companies, searchQuery, selectedIndustry, selectedTrigger, selectedQualified, selectedScore]);

  // Unique list of industries & triggers for dropdowns
  const uniqueIndustries = React.useMemo(() => {
    const set = new Set(companies.map((c) => c.industry).filter(Boolean));
    return Array.from(set);
  }, [companies]);

  const uniqueTriggers = React.useMemo(() => {
    const set = new Set(companies.map((c) => c.trigger).filter(Boolean));
    return Array.from(set);
  }, [companies]);

  // Live Discovery trigger to POST /discover
  const runDiscovery = async (url: string) => {
    setIsDiscovering(true);
    try {
      await apiService.runDiscovery(url);
      // Automatically refresh company list after discovery
      await fetchCompanies();
    } catch (err: any) {
      console.error("Error running discovery on FastAPI:", err);
      throw err; // bubble up to page for notification/handling
    } finally {
      setIsDiscovering(false);
    }
  };

  const resetFilters = () => {
    setSearchQuery("");
    setSelectedIndustry("all");
    setSelectedTrigger("all");
    setSelectedQualified("all");
    setSelectedScore("all");
  };

  return {
    companies,
    filteredCompanies,
    uniqueIndustries,
    uniqueTriggers,
    isLoading,
    error,
    searchQuery,
    setSearchQuery,
    selectedIndustry,
    setSelectedIndustry,
    selectedTrigger,
    setSelectedTrigger,
    selectedQualified,
    setSelectedQualified,
    selectedScore,
    setSelectedScore,
    isDiscovering,
    runDiscovery,
    resetFilters,
    refetch: fetchCompanies
  };
}
