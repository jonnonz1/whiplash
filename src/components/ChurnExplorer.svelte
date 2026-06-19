<script>
  /* View 3 — The full-graph churn explorer: every amendment in the statute
     book since 2008, not the 14 curated acts. Three stacked sections that
     cross-talk: pick a sector in the heatmap (a) and the velocity
     seismograph (b) + drill-down (c) retune to it. Reuses existing
     primitives only — no new palette. */
  import { ui, TIMELINE } from '../lib/state.svelte.js';
  import { db } from '../lib/data.svelte.js';
  import { SECTOR_HEROES } from '../lib/heroes.js';
  import { linkFor, linkLabel } from '../lib/leglinks.js';
  import GovBand from './GovBand.svelte';
  import ActPanel from './ActPanel.svelte';

  const SECTOR_LABELS = {
    tax: 'Tax', health: 'Health', environment: 'Environment',
    justice: 'Justice & work', education: 'Education', transport: 'Transport',
    economy: 'Economy', energy: 'Energy', water: 'Water', other: 'Other / uncategorised',
  };

  const exp = $derived(db.explorer);
  const sectors = $derived(exp?.sectors || []);
  const govList = $derived(db.governments); // chronological in the data file
  const partial = $derived(new Set(exp?.partial_terms || []));

  /* sector -> govt-id -> {amendments, repeals} */
  const cellMap = $derived.by(() => {
    const m = {};
    for (const c of exp?.sector_term || []) (m[c.sector] ||= {})[c.govt] = c;
    return m;
  });
  const globalMax = $derived(Math.max(1, ...(exp?.sector_term || []).map((c) => c.amendments)));

  /* fill ∝ √(count / globalMax), normalised to the global max but perceptually
     scaled so the long tail stays legible; capped at 72% so white .wl-data
     text never loses contrast on the hottest cells. Colour is a secondary cue
     — the printed count is the truth. */
  function fill(amend) {
    if (!amend) return 'transparent';
    const pct = Math.round(8 + Math.sqrt(amend / globalMax) * 64);
    return `color-mix(in srgb, var(--signal) ${pct}%, transparent)`;
  }

  function cell(s, g) {
    return cellMap[s]?.[g] || { amendments: 0, repeals: 0 };
  }
  function yrs(g) {
    return `${g.start.slice(2, 4)}–${g.end ? g.end.slice(2, 4) : 'now'}`;
  }
  function shortName(g) {
    return g.label.split(' (')[0];
  }

  const sector = $derived(ui.exploreSector);
  function selectSector(s) {
    ui.exploreSector = ui.exploreSector === s ? null : s;
  }

  const fmt = new Intl.NumberFormat('en-NZ');

  /* ---- (b) velocity seismograph ---- */
  const series = $derived.by(() => {
    if (!exp) return null;
    const v = exp.velocity;
    const useSector = sector && v.by_sector[sector];
    const s = useSector ? v.by_sector[sector] : v.overall;
    const yMax = Math.max(1, ...s.amendments);
    return { years: v.years, amendments: s.amendments, repeals: s.repeals, yMax, isSector: !!useSector };
  });

  const PLOT_TOP = 4;
  const PLOT_BOT = 42; // within the 0..46 viewBox, room for the baseline
  function poly(arr, max) {
    const n = arr.length;
    return arr
      .map((v, i) => {
        const x = n > 1 ? (i / (n - 1)) * 100 : 0;
        const y = PLOT_BOT - (v / max) * (PLOT_BOT - PLOT_TOP);
        return `${x.toFixed(2)},${y.toFixed(2)}`;
      })
      .join(' ');
  }
  const axisYears = [2008, 2012, 2016, 2020, 2024];
  const xOf = (y) => {
    const ys = series?.years;
    if (!ys?.length) return 0;
    return ((y - ys[0]) / (ys[ys.length - 1] - ys[0])) * 100;
  };

  /* ---- (c) sector drill-down ---- */
  const drill = $derived.by(() => {
    if (!exp) return [];
    if (sector && exp.top_acts_by_sector[sector]) return exp.top_acts_by_sector[sector];
    // default: the workhorses across every sector
    return Object.values(exp.top_acts_by_sector).flat().sort((a, b) => b.count - a.count).slice(0, 6);
  });
  const drillMax = $derived(Math.max(1, ...drill.map((a) => a.count)));

  /* ---- hero band: one emblematic reversal per sector, shown up top ---- */
  const DEFAULT_HERO = 'transport'; // featured marquee when no sector is picked
  const hero = $derived(SECTOR_HEROES[sector] || SECTOR_HEROES[DEFAULT_HERO]);
  const heroFeatured = $derived(!(sector && SECTOR_HEROES[sector]));
  function openStory(pid) {
    ui.selected = pid;
    ui.view = 'map';
  }

  /* the 11 curated acts (matched to the graph) keep their rich ActPanel;
     everything else links out. */
  const curatedByDlm = $derived.by(() => {
    const m = {};
    for (const lane of db.lanes) for (const a of lane.acts) if (a.dlm) m[a.dlm] = { act: a, lane };
    return m;
  });

  let panelAct = $state(null);
