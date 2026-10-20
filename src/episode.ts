import { z } from 'zod';

const identifier = z.string().regex(/^[a-z][a-z0-9-]*$/);
const finiteNonnegative = z.number().finite().nonnegative();
const finitePositive = z.number().finite().positive();

export const Evidence = z.strictObject({
  id: identifier,
  title: z.string().min(1),
  publisher: z.string().min(1),
  url: z.url().refine((value) => value.startsWith('https://'), 'Evidence URL must use HTTPS'),
  accessedAt: z.iso.date(),
  passage: z.string().min(1),
  locator: z.string().min(1).optional(),
});

const BinarySearchCapacity = z.strictObject({
  type: z.literal('binary-search-capacity'),
  universeSize: z.number().int().safe().min(2),
  questions: z.number().int().min(1).max(64),
  strategy: z.literal('balanced'),
});

const OperationCount = z.strictObject({
  type: z.literal('operation-count'),
  n: z.number().int().safe().min(1),
  growth: z.enum(['linear', 'quadratic', 'pairs', 'set-scan']),
  steps: z.number().int().safe().min(1).optional(),
  stepsApprox: z.number().positive().optional(),
  stepsPerSecond: z.number().positive().optional(),
  seconds: z.number().positive().optional(),
  years: z.number().positive().optional(),
});

export const Claim = z.strictObject({
  id: identifier,
  text: z.string().min(1),
  kind: z.enum(['sourced', 'derived']),
  evidenceIds: z.array(identifier),
  assumptions: z.array(z.string().min(1)),
  limitations: z.array(z.string().min(1)),
  check: z.union([BinarySearchCapacity, OperationCount]).optional(),
});

export const Beat = z.strictObject({
  id: identifier,
  start: finiteNonnegative,
  duration: finitePositive,
  narration: z.string().min(1),
  delivery: z.strictObject({
    style: z.string().min(1),
    geminiStyle: z.string().min(1).optional(),
    localSpeed: z.number().finite().min(0.8).max(1.3).optional(),
  }).optional(),
  onScreen: z.string().min(1),
  visual: z.strictObject({
    template: identifier,
    parameters: z.record(z.string(), z.union([z.string(), z.number().finite(), z.boolean()])),
  }),
  claimIds: z.array(identifier),
});

export const Episode = z.strictObject({
  schemaVersion: z.literal(2),
  slug: identifier,
  // A BCP 47 language tag such as "en", "es" or "pt-BR". Narration and captions use this language.
  language: z.string().regex(/^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$/, 'Use a language tag such as "en" or "pt-BR"'),
  audience: z.string().min(1),
  subject: z.string().min(1),
  question: z.string().min(1),
  payoff: z.string().min(1),
  conceptReveal: z.strictObject({
    name: z.string().min(1),
    beatId: identifier,
  }),
  brandVersion: z.string().min(1),
  templateVersion: z.string().min(1),
  durationSeconds: finitePositive.max(180),
  evidence: z.array(Evidence),
  claims: z.array(Claim).min(1),
  beats: z.array(Beat).min(1),
});

export type Episode = z.infer<typeof Episode>;

export type ValidationIssue = { code: string; message: string; path?: string };
export type ValidationResult = { valid: boolean; issues: ValidationIssue[]; episode?: Episode };

/** Every string still containing a TODO marker from the new-reel template. */
function todoPaths(value: unknown, path: string[] = []): string[] {
  if (typeof value === 'string') return value.includes('TODO') ? [path.join('.')] : [];
  if (Array.isArray(value)) return value.flatMap((item, index) => todoPaths(item, [...path, String(index)]));
  if (value && typeof value === 'object') return Object.entries(value).flatMap(([key, item]) => todoPaths(item, [...path, key]));
  return [];
}

function uniqueIds(items: ReadonlyArray<{ id: string }>, path: string, issues: ValidationIssue[]): void {
  const seen = new Set<string>();
  for (const item of items) {
    if (seen.has(item.id)) issues.push({ code: 'DUPLICATE_ID', path, message: `Duplicate ID: ${item.id}` });
    seen.add(item.id);
  }
}

function verifyBinarySearchCapacity(check: z.infer<typeof BinarySearchCapacity>): boolean {
  const n = BigInt(check.universeSize);
  const capacity = 1n << BigInt(check.questions);
  const previousCapacity = capacity >> 1n;
  return previousCapacity < n && n <= capacity;
}

const SECONDS_PER_YEAR = 365.25 * 24 * 3600;
const closeTo = (actual: number, expected: number): boolean => Math.abs(actual - expected) <= expected * 0.005;

