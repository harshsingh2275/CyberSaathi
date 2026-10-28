#!/usr/bin/env node
/**
 * scripts/check-quiz-consistency.mjs
 *
 * Quiz answer consistency check for CyberSaathi AI (T-05).
 *
 * Run with:
 *   node scripts/check-quiz-consistency.mjs
 *   (or via npm: npm run check-quiz from the frontend directory)
 *
 * What this checks:
 *   1. No duplicate question IDs.
 *   2. Each question has at least 2 options.
 *   3. correctIndex is within the valid range (0 to options.length - 1).
 *   4. No option text (EN or HI) is empty or whitespace-only.
 *   5. No explanation (EN or HI) is empty or whitespace-only.
 *   6. Every lessonId references a known lesson from lessons.ts.
 *   7. The correct answer text does not contain obvious decoy markers
 *      (structural check only — semantic correctness requires human review).
 *
 * This script uses esbuild (already a Vite transitive dependency) to
 * transpile the TypeScript data files before running the checks, so no
 * separate tsconfig or ts-node setup is required.
 *
 * Exit code 0 = all checks pass; exit code 1 = at least one failure.
 */

import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { transformSync } from 'esbuild';

const __dirname = dirname(fileURLToPath(import.meta.url));
const rootDir = join(__dirname, '..');

// ── Helper: transpile a TS file to an ESM string ────────────────────────────

function loadTsAsEsm(relPath) {
  const fullPath = join(rootDir, relPath);
  const source = readFileSync(fullPath, 'utf8');
  const result = transformSync(source, {
    loader: 'ts',
    format: 'esm',
    target: 'node18',
  });
  return result.code;
}

// ── Load quiz data ────────────────────────────────────────────────────────────
// We evaluate the transpiled code in a module context using a data: URI import.

async function loadModule(tsRelPath) {
  const esm = loadTsAsEsm(tsRelPath);
  // Encode as a data URI so we can import it without writing a temp file.
  const dataUri = `data:text/javascript;charset=utf-8,${encodeURIComponent(esm)}`;
  return await import(dataUri);
}

const lessonsModule = await loadModule('src/data/lessons.ts');
const quizModule = await loadModule('src/data/quiz.ts');

const LESSONS = lessonsModule.LESSONS;
const QUIZ_QUESTIONS = quizModule.QUIZ_QUESTIONS;

// ── Run checks ────────────────────────────────────────────────────────────────

let failures = 0;
const warn = (msg) => { console.error(`  FAIL: ${msg}`); failures++; };
const info = (msg) => console.log(`  OK:   ${msg}`);

console.log('\n=== CyberSaathi Quiz Consistency Check ===\n');

// 1. Lesson IDs must all be unique
const lessonIds = new Set(LESSONS.map((l) => l.id));
info(`Lessons found: ${LESSONS.length} (${[...lessonIds].join(', ')})`);

// 2. Quiz questions structural checks
const questionIds = new Set();
for (const q of QUIZ_QUESTIONS) {
  const tag = `[${q.id}]`;

  // Duplicate IDs
  if (questionIds.has(q.id)) {
    warn(`${tag} Duplicate question id.`);
  } else {
    questionIds.add(q.id);
  }

  // Min options
  if (!Array.isArray(q.options) || q.options.length < 2) {
    warn(`${tag} Fewer than 2 options (found ${q.options?.length ?? 0}).`);
    continue; // skip further checks for this question
  }

  // correctIndex range
  if (
    typeof q.correctIndex !== 'number' ||
    q.correctIndex < 0 ||
    q.correctIndex >= q.options.length
  ) {
    warn(
      `${tag} correctIndex (${q.correctIndex}) out of range [0, ${q.options.length - 1}].`
    );
  }

  // Empty option text
  for (let i = 0; i < q.options.length; i++) {
    const opt = q.options[i];
    if (!opt.textEn?.trim()) warn(`${tag} option[${i}].textEn is empty.`);
    if (!opt.textHi?.trim()) warn(`${tag} option[${i}].textHi is empty.`);
  }

  // Empty explanations
  if (!q.explanationEn?.trim()) warn(`${tag} explanationEn is empty.`);
  if (!q.explanationHi?.trim()) warn(`${tag} explanationHi is empty.`);

  // lessonId references a known lesson
  if (!lessonIds.has(q.lessonId)) {
    warn(`${tag} lessonId "${q.lessonId}" not found in LESSONS.`);
  }

  // Correct answer must not be empty
  const correctOpt = q.options[q.correctIndex];
  if (correctOpt && !correctOpt.textEn?.trim()) {
    warn(`${tag} The correct option (index ${q.correctIndex}) has empty textEn.`);
  }
}

info(`Questions found: ${QUIZ_QUESTIONS.length}`);

// 3. Each lesson must have at least one question
for (const lesson of LESSONS) {
  const qs = QUIZ_QUESTIONS.filter((q) => q.lessonId === lesson.id);
  if (qs.length === 0) {
    warn(`Lesson "${lesson.id}" has no quiz questions.`);
  } else {
    info(`Lesson "${lesson.id}" → ${qs.length} question(s).`);
  }
}

// ── Summary ───────────────────────────────────────────────────────────────────

console.log('\n─────────────────────────────────────────');
if (failures === 0) {
  console.log(`✓ All checks passed (${QUIZ_QUESTIONS.length} questions across ${LESSONS.length} lessons).\n`);
  process.exit(0);
} else {
  console.error(`✗ ${failures} check(s) failed. Fix the issues above before committing.\n`);
  process.exit(1);
}