</script>

<div class="explore">
  {#if !exp}
    <div class="empty">
      <span class="wl-label">// the explorer dataset isn’t loaded</span>
      <p class="wl-mono">
        <code>churn-explorer.json</code> is missing or failed to parse. The other views are unaffected — this
        feature degrades on its own.
      </p>
    </div>
  {:else}
    <header class="intro">
      <span class="wl-label">// the whole statute book, moving — every provision-level change since 2008</span>
      <div class="head-totals wl-mono">
        <span><b class="wl-data sig">{fmt.format(exp.totals.amendments)}</b> amendments</span>
        <span class="dot">·</span>
        <span><b class="wl-data">{fmt.format(exp.totals.repeals)}</b> repeals</span>
        <span class="dot">·</span>
        <span>{exp.velocity.years[0]}–{exp.velocity.years[exp.velocity.years.length - 1]}</span>
      </div>
    </header>

    <!-- HERO BAND — the emblematic reversal for the selected sector, up top -->
    {#snippet heroBody(h, featured)}
      <span class="herotag wl-label sig">{featured ? '★ featured reversal — tap any sector below' : h.tag}</span>
      <span class="herotitle wl-disp">{h.title}</span>
      <div class="herorows">
        {#each h.rows as r (r.k)}
          <div class="herorow">
            <span class="wl-label hk">{r.k}</span>
            <span class="hv">
              <span class="wl-mono" class:strong={r.strong}>{r.t}</span>
              {#if r.src}<span class="hsrc wl-mono">↗ {r.src}</span>{/if}
              {#if r.sub}<span class="hsub wl-mono">{r.sub}</span>{/if}
            </span>
          </div>
        {/each}
      </div>
      <div class="herogot"><span class="wl-label sig">you got</span> <span class="hgt">{h.got}</span></div>
    {/snippet}

    <section class="herowrap">
      {#if hero.project}
        <button class="hero" onclick={() => openStory(hero.project)} aria-label="{hero.title} — open the full story on the map">
          {@render heroBody(hero, heroFeatured)}
          <span class="herocta wl-mono">full story on the map ▸</span>
        </button>
      {:else}
        <a class="hero" href={hero.href} target="_blank" rel="noopener" aria-label="{hero.title} — source">
          {@render heroBody(hero, heroFeatured)}
          <span class="herocta wl-mono">{hero.hrefLabel}</span>
        </a>
      {/if}
    </section>

    <!-- (a) HEATMAP MATRIX -->
    <section class="block">
      <div class="blockhead">
        <span class="wl-label">// sector × government — fill ∝ amendment intensity, count is the truth</span>
        <span class="rule"></span>
        <span class="wl-mono hint">tap a sector ▸</span>
      </div>

      <!-- desktop / wide: semantic table -->
      <div class="matrixwrap" role="region" aria-label="Amendments by sector and government">
        <table class="matrix">
          <caption class="sr-only">Provision-level amendments (cell fill) and repeals by sector and government, since 2008</caption>
          <thead>
            <tr>
              <th class="corner" scope="col"><span class="wl-label">sector ╲ govt</span></th>
              {#each govList as g (g.id)}
                <th scope="col" class:partial={partial.has(g.id)}>
                  <span class="party {g.party}"></span>
                  <span class="gname wl-mono">{shortName(g)}</span>
                  <span class="gyrs wl-mono">{yrs(g)}</span>
                  {#if partial.has(g.id)}<span class="ptag wl-mono" title="partial term — 2008 truncates the start, or the term is still running">partial</span>{/if}
                </th>
              {/each}
            </tr>
          </thead>
          <tbody>
            {#each sectors as s (s)}
              <tr class:on={sector === s}>
                <th scope="row" class="secth">
                  <button class="seclabel wl-mono" class:sig={sector === s} onclick={() => selectSector(s)} aria-pressed={sector === s}>
                    {SECTOR_LABELS[s] || s}
                  </button>
                </th>
                {#each govList as g (g.id)}
                  {@const c = cell(s, g.id)}
                  <td
                    style="background:{fill(c.amendments)}"
                    title="{SECTOR_LABELS[s] || s} · {g.label} ({yrs(g)}): {fmt.format(c.amendments)} amendments, {fmt.format(c.repeals)} repeals"
                  >
                    <span class="wl-data amend">{fmt.format(c.amendments)}</span>
                    {#if c.repeals}<span class="rep wl-mono">−{fmt.format(c.repeals)}</span>{/if}
                  </td>
                {/each}
              </tr>
            {/each}
          </tbody>
        </table>
      </div>

      <!-- mobile: per-sector stack of 7-segment government mini-bars -->
      <div class="stack" aria-hidden="false">
        {#each sectors as s (s)}
          {@const rowMax = Math.max(1, ...govList.map((g) => cell(s, g.id).amendments))}
          <button class="scard" class:on={sector === s} onclick={() => selectSector(s)} aria-pressed={sector === s}>
            <div class="scard-top">
              <span class="wl-mono sname" class:sig={sector === s}>{SECTOR_LABELS[s] || s}</span>
              <span class="wl-mono stot">{fmt.format(govList.reduce((n, g) => n + cell(s, g.id).amendments, 0))}</span>
            </div>
            <div class="minibars">
              {#each govList as g (g.id)}
                {@const c = cell(s, g.id)}
                <div class="seg">
                  <div class="segbar-track">
                    <div
                      class="segbar {g.party}"
                      class:partial={partial.has(g.id)}
                      style="height:{Math.max(c.amendments ? 6 : 0, Math.sqrt(c.amendments / rowMax) * 100)}%"
                    ></div>
                  </div>
                  <span class="segn wl-mono">{c.amendments ? fmt.format(c.amendments) : '·'}</span>
                </div>
              {/each}
            </div>
          </button>
        {/each}
        <div class="stack-legend wl-label">
          mini-bars: <span style="color:var(--gov-nat)">◼</span> National ·
          <span style="color:var(--gov-lab)">◼</span> Labour · height ∝ amendments (factual)
        </div>
      </div>
    </section>

    <!-- (b) VELOCITY SEISMOGRAPH -->
    {#if series}
      <section class="block">
        <div class="blockhead">
          <span class="wl-label">// amendment velocity — {sector ? SECTOR_LABELS[sector] || sector : 'all sectors'}</span>
          <span class="rule"></span>
          <span class="wl-mono legend">
            <span class="lg-amend">━ amendments</span>
            <span class="lg-rep">┄ repeals</span>
          </span>
        </div>
        <div class="chart">
          <div class="axis">
            {#each axisYears as y (y)}
              <span class="wl-label tick" style="left:{xOf(y)}%">{y}</span>
            {/each}
            <span class="wl-label tick now" style="left:100%">{series.years[series.years.length - 1]}</span>
          </div>
          <svg viewBox="0 0 100 46" preserveAspectRatio="none" aria-hidden="true">
            <polyline points={poly(series.amendments, series.yMax)} fill="none" stroke="var(--signal)" stroke-width="0.8" />
            <polyline
              points={poly(series.repeals, series.yMax)}
              fill="none"
              stroke="var(--signal)"
              stroke-width="0.7"
              stroke-dasharray="2 1.6"
              opacity="0.42"
            />
          </svg>
          <GovBand height={4} />
          <p class="sr-only">
            {sector ? SECTOR_LABELS[sector] : 'All sectors'}: amendments per year from {series.years[0]} to
            {series.years[series.years.length - 1]} peaking at {fmt.format(series.yMax)}; repeals shown as the lower dashed trace.
          </p>
        </div>
      </section>
    {/if}

    <!-- (c) SECTOR DRILL-DOWN -->
    <section class="block">
      <div class="blockhead">
        <span class="wl-label">
          // {sector ? `${SECTOR_LABELS[sector] || sector} — most-amended works` : 'most-amended works, all sectors'}
        </span>
        <span class="rule"></span>
        {#if sector}
          <button class="wl-pill reset" onclick={() => (ui.exploreSector = null)}>✕ all sectors</button>
        {/if}
      </div>

      <ol class="drill">
        {#each drill as a, i (a.id)}
          {@const cur = curatedByDlm[a.id]}
          {@const w = (a.count / drillMax) * 100}
          {#if cur}
            <li>
              <button class="drow" onclick={() => (panelAct = cur)} title="Open the curated history panel">
                <span class="dbar" style="width:{w}%"></span>
                <span class="drank wl-mono">{i + 1}</span>
                <span class="dtitle">{a.title}<span class="tracked wl-mono">tracked ▸</span></span>
                <span class="dcount wl-data">{fmt.format(a.count)}</span>
              </button>
            </li>
          {:else}
            <li>
              <a class="drow" href={linkFor(a)} target="_blank" rel="noopener" title="{a.title} — {linkLabel(a)}">
                <span class="dbar" style="width:{w}%"></span>
                <span class="drank wl-mono">{i + 1}</span>
                <span class="dtitle">{a.title}<span class="dsrc wl-mono">{linkLabel(a)}</span></span>
                <span class="dcount wl-data">{fmt.format(a.count)}</span>
              </a>
            </li>
          {/if}
        {/each}
      </ol>
      <p class="wl-mono note">{exp.ops_note}</p>
    </section>

    <div class="caption">
      <span class="wl-mono captext">
        Counts are provision-level events parsed from the PCO legislation XML and reconciled against the
        per-term aggregates. <span style="color:var(--ink-3)">Clark (2008 cut-off) and the current term are
        partial and marked as such — they are not comparable totals.</span>
      </span>
    </div>
  {/if}

  {#if panelAct}
    <ActPanel act={panelAct.act} lane={panelAct.lane} onclose={() => (panelAct = null)} />
  {/if}
</div>

<style>
  .explore {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    min-height: 0;
    position: relative;
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

  .block {
    padding: 14px 16px 4px;
  }
  .blockhead {
    display: flex;
    align-items: baseline;
    gap: 10px;
    margin-bottom: 10px;
  }
  .rule {
    flex: 1;
    height: 1px;
    background: var(--line);
  }
  .hint {
    font-size: 9px;
    color: var(--ink-3);
  }

  /* ---- (a) heatmap matrix ---- */
  .matrixwrap {
    overflow-x: auto;
  }
  .matrixwrap:focus-visible {
    outline: 2px solid var(--signal);
    outline-offset: 2px;
  }
  .matrix {
    border-collapse: separate;
    border-spacing: 1px;
    background: var(--line-2);
    border: 1px solid var(--line-2);
    width: 100%;
    table-layout: fixed;
  }
  .matrix th,
  .matrix td {
    background: var(--bg);
    padding: 6px 4px;
    text-align: center;
    vertical-align: middle;
  }
  .corner {
    width: 116px;
    text-align: left !important;
    padding-left: 10px !important;
  }
  .matrix thead th {
    position: relative;
    padding-top: 8px;
  }
  .party {
    display: block;
    height: 3px;
    width: 70%;
    margin: 0 auto 5px;
    border-radius: 2px;
    opacity: 0.7;
  }
  .party.national {
    background: var(--gov-nat);
  }
  .party.labour {
    background: var(--gov-lab);
  }
  .gname {
    display: block;
    font-size: 10px;
    font-weight: 700;
    color: var(--ink-2);
    line-height: 1.15;
  }
  .gyrs {
    display: block;
    font-size: 8px;
    color: var(--ink-3);
    margin-top: 1px;
  }
  .ptag {
    display: inline-block;
    margin-top: 3px;
    font-size: 7px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--ink-3);
    border: 1px dashed var(--line-2);
    border-radius: 2px;
    padding: 0 3px;
  }
  thead th.partial {
    background-image: repeating-linear-gradient(45deg, transparent, transparent 3px, var(--line) 3px, var(--line) 4px);
  }

  .secth {
    text-align: left !important;
    padding: 0 !important;
  }
  .seclabel {
    display: block;
    width: 100%;
    text-align: left;
    padding: 9px 8px 9px 10px;
    font-size: 10px;
    letter-spacing: 0.02em;
    color: var(--ink-2);
    min-height: 30px;
  }
  .seclabel:hover {
    color: var(--ink);
  }
  .seclabel.sig {
    color: var(--signal);
    font-weight: 700;
  }
  tr.on td {
    box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--signal) 40%, transparent);
  }
  .amend {
    display: block;
    font-size: 11px;
  }
  .rep {
    display: block;
    font-size: 8px;
    color: var(--ink-3);
    margin-top: 1px;
  }

  /* mobile mini-bars (hidden on wide) */
  .stack {
    display: none;
  }
  .scard {
    display: block;
    width: 100%;
    text-align: left;
    border: 1px solid var(--line-2);
    border-radius: 3px;
    padding: 8px 10px;
    margin-bottom: 6px;
    background: var(--surface-2);
  }
  .scard.on {
    border-color: var(--signal);
  }
  .scard-top {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 6px;
  }
  .sname {
    font-size: 11px;
    color: var(--ink-2);
  }
  .sname.sig {
    color: var(--signal);
    font-weight: 700;
  }
  .stot {
    font-size: 11px;
    font-weight: 700;
    color: var(--ink);
  }
  .minibars {
    display: flex;
    gap: 3px;
    align-items: flex-end;
  }
  .seg {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
  }
  .segbar-track {
    width: 100%;
    height: 34px;
    display: flex;
    align-items: flex-end;
    background: var(--bg);
    border-radius: 1px;
  }
  .segbar {
    width: 100%;
    border-radius: 1px 1px 0 0;
    opacity: 0.62;
    min-height: 0;
  }
  .segbar.national {
    background: var(--gov-nat);
  }
  .segbar.labour {
    background: var(--gov-lab);
  }
  .segbar.partial {
    background-image: repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(255, 255, 255, 0.25) 2px, rgba(255, 255, 255, 0.25) 3px);
  }
  .segn {
    font-size: 7px;
    color: var(--ink-3);
    line-height: 1;
  }
  .stack-legend {
    font-size: 8.5px;
    margin-top: 6px;
    line-height: 1.5;
  }

  /* ---- (b) velocity seismograph ---- */
  .legend {
    font-size: 9px;
    display: flex;
    gap: 10px;
  }
  .lg-amend {
    color: var(--signal);
  }
  .lg-rep {
    color: var(--ink-3);
  }
  .chart {
    position: relative;
  }
  .axis {
    position: relative;
    height: 16px;
  }
  .tick {
    position: absolute;
    top: 2px;
    font-size: 9px;
  }
  .tick.now {
    transform: translateX(-100%);
    color: var(--signal);
  }
  .chart svg {
    width: 100%;
    height: 120px;
    display: block;
  }
  .chart :global(.gov-band) {
    margin-top: 2px;
  }

  /* ---- (c) drill-down ---- */
  .reset {
    flex: none;
  }

  /* hero band — the emblematic reversal for the selected sector, up top */
  .herowrap {
    padding: 14px 16px 4px;
  }
  .hero {
    display: block;
    width: 100%;
    text-align: left;
    border: 1px solid var(--line-2);
    border-radius: 3px;
    background: var(--surface);
    padding: 16px 18px;
    color: inherit;
    text-decoration: none;
    transition: border-color 0.15s ease;
  }
  .hero:hover {
    border-color: rgba(212, 168, 83, 0.55);
  }
  .herotag {
    display: block;
    font-size: 9px;
  }
  .herotitle {
    display: block;
    font-size: clamp(22px, 6vw, 30px);
    margin: 7px 0 12px;
  }
  .herorows {
    display: flex;
    flex-direction: column;
    gap: 7px;
  }
  .herorow,
  .herogot {
    display: grid;
    grid-template-columns: 76px 1fr;
    gap: 10px;
    align-items: baseline;
  }
  .hk {
    font-size: 9px;
  }
  .hv .wl-mono {
    font-size: 12px;
    color: var(--ink);
    line-height: 1.45;
  }
  .hv .strong {
    font-weight: 700;
  }
  .hsrc {
    font-size: 9px;
    color: var(--signal);
    margin-left: 7px;
    white-space: nowrap;
  }
  .hsub {
    display: block;
    font-size: 9px;
    color: var(--ink-3);
    margin-top: 2px;
  }
  .herogot {
    border-top: 1px solid var(--line);
    margin-top: 12px;
    padding-top: 11px;
  }
  .hgt {
    font-family: var(--font-sans);
    font-weight: 500;
    font-size: 15px;
    color: var(--ink);
    line-height: 1.4;
  }
  .herocta {
    display: inline-block;
    margin-top: 12px;
    font-size: 10px;
    color: var(--ink-3);
  }
  .hero:hover .herocta {
    color: var(--signal);
  }
  .drill {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .drill li {
    border-bottom: 1px solid var(--line);
  }
  .drow {
    position: relative;
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    text-align: left;
    padding: 9px 10px;
    min-height: 38px;
    color: inherit;
    text-decoration: none;
  }
  .drow:hover {
    background: var(--surface-2);
  }
  .dbar {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    background: color-mix(in srgb, var(--signal) 9%, transparent);
    pointer-events: none;
  }
  .drank {
    position: relative;
    font-size: 9px;
    color: var(--ink-3);
    width: 16px;
    flex: none;
  }
  .dtitle {
    position: relative;
    flex: 1;
    font-size: 11.5px;
    color: var(--ink-2);
    line-height: 1.35;
  }
  .tracked,
  .dsrc {
    display: inline-block;
    margin-left: 8px;
    font-size: 8px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }
  .tracked {
    color: var(--signal);
  }
  .dsrc {
    color: var(--ink-3);
  }
  .drow:hover .dsrc {
    color: var(--signal);
  }
  .dcount {
    position: relative;
    font-size: 12px;
    flex: none;
  }
  .note {
    font-size: 8.5px;
    color: var(--ink-3);
    line-height: 1.5;
    margin: 8px 0 0;
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

  @media (max-width: 560px) {
    .matrixwrap {
      display: none;
    }
    .stack {
      display: block;
    }
    .blockhead .hint {
      display: none;
    }
  }
</style>
