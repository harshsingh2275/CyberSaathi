/**
 * AnalysisForm — URL / message input form with client-side validation.
 *
 * Responsibilities:
 *  - Accepts mode prop ('url' | 'message') and calls onSubmit with the value.
 *  - Enforces input limits matching backend Pydantic constraints.
 *  - Shows inline character count and validation messages.
 *  - Manages loading state; disables submit during pending request.
 *  - Accessible: labeled inputs, aria-describedby for errors, keyboard nav.
 */

import { useState, useRef, type FormEvent, type KeyboardEvent } from 'react';
import { Button, Alert } from './ui';

export type AnalysisMode = 'url' | 'message';

interface Props {
  mode: AnalysisMode;
  onSubmit: (value: string) => Promise<void>;
  loading: boolean;
  language: 'en' | 'hinglish';
}

const URL_MAX = 2048;
const MSG_MAX = 5000;

const COPY: Record<'en' | 'hinglish', Record<AnalysisMode, {
  label: string;
  placeholder: string;
  hint: string;
  submit: string;
}>> = {
  en: {
    url: {
      label: 'Paste URL to analyse',
      placeholder: 'https://example.com/offer?ref=…',
      hint: 'Only the URL string is checked — it is never opened or visited.',
      submit: 'Analyse URL',
    },
    message: {
      label: 'Paste message text to analyse',
      placeholder: 'Paste SMS, email, job offer, or scholarship message here…',
      hint: 'Paste the full message. Your text is not stored.',
      submit: 'Analyse Message',
    },
  },
  hinglish: {
    url: {
      label: 'URL paste karein analysis ke liye',
      placeholder: 'https://example.com/offer?ref=…',
      hint: 'Sirf URL string check hota hai — isse kabhi open nahi kiya jata.',
      submit: 'URL Analyse Karein',
    },
    message: {
      label: 'Message text paste karein analysis ke liye',
      placeholder: 'SMS, email, job offer, ya scholarship message paste karein…',
      hint: 'Poora message paste karein. Aapka text store nahi hota.',
      submit: 'Message Analyse Karein',
    },
  },
};

function validateInput(mode: AnalysisMode, value: string): string | null {
  const trimmed = value.trim();
  if (!trimmed) {
    return mode === 'url' ? 'Please enter a URL.' : 'Please enter a message.';
  }
  if (mode === 'url') {
    if (trimmed.length > URL_MAX) {
      return `URL must not exceed ${URL_MAX.toLocaleString()} characters.`;
    }
    // Loose check: must look like a URL (starts with scheme or www)
    if (!/^(https?:\/\/|ftp:\/\/|www\.)/i.test(trimmed)) {
      return 'Please enter a URL starting with http://, https://, or www.';
    }
  } else {
    if (trimmed.length > MSG_MAX) {
      return `Message must not exceed ${MSG_MAX.toLocaleString()} characters.`;
    }
    if (trimmed.length < 5) {
      return 'Message is too short to analyse.';
    }
  }
  return null;
}

export function AnalysisForm({ mode, onSubmit, loading, language }: Props) {
  const [value, setValue] = useState('');
  const [touched, setTouched] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement | null>(null);

  const copy = COPY[language][mode];
  const max = mode === 'url' ? URL_MAX : MSG_MAX;
  const validationError = touched ? validateInput(mode, value) : null;
  const errorId = `${mode}-input-error`;
  const hintId = `${mode}-input-hint`;
  const countId = `${mode}-char-count`;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setTouched(true);
    setSubmitError(null);

    const err = validateInput(mode, value);
    if (err) {
      (inputRef.current as HTMLElement | null)?.focus();
      return;
    }

    try {
      await onSubmit(value.trim());
    } catch (err) {
      // Surface unexpected errors (API errors are handled by the parent)
      if (err instanceof Error) setSubmitError(err.message);
    }
  }

  // Allow Ctrl+Enter / Cmd+Enter to submit from textarea
  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit(e as unknown as FormEvent);
    }
  }

  const inputClassName =
    `w-full rounded-md border px-3 py-2.5 text-sm text-slate-800 placeholder-slate-400 ` +
    `transition-colors focus:outline-none focus:ring-2 focus:ring-slate-700 focus:border-slate-700 ` +
    (validationError
      ? 'border-red-400 bg-red-50 focus:ring-red-400'
      : 'border-slate-300 bg-white');

  return (
    <form onSubmit={handleSubmit} noValidate aria-label={`${mode === 'url' ? 'URL' : 'Message'} analysis form`}>
      <div className="space-y-3">
        <label
          htmlFor={`${mode}-input`}
          className="block text-sm font-medium text-slate-700"
        >
          {copy.label}
        </label>

        {mode === 'url' ? (
          <input
            ref={inputRef as React.RefObject<HTMLInputElement>}
            id="url-input"
            type="url"
            autoComplete="off"
            spellCheck={false}
            value={value}
            maxLength={URL_MAX}
            onChange={(e) => {
              setValue(e.target.value);
              if (touched) setSubmitError(null);
            }}
            onBlur={() => setTouched(true)}
            placeholder={copy.placeholder}
            aria-describedby={`${validationError ? errorId + ' ' : ''}${hintId} ${countId}`}
            aria-invalid={validationError ? 'true' : undefined}
            className={inputClassName}
            disabled={loading}
          />
        ) : (
          <textarea
            ref={inputRef as React.RefObject<HTMLTextAreaElement>}
            id="message-input"
            rows={6}
            value={value}
            maxLength={MSG_MAX}
            onChange={(e) => {
              setValue(e.target.value);
              if (touched) setSubmitError(null);
            }}
            onBlur={() => setTouched(true)}
            onKeyDown={handleKeyDown}
            placeholder={copy.placeholder}
            aria-describedby={`${validationError ? errorId + ' ' : ''}${hintId} ${countId}`}
            aria-invalid={validationError ? 'true' : undefined}
            className={`${inputClassName} resize-none font-mono leading-relaxed`}
            disabled={loading}
          />
        )}

        <div className="flex items-start justify-between gap-3">
          <div className="flex flex-col gap-1">
            {validationError && (
              <p id={errorId} role="alert" className="text-xs text-red-600">
                {validationError}
              </p>
            )}
            <p id={hintId} className="text-xs text-slate-500">
              {copy.hint}
              {mode === 'message' && (
                <span className="ml-1 text-slate-400">(Ctrl+Enter to submit)</span>
              )}
            </p>
          </div>
          <p
            id={countId}
            aria-live="polite"
            className={`shrink-0 text-xs tabular-nums ${
              value.length > max * 0.9 ? 'text-amber-600' : 'text-slate-400'
            }`}
          >
            {value.length.toLocaleString()}/{max.toLocaleString()}
          </p>
        </div>

        {submitError && (
          <Alert variant="error">
            <strong>Error:</strong> {submitError}
          </Alert>
        )}

        <Button type="submit" loading={loading} className="w-full sm:w-auto">
          {copy.submit}
        </Button>
      </div>
    </form>
  );
}
