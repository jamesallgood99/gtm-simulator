import React, { useEffect, useMemo, useRef, useState } from 'react';
import CompareView from './components/CompareView.jsx';
import ScoreView from './components/ScoreView.jsx';
import TalkView from './components/TalkView.jsx';
import StressView from './components/StressView.jsx';
import { MarketView, PersonasView } from './components/MarketView.jsx';
import { SettingsDialog, CampaignDialog } from './components/Dialogs.jsx';
import { Icon } from './components/ui.jsx';
import { analyze } from './lib/analysis.js';
import { stratifiedSample } from './lib/stats.js';
import { runScore, runStress, runTalk, resultsToCsv, parseCsv } from './lib/simulate.js';

const REPO_URL = 'https://github.com/jamesallgood/synthetic-market-simulator';

const NAV = [
  { group: 'Simulate', items: [
    { id: 'compare', label: 'Compare', hint: 'A vs B', icon: 'compare' },
    { id: 'score', label: 'Score', hint: 'one message', icon: 'score' },
    { id: 'talk', label: 'Talk', hint: 'one persona', icon: 'talk' },
    { id: 'stress', label: 'Stress', hint: 'weakest claim', icon: 'stress' },
  ] },
  { group: 'Market', items: [
    { id: 'market', label: 'Segments', icon: 'market' },
    { id: 'personas', label: 'Personas', icon: 'personas' },
  ] },
];

const store = {
  get(k, fallback, session = false) {
    try {
      const v = (session ? sessionStorage : localStorage).getItem(k);
      return v == null ? fallback : JSON.parse(v);
    } catch { return fallback; }
  },
  set(k, v, session = false) {
    try { (session ? sessionStorage : localStorage).setItem(k, JSON.stringify(v)); } catch { /* storage unavailable */ }
  },
  del(k) {
    try { localStorage.removeItem(k); sessionStorage.removeItem(k); } catch { /* storage unavailable */ }
  },
};

function loadSettings() {
  const prefs = store.get('sms.prefs', {});
  const key = store.get('sms.key', '', false) || store.get('sms.key', '', true);
  return {
    apiKey: key,
    rememberKey: Boolean(store.get('sms.key', '', false)),
    model: prefs.model ?? 'claude-sonnet-5-5',
    sampleSize: prefs.sampleSize ?? 100,
    concurrency: prefs.concurrency ?? 3,
  };
}

