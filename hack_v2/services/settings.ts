import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

export interface IcpSettings {
  industry: string;
  min_employees: number;
  max_employees: number;
  qualification_threshold: number;
}

export interface PersonaSettings {
  default: string[];
  options: string[];
}

export interface SettingsResponse {
  icp: IcpSettings;
  personas: PersonaSettings;
}

export const settingsService = {
  async get(): Promise<SettingsResponse> {
    const res = await client.get("/settings/icp");
    return res.data;
  },

  async updateIcp(icp: IcpSettings): Promise<SettingsResponse> {
    const res = await client.put("/settings/icp", icp);
    return res.data;
  },

  async updatePersonas(personas: PersonaSettings): Promise<SettingsResponse> {
    const res = await client.put("/settings/personas", personas);
    return res.data;
  },
};
