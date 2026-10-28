/**
 * QuizSection — interactive awareness quiz for CyberSaathi AI (T-05).
 *
 * Design principles:
 *  - One question visible at a time with Previous/Next navigation.
 *  - Immediate per-answer feedback: correct (green) or incorrect (red),
 *    with the correct answer highlighted when wrong.
 *  - Explanation shown after any answer is selected.
 *  - Final score screen after the last question.
 *  - Explicit disclaimer: completing the quiz does not make the user safe.
 *  - No external API; all data is from quiz.ts.
 *  - Fully keyboard accessible (radio group pattern).
 *
 * Accessibility:
 *  - Questions are <fieldset>/<legend> radio groups.
 *  - Feedback region uses aria-live="polite".
 *  - Navigation buttons are standard <button> elements.
 *  - Score screen is announced via aria-live.
 */

import { useState } from 'react';
import { QUIZ_QUESTIONS } from '../data/quiz';
import type { Language } from '../types/api';

// ── Sub-components ─────────────────────────────────────────────────────────────

function ProgressBar({ current, total }: { current: number; total: number }) {
  const pct = Math.round((current / total) * 100);
  return (
    <div
      className="w-full bg-slate-100 rounded-full h-1.5"
      role="progressbar"
      aria-valuenow={current}
      aria-valuemin={0}
      aria-valuemax={total}
      aria-label={`Question ${current} of ${total}`}
    >
      <div
        className="bg-slate-700 h-1.5 rounded-full transition-all duration-300"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

// ── Main component ─────────────────────────────────────────────────────────────

interface QuizSectionProps {
  language: Language;
}

type AnswerMap = Record<string, number>; // questionId → chosen option index

export function QuizSection({ language }: QuizSectionProps) {
  const isHi = language === 'hinglish';
  const total = QUIZ_QUESTIONS.length;

  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState<AnswerMap>({});
  const [quizDone, setQuizDone] = useState(false);
  const [showReview, setShowReview] = useState(false);

  const question = QUIZ_QUESTIONS[currentIdx];
  const chosenIndex = answers[question.id] ?? -1;
  const hasAnswered = chosenIndex !== -1;
  const isCorrect = hasAnswered && chosenIndex === question.correctIndex;

  // Count correct answers (only questions that have been answered)
  const score = Object.entries(answers).filter(([qid, chosen]) => {
    const q = QUIZ_QUESTIONS.find((q) => q.id === qid);
    return q != null && chosen === q.correctIndex;
  }).length;

  function handleSelect(optionIdx: number) {
    if (hasAnswered) return; // prevent changing answer after selection
    setAnswers((prev) => ({ ...prev, [question.id]: optionIdx }));
  }

  function handleNext() {
    if (currentIdx < total - 1) {
      setCurrentIdx((i) => i + 1);
    } else {
      setQuizDone(true);
    }
  }

  function handlePrev() {
    if (currentIdx > 0) setCurrentIdx((i) => i - 1);
  }

  function handleRestart() {
    setAnswers({});
    setCurrentIdx(0);
    setQuizDone(false);
    setShowReview(false);
  }

  // ── Score screen ────────────────────────────────────────────────────────────
  if (quizDone && !showReview) {
    const pct = Math.round((score / total) * 100);
    return (
      <div
        className="rounded-lg border border-slate-200 bg-white shadow-sm p-6 space-y-5"
        aria-live="polite"
      >
        <div className="text-center space-y-2">
          <div className="text-4xl font-bold text-slate-900">
            {score}/{total}
          </div>
          <p className="text-sm text-slate-500">
            {isHi ? `Aapne ${pct}% sawaal sahi kiye.` : `You answered ${pct}% of questions correctly.`}
          </p>
        </div>

        {/* Non-guarantee disclaimer — always shown on score screen */}
        <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          <strong>
            {isHi ? 'Yaad rakhein: ' : 'Remember: '}
          </strong>
          {isHi
            ? 'Yeh quiz complete karna aapko cyber threats se safe nahi karta. Vigilance ek ongoing practice hai — sochte rahein aur hamesha suspicious offers verify karein.'
            : 'Completing this quiz does not make you immune to cyber threats. Vigilance is an ongoing practice — keep thinking critically and always verify suspicious offers.'}
        </div>

        <div className="flex flex-wrap gap-3 justify-center">
          <button
            onClick={() => setShowReview(true)}
            className="rounded-md border border-slate-300 bg-white px-5 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-500"
          >
            {isHi ? 'Jawab Review Karein' : 'Review Answers'}
          </button>
          <button
            onClick={handleRestart}
            className="rounded-md bg-slate-800 px-5 py-2 text-sm font-semibold text-white hover:bg-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-800"
          >
            {isHi ? 'Quiz Dobara Karein' : 'Retake Quiz'}
          </button>
        </div>
      </div>
    );
  }

  // ── Review screen ───────────────────────────────────────────────────────────
  if (quizDone && showReview) {
    return (
      <div className="space-y-5">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-500">
            {isHi ? 'Jawab Review' : 'Answer Review'}
          </h3>
          <button
            onClick={handleRestart}
            className="text-xs text-slate-500 underline hover:text-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-500"
          >
            {isHi ? 'Dobara Karein' : 'Restart'}
          </button>
        </div>
        {QUIZ_QUESTIONS.map((q, idx) => {
          const chosen = answers[q.id] ?? -1;
          const correct = chosen === q.correctIndex;
          return (
            <div
              key={q.id}
              className={`rounded-lg border p-4 space-y-3 text-sm ${
                correct
                  ? 'border-emerald-200 bg-emerald-50'
                  : 'border-red-200 bg-red-50'
              }`}
            >
              <p className="font-semibold text-slate-800">
                {idx + 1}. {isHi ? q.questionHi : q.questionEn}
              </p>
              <ul className="space-y-1">
                {q.options.map((opt, oi) => {
                  const isChosen = oi === chosen;
                  const isAnswer = oi === q.correctIndex;
                  let cls = 'text-slate-600';
                  if (isAnswer) cls = 'font-semibold text-emerald-800';
                  if (isChosen && !isAnswer) cls = 'font-semibold text-red-700 line-through';
                  return (
                    <li key={oi} className={cls}>
                      {isAnswer ? '✓ ' : isChosen ? '✗ ' : '  '}
                      {isHi ? opt.textHi : opt.textEn}
                    </li>
                  );
                })}
              </ul>
              <p className="text-slate-600 border-t border-slate-200 pt-2 leading-relaxed">
                {isHi ? q.explanationHi : q.explanationEn}
              </p>
            </div>
          );
        })}
        <button
          onClick={handleRestart}
          className="w-full rounded-md bg-slate-800 py-2.5 text-sm font-semibold text-white hover:bg-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-800"
        >
          {isHi ? 'Quiz Dobara Karein' : 'Retake Quiz'}
        </button>
      </div>
    );
  }

  // ── Question screen ─────────────────────────────────────────────────────────
  return (
    <div className="space-y-5">
      {/* Progress */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-xs text-slate-400">
          <span>
            {isHi
              ? `Sawaal ${currentIdx + 1} / ${total}`
              : `Question ${currentIdx + 1} of ${total}`}
          </span>
          {Object.keys(answers).length > 0 && (
            <span>
              {isHi
                ? `${score} sahi`
                : `${score} correct`}
            </span>
          )}
        </div>
        <ProgressBar current={currentIdx + 1} total={total} />
      </div>

      {/* Question card */}
      <div className="rounded-lg border border-slate-200 bg-white shadow-sm">
        <fieldset className="p-5 space-y-4">
          <legend className="text-sm font-semibold text-slate-900 leading-relaxed w-full">
            {isHi ? question.questionHi : question.questionEn}
          </legend>

          {/* Options */}
          <div className="space-y-2" role="group" aria-label={isHi ? 'Jawab chunein' : 'Choose an answer'}>
            {question.options.map((opt, oi) => {
              const isChosen = chosenIndex === oi;
              const isAnswer = oi === question.correctIndex;

              // Colour scheme after answering
              let optionStyle =
                'border-slate-200 bg-white hover:bg-slate-50 text-slate-700';
              if (hasAnswered) {
                if (isAnswer) {
                  optionStyle = 'border-emerald-400 bg-emerald-50 text-emerald-900';
                } else if (isChosen) {
                  optionStyle = 'border-red-400 bg-red-50 text-red-900';
                } else {
                  optionStyle = 'border-slate-200 bg-white text-slate-400';
                }
              } else if (isChosen) {
                optionStyle = 'border-slate-500 bg-slate-50 text-slate-900';
              }

              return (
                <label
                  key={oi}
                  className={`flex items-start gap-3 rounded-md border px-4 py-3 text-sm cursor-pointer transition-colors ${optionStyle} ${
                    hasAnswered ? 'cursor-default' : ''
                  }`}
                >
                  <input
                    type="radio"
                    name={`q-${question.id}`}
                    value={oi}
                    checked={isChosen}
                    disabled={hasAnswered}
                    onChange={() => handleSelect(oi)}
                    className="mt-0.5 shrink-0 accent-slate-700"
                    aria-describedby={hasAnswered ? `feedback-${question.id}` : undefined}
                  />
                  <span className="leading-relaxed">{isHi ? opt.textHi : opt.textEn}</span>
                  {hasAnswered && isAnswer && (
                    <span className="ml-auto shrink-0 text-emerald-700 font-bold" aria-hidden="true">
                      ✓
                    </span>
                  )}
                  {hasAnswered && isChosen && !isAnswer && (
                    <span className="ml-auto shrink-0 text-red-700 font-bold" aria-hidden="true">
                      ✗
                    </span>
                  )}
                </label>
              );
            })}
          </div>
        </fieldset>

        {/* Feedback region — appears after selection */}
        {hasAnswered && (
          <div
            id={`feedback-${question.id}`}
            aria-live="polite"
            className={`border-t px-5 py-4 text-sm leading-relaxed space-y-2 ${
              isCorrect
                ? 'border-emerald-200 bg-emerald-50'
                : 'border-red-200 bg-red-50'
            }`}
          >
            <p
              className={`font-semibold ${
                isCorrect ? 'text-emerald-800' : 'text-red-800'
              }`}
            >
              {isCorrect
                ? isHi
                  ? '✓ Sahi Jawab!'
                  : '✓ Correct!'
                : isHi
                ? '✗ Galat Jawab'
                : '✗ Incorrect'}
            </p>
            <p className="text-slate-700">
              {isHi ? question.explanationHi : question.explanationEn}
            </p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between gap-3">
        <button
          onClick={handlePrev}
          disabled={currentIdx === 0}
          className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:pointer-events-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-500"
        >
          {isHi ? '← Pichla' : '← Previous'}
        </button>

        <button
          onClick={handleNext}
          disabled={!hasAnswered}
          className="rounded-md bg-slate-800 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700 disabled:opacity-40 disabled:pointer-events-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-800"
        >
          {currentIdx < total - 1
            ? isHi
              ? 'Agla →'
              : 'Next →'
            : isHi
            ? 'Natija Dekhein'
            : 'See Results'}
        </button>
      </div>

      {/* Unanswered hint */}
      {!hasAnswered && (
        <p className="text-xs text-center text-slate-400" aria-live="polite">
          {isHi
            ? 'Aage badhne ke liye ek jawab chunein.'
            : 'Select an answer to continue.'}
        </p>
      )}
    </div>
  );
}
