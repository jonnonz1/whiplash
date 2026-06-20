<script>
  /* View — "where the churn lands": the statute book's sectors ranked by how
     much they've changed since 2008, each expandable to its most-amended works.
     Numbers come straight from the explorer graph (sector_term / top_acts_by_
     sector); the one-line summaries say *what* moved, not just how much. Every
     act row links to its change trail (git history on nz-statute-book, or
     legislation.govt.nz for regulations). Reuses existing primitives only. */
  import { ui } from '../lib/state.svelte.js';
  import { db } from '../lib/data.svelte.js';
  import { linkFor, linkLabel } from '../lib/leglinks.js';

  const SECTOR_LABELS = {
    tax: 'Tax', health: 'Health', environment: 'Environment / RMA',
    justice: 'Justice & work', education: 'Education', transport: 'Transport',
    economy: 'Economy', energy: 'Energy', water: 'Water', other: 'Other / uncategorised',
  };

  /* What actually moved in each sector — grounded in the leaderboard below and
     the curated reversal stories. Editorial, factual, party shown never blamed. */
  const SECTOR_SUMMARY = {
    tax: 'Never finished. The Income Tax Act 2007 has taken more provision-level changes than any other law in the country — its 2004 predecessor and the GST Act churn close behind. Annual rewrites are the baseline.',
    environment: 'The RMA 1991 was finally replaced in Aug 2023 — then the replacement was repealed about four months later, leaving the RMA still in force. Climate-change and fisheries law churn underneath.',
    justice: 'A steady grind across courts and work: the Family Court Rules and the Employment Relations Act lead, with sentencing and criminal-procedure law constantly retuned.',
    transport: 'The Land Transport Act 1998 anchors the sector; maritime and aviation law churn alongside it. Auckland light rail burned $228m on plans for zero metres of track.',
    health: 'The 1956 Health Act still does heavy lifting, with smokefree and mental-health law amended around it. Dunedin Hospital was rescoped for eight years across both governments.',
    economy: 'The Companies, Commerce and Public Finance Acts churn steadily. Pausing NZ Super Fund contributions (2009–17) left a hole the fund puts at ~$27.5b.',
    education: 'The Education Act 1989 was replaced by the Education and Training Act 2020 — now amended 1,500+ times itself — while student-loan and allowance rules are rewritten underneath, year after year.',
    energy: 'The Crown Minerals Act leads as offshore-exploration policy swings; electricity and gas safety regulations churn beneath it.',
    water: 'The newest churn in the book: Three Waters was built 2020–22, repealed in 2024, and restarted under new names — the Water Services Entities Act 2022 was already amended 821 times before its repeal.',
  };

  const exp = $derived(db.explorer);
  const fmt = new Intl.NumberFormat('en-NZ');

  /* sector -> {amendments, repeals, total}, summed across every term, ranked.
     'other' is the uncategorised bucket — not a real area, so it's left out of
     the leaderboard. */
  const ranked = $derived.by(() => {
    if (!exp) return [];
    const agg = {};
    for (const c of exp.sector_term) {
      if (c.sector === 'other') continue;
      const s = (agg[c.sector] ||= { sector: c.sector, amendments: 0, repeals: 0 });
      s.amendments += c.amendments;
      s.repeals += c.repeals;
    }
    return Object.values(agg)
      .map((s) => ({ ...s, total: s.amendments + s.repeals }))
      .sort((a, b) => b.total - a.total);
  });
  const max = $derived(Math.max(1, ...ranked.map((s) => s.total)));

  let open = $state(null);
  function toggle(s) {
    open = open === s ? null : s;
    openAct = null;
  }

  let openAct = $state(null);
  function toggleAct(id) {
    openAct = openAct === id ? null : id;
  }

  function inExplorer(s) {
    ui.exploreSector = s;
    ui.view = 'explore';
  }

  function actsFor(s) {
    return exp?.top_acts_by_sector?.[s] || [];
  }

  /* precomputed change-history digest (summary + recent timeline) for an act */
  const history = (id) => db.actHistory?.[id] || null;

  const OP_LABEL = {
    amended: 'amended', inserted: 'inserted', substituted: 'replaced',
    replaced: 'replaced', repealed: 'repealed', revoked: 'revoked', other: 'changed',
  };
  const DEAD = new Set(['repealed', 'revoked']);
</script>

