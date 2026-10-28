/**
 * Shared TypeScript types for the CyberSaathi AI API.
 *
 * These must stay in sync with the Pydantic schemas in
 * backend/app/schemas/__init__.py.  Any breaking change to the backend
 * contract must be reflected here.
 */

export type Language = 'en' | 'hinglish';

export type RiskCategory =
  | 'High Risk'
  | 'Suspicious'
  | 'No Obvious Warning Signs'
  | 'Unable to Assess';

export type AnalysisMethod =
  | 'ml_model'
  | 'rules'
  | 'ml_model_and_rules'
  | 'unable_to_assess';

export interface Indicator {
  code: string;
  label: string;
  explanation: string;
}

// ── Request types ─────────────────────────────────────────────────────────────

export interface UrlAnalysisRequest {
  url: string;
  language: Language;
}

export interface MessageAnalysisRequest {
  message: string;
  language: Language;
}

// ── Response types ────────────────────────────────────────────────────────────

export interface AnalysisResponse {
  category: RiskCategory;
  method: AnalysisMethod;
  indicators: Indicator[];
  summary: string;
  recommendations: string[];
  disclaimer: string;
  language: Language;
}

export type UrlAnalysisResponse = AnalysisResponse;
export type MessageAnalysisResponse = AnalysisResponse;

export interface HealthResponse {
  status: 'ok';
}

// ── API error ─────────────────────────────────────────────────────────────────

export interface ApiError {
  type: 'network' | 'validation' | 'server' | 'unknown';
  message: string;
  status?: number;
}
