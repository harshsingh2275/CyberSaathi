/**
 * ResultCard — renders a full analysis response.
 *
 * Shows: risk category badge, summary, method/source pill, warning
 * indicators (each expandable), safe next steps, disclaimer.
 * Never presents any result as a "safe" determination.
 */

import { useState } from 'react';
import type { AnalysisResponse } from '../types/api';
import { RiskBadge, MethodPill, SectionHeading } from './ui';

interface Props {
  result: AnalysisResponse;
  inputMode: 'url' | 'message';
}

const CATEGORY_DESCRIPTION: Record<string, string> = {
  'High Risk':
    'Strong indicators of phishing or fraud were found. Do not interact with this content.',
  Suspicious:
    'Some indicators warrant caution. Verify independently before taking any action.',
  'No Obvious Warning Signs':
    'No obvious warning indicators detected. This is not a guarantee of safety.',
  'Unable to Assess':
    'The input could not be assessed. Verify through official channels.',
};

function IndicatorRow({ label, explanation }: { label: string; explanation: string }) {
  const [expanded, setExpanded] = useState(false);
  const id = `indicator-${label.replace(/\s+/g, '-').toLowerCase().slice(0, 30)}`;

  return (
    <li className="border border-slate-200 rounded-md overflow-hidden">
      <button
        type="button"
        aria-expanded={expanded}
        aria-controls={id}
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center justify-between gap-3 px-4 py-3 text-left text-sm font-medium text-slate-800 bg-white hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-slate-700 transition-colors"
      >
        <span className="flex items-center gap-2">
          <span className="shrink-0 text-amber-500" aria-hidden="true">◆</span>
          {label}
        </span>
        <span
          aria-hidden="true"
          className={`shrink-0 text-slate-400 text-xs transition-transform duration-150 ${
            expanded ? 'rotate-90' : ''
          }`}
        >
          ▶
        </span>
      </button>
      {expanded && (
        <div id={id} className="px-4 pb-3 pt-1 text-sm text-slate-600 bg-slate-50 border-t border-slate-200 leading-relaxed">
          {explanation}
        </div>
      )}
    </li>
  );
}

export function ResultCard({ result, inputMode }: Props) {
  const desc = CATEGORY_DESCRIPTION[result.category] ?? '';

  return (
    <section aria-label="Analysis result" className="space-y-5">
      {/* ── Risk category header ─────────────────────────────────────────── */}
      <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm space-y-3">
        <div className="flex flex-wrap items-start gap-3">
          <RiskBadge category={result.category} />
          <MethodPill method={result.method} />
        </div>
        <p className="text-sm text-slate-700 leading-relaxed font-medium">{desc}</p>
        <p className="text-sm text-slate-600 leading-relaxed">{result.summary}</p>
      </div>

      {/* ── Warning indicators ───────────────────────────────────────────── */}
      {result.indicators.length > 0 ? (
        <div className="space-y-2">
          <SectionHeading>
            Warning indicators ({result.indicators.length})
            {' '}<span className="normal-case font-normal text-slate-400">— click to expand</span>
          </SectionHeading>
          <ul className="space-y-2" aria-label="Warning indicators">
            {result.indicators.map((ind) => (
              <IndicatorRow
                key={ind.code}
                label={ind.label}
                explanation={ind.explanation}
              />
            ))}
          </ul>
        </div>
      ) : (
        <div className="rounded-md border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
          No specific warning indicators were detected for this {inputMode === 'url' ? 'URL' : 'message'}.
        </div>
      )}

      {/* ── Safe next steps ──────────────────────────────────────────────── */}
      {result.recommendations.length > 0 && (
        <div className="space-y-2">
          <SectionHeading>Safe next steps</SectionHeading>
          <ol
            className="space-y-2"
            aria-label="Recommended next steps"
          >
            {result.recommendations.map((rec, i) => (
              <li
                key={i}
                className="flex gap-3 items-start text-sm text-slate-700 leading-relaxed"
              >
                <span
                  aria-hidden="true"
                  className="shrink-0 mt-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-slate-800 text-white text-xs font-bold"
                >
                  {i + 1}
                </span>
                {rec}
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* ── Method / source disclosure ───────────────────────────────────── */}
      <div className="space-y-2">
        <SectionHeading>Analysis method</SectionHeading>
        <p className="text-xs text-slate-500 leading-relaxed">
          {result.method === 'ml_model' && (
            <>
              This result was produced by a trained machine-learning classifier applied to
              {inputMode === 'url' ? ' URL structure features' : ' message text patterns'}.
              The model can make mistakes and does not cover all phishing techniques.
            </>
          )}
          {result.method === 'rules' && (
            <>
              This result was produced by transparent rule-based pattern matching.
              No ML classifier was used.
            </>
          )}
          {result.method === 'ml_model_and_rules' && (
            <>
              This result combines a trained ML classifier with rule-based pattern checks.
              Both components can make mistakes.
            </>
          )}
          {result.method === 'unable_to_assess' && (
            <>
              The input could not be assessed by automated methods.
              Verify through official channels.
            </>
          )}
        </p>
      </div>

      {/* ── Limitations / disclaimer ─────────────────────────────────────── */}
      <div className="rounded-md border border-slate-200 bg-slate-50 px-4 py-3 space-y-1">
        <SectionHeading as="h3">Limitations</SectionHeading>
        <p className="text-xs text-slate-500 leading-relaxed mt-1">
          {result.disclaimer}
        </p>
      </div>
    </section>
  );
}