function download(name, text) {
  const url = URL.createObjectURL(new Blob([text], { type: 'text/csv' }));
  const a = Object.assign(document.createElement('a'), { href: url, download: name });
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export default function App() {
  const [market, setMarket] = useState(null);
  const [loadError, setLoadError] = useState('');
  const [demo, setDemo] = useState(null);
  const [settings, setSettings] = useState(loadSettings);
  const [view, setView] = useState('compare');
  const [campaign, setCampaign] = useState(null);
  const [results, setResults] = useState({});
  const [source, setSource] = useState('demo');
  const [sampleSize, setSampleSize] = useState(0);
  const [stress, setStress] = useState(null);
  const [transcripts, setTranscripts] = useState({});
  const [talkPersona, setTalkPersona] = useState(null);
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState('');
  const [dialog, setDialog] = useState(null);
  const fileRef = useRef(null);
  const abortRef = useRef(null);

  useEffect(() => {
    Promise.all([
      fetch('./data/market.json').then((r) => { if (!r.ok) throw new Error('market.json'); return r.json(); }),
      fetch('./data/demo/q2-launch.json').then((r) => (r.ok ? r.json() : null)),
    ]).then(([m, d]) => {
      setMarket(m);
      if (d) {
        setDemo(d);
        setCampaign(d.campaign);
        setResults(d.results);
        setSampleSize(d.sample_ids.length);
        setStress(d.stress);
        setTranscripts({ [d.talk.persona_id]: d.talk.transcript });
        setTalkPersona(d.talk.persona_id);
      } else {
        setCampaign({ name: 'New campaign', product: '', variants: [{ id: 'A', name: 'Variant A', headline: '', message: '', focus: '' }] });
      }
    }).catch(() => setLoadError('Could not load data/market.json. Run python market/generate_market.py, then reload.'));
  }, []);

  const live = Boolean(settings.apiKey);
  const analysis = useMemo(() => (market && campaign ? analyze(market, campaign.variants, results) : null), [market, campaign, results]);

  const saveSettings = (s) => {
    store.del('sms.key');
    if (s.apiKey) store.set('sms.key', s.apiKey, !s.rememberKey);
    store.set('sms.prefs', { model: s.model, sampleSize: s.sampleSize, concurrency: s.concurrency });
    setSettings(s);
    setDialog(null);
  };

  const needKey = () => { setDialog('settings'); };

  async function simulate(c) {
    if (!live) return needKey();
    setError('');
    setBusy(true);
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    try {
      const sample = stratifiedSample(market.personas, settings.sampleSize, market.roles);
      setProgress({ done: 0, total: 1, label: `Scoring ${c.variants.length} variant${c.variants.length > 1 ? 's' : ''} against ${sample.length} personas` });
      const res = await runScore({
        settings, market, product: c.product, variants: c.variants, sample, signal: ctrl.signal,
        onProgress: (done, total) => setProgress((p) => ({ ...p, done, total })),
      });
      setResults(res);
      setSampleSize(sample.length);
      setSource('live');
    } catch (e) {
      if (e.name !== 'AbortError') setError(e.message);
    } finally {
      setBusy(false);
      setProgress(null);
    }
  }

  const saveCampaign = (c, run) => {
    setCampaign(c);
    setDialog(null);
    // Keep results only for variants whose message didn't change.
    const kept = {};
    for (const v of c.variants) {
      const old = campaign.variants.find((o) => o.id === v.id);
      if (old && old.message === v.message && results[v.id]) kept[v.id] = results[v.id];
    }
    setResults(kept);
    if (run) simulate(c);
  };

  const scoreNew = (message) => {
    if (!live) return needKey();
    const variants = campaign.variants.length >= 4 ? campaign.variants.slice(1) : campaign.variants;
    const next = { id: '', name: '', headline: message.split(/(?<=[.!?])\s/)[0].slice(0, 80), message, focus: 'Scored from the Score view' };
    const c = { ...campaign, variants: [...variants, next].map((v, i) => ({ ...v, id: String.fromCharCode(65 + i), name: `Variant ${String.fromCharCode(65 + i)}` })) };
    setCampaign(c);
    // Every variant is re-scored on the same live sample, so new and old copy are compared fairly.
    simulate(c);
  };

  const sendTalk = async (persona, text) => {
    const prior = transcripts[persona.id] ?? [];
    const next = [...prior, { role: 'user', text }];
    setTranscripts((t) => ({ ...t, [persona.id]: next }));
    setBusy(true);
    setError('');
    try {
      const reply = await runTalk({ settings, market, product: campaign?.product, persona, transcript: next });
      setTranscripts((t) => ({ ...t, [persona.id]: [...next, { role: 'persona', text: reply }] }));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const runStressTest = async (claim, critics) => {
    if (!live) {
      if (demo && claim === demo.stress.claim) { setStress(demo.stress); return; }
      return needKey();
    }
    setBusy(true);
    setError('');
    setProgress({ done: 0, total: 1, label: `${critics.length} critics are reading your claim` });
    try {
      setStress(await runStress({ settings, market, product: campaign?.product, claim, critics }));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
      setProgress(null);
    }
  };

  const importCsv = async (file) => {
    try {
      const res = parseCsv(await file.text());
      const ids = new Set(market.personas.map((p) => p.id));
      const unknown = Object.values(res).flat().filter((r) => !ids.has(r.persona_id)).length;
      if (unknown) throw new Error(`${unknown} rows reference personas that aren't in this market. Import results run against the same market.json.`);
      const vids = Object.keys(res);
      const variants = vids.map((id, i) => campaign.variants.find((v) => v.id === id || v.name === id)
        ?? { id, name: id.length === 1 ? `Variant ${id}` : id, headline: id, message: '(imported results)', focus: 'Imported from CSV' });
      setCampaign({ ...campaign, name: `${campaign.name} (imported)`, variants });
      setResults(Object.fromEntries(variants.map((v, i) => [v.id, res[vids[i]]])));
      setSampleSize(Math.max(...Object.values(res).map((r) => r.length)));
      setSource('import');
      setView('compare');
    } catch (e) {
      setError(e.message);
    }
  };

  const openTalk = (id) => { setTalkPersona(id); setView('talk'); };

  if (loadError) return <div className="main"><div className="banner error">{loadError}</div></div>;
  if (!market || !campaign) return <div className="main"><p className="note">Loading the market…</p></div>;

  const variantCount = campaign.variants.length;
  const heads = {
    compare: [`Campaign simulation: ${campaign.name}`, `Testing ${variantCount} message variation${variantCount > 1 ? 's' : ''} against ${sampleSize} AI personas from ${market.market_name.toLowerCase()}.`],
    score: ['Score', 'Run one message past the market and read it by segment.'],
    talk: ['Talk', 'Interview one persona and let them push back on your pitch.'],
    stress: ['Stress', 'Point your toughest critics at your weakest claim.'],
    market: [market.market_name, market.description],
    personas: ['Personas', 'Every buyer in the synthetic market. Click anyone to talk to them.'],
  };

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <svg className="brand-mark" viewBox="0 0 32 32" aria-hidden="true">
            <rect width="32" height="32" rx="8" fill="var(--ink)" />
            <rect x="7" y="17" width="4" height="8" rx="1" fill="var(--a)" />
            <rect x="14" y="9" width="4" height="16" rx="1" fill="var(--b)" />
            <rect x="21" y="13" width="4" height="12" rx="1" fill="var(--c)" />
          </svg>
          <span className="brand-name">Synthetic Market</span>
        </div>
        <nav className="nav" aria-label="Main">
          {NAV.map((g) => (
            <React.Fragment key={g.group}>
              <div className="nav-group-label">{g.group}</div>
              {g.items.map((it) => (
                <button key={it.id} aria-current={view === it.id ? 'page' : undefined} onClick={() => setView(it.id)}>
                  <Icon name={it.icon} />{it.label}{it.hint && <span className="verb-hint">{it.hint}</span>}
                </button>
              ))}
            </React.Fragment>
          ))}
        </nav>
        <div className="side-card">
          <h4>Target market</h4>
          <div className="big">{market.market_name}</div>
          <div className="sub">{market.companies.length} companies, {market.personas.length} personas</div>
        </div>
        <div className="side-card">
          <h4>Pain spectrum</h4>
          <div className="spectrum" />
          <div className="spectrum-labels"><span>Low pain</span><span>High pain</span></div>
        </div>
        <div className="sidebar-foot">
          <span className={`mode-pill ${live ? 'live' : 'demo'}`}>{live ? `Live: ${settings.model}` : 'Demo data'}</span>
          <button className="btn small" onClick={() => setDialog('settings')}><Icon name="settings" />Settings</button>
          <a className="btn small ghost" href={REPO_URL} target="_blank" rel="noreferrer"><Icon name="github" />Source and method</a>
        </div>
      </aside>

      <main className="main">
        {!live && source === 'demo' && (
          <div className="banner">
            <span>You're looking at demo data. It was scored by a simple heuristic, not a model, so the shape is realistic but the quotes are canned. Add your Claude API key to run the market live.</span>
            <button className="btn small" onClick={() => setDialog('settings')}>Add API key</button>
          </div>
        )}
        {source === 'demo' && live && view === 'compare' && (
          <div className="banner">
            <span>Still showing demo data. Run the simulation to score these messages with {settings.model}.</span>
            <button className="btn small" onClick={() => simulate(campaign)} disabled={busy}>Run live</button>
          </div>
        )}
        {error && (
          <div className="banner error" role="alert">
            <span>{error}</span>
            <button className="btn small" onClick={() => setError('')}>Dismiss</button>
          </div>
        )}
        {progress && (
          <div className="panel" style={{ marginBottom: 18 }} role="status">
            <div className="row" style={{ justifyContent: 'space-between', marginBottom: 8 }}>
              <span>{progress.label}{progress.total > 1 ? `: batch ${progress.done} of ${progress.total}` : '…'}</span>
              <button className="btn small" onClick={() => abortRef.current?.abort()}>Stop</button>
            </div>
            <div className="progress"><span style={{ width: `${progress.total > 1 ? (progress.done / progress.total) * 100 : 40}%` }} /></div>
          </div>
        )}

        <header className="page-head">
          <div>
            <h1>{heads[view][0]}</h1>
            <p>{heads[view][1]}</p>
          </div>
          {view === 'compare' && (
            <div className="actions">
              <button className="btn" onClick={() => setDialog('campaign')}><Icon name="edit" />Edit campaign</button>
              <button className="btn" onClick={() => fileRef.current?.click()}><Icon name="upload" />Import CSV</button>
              <button className="btn" disabled={!analysis} onClick={() => download('simulation-results.csv', resultsToCsv(results, analysis.personasById))}><Icon name="download" />Export CSV</button>
              <button className="btn primary" disabled={busy} onClick={() => simulate(campaign)}><Icon name="play" />{live ? 'Run simulation' : 'Run live'}</button>
              <input ref={fileRef} type="file" accept=".csv,text/csv" hidden onChange={(e) => { if (e.target.files[0]) importCsv(e.target.files[0]); e.target.value = ''; }} />
            </div>
          )}
        </header>

        {view === 'compare' && <CompareView campaign={campaign} analysis={analysis} sampleSize={sampleSize} onTalk={openTalk} />}
        {view === 'score' && <ScoreView market={market} analysis={analysis} live={live} busy={busy} onScoreNew={scoreNew} onTalk={openTalk} />}
        {view === 'talk' && (
          <TalkView market={market} analysis={analysis} live={live} busy={busy} personaId={talkPersona}
            onSelect={setTalkPersona} transcripts={transcripts} onSend={sendTalk} />
        )}
        {view === 'stress' && <StressView market={market} live={live} busy={busy} result={stress} defaultClaim={demo?.stress.claim} onRun={runStressTest} />}
        {view === 'market' && <MarketView market={market} />}
        {view === 'personas' && <PersonasView market={market} onTalk={openTalk} />}
      </main>

      {dialog === 'settings' && <SettingsDialog settings={settings} onSave={saveSettings} onClose={() => setDialog(null)} />}
      {dialog === 'campaign' && <CampaignDialog campaign={campaign} live={live} onSave={saveCampaign} onClose={() => setDialog(null)} />}
    </div>
  );
}
