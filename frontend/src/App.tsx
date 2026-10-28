/**
 * CyberSaathi AI — Root application component.
 *
 * Layout:
 *  ┌─────────────────────────────────────────────────────────────────┐
 *  │ Header: logo · tagline · language toggle                        │
 *  ├─────────────────────────────────────────────────────────────────┤
 *  │ Mode tabs: URL Analysis | Message Analysis                      │
 *  ├─────────────────────────────────────────────────────────────────┤
 *  │ Input form (validated; loading / error states)                  │
 *  ├─────────────────────────────────────────────────────────────────┤
 *  │ Result card (risk, indicators, next steps, method, disclaimer)  │
 *  └─────────────────────────────────────────────────────────────────┘
 *  Footer: privacy notice, non-guarantee disclaimer
 *
 * Calls the real backend via api.ts.  No mock results are ever shown.
 */

import { useState } from 'react';
import { AnalysisForm, type AnalysisMode } from './components/AnalysisForm';
import { ResultCard } from './components/ResultCard';
import { LearnSection } from './components/LearnSection';
import { Alert, Spinner } from './components/ui';
import { analyzeUrl, analyzeMessage } from './services/api';
import type { AnalysisResponse, ApiError, Language } from './types/api';

// ── Tab configuration ─────────────────────────────────────────────────────────

type AppTab = AnalysisMode | 'learn';

interface AppTabDef {
  id: AppTab;
  labelEn: string;
  labelHi: string;
}

const APP_TABS: AppTabDef[] = [
  { id: 'url',     labelEn: 'URL Analysis',     labelHi: 'URL Analysis' },
  { id: 'message', labelEn: 'Message Analysis',  labelHi: 'Message Analysis' },
  { id: 'learn',   labelEn: 'Learn',             labelHi: 'Seekhein' },
];

// Analysis-specific tab metadata (description line under the tab bar)
interface AnalysisModeTab {
  id: AnalysisMode;
  descEn: string;
  descHi: string;
}

const ANALYSIS_MODES: AnalysisModeTab[] = [
  {
    id: 'url',
    descEn: 'Paste a suspicious link to check for phishing indicators.',
    descHi: 'Koi suspicious link paste karein phishing indicators check karne ke liye.',
  },
  {
    id: 'message',
    descEn: 'Paste a suspicious SMS, email, or offer message.',
    descHi: 'Koi suspicious SMS, email, ya offer message paste karein.',
  },
];

// ── State types ───────────────────────────────────────────────────────────────

type AppState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; result: AnalysisResponse; mode: AnalysisMode }
  | { status: 'error'; error: ApiError };

// ── Helper: format API error for display ──────────────────────────────────────

