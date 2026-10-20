import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import { validateEpisode } from '../src/episode.js';

const load = async (path: string) => JSON.parse(await readFile(new URL(`../../${path}`, import.meta.url), 'utf8'));
const race = await load('examples/time-complexity-45/episode.json');
const loops = await load('examples/time-complexity-loops/episode.json');
// `npm run reel -- new <name>` fills in the slug; everything else is left for the creator.
const template = JSON.parse(JSON.stringify(await load('templates/reel/episode.json')).replaceAll('__SLUG__', 'my-reel'));

type Claim = { id: string; kind: string; check?: Record<string, unknown> };
const claim = (episode: { claims: Claim[] }, id: string) => {
  const found = episode.claims.find((item) => item.id === id);
  assert.ok(found, `missing claim ${id}`);
  return found;
};
const codes = (episode: unknown) => validateEpisode(episode).issues.map((issue) => issue.code);

test('shipped examples pass deterministic validation', () => {
  assert.deepEqual(validateEpisode(race).issues, []);
  assert.deepEqual(validateEpisode(loops).issues, []);
});

test('incorrect binary-search capacity is rejected', () => {
  const episode = structuredClone(race);
  claim(episode, 'twenty-halvings').check!.questions = 19;
  assert.ok(codes(episode).includes('FAILED_CHECK'));
});

test('sourced claim without evidence is rejected', () => {
  const episode = structuredClone(race);
  const target = claim(episode, 'twenty-halvings');
  target.kind = 'sourced';
  delete target.check;
  assert.ok(codes(episode).includes('MISSING_EVIDENCE'));
});

test('derived claim without a check is rejected', () => {
  const episode = structuredClone(race);
  delete claim(episode, 'twenty-halvings').check;
  assert.ok(codes(episode).includes('MISSING_CHECK'));
});

test('timeline gaps and a wrong total are rejected', () => {
  const episode = structuredClone(race);
  episode.beats[1].start = 7;
  assert.ok(codes(episode).includes('TIMELINE_GAP_OR_OVERLAP'));
  const short = structuredClone(race);
  short.durationSeconds = 50;
  assert.ok(codes(short).includes('TIMELINE_END'));
});

test('unknown claim IDs and unvisualised claims are rejected', () => {
  const episode = structuredClone(race);
  episode.beats[0].claimIds = ['invented'];
  assert.ok(codes(episode).includes('UNKNOWN_CLAIM'));
  const hidden = structuredClone(race);
  for (const beat of hidden.beats) beat.claimIds = beat.claimIds.filter((id: string) => id !== 'big-o-name');
  assert.ok(codes(hidden).includes('UNVISUALIZED_CLAIM'));
});

test('concept reveal must be named in a late narration and visual beat', () => {
  const episode = structuredClone(race);
  const reveal = episode.beats.findIndex((beat: { id: string }) => beat.id === 'reveal');
  episode.beats[reveal].narration = 'And that is the whole trick.';
  assert.ok(codes(episode).includes('MISSING_CONCEPT_REVEAL'));
  const early = structuredClone(race);
  early.beats[0].narration += ' This is time complexity.';
  early.beats[0].onScreen += ' time complexity';
  early.conceptReveal.beatId = 'hook';
  assert.ok(codes(early).includes('EARLY_CONCEPT_REVEAL'));
});

test('operation-count checks accept exact counts and stated-rate run times', () => {
  const episode = structuredClone(race);
  const target = claim(episode, 'twenty-halvings');
  target.check = { type: 'operation-count', n: 1000, growth: 'quadratic', steps: 1000000 };
  assert.deepEqual(validateEpisode(episode).issues, []);
  target.check = { type: 'operation-count', n: 1000000000, growth: 'quadratic', stepsApprox: 1e18, stepsPerSecond: 2e8, years: 158.4 };
  assert.deepEqual(validateEpisode(episode).issues, []);
});

test('operation-count checks reject wrong counts and unstated rates', () => {
  const episode = structuredClone(race);
  const target = claim(episode, 'twenty-halvings');
  target.check = { type: 'operation-count', n: 1000, growth: 'quadratic', steps: 100000 };
  assert.ok(codes(episode).includes('FAILED_CHECK'));
  target.check = { type: 'operation-count', n: 1000, growth: 'linear', steps: 1000, seconds: 5 };
  assert.ok(codes(episode).includes('FAILED_CHECK'));
  target.check = { type: 'operation-count', n: 1000, growth: 'pairs', steps: 499500 };
  assert.deepEqual(validateEpisode(episode).issues, []);
});

test('duplicate comparison checks pair count and both set operations at one billion items', () => {
  const pair = claim(loops, 'billion-pairs').check!;
  const set = claim(loops, 'billion-set').check!;
  assert.equal(pair.growth, 'pairs');
  assert.equal(set.growth, 'set-scan');
  assert.ok(Math.abs(Number(pair.years) - 79.228) < 0.01);
  assert.equal(set.seconds, 10);
  const omittedInsertion = structuredClone(loops);
  claim(omittedInsertion, 'billion-set').check!.steps = 1_000_000_000;
  assert.ok(codes(omittedInsertion).includes('FAILED_CHECK'));
  const squaredPairs = structuredClone(loops);
  claim(squaredPairs, 'billion-pairs').check!.stepsApprox = 1e18;
  assert.ok(codes(squaredPairs).includes('FAILED_CHECK'));
});

test('the new-reel template is rejected until every TODO is replaced', () => {
  const issues = validateEpisode(template).issues;
  assert.ok(!issues.some((issue) => issue.code === 'SCHEMA'), 'the template itself must parse');
  assert.ok(issues.some((issue) => issue.path === 'beats.0.narration'));
});

test('episodes may use any language tag and any subject', () => {
  const episode = structuredClone(race);
  episode.language = 'pt-BR';
  episode.subject = 'history';
  assert.deepEqual(validateEpisode(episode).issues, []);
  episode.language = 'Portuguese';
  assert.ok(codes(episode).includes('SCHEMA'));
});
