import React, { useEffect, useMemo, useRef, useState } from 'react';
import { analyze } from '../lib/analysis.js';
import { analyzeCompetition } from '../lib/competition.js';
import { mean } from '../lib/stats.js';
import { Icon, variantVars } from './ui.jsx';

// Product tour for the public demo: an intro screen and the four features worth seeing.
// It opens on a first visit (or with ?tour in the URL), and the "Take the tour" button in the
// project ribbon reopens it. As you step through, the app behind it switches to that feature's view.
// Every number comes from the demo data, never from a live run, so the copy always matches.

const SEEN_KEY = 'gtm-tour-seen';
const seen = () => { try { return localStorage.getItem(SEEN_KEY) === '1'; } catch { return false; } };
const markSeen = () => { try { localStorage.setItem(SEEN_KEY, '1'); } catch { /* private mode: fine */ } };

function useTourFacts(market, demo, active) {
  return useMemo(() => {
    if (!active || !market || !demo) return null;
    const roleLabel = Object.fromEntries(market.roles.map((r) => [r.key, r.label]));
    const short = (k) => ({ it_manager: 'IT', safety_manager: 'Safety', worker: 'Workers', broker: 'Brokers', cfo: 'CFOs' })[k] ?? roleLabel[k];
    const plural = (k) => ({ broker: 'brokers', cfo: 'CFOs', it_manager: 'IT managers', safety_manager: 'safety managers', worker: 'frontline workers' })[k] ?? k;

    // Compare: the role-by-variant table and where the overall leader loses.
    const variants = demo.campaign.variants;
    const an = analyze(market, variants, demo.results);
    const roleRows = an?.matrix[0].rows ?? [];
    const lead = an?.winner.index ?? 0;
    const losses = roleRows
      .filter((r) => r.flagWinner)
      .map((r) => ({ role: r.key, by: Math.round(r.loss), to: variants[r.bestIdx] }));

    // Adoption: enthusiasm by role for the most divisive feature, and what fades or grows by month 12.
    const byId = Object.fromEntries(market.personas.map((p) => [p.id, p]));
    const features = demo.brief.features;
    const agg = {};
    for (const r of demo.adoption?.rows ?? []) {
      const role = byId[r.persona_id]?.role;
      if (role) ((agg[r.feature_id] ??= {})[role] ??= []).push(r);
    }
    const cell = (fid, role) => {
      const rs = agg[fid]?.[role] ?? [];
      return rs.length ? { enth: mean(rs.map((x) => x.enthusiasm)), a90: mean(rs.map((x) => x.adopt_90d)), a12: mean(rs.map((x) => x.adopt_12m)) } : null;
    };
    // Prefer a feature whose least enthusiastic role can veto the deal: that's the finding that matters.
    const VETO = ['broker', 'cfo', 'it_manager'];
    let divisive = null;
    for (const f of features) {
      const vals = market.roles.map((r) => ({ role: r.key, enth: cell(f.id, r.key)?.enth })).filter((x) => x.enth != null);
      if (!vals.length) continue;
      vals.sort((a, b) => b.enth - a.enth);
      const spread = vals[0].enth - vals.at(-1).enth;
      const rank = spread + (VETO.includes(vals.at(-1).role) ? 1000 : 0);
      if (!divisive || rank > divisive.rank) divisive = { f, spread, rank, top: vals[0].role, low: vals.at(-1).role, veto: VETO.includes(vals.at(-1).role) };
    }
    const enthRows = divisive
      ? market.roles.map((r) => ({ role: r.key, label: roleLabel[r.key], enth: Math.round(cell(divisive.f.id, r.key)?.enth ?? 0) }))
      : [];
    const moves = [];
    for (const f of features) for (const r of market.roles) {
      const c = cell(f.id, r.key);
      if (c && c.a90 >= 20) moves.push({ f, role: r.key, a90: Math.round(c.a90), a12: Math.round(c.a12), d: c.a12 - c.a90 });
    }
    moves.sort((a, b) => a.d - b.d);
    const fade = moves[0]?.d < 0 ? moves[0] : null;
    const grow = moves.at(-1)?.d > 0 ? moves.at(-1) : null;

    // Competition: the head-to-head record and the first findings.
    let comp = null;
    if (demo.competition) {
      const ca = analyzeCompetition(market, demo.brief, { ...demo.competition, source: 'demo' });
      comp = {
        ours: ca.ourName,
        record: ca.brands.filter((b) => b.id !== 'ours').map((b) => ({ name: b.name, ...(ca.record[b.id] ?? { win: 0, tie: 0, loss: 0 }) })),
        findings: ca.findings.slice(0, 2).map((x) => x.text),
        features: demo.competition.features.length,
      };
    }

    const claims = demo.brief.claims;
    const weakest = [...claims].sort((a, b) => a.proof_strength - b.proof_strength)[0];
    return {
      roles: market.roles.length,
      personas: market.personas.length,
      companies: market.companies.length,
      product: demo.brief.product_name,
      docs: demo.documents ?? [],
      features, claims, weakest, variants,
      compare: { roleRows, lead, losses, overall: an?.perVariant.map((p) => Math.round(p.mc.mean)) ?? [], short, plural },
      adoption: { feature: divisive?.f, top: divisive?.top, low: divisive?.low, veto: divisive?.veto, enthRows, fade, grow, plural },
      comp,
    };
  }, [market, demo, active]);
}