function describeApiError(err: ApiError): string {
  if (err.type === 'network') {
    return (
      'Could not reach the backend server. Make sure it is running at the configured address.'
    );
  }
  if (err.type === 'validation') {
    return `The server rejected the input (${err.status ?? 'validation error'}). ${err.message}`;
  }
  if (err.type === 'server') {
    return `The server encountered an error (${err.status ?? 'unknown'}). Try again in a moment.`;
  }
  return err.message ?? 'An unexpected error occurred.';
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function App() {
  const [activeTab, setActiveTab] = useState<AppTab>('url');
  const [analysisMode, setAnalysisMode] = useState<AnalysisMode>('url');
  const [language, setLanguage] = useState<Language>('en');
  const [appState, setAppState] = useState<AppState>({ status: 'idle' });

  // Switch top-level tab
  function handleTabChange(next: AppTab) {
    if (next === activeTab) return;
    setActiveTab(next);
    // When switching to an analysis tab, also update analysisMode and reset state
    if (next === 'url' || next === 'message') {
      setAnalysisMode(next);
      setAppState({ status: 'idle' });
    }
  }

  // Legacy alias kept for AnalysisForm usage
  const mode = analysisMode;

  // Switch language — keep result visible but note language was used at submission time
  function handleLanguageChange(lang: Language) {
    setLanguage(lang);
  }

  async function handleSubmit(value: string) {
    setAppState({ status: 'loading' });
    try {
      const result =
        analysisMode === 'url'
          ? await analyzeUrl(value, language)
          : await analyzeMessage(value, language);
      setAppState({ status: 'success', result, mode });
    } catch (e) {
      // api.ts always throws ApiError-shaped objects
      const err = e as ApiError;
      setAppState({
        status: 'error',
        error: err.type ? err : { type: 'unknown', message: String(e) },
      });
    }
  }

  const isLoading = appState.status === 'loading';
  const isAnalysisTab = activeTab === 'url' || activeTab === 'message';
  const activeAnalysisDesc = isAnalysisTab
    ? ANALYSIS_MODES.find((m) => m.id === activeTab)
    : null;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* ── Skip link for keyboard users ─────────────────────────────────── */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:rounded focus:bg-slate-800 focus:px-4 focus:py-2 focus:text-white focus:text-sm"
      >
        Skip to main content
      </a>

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <header className="bg-white border-b border-slate-200 px-4 py-4">
        <div className="max-w-2xl mx-auto flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-lg font-bold text-slate-900 leading-tight">
              CyberSaathi AI
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              {language === 'en'
                ? 'Cybersecurity awareness for college students'
                : 'College students ke liye cybersecurity awareness'}
            </p>
          </div>

          {/* Language toggle */}
          <div
            role="radiogroup"
            aria-label="Explanation language"
            className="flex rounded-md border border-slate-200 overflow-hidden text-xs font-medium"
          >
            {(['en', 'hinglish'] as Language[]).map((lang) => (
              <button
                key={lang}
                role="radio"
                aria-checked={language === lang}
                onClick={() => handleLanguageChange(lang)}
                className={`px-3 py-1.5 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-slate-700 ${
                  language === lang
                    ? 'bg-slate-800 text-white'
                    : 'bg-white text-slate-600 hover:bg-slate-50'
                }`}
              >
                {lang === 'en' ? 'English' : 'Hinglish'}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* ── Main content ─────────────────────────────────────────────────── */}
      <main id="main-content" className="flex-1 px-4 py-6 sm:py-8">
        <div className="max-w-2xl mx-auto space-y-6">

          {/* ── Top-level tab bar ─────────────────────────────────────────── */}
          <div
            role="tablist"
            aria-label="Application sections"
            className="flex rounded-lg border border-slate-200 bg-white overflow-hidden shadow-sm"
          >
            {APP_TABS.map((tab) => {
              const label = language === 'en' ? tab.labelEn : tab.labelHi;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  role="tab"
                  aria-selected={isActive}
                  aria-controls={`panel-${tab.id}`}
                  id={`tab-${tab.id}`}
                  onClick={() => handleTabChange(tab.id)}
                  disabled={isLoading && tab.id !== activeTab}
                  className={`flex-1 px-4 py-3 text-sm font-semibold transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-slate-700 disabled:opacity-50 ${
                    isActive
                      ? 'bg-slate-800 text-white'
                      : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  {label}
                </button>
              );
            })}
          </div>

          {/* ── Analysis panel (URL / Message) ────────────────────────────── */}
          <div
            id={`panel-${analysisMode}`}
            role="tabpanel"
            aria-labelledby={`tab-${analysisMode}`}
            hidden={!isAnalysisTab}
            className="space-y-6"
          >
            {activeAnalysisDesc && (
              <p className="text-sm text-slate-500">
                {language === 'en'
                  ? activeAnalysisDesc.descEn
                  : activeAnalysisDesc.descHi}
              </p>
            )}

            {/* ── Input form ───────────────────────────────────────────────── */}
            <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
              <AnalysisForm
                mode={mode}
                onSubmit={handleSubmit}
                loading={isLoading}
                language={language}
              />
            </div>

            {/* ── Loading skeleton ─────────────────────────────────────────── */}
            {isLoading && (
              <div
                className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white p-5 text-sm text-slate-500 shadow-sm"
                aria-live="polite"
                aria-busy="true"
              >
                <Spinner label="Analysing…" />
                <span>
                  {language === 'en'
                    ? 'Analysing — this usually takes under a second…'
                    : 'Analysis ho raha hai — yeh ek second se kam lagta hai…'}
                </span>
              </div>
            )}

            {/* ── Error state ───────────────────────────────────────────────── */}
            {appState.status === 'error' && (
              <Alert variant="error">
                <p className="font-semibold mb-1">
                  {language === 'en' ? 'Analysis failed' : 'Analysis fail ho gayi'}
                </p>
                <p>{describeApiError(appState.error)}</p>
                {appState.error.type === 'network' && (
                  <p className="mt-2 text-xs opacity-80">
                    {language === 'en'
                      ? 'If the backend is not yet running, start it with: cd backend && uvicorn app.main:app --reload'
                      : 'Agar backend abhi nahi chal raha, toh start karein: cd backend && uvicorn app.main:app --reload'}
                  </p>
                )}
              </Alert>
            )}

            {/* ── Result ───────────────────────────────────────────────────── */}
            {appState.status === 'success' && (
              <ResultCard result={appState.result} inputMode={appState.mode} />
            )}
          </div>

          {/* ── Learn panel ───────────────────────────────────────────────── */}
          <div
            id="panel-learn"
            role="tabpanel"
            aria-labelledby="tab-learn"
            hidden={activeTab !== 'learn'}
          >
            {activeTab === 'learn' && <LearnSection language={language} />}
          </div>
        </div>
      </main>

      {/* ── Footer ──────────────────────────────────────────────────────── */}
      <footer className="border-t border-slate-200 bg-white px-4 py-5">
        <div className="max-w-2xl mx-auto space-y-2 text-xs text-slate-400">
          <p>
            <strong className="text-slate-600">Privacy:</strong>{' '}
            {language === 'en'
              ? 'Your input is sent to the analysis server and is not stored or logged. No account or cookies are required.'
              : 'Aapka input analysis server ko bheja jata hai aur store ya log nahi hota. Koi account ya cookies zaruri nahi.'}
          </p>
          <p>
            <strong className="text-slate-600">
              {language === 'en' ? 'Limitations:' : 'Limitations:'}
            </strong>{' '}
            {language === 'en'
              ? 'Automated analysis can be wrong. A "No Obvious Warning Signs" result is not a guarantee of safety. Always verify through official channels independently.'
              : 'Automated analysis galat ho sakta hai. "No Obvious Warning Signs" ka matlab safe nahi hai. Hamesha official channels se independently verify karein.'}
          </p>
          <p className="pt-1 border-t border-slate-100">
            CyberSaathi AI · IBM SkillsBuild – AICTE – BharatCares ML &amp; Applied AI Internship 2026
          </p>
        </div>
      </footer>
    </div>
  );
}
