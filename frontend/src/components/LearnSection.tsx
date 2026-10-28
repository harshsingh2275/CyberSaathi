/**
 * LearnSection — top-level educational content component for CyberSaathi AI (T-05).
 *
 * Layout:
 *   ┌─────────────────────────────────────────────────────────────────┐
 *   │ Tab bar: [Lessons] [Quiz]                                       │
 *   ├─────────────────────────────────────────────────────────────────┤
 *   │ Lessons view:                                                   │
 *   │   Horizontal scrollable lesson-picker + full LessonCard below  │
 *   ├─────────────────────────────────────────────────────────────────┤
 *   │ Quiz view:                                                      │
 *   │   QuizSection (one question at a time with feedback)            │
 *   └─────────────────────────────────────────────────────────────────┘
 *
 * The disclaimer strip at the bottom of each view makes clear that
 * awareness alone does not guarantee safety.
 */

import { useState } from 'react';
import { LESSONS } from '../data/lessons';
import { LessonCard } from './LessonCard';
import { QuizSection } from './QuizSection';
import type { Language } from '../types/api';

type ContentTab = 'lessons' | 'quiz';

interface LearnSectionProps {
  language: Language;
}

export function LearnSection({ language }: LearnSectionProps) {
  const isHi = language === 'hinglish';
  const [tab, setTab] = useState<ContentTab>('lessons');
  const [activeLessonId, setActiveLessonId] = useState<string>(LESSONS[0].id);

  const activeLesson = LESSONS.find((l) => l.id === activeLessonId) ?? LESSONS[0];

  return (
    <section aria-labelledby="learn-section-heading" className="space-y-5">
      {/* Section heading (screen-reader visible, visually compact) */}
      <h2
        id="learn-section-heading"
        className="text-xs font-semibold uppercase tracking-wider text-slate-500"
      >
        {isHi ? 'Cybersecurity Awareness' : 'Cybersecurity Awareness'}
      </h2>

      {/* Lessons / Quiz tab switcher */}
      <div
        role="tablist"
        aria-label={isHi ? 'Learning content tabs' : 'Learning content tabs'}
        className="flex rounded-lg border border-slate-200 bg-white overflow-hidden shadow-sm"
      >
        {(
          [
            { id: 'lessons' as ContentTab, labelEn: 'Lessons', labelHi: 'Lessons' },
            { id: 'quiz' as ContentTab, labelEn: 'Awareness Quiz', labelHi: 'Awareness Quiz' },
          ] as const
        ).map((t) => {
          const isActive = tab === t.id;
          return (
            <button
              key={t.id}
              role="tab"
              aria-selected={isActive}
              aria-controls={`learn-panel-${t.id}`}
              id={`learn-tab-${t.id}`}
              onClick={() => setTab(t.id)}
              className={`flex-1 px-4 py-3 text-sm font-semibold transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-slate-700 ${
                isActive
                  ? 'bg-slate-800 text-white'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              {isHi ? t.labelHi : t.labelEn}
            </button>
          );
        })}
      </div>

      {/* ── Lessons panel ─────────────────────────────────────────────────────── */}
      <div
        id="learn-panel-lessons"
        role="tabpanel"
        aria-labelledby="learn-tab-lessons"
        hidden={tab !== 'lessons'}
        className="space-y-4"
      >
        {/* Lesson picker — horizontal scroll on small screens */}
        <nav
          aria-label={isHi ? 'Sabak list' : 'Lesson list'}
          className="flex gap-2 overflow-x-auto pb-1 -mx-0.5 px-0.5"
          style={{ scrollbarWidth: 'thin' }}
        >
          {LESSONS.map((lesson) => {
            const isActive = lesson.id === activeLessonId;
            return (
              <button
                key={lesson.id}
                onClick={() => setActiveLessonId(lesson.id)}
                aria-pressed={isActive}
                aria-label={isHi ? lesson.titleHi : lesson.titleEn}
                className={`shrink-0 flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-700 ${
                  isActive
                    ? 'border-slate-700 bg-slate-800 text-white'
                    : 'border-slate-200 bg-white text-slate-600 hover:border-slate-400 hover:bg-slate-50'
                }`}
              >
                <span aria-hidden="true">{lesson.icon}</span>
                <span>{isHi ? lesson.titleHi : lesson.titleEn}</span>
              </button>
            );
          })}
        </nav>

        {/* Active lesson full card */}
        <LessonCard lesson={activeLesson} language={language} />

        {/* Awareness caveat */}
        <p className="text-xs text-slate-400 leading-relaxed border-t border-slate-100 pt-3">
          {isHi
            ? 'Yeh lessons awareness ke liye hain. In topics ko padhna aapko poori tarah cyber threats se protect nahi karta — hamesha specific situations mein sochna aur verify karna zaruri hai.'
            : 'These lessons are for awareness only. Reading them does not fully protect you from cyber threats — always think critically and verify in specific situations.'}
        </p>
      </div>

      {/* ── Quiz panel ────────────────────────────────────────────────────────── */}
      <div
        id="learn-panel-quiz"
        role="tabpanel"
        aria-labelledby="learn-tab-quiz"
        hidden={tab !== 'quiz'}
        className="space-y-4"
      >
        {/* Quiz intro */}
        <p className="text-sm text-slate-500">
          {isHi
            ? 'Apni cybersecurity awareness test karein. Har sawaal ka ek jawab chunein — phir explanation padein.'
            : 'Test your cybersecurity awareness. Select one answer per question, then read the explanation.'}
        </p>

        <QuizSection language={language} />

        {/* Persistent awareness caveat below quiz */}
        <p className="text-xs text-slate-400 leading-relaxed border-t border-slate-100 pt-3">
          {isHi
            ? 'Yeh ek educational quiz hai, certification nahi. Zyada score milna acha hai, lekin real scams hamesha evolve hoti rehti hain. Vigilant rehna ek habit hai, ek baar ki koshish nahi.'
            : 'This is an educational quiz, not a certification. A high score is encouraging, but real scams always evolve. Staying vigilant is a habit, not a one-time effort.'}
        </p>
      </div>
    </section>
  );
}
