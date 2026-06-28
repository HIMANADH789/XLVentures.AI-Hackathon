import axios from "axios";
import { Company } from "@/types/company";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// Create Axios Client
const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Maps the live backend data properties to the expected frontend models.
 * Mappings:
 * - name -> company
 * - employee_count -> employees
 * - trigger_type -> trigger
 * - icp_score -> score
 */
export function mapBackendCompanyToFrontend(backend: any): Company {
  if (!backend) {
    throw new Error("Invalid backend company payload");
  }
  
  return {
    id: backend.id || "",
    company: backend.name || "Unnamed Company",
    website: backend.website || "",
    industry: backend.industry || "N/A",
    employees: backend.employee_count !== undefined && backend.employee_count !== null ? backend.employee_count : null,
    trigger: backend.trigger_type || "No trigger detected",
    score: backend.icp_score !== undefined && backend.icp_score !== null ? Math.round(backend.icp_score) : 0,
    summary: backend.summary ? backend.summary.replace(/\*\*/g, "").replace(/__/g, "") : "",
    qualified: backend.qualified !== undefined ? backend.qualified : (backend.icp_score >= 60),
    trigger_source: backend.trigger_source || null,
    trigger_confidence: backend.trigger_confidence !== undefined && backend.trigger_confidence !== null ? backend.trigger_confidence : null,
    contact_confidence: backend.contact_confidence !== undefined && backend.contact_confidence !== null ? backend.contact_confidence : null,
    summary_confidence: backend.summary_confidence !== undefined && backend.summary_confidence !== null ? backend.summary_confidence : null,
    status: backend.status || null,
    created_at: backend.created_at || null,
    firecrawl_used: backend.firecrawl_used || false,
    news_used: backend.news_used || false,
    news_headlines: backend.news_headlines || null,
    discovery_timestamp: backend.discovery_timestamp || null,
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
  /**
   * Fetch all companies from the database.
   */
  async getCompanies(): Promise<Company[]> {
    const response = await axiosClient.get("/companies");
    const data = response.data;
    if (Array.isArray(data)) {
      return data.map(mapBackendCompanyToFrontend);
    }
    return [];
  },

  /**
   * Fetch detailed company info, including related contacts.
   */
  async getCompanyById(id: string): Promise<Company> {
    const response = await axiosClient.get(`/companies/${id}`);
    return mapBackendCompanyToFrontend(response.data);
  },

  /**
   * Post manual discovery event.
   */
  async runDiscovery(url: string): Promise<any> {
    const payload = {
      company_inputs: [
        {
          url: url,
          source: "manual",
        },
      ],
      force_refresh: true,
    };
    const response = await axiosClient.post("/discover", payload);
    return response.data;
  },
};
