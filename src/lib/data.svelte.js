/* Data loading + derived lookups. All four JSON files are part of the
   pipeline contract (specs/whiplash/02-app-spec.md in the jonno.nz repo). */

import { dateToFrac } from './format.js';

export const db = $state({
  ready: false,
  error: null,
  governments: [],
  projects: [],
  lanes: [],
  aggregates: null,
  explorer: null,
  actHistory: null,
  generated: null,
});

export async function loadData() {
  /* The full-graph explorer dataset is optional: fetch it on its own, never
     inside the fatal Promise.all, so a missing or broken churn-explorer.json
     degrades to an empty-state and never blocks the map/churn/method views. */
  fetch(`${import.meta.env.BASE_URL}data/churn-explorer.json`)
    .then((r) => (r.ok ? r.json() : null))
    .then((j) => (db.explorer = j))
    .catch(() => (db.explorer = null));

  /* Per-act change-history digests (summary + timeline) for the Top-change
     view's inline expand. Optional too — the view falls back to the GitHub
     link when an act isn't precomputed. */
  fetch(`${import.meta.env.BASE_URL}data/act-history.json`)
    .then((r) => (r.ok ? r.json() : null))
    .then((j) => (db.actHistory = j?.acts || null))
    .catch(() => (db.actHistory = null));

  try {
    const [govs, projects, acts, aggregates] = await Promise.all(
      ['governments', 'projects', 'churn-acts', 'churn-aggregates'].map((f) =>
        fetch(`${import.meta.env.BASE_URL}data/${f}.json`).then((r) => {
          if (!r.ok) throw new Error(`${f}.json → HTTP ${r.status}`);
          return r.json();
        })
      )
    );
    db.governments = govs;
    db.projects = projects.projects;
    db.lanes = acts.lanes;
    db.aggregates = aggregates;
    db.generated = projects.generated;
    db.ready = true;
  } catch (e) {
    db.error = String(e);
  }
}

export function govtAt(frac) {
  for (const g of db.governments) {
    const s = dateToFrac(g.start);
    const e = g.end ? dateToFrac(g.end) : Infinity;
    if (frac >= s && frac < e) return g;
  }
  return db.governments[db.governments.length - 1] || null;
}

export function govtById(id) {
  return db.governments.find((g) => g.id === id) || null;
}

/* Project state at scrubber time t: null = not yet announced,
   'underway' = announced but not yet ended, else its final status. */
export function projectStateAt(p, t) {
  if (dateToFrac(p.announced) > t) return null;
  if (p.ended && dateToFrac(p.ended) <= t) return p.status;
  return 'underway';
}

export function matchesFilters(p, f) {
  if (f.govt && p.started_by !== f.govt && p.ended_by !== f.govt) return false;
  if (f.sector && p.sector !== f.sector) return false;
  if (f.status && p.status !== f.status) return false;
  if (f.minCost && (p.sunk_nzd || 0) < f.minCost) return false;
  return true;
}

/* The HUD numbers: directly sunk + cancellation costs for reversals landed
   by the government in power at time t, up to time t — firm figures only —
   plus the separately-tracked consequential (do-over) spend, never summed. */
export function hudTotal(t) {
  const g = govtAt(t);
  if (!g) return { govt: null, total: 0, count: 0, consequential: 0 };
  let total = 0;
  let count = 0;
  let consequential = 0;
  for (const p of db.projects) {
    if (p.ended_by !== g.id || !p.ended) continue;
    if (dateToFrac(p.ended) > t) continue;
    if (p.sunk_nzd) {
      total += p.sunk_nzd;
      count++;
    }
    for (const c of p.consequential || []) {
      if (c.amount_nzd) consequential += c.amount_nzd;
    }
  }
  return { govt: g, total, count, consequential };
}
