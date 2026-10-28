/**
 * Minimal shared UI primitives for CyberSaathi AI.
 *
 * No external component library — plain Tailwind + semantic HTML.
 * Accessible: roles, aria-labels, focus-visible rings, keyboard nav.
 */

import type { ReactNode, ButtonHTMLAttributes } from 'react';

// ── Spinner ───────────────────────────────────────────────────────────────────

export function Spinner({ label = 'Loading…' }: { label?: string }) {
  return (
    <span role="status" aria-label={label} className="inline-flex items-center justify-center">
      <svg
        className="animate-spin h-5 w-5 text-current"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
        />
      </svg>
    </span>
  );
}

// ── Risk badge ────────────────────────────────────────────────────────────────

const RISK_STYLES: Record<string, string> = {
  'High Risk':
    'bg-red-50 text-red-800 border border-red-200',
  Suspicious:
    'bg-amber-50 text-amber-800 border border-amber-200',
  'No Obvious Warning Signs':
    'bg-emerald-50 text-emerald-800 border border-emerald-200',
  'Unable to Assess':
    'bg-gray-100 text-gray-700 border border-gray-300',
};

const RISK_ICON: Record<string, string> = {
  'High Risk': '⚠',
  Suspicious: '◉',
  'No Obvious Warning Signs': '✓',
  'Unable to Assess': '?',
};

export function RiskBadge({ category }: { category: string }) {
  const styles = RISK_STYLES[category] ?? RISK_STYLES['Unable to Assess'];
  const icon = RISK_ICON[category] ?? '?';
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-semibold ${styles}`}
      aria-label={`Risk level: ${category}`}
    >
      <span aria-hidden="true">{icon}</span>
      {category}
    </span>
  );
}

// ── Method pill ───────────────────────────────────────────────────────────────

const METHOD_LABELS: Record<string, string> = {
  ml_model: 'ML model',
  rules: 'Rule-based',
  ml_model_and_rules: 'ML model + rules',
  unable_to_assess: 'Unable to assess',
};

export function MethodPill({ method }: { method: string }) {
  const label = METHOD_LABELS[method] ?? method;
  return (
    <span className="inline-flex items-center rounded px-2 py-0.5 text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
      Method: {label}
    </span>
  );
}

// ── Alert box ─────────────────────────────────────────────────────────────────

type AlertVariant = 'error' | 'warning' | 'info';

const ALERT_STYLES: Record<AlertVariant, string> = {
  error: 'bg-red-50 border-red-300 text-red-800',
  warning: 'bg-amber-50 border-amber-300 text-amber-800',
  info: 'bg-blue-50 border-blue-300 text-blue-800',
};

export function Alert({
  variant,
  children,
}: {
  variant: AlertVariant;
  children: ReactNode;
}) {
  return (
    <div
      role="alert"
      className={`rounded-md border px-4 py-3 text-sm ${ALERT_STYLES[variant]}`}
    >
      {children}
    </div>
  );
}

// ── Button ────────────────────────────────────────────────────────────────────

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
  loading?: boolean;
  children: ReactNode;
}

export function Button({
  variant = 'primary',
  loading = false,
  children,
  disabled,
  className = '',
  ...rest
}: ButtonProps) {
  const base =
    'inline-flex items-center justify-center gap-2 rounded-md px-5 py-2.5 text-sm font-semibold transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:opacity-50 disabled:pointer-events-none';
  const variants = {
    primary:
      'bg-slate-800 text-white hover:bg-slate-700 focus-visible:outline-slate-800',
    secondary:
      'bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 focus-visible:outline-slate-500',
  };

  return (
    <button
      disabled={disabled ?? loading}
      aria-busy={loading}
      className={`${base} ${variants[variant]} ${className}`}
      {...rest}
    >
      {loading && <Spinner />}
      {children}
    </button>
  );
}

// ── Section heading ───────────────────────────────────────────────────────────

export function SectionHeading({
  as: Tag = 'h2',
  children,
  className = '',
}: {
  as?: 'h2' | 'h3';
  children: ReactNode;
  className?: string;
}) {
  return (
    <Tag className={`text-xs font-semibold uppercase tracking-wider text-slate-500 ${className}`}>
      {children}
    </Tag>
  );
}
