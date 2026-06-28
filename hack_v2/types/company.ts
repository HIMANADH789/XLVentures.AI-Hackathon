export interface Contact {
  id: string;
  name: string;
  role: string | null;
  email: string | null;
  linkedin: string | null;
  source?: string;
}

export interface Company {
  id: string;
  company: string;
  website: string;
  industry: string;
  employees: number | null;
  trigger: string;
  score: number;
  summary: string;
  contacts: Contact[];
  qualified?: boolean;
  trigger_source?: string | null;
  trigger_confidence?: number | null;
  contact_confidence?: number | null;
  summary_confidence?: number | null;
  status?: string | null;
  created_at?: string | null;
  firecrawl_used?: boolean;
  news_used?: boolean;
  news_headlines?: string | null;
  discovery_timestamp?: string | null;
}
