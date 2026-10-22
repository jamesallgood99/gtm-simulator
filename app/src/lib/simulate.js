import { callClaude, toolInput, pool, text } from './anthropic.js';
import { scoreSystem, scoreUser, SCORE_TOOL, stressSystem, stressUser, STRESS_TOOL, talkSystem } from './prompts.js';

const BATCH = 20;

/** Score one or more variants against the same persona sample. */
export async function runScore({ settings, market, product, variants, sample, onProgress, signal }) {
  const batches = [];
  for (let i = 0; i < sample.length; i += BATCH) batches.push(sample.slice(i, i + BATCH));
  const total = variants.length * batches.length;
  let done = 0;

  const jobs = [];
  for (const v of variants) {
    for (const batch of batches) {
      jobs.push(async () => {
        const res = await callClaude({
          apiKey: settings.apiKey,
          model: settings.model,
          system: scoreSystem(market),
          messages: [{ role: 'user', content: scoreUser({ message: v.message, variantName: v.name, product, personas: batch }) }],
          tools: [SCORE_TOOL],
          toolChoice: { type: 'tool', name: SCORE_TOOL.name },
          maxTokens: 6000,
          signal,
        });
        const ids = new Set(batch.map((p) => p.id));
        const rows = (toolInput(res, SCORE_TOOL.name).results ?? [])
          .filter((r) => ids.has(r.persona_id))
          .map((r) => ({ ...r, score: Math.max(0, Math.min(100, Math.round(Number(r.score)))) }));
        return { variant: v.id, rows };
      });
    }
  }
  const out = await pool(jobs, settings.concurrency ?? 3, () => onProgress?.(++done, total));
  const results = Object.fromEntries(variants.map((v) => [v.id, []]));
  for (const { variant, rows } of out) results[variant].push(...rows);
  return results;
}

export async function runStress({ settings, market, product, claim, critics, signal }) {
  const res = await callClaude({
    apiKey: settings.apiKey,
    model: settings.model,
    system: stressSystem(market),
    messages: [{ role: 'user', content: stressUser({ claim, product, personas: critics }) }],
    tools: [STRESS_TOOL],
    toolChoice: { type: 'tool', name: STRESS_TOOL.name },
    maxTokens: 4000,
    signal,
  });
  return { claim, ...toolInput(res, STRESS_TOOL.name) };
}

export async function runTalk({ settings, market, product, persona, transcript, signal }) {
  const messages = transcript.map((t) => ({ role: t.role === 'user' ? 'user' : 'assistant', content: t.text }));
  const res = await callClaude({
    apiKey: settings.apiKey,
    model: settings.model,
    system: talkSystem(persona, product),
    messages,
    maxTokens: 600,
    signal,
  });
  return text(res);
}

// ---- CSV import/export so runs from the Claude skill and the dashboard are interchangeable ----

const COLS = ['persona_id', 'role', 'industry', 'size_band', 'pain_level', 'variant', 'score', 'confidence', 'reaction', 'objection'];

export function resultsToCsv(results, personasById) {
  const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
  const lines = [COLS.join(',')];
  for (const [variant, rows] of Object.entries(results)) {
    for (const r of rows) {
      const p = personasById[r.persona_id] ?? {};
      lines.push([r.persona_id, p.role_label, p.industry, p.size_band, p.pain_level, variant, r.score, r.confidence, r.reaction, r.objection].map(esc).join(','));
    }
  }
  return lines.join('\n');
}

export function parseCsv(textIn) {
  const rows = [];
  let row = [];
  let cell = '';
  let quoted = false;
  for (let i = 0; i < textIn.length; i++) {
    const c = textIn[i];
    if (quoted) {
      if (c === '"' && textIn[i + 1] === '"') { cell += '"'; i++; }
      else if (c === '"') quoted = false;
      else cell += c;
    } else if (c === '"') quoted = true;
    else if (c === ',') { row.push(cell); cell = ''; }
    else if (c === '\n' || c === '\r') {
      if (c === '\r' && textIn[i + 1] === '\n') i++;
      row.push(cell); rows.push(row); row = []; cell = '';
    } else cell += c;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  const [head, ...body] = rows.filter((r) => r.some((c) => c.trim()));
  const idx = Object.fromEntries(head.map((h, i) => [h.trim().toLowerCase(), i]));
  for (const need of ['persona_id', 'variant', 'score']) {
    if (!(need in idx)) throw new Error(`The CSV needs a "${need}" column.`);
  }
  const results = {};
  for (const r of body) {
    const v = r[idx.variant].trim();
    (results[v] ??= []).push({
      persona_id: r[idx.persona_id].trim(),
      score: Math.round(Number(r[idx.score])),
      confidence: (r[idx.confidence] ?? 'medium').trim() || 'medium',
      reaction: r[idx.reaction] ?? '',
      objection: r[idx.objection] ?? '',
    });
  }
  return results;
}
