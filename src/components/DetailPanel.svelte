<script>
  /* Project detail — the firm-vs-contested credibility mechanic, rendered.
     Firm figures: bold, sourced, counted. Contested: hatched, bracketed,
     behind a "claimed" chip, never counted. */
  import { onDestroy } from 'svelte';
  import { db, govtById } from '../lib/data.svelte.js';
  import { fmtMoney, dateLabel, dateToFrac } from '../lib/format.js';
  import StatusChip from './StatusChip.svelte';
  import { SERIES_NAME } from '../lib/essays.js';

  let { project, onclose } = $props();

  let panel;
  let returnFocus;

  $effect(() => {
    if (project && panel) {
      returnFocus = document.activeElement;
      panel.focus();
    }
  });

  onDestroy(() => {
    if (returnFocus?.isConnected && returnFocus !== document.body) returnFocus.focus();
  });

  function partyTag(govtId, dateIso) {
    const g = govtById(govtId);
    const year = dateIso ? dateIso.slice(0, 4) : '';
    if (!g) return year;
    const party = g.party === 'labour' ? 'Labour' : 'National';
    return `${year} · ${party}`;
  }

  function eventParty(dateIso) {
    const frac = dateToFrac(dateIso);
    for (const g of db.governments) {
      const s = dateToFrac(g.start);
      const e = g.end ? dateToFrac(g.end) : Infinity;
      if (frac >= s && frac < e) return g.party;
    }
    return 'national';
  }

  function domain(url) {
    try {
      return new URL(url).hostname.replace('www.', '');
    } catch {
      return url;
    }
  }

  function onKey(e) {
    if (e.key === 'Escape') onclose();
  }
</script>

<svelte:window onkeydown={onKey} />

