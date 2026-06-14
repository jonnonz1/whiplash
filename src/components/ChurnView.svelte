<script>
  /* View 2 — The Churn: the statute book as sector swimlanes.
     Bars run enactment → repeal; ticks are amendments; dashed connectors
     link a repeal to its replacement. The RMA lane is the poster child. */
  import { ui, TIMELINE } from '../lib/state.svelte.js';
  import { db } from '../lib/data.svelte.js';
  import { dateToFrac, clamp } from '../lib/format.js';
  import { STATUS } from '../lib/status.js';
  import GovBand from './GovBand.svelte';
  import ActPanel from './ActPanel.svelte';

  const span = TIMELINE.to - TIMELINE.from;
  const x = (frac) => clamp(((frac - TIMELINE.from) / span) * 100, 0, 100);

  const lanes = $derived(ui.sector ? db.lanes.filter((l) => l.sector === ui.sector) : db.lanes);

  const axisYears = [2008, 2012, 2016, 2020, 2024];

  /* Pack overlapping bars into stacked slots so open-ended acts never
     draw over each other (Pae Ora vs Smokefree, bright-line vs interest). */
  const ROW = 46;

  function packLane(lane) {
    const sorted = [...lane.acts].sort((a, b) => a.enacted.localeCompare(b.enacted));
    const slotEnds = [];
    const placed = sorted.map((act) => {
      const s = Math.max(dateToFrac(act.enacted), TIMELINE.from);
      const e = act.repealed ? dateToFrac(act.repealed) : TIMELINE.to;
      let slot = act.slot_hint;
      if (slot == null) {
        slot = slotEnds.findIndex((end) => end <= s - 0.05);
        if (slot === -1) slot = slotEnds.length;
      }
      slotEnds[slot] = Math.max(slotEnds[slot] ?? -Infinity, e + 0.1);
      return { act, slot };
    });
    return { lane, placed, nSlots: Math.max(slotEnds.length, 1) };
  }

  const packedLanes = $derived(lanes.map(packLane));

  /* Bar colour: a repealed act reads as reversed/cancelled; an open act is
     neutral; zombies and restorations carry their own shapes. */
  function actStatus(act) {
    if (act.status_hint) return act.status_hint;
    if (act.zombie_of) return 'zombie';
    if (act.repealed) return 'reversed';
    return 'underway';
  }

  function barGeom(act) {
    const s = dateToFrac(act.enacted);
    const e = act.repealed ? dateToFrac(act.repealed) : TIMELINE.to;
    const clampedStart = Math.max(s, TIMELINE.from);
    const left = x(clampedStart);
    const width = Math.max(x(e) - left, 1.2);
    return { left, width, preDates: s < TIMELINE.from, open: !act.repealed };
  }

  const selectedAct = $derived.by(() => {
    for (const lane of db.lanes) {
      const act = lane.acts.find((a) => a.id === ui.selectedAct);
      if (act) return { act, lane };
    }
    return null;
  });

  const cards = $derived(db.aggregates?.stat_cards || []);
</script>