// ---------- visuals ----------
function IntroVisual({ t }) {
  const modes = [
    ['docs', 'Documents', 'Your PRD, MRD and brief become the test'],
    ['compare', 'Compare', 'Messages A, B and C, side by side'],
    ['talk', 'Talk', 'Interview one persona'],
    ['stress', 'Stress', 'Critics attack your weakest claim'],
    ['adopt', 'Adoption', 'Who keeps using each feature'],
    ['rival', 'Competition', 'Your copy against theirs, blind'],
  ];
  return (
    <div className="tv-intro">
      <div className="tv-market">
        <div className="tv-market-num">{t.personas}</div>
        <div className="tv-market-sub">AI buyer personas<br />at {t.companies} companies</div>
        <div className="tv-dots" aria-hidden="true">
          {Array.from({ length: 50 }, (_, i) => <span key={i} style={{ background: `var(--${['a', 'b', 'c', 'd', 'ink-3'][i % 5]})` }} />)}
        </div>
      </div>
      <ul className="tv-modes">
        {modes.map(([icon, name, what]) => (
          <li key={name}><Icon name={icon} /><b>{name}</b><span>{what}</span></li>
        ))}
      </ul>
    </div>
  );
}

function DocsVisual({ t }) {
  return (
    <div className="tv-flow">
      <div className="tv-col">
        <span className="tv-label">You upload</span>
        {t.docs.map((d) => <div key={d.path} className="tv-doc"><Icon name="docs" /><span><b>{d.type}</b>{d.name}</span></div>)}
      </div>
      <div className="tv-arrow" aria-hidden="true">→</div>
      <div className="tv-col">
        <span className="tv-label">Claude pulls out</span>
        <div className="tv-pull"><b>{t.features.length}</b> features, with who each is for</div>
        <div className="tv-pull"><b>{t.claims.length}</b> claims, proof rated 1 to 5</div>
        {t.weakest && <div className="tv-pull tv-weak"><b>{t.weakest.proof_strength}/5</b> {t.weakest.text}</div>}
      </div>
      <div className="tv-arrow" aria-hidden="true">→</div>
      <div className="tv-col">
        <span className="tv-label">And writes</span>
        {t.variants.map((v, i) => (
          <div key={v.id} className="tv-variant" style={variantVars(i)}><span className="tv-vid">{v.id}</span>{v.headline}</div>
        ))}
      </div>
    </div>
  );
}