<div class="panel" role="dialog" bind:this={panel} tabindex="-1" aria-label="{project.name} details">
  <div class="sheet-handle" aria-hidden="true"></div>
  <div class="head">
    <div class="row">
      <StatusChip status={project.status} />
      <button class="close wl-mono" onclick={onclose} aria-label="Close panel">✕</button>
    </div>
    <h2 class="wl-disp name">{project.name}</h2>
    <div class="meta">
      <div>
        <div class="wl-label">Started</div>
        <div class="wl-mono mval">{partyTag(project.started_by, project.announced)}</div>
      </div>
      <div>
        <div class="wl-label">Stopped</div>
        <div class="wl-mono mval">{project.ended ? partyTag(project.ended_by, project.ended) : 'ongoing'}</div>
      </div>
      {#if project.region}
        <div>
          <div class="wl-label">Where</div>
          <div class="wl-mono mval">{project.region}</div>
        </div>
      {/if}
    </div>
  </div>

  <div class="body">
    <p class="what">{project.plain}</p>

    <div class="wl-label sig sect">// Firm figures — sourced &amp; counted</div>
    {#if project.firm?.length}
      <div class="firmlist">
        {#each project.firm as f, i (i)}
          <div class="firmrow" class:last={i === project.firm.length - 1 && project.firm.length === 1}>
            <span class="wl-mono fkey">{f.label}</span>
            <span class="fval">
              <span class="fig-firm" style="font-size:15px">{fmtMoney(f.amount_nzd)}</span>
              <span class="fig-firm fsrc">
                {#if f.url}<a class="src" href={f.url} target="_blank" rel="noopener">↗ {f.source}</a>{:else}↗ {f.source}{/if}
              </span>
            </span>
          </div>
        {/each}
        {#if project.firm.length > 1}
          <div class="firmrow total">
            <span class="wl-mono fkey">Total on the public record</span>
            <span class="fig-firm" style="font-size:22px">{fmtMoney(project.sunk_nzd)}</span>
          </div>
        {/if}
      </div>
    {:else}
      <p class="note">
        {project.firm_note || 'No firm sunk-cost figure is on the public record for this one.'}
      </p>
    {/if}

    {#if project.contested?.length}
      <div class="chead">
        <span class="wl-label">// Contested — not counted in totals</span>
        <span class="chip-claimed">⚠ claimed</span>
      </div>
      <div class="clist">
        {#each project.contested as c, i (i)}
          <div class="crow">
            <span class="fig-contested" style="font-size:13px">[ {c.figure} ]</span>
            <span class="wl-mono cwho">{c.label}{c.note ? ` — ${c.note}` : ''}</span>
          </div>
        {/each}
      </div>
    {/if}

    {#if project.consequential?.length}
      <div class="wl-label sect" style="color:var(--st-reversed)">// The do-over — real money, never counted in totals</div>
      <div class="firmlist">
        {#each project.consequential as c, i (i)}
          <div class="firmrow">
            <span class="wl-mono fkey">{c.label}{c.note ? ` — ${c.note}` : ''}</span>
            <span class="fval">
              <span class="fig-firm" style="font-size:14px;color:var(--st-reversed)">{c.amount_nzd ? fmtMoney(c.amount_nzd) : '—'}</span>
              {#if c.source}<span class="fig-firm fsrc" style="color:var(--ink-3)">{c.source}</span>{/if}
            </span>
          </div>
        {/each}
      </div>
    {/if}

    {#if project.extra_costs?.length}
      <div class="wl-label sect">// Worth knowing</div>
      <ul class="extras">
        {#each project.extra_costs as x, i (i)}
          <li><span class="wl-mono xlabel">{x.label}:</span> {x.note}</li>
        {/each}
      </ul>
    {/if}

    {#if project.events?.length}
      <div class="wl-label sect">// This project's own lurches</div>
      <div class="lurches">
        <div class="spine"></div>
        {#each project.events as ev, i (i)}
          <div class="lurch">
            <span class="dot {eventParty(ev.date)}" aria-hidden="true"></span>
            <span class="wl-mono ldate">{dateLabel(ev.date)}<span class="sr-only"> — {eventParty(ev.date) === 'labour' ? 'Labour' : 'National'} government</span></span>
            <span class="wl-mono lop">{ev.op}</span>
            <span class="ltext">{ev.what}</span>
          </div>
        {/each}
      </div>
    {/if}
  </div>

  <div class="foot">
    {#if project.sources?.length}
      <div class="wl-label" style="margin-bottom:6px">// Sources</div>
      <div class="sources">
        {#each project.sources as s, i (i)}
          <a class="wl-mono srclink" href={typeof s === 'string' ? s : s.url} target="_blank" rel="noopener">
            <span style="color:var(--signal)">↗</span>
            {typeof s === 'string' ? domain(s) : s.title}
          </a>
        {/each}
      </div>
    {/if}
    {#if project.essay}
      <a class="wl-mono essay" href={project.essay}>↗ Read the essay on jonno.nz</a>
    {:else}
      <span class="wl-mono essay soon">Featured in the {SERIES_NAME} essays on jonno.nz — coming soon</span>
    {/if}
  </div>
</div>

<style>
  .sheet-handle {
    display: none;
  }

  @media (max-width: 560px) {
    .sheet-handle {
      display: block;
      flex: none;
      width: 34px;
      height: 3px;
      border-radius: 2px;
      background: var(--line-2);
      margin: 8px auto 0;
    }
  }

  .panel {
    position: absolute;
    top: 14px;
    right: 14px;
    bottom: 14px;
    width: 380px;
    max-width: calc(100% - 28px);
    background: var(--surface-2);
    border: 1px solid var(--line-2);
    border-radius: 3px;
    display: flex;
    flex-direction: column;
    z-index: 7;
    outline: none;
  }

  .head {
    padding: 16px 18px 14px;
    border-bottom: 1px solid var(--line-2);
  }

  .row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }

  .close {
    font-size: 13px;
    color: var(--ink-3);
    padding: 2px 6px;
  }

  .close:hover {
    color: var(--ink);
  }

  .name {
    font-size: 23px;
    margin: 11px 0 0;
  }

  .meta {
    display: flex;
    gap: 14px;
    margin-top: 10px;
    flex-wrap: wrap;
  }

  .mval {
    font-size: 11px;
    color: var(--ink-2);
    margin-top: 2px;
  }

  .body {
    flex: 1;
    overflow-y: auto;
    padding: 12px 18px;
  }

  .what {
    font-weight: 300;
    font-size: 12.5px;
    line-height: 1.55;
    color: var(--ink-2);
    margin: 0 0 12px;
  }

  .sect {
    margin: 12px 0 6px;
  }

  .sect:first-of-type {
    margin-top: 0;
  }

  .firmlist {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  .firmrow {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 12px;
    padding-bottom: 6px;
    border-bottom: 1px dotted var(--line);
  }

  .firmrow.total {
    border-bottom: none;
    padding-top: 2px;
  }

  .fkey {
    font-size: 10.5px;
    color: var(--ink-3);
    letter-spacing: 0.02em;
  }

  .fval {
    text-align: right;
    flex: none;
  }

  .fsrc {
    display: block;
    font-size: 8.5px;
    font-weight: 400;
  }

  .note {
    font-size: 11px;
    font-weight: 300;
    line-height: 1.5;
    color: var(--ink-3);
    border: 1px dashed var(--line-2);
    border-radius: 2px;
    padding: 8px 10px;
    margin: 0;
  }

  .chead {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 12px 0 6px;
  }

  .clist {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .crow {
    display: flex;
    align-items: baseline;
    gap: 9px;
  }

  .cwho {
    font-size: 9.5px;
    color: var(--ink-3);
    line-height: 1.4;
  }

  .extras {
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .extras li {
    font-size: 11px;
    font-weight: 300;
    line-height: 1.5;
    color: var(--ink-2);
    margin-bottom: 6px;
  }

  .xlabel {
    font-size: 9.5px;
    color: var(--ink-3);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .lurches {
    position: relative;
    padding-left: 14px;
  }

  .spine {
    position: absolute;
    left: 3px;
    top: 3px;
    bottom: 3px;
    width: 1px;
    background: var(--line-2);
  }

  .lurch {
    position: relative;
    display: flex;
    gap: 8px;
    align-items: baseline;
    padding-bottom: 7px;
  }

  .dot {
    position: absolute;
    left: -14px;
    top: 3px;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    opacity: 0.85;
  }

  .dot.labour {
    background: var(--gov-lab);
  }

  .dot.national {
    background: var(--gov-nat);
  }

  .ldate {
    font-size: 9.5px;
    color: var(--ink-3);
    width: 72px;
    flex: none;
  }

  .lop {
    font-size: 10px;
    color: var(--signal);
    font-weight: 700;
    width: 64px;
    flex: none;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .ltext {
    font-weight: 300;
    font-size: 10.5px;
    color: var(--ink-2);
    line-height: 1.4;
  }

  .foot {
    padding: 10px 18px 14px;
    border-top: 1px solid var(--line-2);
  }

  .sources {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 8px;
  }

  .srclink {
    font-size: 9.5px;
    color: var(--ink-2);
    text-decoration: none;
  }

  .srclink:hover {
    color: var(--signal);
  }

  .essay {
    font-size: 9.5px;
    color: var(--signal);
    text-decoration: none;
  }

  .essay.soon {
    color: var(--ink-3);
  }

  @media (max-width: 560px) {
    .panel {
      top: auto;
      left: 0;
      right: 0;
      bottom: 0;
      width: auto;
      max-width: none;
      max-height: 62%;
      border-radius: 8px 8px 0 0;
      border-left: none;
      border-right: none;
      border-bottom: none;
    }
  }
</style>