<div class="churn">
  <div class="wl-grid cards">
    {#each cards as c (c.id)}
      <div class="wl-cell card" class:pending={c.status === 'pending'}>
        {#if c.status === 'sourced'}
          <div class="wl-disp cval" style="color:{c.id === 'urgency-hours' ? 'var(--signal)' : 'var(--ink)'}">{c.value}</div>
          <div class="wl-label clabel">{c.label}</div>
          {#if c.sub}<div class="wl-mono csub">{c.sub}</div>{/if}
          {#if c.source}
            <a class="wl-mono csrc" href={c.source_url} target="_blank" rel="noopener">↗ {c.source}</a>
          {/if}
        {:else}
          <div class="wl-disp cval pendingval">—</div>
          <div class="wl-label clabel">{c.label}</div>
          <div class="wl-mono csub">{c.sub}</div>
        {/if}
      </div>
    {/each}
  </div>

  <div class="lanehead">
    <span class="wl-label">// Sector lanes — enactment → repeal · ticks = amendments</span>
    <span class="rule"></span>
    <span class="wl-mono conn-hint">repeal → replacement ┈┈▸</span>
  </div>

  <div class="lanes">
    <div class="axis">
      {#each axisYears as y (y)}
        <span class="wl-label tick" style="left:{x(y)}%">{y}</span>
      {/each}
      <span class="wl-label tick now" style="left:100%">NOW</span>
    </div>

    {#each packedLanes as p (p.lane.sector)}
      <div class="lane" class:hero={p.lane.hero} style="height:{p.nSlots * ROW + 6}px">
        <div class="lanelabel">
          <span class="wl-mono lname" class:sig={p.lane.hero}>{p.lane.label}</span>
        </div>
        <div class="bars">
          {#each p.placed as { act, slot }, i (act.id)}
            {@const st = STATUS[actStatus(act)]}
            {@const geom = barGeom(act)}
            {@const wide = geom.width > 20}
            {@const mid = slot * ROW + ROW / 2 + 3}
            <button
              class="bar"
              class:zombie={actStatus(act) === 'zombie'}
              class:cancelled={actStatus(act) === 'cancelled'}
              class:restored={actStatus(act) === 'restored'}
              class:openend={geom.open}
              style="left:{geom.left}%;width:{geom.width}%;--bar-color:{st.hex};top:{mid - 9}px"
              onclick={() => (ui.selectedAct = act.id)}
              aria-label="{act.title} — {st.label}, {act.enacted.slice(0, 4)}–{act.repealed ? act.repealed.slice(0, 4) : 'now'}. Full history"
              title={act.title}
            >
              {#if geom.preDates}<span class="pre wl-mono">◂ {act.enacted.slice(0, 4)}</span>{/if}
              {#if wide}<span class="wl-mono blabel">{act.title}</span>{/if}
            </button>
            {#if !wide}
              {@const rightSide = geom.open || geom.left > 72}
              <button
                class="wl-mono floatlabel"
                style="top:{i % 2 === 1 ? mid + 11 : mid - 22}px;{rightSide
                  ? `right:${100 - geom.left - geom.width}%;text-align:right`
                  : `left:${geom.left}%`}"
                onclick={() => (ui.selectedAct = act.id)}
              >
                {act.title}
              </button>
            {/if}
            {#each (act.ticks || []).filter((t) => dateToFrac(t.date) >= TIMELINE.from) as t (t.date)}
              <span class="tickmark" aria-hidden="true" style="left:{x(dateToFrac(t.date))}%;top:{mid - 11}px"></span>
            {/each}
            {#if act.replaced_by_id && act.repealed}
              {@const target = p.placed.find((q) => q.act.id === act.replaced_by_id)}
              {#if target}
                {@const cx = x(dateToFrac(act.repealed))}
                {@const nx = x(Math.max(dateToFrac(target.act.enacted), TIMELINE.from))}
                {#if nx > cx}
                  <span class="connector" style="left:{cx}%;width:{nx - cx}%;top:{mid - 1}px"></span>
                {/if}
              {/if}
            {/if}
          {/each}
        </div>
      </div>
    {/each}

    <div class="bandrow">
      <GovBand />
      <div class="bandlegend">
        <span class="wl-label" style="font-size:8.5px">government bands: <span style="color:var(--gov-nat)">◼</span> National · <span style="color:var(--gov-lab)">◼</span> Labour (factual, never a verdict)</span>
      </div>
    </div>
  </div>

  <div class="caption">
    <span class="wl-mono captext">
      <span style="color:var(--signal)">RMA 1991</span> → replacement passed Aug 2023 → replacement repealed Dec 2023 →
      new replacement before the House now. The original is still in force.
      <span style="color:var(--ink-3)"> Click any act for its history. Full amendment density lands with the data pipeline.</span>
    </span>
  </div>

  {#if selectedAct}
    <ActPanel act={selectedAct.act} lane={selectedAct.lane} onclose={() => (ui.selectedAct = null)} />
  {/if}
</div>

<style>
  .churn {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    position: relative;
    min-height: 0;
  }

  .cards {
    grid-template-columns: repeat(4, 1fr);
    margin: 14px 16px 0;
  }

  .card.pending {
    opacity: 0.75;
  }

  .cval {
    font-size: 22px;
  }

  .pendingval {
    color: var(--ink-3);
  }

  .clabel {
    margin-top: 5px;
    line-height: 1.4;
    text-transform: none;
    letter-spacing: 0.02em;
  }

  .csub {
    font-size: 9px;
    color: var(--ink-3);
    margin-top: 4px;
    line-height: 1.5;
  }

  .csrc {
    display: inline-block;
    font-size: 8.5px;
    color: var(--signal);
    text-decoration: none;
    margin-top: 5px;
  }

  .lanehead {
    padding: 16px 16px 4px;
    display: flex;
    align-items: baseline;
    gap: 10px;
  }

  .rule {
    flex: 1;
    height: 1px;
    background: var(--line);
  }

  .conn-hint {
    font-size: 9px;
    color: var(--ink-3);
  }

  .lanes {
    padding: 0 16px 8px;
  }

  .axis {
    position: relative;
    height: 22px;
    margin-left: 130px;
  }

  .tick {
    position: absolute;
    top: 4px;
    font-size: 9px;
  }

  .tick.now {
    transform: translateX(-100%);
    color: var(--signal);
  }

  .lane {
    position: relative;
    border-bottom: 1px solid var(--line);
    display: flex;
  }

  .lanelabel {
    width: 130px;
    flex: none;
    display: flex;
    align-items: center;
    padding-right: 10px;
    border-right: 1px solid var(--line-2);
  }

  .lname {
    font-size: 10.5px;
    letter-spacing: 0.03em;
    color: var(--ink-2);
  }

  .lname.sig {
    color: var(--signal);
    font-weight: 700;
  }

  .bars {
    position: relative;
    flex: 1;
  }

  .bar {
    position: absolute;
    height: 18px;
    background: color-mix(in srgb, var(--bar-color) 20%, transparent);
    border: 1.4px solid var(--bar-color);
    border-radius: 2px;
    display: flex;
    align-items: center;
    overflow: visible;
    white-space: nowrap;
    padding: 0;
  }

  /* guaranteed >=24px hit target regardless of bar width */
  .bar::after {
    content: '';
    position: absolute;
    top: -6px;
    bottom: -6px;
    left: 50%;
    transform: translateX(-50%);
    width: max(calc(100% + 10px), 24px);
  }

  .bar:hover {
    background: color-mix(in srgb, var(--bar-color) 32%, transparent);
  }

  /* non-colour status cues */
  .bar.cancelled {
    background-image: repeating-linear-gradient(
      45deg,
      transparent 0 3px,
      color-mix(in srgb, var(--bar-color) 40%, transparent) 3px 5px
    );
  }

  .bar.restored {
    border-style: double;
    border-width: 3px;
  }

  .bar.zombie {
    border-style: dashed;
  }

  .bar.openend {
    border-right-style: dashed;
  }

  .blabel {
    font-size: 8.5px;
    color: var(--ink);
    padding: 0 6px;
    font-weight: 600;
    letter-spacing: 0.01em;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
  }

  .pre {
    font-size: 7.5px;
    color: var(--ink-3);
    padding-left: 3px;
    flex: none;
  }

  .floatlabel {
    position: absolute;
    top: calc(50% - 22px);
    font-size: 8px;
    font-weight: 600;
    color: var(--ink-2);
    white-space: nowrap;
    background: var(--bg);
    padding: 0 3px;
    z-index: 2;
  }

  .floatlabel:hover {
    color: var(--signal);
  }

  /* >=24px-tall hit target without painting over neighbours */
  .floatlabel::after {
    content: '';
    position: absolute;
    left: -4px;
    right: -4px;
    top: 50%;
    transform: translateY(-50%);
    height: 24px;
  }

  .tickmark {
    position: absolute;
    top: calc(50% - 11px);
    width: 1.5px;
    height: 22px;
    background: var(--ink-3);
    opacity: 0.8;
    pointer-events: none;
  }

  .connector {
    position: absolute;
    top: calc(50% - 1px);
    height: 0;
    border-top: 1px dashed var(--signal);
    opacity: 0.8;
    pointer-events: none;
  }

  .bandrow {
    margin-left: 130px;
    margin-top: 7px;
  }

  .bandlegend {
    margin-top: 4px;
  }

  .caption {
    margin-top: auto;
    padding: 8px 16px 12px;
    border-top: 1px solid var(--line-2);
    background: var(--surface-2);
  }

  .captext {
    font-size: 10px;
    color: var(--ink-2);
    line-height: 1.6;
  }

  @media (max-width: 760px) {
    .cards {
      grid-template-columns: repeat(2, 1fr);
    }

    .lanelabel {
      width: 86px;
    }

    .axis,
    .bandrow {
      margin-left: 86px;
    }

    .lname {
      font-size: 9px;
    }
  }
</style>