function CompareVisual({ t }) {
  const { roleRows, lead, overall, short } = t.compare;
  return (
    <table className="tv-matrix">
      <thead>
        <tr><th scope="col">Mean score</th>{t.variants.map((v, i) => <th key={v.id} scope="col" style={variantVars(i)}><span className="tv-vid">{v.id}</span></th>)}</tr>
      </thead>
      <tbody>
        <tr className="tv-overall"><th scope="row">Everyone</th>{overall.map((s, i) => <td key={i} className={i === lead ? 'tv-lead' : ''}>{s}{i === lead && <small>leads</small>}</td>)}</tr>
        {roleRows.map((r) => (
          <tr key={r.key}>
            <th scope="row">{short(r.key)}</th>
            {r.cells.map((c, i) => (
              <td key={i} className={`${i === r.bestIdx ? 'tv-best' : ''} ${r.flagWinner && i === lead ? 'tv-flag' : ''}`} style={variantVars(i)}>
                {c ? Math.round(c.mean) : '–'}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function AdoptionVisual({ t }) {
  const { feature, enthRows, fade, grow } = t.adoption;
  const max = Math.max(...enthRows.map((r) => r.enth), 1);
  const curve = (m, cls) => m && (
    <div className={`tv-curve ${cls}`}>
      <span className="tv-curve-name">{m.f.short}, {t.adoption.plural(m.role)}</span>
      <span className="tv-curve-nums"><b>{m.a90}%</b> at 90 days <span aria-hidden="true">→</span> <b>{m.a12}%</b> at 12 months</span>
    </div>
  );
  return (
    <div className="tv-adopt">
      <div>
        <span className="tv-label">{feature?.short}: enthusiasm by role</span>
        {enthRows.map((r) => (
          <div key={r.role} className="tv-bar">
            <span>{r.label}</span>
            <span className="tv-bar-track"><span style={{ width: `${(r.enth / max) * 100}%` }} /></span>
            <b>{r.enth}</b>
          </div>
        ))}
      </div>
      <div className="tv-curves">
        <span className="tv-label">Still using it</span>
        {curve(fade, 'tv-fade')}
        {curve(grow, 'tv-grow')}
      </div>
    </div>
  );
}

function CompetitionVisual({ t }) {
  const c = t.comp;
  return (
    <div className="tv-comp">
      <div className="tv-record">
        <span className="tv-label">{c.ours} vs. each competitor, feature by feature</span>
        {c.record.map((r) => (
          <div key={r.name} className="tv-rec-row">
            <span>{r.name}</span>
            <span className="tv-rec"><b className="w">{r.win}</b> won <b className="t">{r.tie}</b> tied <b className="l">{r.loss}</b> lost</span>
          </div>
        ))}
      </div>
      <ul className="tv-findings">{c.findings.map((f) => <li key={f}>{f}</li>)}</ul>
    </div>
  );
}

export default function Tour({ market, demo, onGo }) {
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState(0);
  const dialogRef = useRef(null);
  const nextRef = useRef(null);
  const openerRef = useRef(null);
  const t = useTourFacts(market, demo, open);

  const start = () => {
    openerRef.current = document.activeElement;
    setStep(0);
    setOpen(true);
  };
  const close = () => {
    markSeen();
    setOpen(false);
    openerRef.current?.focus?.();
  };

  // Auto-open on a first visit, or whenever ?tour is in the URL. The ribbon button reopens it.
  useEffect(() => {
    if (!demo) return;
    const forced = new URLSearchParams(location.search).has('tour');
    if (forced || !seen()) start();
    const onClick = (e) => { if (e.target.closest?.('[data-tour-open]')) start(); };
    document.addEventListener('click', onClick);
    return () => document.removeEventListener('click', onClick);
  }, [demo]);

  const steps = useMemo(() => {
    if (!t) return [];
    const { losses, plural } = t.compare;
    const leadV = t.variants[t.compare.lead];
    const list = (xs) => (xs.length < 2 ? xs.join('') : `${xs.slice(0, -1).join(', ')} and ${xs.at(-1)}`);
    const lossText = losses.length
      ? `but trails ${list(losses.map((l, i) => `${l.to.id} by ${l.by}${i ? '' : ' points'} with ${plural(l.role)}`))}`
      : 'and holds up in every role';
    const ad = t.adoption;
    const adoptLine = ad.feature
      ? `${ad.feature.short} scores highest with ${plural(ad.top)} and lowest with ${plural(ad.low)}${ad.veto ? ', who can block it' : ''}.`
      : '';
    return [
      {
        intro: true,
        kicker: 'Product tour',
        title: 'Test your launch on a synthetic market before it ships',
        body: `Every company here has the five people who decide whether a workers' comp safety product gets bought and used: the broker, the CFO, IT, the safety manager and a frontline worker. Each one carries pain points from their role and their industry. The demo shows a launch for ${t.product}, a fictional product, scored on demo data.`,
        Visual: IntroVisual,
        view: 'documents',
      },
      {
        kicker: 'Feature 1 of 4',
        title: 'Start from the launch documents',
        body: 'Upload the PRD, MRD and creative brief. Claude pulls out the features and the claims, rates the proof behind each claim, and writes three message directions that follow the brief and only use claims the documents can back up. The weakest claim goes straight to Stress.',
        Visual: DocsVisual,
        view: 'documents',
        cta: 'Look at the extracted brief',
      },
      {
        kicker: 'Feature 2 of 4',
        title: 'The average hides who will block the deal',
        body: `Compare runs all three messages past the same personas. Variant ${leadV.id} (“${leadV.headline}”) has the best overall odds, ${lossText}. Those roles can stop a purchase, so the dashboard flags the split instead of averaging it away.`,
        Visual: CompareVisual,
        view: 'compare',
        cta: 'Open the full comparison',
      },
      {
        kicker: 'Feature 3 of 4',
        title: 'See who keeps using each feature',
        body: `Adoption matches every feature against every persona: how enthusiastic they are, and how many are still using it at 90 days and at 12 months. ${adoptLine} Some features fade after launch, and others grow as renewal comes around.`,
        Visual: AdoptionVisual,
        view: 'adoption',
        cta: 'Explore the adoption grid',
      },
      t.comp && {
        kicker: 'Feature 4 of 4',
        title: 'Put your copy next to theirs',
        body: `For each feature, the same personas read your message and each competitor's, blind, with the brand names removed. You see whose copy lands and with which roles, including when a competitor wins over a role that can veto the deal.`,
        Visual: CompetitionVisual,
        view: 'competition',
        cta: 'See the head-to-head',
      },
    ].filter(Boolean);
  }, [t]);

  // Move the app behind the dialog to the step's view.
  useEffect(() => {
    if (open && steps[step]) onGo(steps[step].view);
  }, [open, step, steps]);

  useEffect(() => {
    if (!open) return;
    nextRef.current?.focus({ preventScroll: true });
    if (dialogRef.current) dialogRef.current.scrollTop = 0;
  }, [open, step]);

  if (!open || !steps.length) return null;
  const s = steps[step];
  const last = step === steps.length - 1;
  const go = (i) => setStep(Math.max(0, Math.min(steps.length - 1, i)));

  const onKey = (e) => {
    if (e.key === 'Escape') { e.preventDefault(); close(); return; }
    if (e.key === 'ArrowRight') { e.preventDefault(); if (!last) go(step + 1); return; }
    if (e.key === 'ArrowLeft') { e.preventDefault(); go(step - 1); return; }
    if (e.key !== 'Tab') return;
    const els = [...dialogRef.current.querySelectorAll('button')].filter((el) => !el.disabled);
    if (!els.length) return;
    if (e.shiftKey && document.activeElement === els[0]) { e.preventDefault(); els.at(-1).focus(); }
    else if (!e.shiftKey && document.activeElement === els.at(-1)) { e.preventDefault(); els[0].focus(); }
  };

  return (
    <div className="tour" onKeyDown={onKey}>
      <div className="tour-backdrop" onMouseDown={close} />
      <div ref={dialogRef} className={`tour-dialog ${s.intro ? 'is-intro' : ''}`} role="dialog" aria-modal="true" aria-labelledby="tour-title" aria-describedby="tour-body">
        <div className="tour-bar">
          <span className="tour-kicker">{s.kicker}</span>
          <button className="btn ghost small" type="button" onClick={close} aria-label="Close the tour"><Icon name="close" /></button>
        </div>
        <div className="tour-visual" key={step}><s.Visual t={t} /></div>
        <div className="tour-copy">
          <h2 id="tour-title">{s.title}</h2>
          <p id="tour-body">{s.body}</p>
          {s.cta && <button type="button" className="tour-cta" onClick={close}>{s.cta} →</button>}
        </div>
        <div className="tour-foot">
          <ol className="tour-steps" aria-label="Tour steps">
            {steps.map((x, i) => (
              <li key={i}><button type="button" aria-label={i === 0 ? 'Intro' : x.title} aria-current={i === step ? 'step' : undefined} onClick={() => go(i)} /></li>
            ))}
          </ol>
          <div className="tour-buttons">
            <button type="button" className="btn" onClick={() => (s.intro ? close() : go(step - 1))}>{s.intro ? "Skip, I'll explore" : 'Back'}</button>
            <button ref={nextRef} type="button" className="btn primary" onClick={() => (last ? close() : go(step + 1))}>
              {s.intro ? 'Show me around' : last ? 'Start exploring' : 'Next'}
            </button>
          </div>
        </div>
        <p className="visually-hidden" aria-live="polite">{s.intro ? '' : `${s.kicker}: ${s.title}`}</p>
      </div>
    </div>
  );
}
