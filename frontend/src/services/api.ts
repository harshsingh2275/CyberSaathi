/**
 * API service module.
 *
 * All calls to the backend go through this module.
 * The base URL is read from the VITE_API_BASE_URL environment variable
 * (set in .env for local development; injected as a build-time variable
 * for production).
 *
 * Security note: this module never opens, fetches, previews, or resolves
 * user-submitted URLs.  It only sends them as JSON strings to the backend.
 */

import type {
  ApiError,
  HealthResponse,
  Language,
  MessageAnalysisResponse,
  UrlAnalysisResponse,
} from '../types/api';

const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000';

// ── Internal helper ────────────────────────────────────────────────────────────

async function post<T>(path: string, body: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
  } catch {
    const err: ApiError = {
      type: 'network',
      message: 'Could not reach the CyberSaathi AI backend. Please check your connection.',
    };
    throw err;
  }

  if (!response.ok) {
    const err: ApiError = {
      type: response.status >= 500 ? 'server' : 'validation',
      message: `Server returned ${response.status}. ${response.statusText}`,
      status: response.status,
    };
    throw err;
  }

  return response.json() as Promise<T>;
}

// ── Public API ────────────────────────────────────────────────────────────────

export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${BASE_URL}/health`);
  if (!response.ok) {
    const err: ApiError = { type: 'server', message: 'Backend health check failed.', status: response.status };
    throw err;
  }
  return response.json() as Promise<HealthResponse>;
}

export async function analyzeUrl(url: string, language: Language): Promise<UrlAnalysisResponse> {
  return post<UrlAnalysisResponse>('/api/analyze/url', { url, language });
}

export async function analyzeMessage(
  message: string,
  language: Language,
): Promise<MessageAnalysisResponse> {
  return post<MessageAnalysisResponse>('/api/analyze/message', { message, language });
}
