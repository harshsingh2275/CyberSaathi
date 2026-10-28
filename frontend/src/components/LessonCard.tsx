/**
 * LessonCard — displays a single lesson as a list of expandable steps.
 *
 * Navigation:
 *  - Each step is shown in full (no accordion needed given compact content).
 *  - The parent controls which lesson is displayed via the `lesson` prop.
 *
 * Accessibility:
 *  - Section headings use <h3>/<h4> so they fit into the App's heading
 *    hierarchy (App h1 → LearnSection h2 → LessonCard h3/h4).
 *  - No interactive elements beyond the step list itself.
 */

import type { Lesson } from '../data/lessons';
import type { Language } from '../types/api';

interface LessonCardProps {
  lesson: Lesson;
  language: Language;
}

export function LessonCard({ lesson, language }: LessonCardProps) {
  const isHi = language === 'hinglish';

  return (
    <article
      aria-labelledby={`lesson-title-${lesson.id}`}
      className="rounded-lg border border-slate-200 bg-white shadow-sm overflow-hidden"
    >
      {/* Lesson header */}
      <div className="bg-slate-50 border-b border-slate-200 px-5 py-4 flex items-start gap-3">
        <span aria-hidden="true" className="text-2xl leading-none mt-0.5">
          {lesson.icon}
        </span>
        <div>
          <h3
            id={`lesson-title-${lesson.id}`}
            className="text-base font-bold text-slate-900 leading-snug"
          >
            {isHi ? lesson.titleHi : lesson.titleEn}
          </h3>
          <p className="text-sm text-slate-500 mt-0.5">
            {isHi ? lesson.summaryHi : lesson.summaryEn}
          </p>
        </div>
      </div>

      {/* Steps */}
      <ol className="divide-y divide-slate-100">
        {lesson.steps.map((step, idx) => (
          <li key={idx} className="px-5 py-4">
            <h4 className="text-sm font-semibold text-slate-800 mb-1">
              {isHi ? step.headingHi : step.headingEn}
            </h4>
            <p className="text-sm text-slate-600 leading-relaxed">
              {isHi ? step.bodyHi : step.bodyEn}
            </p>
          </li>
        ))}
      </ol>
    </article>
  );
}
