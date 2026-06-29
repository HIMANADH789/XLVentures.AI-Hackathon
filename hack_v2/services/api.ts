import axios from "axios";
import { Company } from "@/types/company";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export function mapBackendCompanyToFrontend(backend: any): Company {
  if (!backend) {
    throw new Error("Invalid backend company payload");
  }

  const triggerEvents = backend.trigger_events || [];

  return {
    id: backend.id || backend.company_id || "",
    company: backend.name || backend.company_name || backend.company || "Unnamed Company",
    website: backend.website || "",
    industry: backend.industry || "N/A",
    employees: backend.employee_count !== undefined && backend.employee_count !== null ? backend.employee_count : null,
    trigger: backend.trigger_type || backend.trigger || (triggerEvents[0]?.trigger_type) || "No trigger detected",
    score: backend.icp_score !== undefined && backend.icp_score !== null
      ? Math.round(backend.icp_score)
      : backend.qualification_score !== undefined && backend.qualification_score !== null
        ? Math.round(backend.qualification_score)
        : backend.score !== undefined ? Math.round(backend.score) : 0,
    summary: backend.summary ? backend.summary.replace(/\*\*/g, "").replace(/__/g, "") : "",
    qualified: backend.qualified !== undefined
      ? backend.qualified
      : backend.is_qualified !== undefined
        ? backend.is_qualified
        : backend.score >= 60 || false,
    trigger_source: backend.trigger_source || null,
    trigger_confidence: backend.trigger_confidence !== undefined && backend.trigger_confidence !== null
      ? backend.trigger_confidence
      : triggerEvents[0]?.confidence || null,
    contact_confidence: backend.contact_confidence !== undefined && backend.contact_confidence !== null
      ? backend.contact_confidence
      : null,
    summary_confidence: backend.summary_confidence !== undefined && backend.summary_confidence !== null
      ? backend.summary_confidence
      : null,
    status: backend.status || null,
    approval_status: backend.approval_status || "pending",
    created_at: backend.created_at || null,
    firecrawl_used: backend.firecrawl_used || false,
    news_used: backend.news_used || false,
    news_headlines: backend.news_headlines || null,
    discovery_timestamp: backend.discovery_timestamp || null,
    trigger_score: backend.trigger_score ?? null,
    industry_score: backend.industry_score ?? null,
    employee_score: backend.employee_score ?? null,
    trigger_events: triggerEvents.map((t: any) => ({
      trigger_type: t.trigger_type,
      description: t.description,
      confidence: t.confidence,
    })),
    recommended_action: backend.recommended_action || null,
    prospect_intelligence: backend.prospect_intelligence || null,
    execution_plan: backend.execution_plan || null,
    contacts: Array.isArray(backend.contacts)
      ? backend.contacts.map((contact: any) => ({
          id: contact.id || "",
          name: contact.name || "Unnamed Contact",
          role: contact.role || null,
          email: contact.email || null,
          linkedin: contact.linkedin || null,
          source: contact.source || "Manual",
        }))
      : [],
  };
}

export const apiService = {
  async getCompanies(status?: string, approvalStatus?: string, signal?: AbortSignal): Promise<Company[]> {
    const params: Record<string, string> = {};
    if (status) params.status = status;
    if (approvalStatus) params.approval_status = approvalStatus;
    const response = await axiosClient.get("/companies", { params, signal });
    const data = response.data;
    if (Array.isArray(data)) {
      return data.map(mapBackendCompanyToFrontend);
    }
    return [];
  },

  async getCompanyById(id: string, signal?: AbortSignal): Promise<Company> {
    const response = await axiosClient.get(`/companies/${id}`, { signal });
    return mapBackendCompanyToFrontend(response.data);
  },

  async runDiscovery(urls: string[], autoApprove = false, pipelineId?: string): Promise<any> {
    const payload = {
      company_inputs: urls.map((url) => ({
        url,
        source: "manual",
        pipeline_id: pipelineId || undefined,
      })),
      force_refresh: true,
      auto_approve: autoApprove,
    };
    if (pipelineId) {
      (payload as any).pipeline_id = pipelineId;
    }
    const response = await axiosClient.post("/discover", payload);
    return response.data;
  },

  async approveCompany(companyId: string, personas?: string[]): Promise<any> {
    const response = await axiosClient.post(`/discover/${companyId}/approve`, {
      company_id: companyId,
      personas: personas || [],
    });
    return response.data;
  },

  async rejectCompany(companyId: string): Promise<any> {
    const response = await axiosClient.post(`/discover/${companyId}/reject`, {
      company_id: companyId,
    });
    return response.data;
  },

  async rescoreCompany(companyId: string, icpCriteria: Record<string, any>): Promise<any> {
    const response = await axiosClient.post(`/discover/${companyId}/re-score`, {
      company_id: companyId,
      icp_criteria: icpCriteria,
    });
    return response.data;
  },

  async getPipelineStatus(pipelineId: string): Promise<any> {
    const response = await axiosClient.get(`/discover/pipeline/${pipelineId}`);
    return response.data;
  },
};