/** Exact step counts and, when a rate is stated, the run time those steps imply. */
function verifyOperationCount(check: z.infer<typeof OperationCount>): boolean {
  const n = BigInt(check.n);
  const exact = check.growth === 'linear' ? n
    : check.growth === 'quadratic' ? n * n
    : check.growth === 'set-scan' ? 2n * n
    : n * (n - 1n) / 2n;
  if (check.steps !== undefined && BigInt(check.steps) !== exact) return false;
  // Counts above 2^53 cannot be written as exact JSON integers; state them approximately.
  if (check.stepsApprox !== undefined && !closeTo(check.stepsApprox, Number(exact))) return false;
  if (check.steps === undefined && check.stepsApprox === undefined) return false;
  if (check.seconds !== undefined || check.years !== undefined) {
    if (check.stepsPerSecond === undefined) return false;
    const seconds = Number(exact) / check.stepsPerSecond;
    if (check.seconds !== undefined && !closeTo(check.seconds, seconds)) return false;
    if (check.years !== undefined && !closeTo(check.years, seconds / SECONDS_PER_YEAR)) return false;
  }
  return true;
}

/** Structural and deterministic truth checks. This does not approve a claim for publication. */
export function validateEpisode(input: unknown): ValidationResult {
  const parsed = Episode.safeParse(input);
  if (!parsed.success) {
    return {
      valid: false,
      issues: parsed.error.issues.map((issue) => ({
        code: 'SCHEMA',
        path: issue.path.join('.'),
        message: issue.message,
      })),
    };
  }

  const episode = parsed.data;
  const issues: ValidationIssue[] = todoPaths(episode).map((path) => ({
    code: 'TODO_LEFT', path, message: 'Replace the TODO placeholder with real content.',
  }));
  uniqueIds(episode.evidence, 'evidence', issues);
  uniqueIds(episode.claims, 'claims', issues);
  uniqueIds(episode.beats, 'beats', issues);
  const evidenceIds = new Set(episode.evidence.map((item) => item.id));
  const claimIds = new Set(episode.claims.map((item) => item.id));
  const visualizedClaims = new Set(episode.beats.flatMap((item) => item.claimIds));
  const revealBeat = episode.beats.find((beat) => beat.id === episode.conceptReveal.beatId);
  if (!revealBeat) {
    issues.push({ code: 'MISSING_CONCEPT_REVEAL', path: 'conceptReveal.beatId', message: 'Concept reveal must reference a beat.' });
  } else {
    const lower = (text: string) => text.toLocaleLowerCase(episode.language);
    const concept = lower(episode.conceptReveal.name);
    if (!lower(revealBeat.narration).includes(concept) || !lower(revealBeat.onScreen).includes(concept)) {
      issues.push({ code: 'MISSING_CONCEPT_REVEAL', path: `beats.${revealBeat.id}`, message: 'Reveal beat must name the concept in narration and on screen.' });
    }
    if (episode.beats.indexOf(revealBeat) < 2) {
      issues.push({ code: 'EARLY_CONCEPT_REVEAL', path: `beats.${revealBeat.id}`, message: 'Show the concrete reasoning before naming the concept.' });
    }
  }

  for (const claim of episode.claims) {
    if (claim.kind === 'sourced' && claim.evidenceIds.length === 0) {
      issues.push({ code: 'MISSING_EVIDENCE', path: `claims.${claim.id}`, message: 'Sourced claim needs evidence.' });
    }
    if (claim.kind === 'derived' && !claim.check) {
      issues.push({ code: 'MISSING_CHECK', path: `claims.${claim.id}`, message: 'Derived claim needs a deterministic check.' });
    }
    for (const id of claim.evidenceIds) {
      if (!evidenceIds.has(id)) issues.push({ code: 'UNKNOWN_EVIDENCE', path: `claims.${claim.id}`, message: `Unknown evidence: ${id}` });
    }
    if (claim.check?.type === 'binary-search-capacity' && !verifyBinarySearchCapacity(claim.check)) {
      issues.push({ code: 'FAILED_CHECK', path: `claims.${claim.id}`, message: 'Binary search capacity does not match the claimed minimal number of balanced yes/no questions.' });
    }
    if (claim.check?.type === 'operation-count' && !verifyOperationCount(claim.check)) {
      issues.push({ code: 'FAILED_CHECK', path: `claims.${claim.id}`, message: 'Operation count or implied run time does not match the stated growth, input size, and step rate.' });
    }
    if (!visualizedClaims.has(claim.id)) {
      issues.push({ code: 'UNVISUALIZED_CLAIM', path: `claims.${claim.id}`, message: 'Claim is not mapped to a visual beat.' });
    }
  }

  for (const beat of episode.beats) {
    for (const id of beat.claimIds) {
      if (!claimIds.has(id)) issues.push({ code: 'UNKNOWN_CLAIM', path: `beats.${beat.id}`, message: `Unknown claim: ${id}` });
    }
  }

  const tolerance = 0.001;
  let cursor = 0;
  for (const beat of episode.beats) {
    if (Math.abs(beat.start - cursor) > tolerance) {
      issues.push({ code: 'TIMELINE_GAP_OR_OVERLAP', path: `beats.${beat.id}`, message: `Beat must start at ${cursor} seconds.` });
    }
    cursor = beat.start + beat.duration;
  }
  if (Math.abs(cursor - episode.durationSeconds) > tolerance) {
    issues.push({ code: 'TIMELINE_END', path: 'durationSeconds', message: `Beats end at ${cursor}, not ${episode.durationSeconds}.` });
  }

  return { valid: issues.length === 0, issues, episode };
}