<div class="top">
  {#if !exp}
    <div class="empty">
      <span class="wl-label">// the explorer dataset isn’t loaded</span>
      <p class="wl-mono">
        <code>churn-explorer.json</code> is missing or failed to parse — this view needs it. The other views are unaffected.
      </p>
    </div>
  {:else}
    <header class="intro">
      <span class="wl-label">// where the churn lands — sectors ranked by total change since 2008</span>
      <div class="head-totals wl-mono">
        <span><b class="wl-data sig">{fmt.format(exp.totals.amendments)}</b> amendments</span>
        <span class="dot">·</span>
        <span><b class="wl-data">{fmt.format(exp.totals.repeals)}</b> repeals</span>
        <span class="dot">·</span>
        <span>open a row for the works underneath</span>
      </div>
    </header>

    <ol class="board">
      {#each ranked as s, i (s.sector)}
        {@const w = (s.total / max) * 100}
        {@const isOpen = open === s.sector}
        <li class="row" class:open={isOpen}>
          <button class="head" onclick={() => toggle(s.sector)} aria-expanded={isOpen}>
            <span class="bar" style="width:{w}%"></span>
            <span class="rank wl-mono">{i + 1}</span>
            <span class="body">
              <span class="line1">
                <span class="name wl-disp" class:sig={isOpen}>{SECTOR_LABELS[s.sector] || s.sector}</span>
                <span class="caret wl-mono">{isOpen ? '▼' : '▶'}</span>
              </span>
              <span class="summary">{SECTOR_SUMMARY[s.sector] || ''}</span>
            </span>
            <span class="metric">
              <span class="total wl-data">{fmt.format(s.total)}</span>
              <span class="split wl-mono">{fmt.format(s.amendments)} amend · {fmt.format(s.repeals)} repeal</span>
            </span>
          </button>

          {#if isOpen}
            <div class="drawer">
              <div class="drawerhead wl-label">
                // most-changed works in {SECTOR_LABELS[s.sector] || s.sector}
                <button class="wl-pill" onclick={() => inExplorer(s.sector)}>open in Explore ▸</button>
              </div>
              <ol class="acts">
                {#each actsFor(s.sector) as a (a.id)}
                  {@const h = history(a.id)}
                  {@const actOpen = openAct === a.id}
                  <li>
                    {#if h}
                      <button class="act" onclick={() => toggleAct(a.id)} aria-expanded={actOpen} title="See what changed">
                        <span class="acaret wl-mono">{actOpen ? '▼' : '▶'}</span>
                        <span class="atitle">{a.title}</span>
                        <span class="acount wl-data">{fmt.format(a.count)}</span>
                      </button>
                      {#if actOpen}
                        <div class="hist">
                          <p class="summary">{h.summary}</p>
                          <div class="stats wl-mono">
                            <span>{fmt.format(h.total)} changes</span>
                            <span class="dot">·</span>
                            <span>{h.span.first.slice(0, 4)}–{h.span.last.slice(0, 4)}</span>
                            <span class="dot">·</span>
                            <span>busiest {h.busiest.year} ({fmt.format(h.busiest.count)})</span>
                            {#if h.repeals}<span class="dot">·</span><span>{fmt.format(h.repeals)} repeals</span>{/if}
                          </div>
                          <ol class="events">
                            {#each h.timeline as ev, ei (ei)}
                              <li class="ev">
                                <span class="evdate wl-mono">{ev.date}</span>
                                <span class="evop wl-mono" class:dead={DEAD.has(ev.op)}>{OP_LABEL[ev.op] || ev.op}</span>
                                <span class="evbody">
                                  <span class="evprov">{ev.provision || '—'}</span>
                                  {#if ev.by_title}<span class="evby wl-mono">← {ev.by_title}</span>{/if}
                                </span>
                              </li>
                            {/each}
                          </ol>
                          <a class="histlink wl-mono" href={linkFor(a)} target="_blank" rel="noopener">
                            every change as commits — {linkLabel(a)}
                          </a>
                        </div>
                      {/if}
                    {:else}
                      <a class="act" href={linkFor(a)} target="_blank" rel="noopener" title="{a.title} — {linkLabel(a)}">
                        <span class="acaret"></span>
                        <span class="atitle">{a.title}</span>
                        <span class="asrc wl-mono">{linkLabel(a)}</span>
                        <span class="acount wl-data">{fmt.format(a.count)}</span>
                      </a>
                    {/if}
                  </li>
                {/each}
              </ol>
            </div>
          {/if}
        </li>
      {/each}
    </ol>

    <div class="caption">
      <span class="wl-mono captext">
        Counts are provision-level events parsed from the PCO legislation XML. “git history ↗” opens that act’s commit
        trail on <code>nz-statute-book</code> — each amendment is a commit, so the log is the diff. Regulations link to
        legislation.govt.nz. The uncategorised bucket is excluded from the ranking.
      </span>
    </div>
  {/if}
</div>

<style>
  .top {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    min-height: 0;
  }

  .empty {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 24px;
    text-align: center;
  }
  .empty p {
    font-size: 11px;
    color: var(--ink-3);
    max-width: 420px;
    line-height: 1.6;
  }
  .empty code {
    color: var(--signal);
  }

  .intro {
    padding: 14px 16px 4px;
  }
  .head-totals {
    margin-top: 7px;
    font-size: 12px;
    color: var(--ink-2);
    display: flex;
    gap: 8px;
    align-items: baseline;
    flex-wrap: wrap;
  }
  .head-totals .wl-data {
    font-size: 15px;
  }
  .head-totals .sig {
    color: var(--signal);
  }
  .head-totals .dot {
    color: var(--ink-3);
  }

  .board {
    list-style: none;
    margin: 8px 0 0;
    padding: 0;
  }
  .row {
    border-bottom: 1px solid var(--line);
  }
  .row.open {
    background: var(--surface-2);
  }

  .head {
    position: relative;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    width: 100%;
    text-align: left;
    padding: 14px 16px;
    color: inherit;
  }
  .head:hover {
    background: var(--surface-2);
  }
  .bar {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    background: color-mix(in srgb, var(--signal) 9%, transparent);
    pointer-events: none;
  }
  .rank {
    position: relative;
    font-size: 13px;
    color: var(--ink-3);
    width: 20px;
    flex: none;
    padding-top: 2px;
  }
  .body {
    position: relative;
    flex: 1;
    min-width: 0;
  }
  .line1 {
    display: flex;
    align-items: baseline;
    gap: 8px;
  }
  .name {
    font-size: clamp(16px, 4vw, 21px);
  }
  .name.sig {
    color: var(--signal);
  }
  .caret {
    font-size: 9px;
    color: var(--ink-3);
  }
  .summary {
    display: block;
    margin-top: 5px;
    font-size: 11.5px;
    color: var(--ink-2);
    line-height: 1.5;
    max-width: 60ch;
  }
  .metric {
    position: relative;
    flex: none;
    text-align: right;
    padding-top: 2px;
  }
  .total {
    display: block;
    font-size: 16px;
  }
  .split {
    display: block;
    font-size: 8.5px;
    color: var(--ink-3);
    margin-top: 2px;
    white-space: nowrap;
  }

  .drawer {
    padding: 0 16px 12px 48px;
  }
  .drawerhead {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    font-size: 9px;
    margin-bottom: 4px;
  }
  .acts {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .acts li {
    border-top: 1px solid var(--line);
  }
  .act {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    text-align: left;
    padding: 8px 2px;
    color: inherit;
    text-decoration: none;
  }
  .act:hover {
    color: var(--signal);
  }
  .acaret {
    flex: none;
    width: 10px;
    font-size: 8px;
    color: var(--ink-3);
  }
  .atitle {
    flex: 1;
    font-size: 11.5px;
    color: var(--ink-2);
    line-height: 1.35;
  }
  .act:hover .atitle {
    color: var(--ink);
  }
  .asrc {
    flex: none;
    font-size: 8px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--ink-3);
  }
  .act:hover .asrc {
    color: var(--signal);
  }
  .acount {
    flex: none;
    width: 56px;
    text-align: right;
    font-size: 12px;
  }

  /* inline change history */
  .hist {
    padding: 2px 2px 12px 22px;
  }
  .summary {
    margin: 0 0 8px;
    font-size: 12px;
    color: var(--ink);
    line-height: 1.55;
    max-width: 64ch;
  }
  .stats {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    font-size: 9.5px;
    color: var(--ink-3);
    margin-bottom: 8px;
  }
  .stats .dot {
    color: var(--line-2);
  }
  .events {
    list-style: none;
    margin: 0 0 8px;
    padding: 0;
    border-left: 1px solid var(--line);
  }
  .ev {
    display: flex;
    gap: 8px;
    padding: 3px 0 3px 10px;
    align-items: baseline;
  }
  .evdate {
    flex: none;
    width: 74px;
    font-size: 9.5px;
    color: var(--ink-3);
  }
  .evop {
    flex: none;
    width: 58px;
    font-size: 9px;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    color: var(--signal);
  }
  .evop.dead {
    color: var(--st-reversed, var(--ink-3));
  }
  .evbody {
    flex: 1;
    min-width: 0;
    font-size: 10.5px;
    color: var(--ink-2);
    line-height: 1.4;
  }
  .evprov {
    color: var(--ink);
  }
  .evby {
    font-size: 9.5px;
    color: var(--ink-3);
  }
  .histlink {
    display: inline-block;
    font-size: 9.5px;
    color: var(--ink-3);
  }
  .histlink:hover {
    color: var(--signal);
  }

  .caption {
    margin-top: auto;
    padding: 10px 16px 14px;
    border-top: 1px solid var(--line-2);
    background: var(--surface-2);
  }
  .captext {
    font-size: 9.5px;
    color: var(--ink-2);
    line-height: 1.6;
  }
  .captext code {
    color: var(--signal);
  }

  @media (max-width: 560px) {
    .metric {
      display: none;
    }
    .drawer {
      padding-left: 16px;
    }
  }
</style>
