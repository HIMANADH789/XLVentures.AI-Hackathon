export interface Contact {
  id: string;
  name: string;
  role: string | null;
  email: string | null;
  linkedin: string | null;
  source?: string;
}

export interface TriggerEvent {
  trigger_type: string;
  description?: string;
  confidence?: number;
  source_url?: string;
}

export interface RecommendedAction {
  action_type?: string;
  reasoning?: string;
  draft_message?: string;
}

export interface ProspectIntelligence {
  tech_stack?: string[];
  sentiment?: string;
  hiring_velocity?: string;
  strategic_insight?: string;
}

export interface ExecutionPlanStep {
  tool: string;
  reason: string;
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
  approval_status?: string | null;
  created_at?: string | null;
  firecrawl_used?: boolean;
  news_used?: boolean;
  news_headlines?: string | null;
  discovery_timestamp?: string | null;
  trigger_score?: number | null;
  industry_score?: number | null;
  employee_score?: number | null;
  trigger_events?: TriggerEvent[];
  recommended_action?: RecommendedAction | null;
  prospect_intelligence?: ProspectIntelligence | null;
  execution_plan?: ExecutionPlanStep[] | null;
}
