<script>
  /* Click an act → its history as a vertical timeline, each event stamped
     with the government in power. */
  import { onDestroy } from 'svelte';
  import { db } from '../lib/data.svelte.js';
  import { dateLabel, dateToFrac } from '../lib/format.js';

  let { act, lane, onclose } = $props();

  let panel;
  let returnFocus;

  $effect(() => {
    if (act && panel) {
      returnFocus = document.activeElement;
      panel.focus();
    }
  });

  onDestroy(() => {
    if (returnFocus?.isConnected && returnFocus !== document.body) returnFocus.focus();
  });

  function govtFor(dateIso) {
    const frac = dateToFrac(dateIso);
    for (const g of db.governments) {
      const s = dateToFrac(g.start);
      const e = g.end ? dateToFrac(g.end) : Infinity;
      if (frac >= s && frac < e) return g;
    }
    return null;
  }

  const OP_LABEL = {
    amended: 'Amended',
    inserted: 'Inserted',
    substituted: 'Substituted',
    replaced: 'Replaced',
    repealed: 'Repealed',
    revoked: 'Revoked',
    other: 'Changed',
  };

  /* Pipeline-parsed events when available; hand-curated ticks otherwise. */
  const events = $derived.by(() => {
    const list = [{ date: act.enacted, op: act.is_bill ? 'Introduced' : act.is_setting ? 'Introduced' : 'Enacted', what: act.title }];
    if (act.events?.length) {
      for (const e of act.events) {
        list.push({
          date: e.date,
          op: OP_LABEL[e.op] || 'Changed',
          what: [e.provision, e.by_title].filter(Boolean).join(' — '),
        });
      }
      const hasDeath = act.events.some((e) => e.op === 'repealed' || e.op === 'revoked');
      if (act.repealed && !hasDeath) list.push({ date: act.repealed, op: 'Repealed', what: act.repealed_by || '' });
    } else {
      for (const t of act.ticks || []) list.push({ date: t.date, op: act.is_setting ? 'Setting changed' : 'Amended', what: t.what });
      if (act.repealed) list.push({ date: act.repealed, op: 'Repealed', what: act.repealed_by || '' });
    }
    return list.sort((a, b) => a.date.localeCompare(b.date));
  });

  /* heavily-amended acts can carry hundreds of provision-level events —
     show the enactment plus the most recent slice */
  const MAX_EVENTS = 40;
  const shownEvents = $derived(
    events.length > MAX_EVENTS ? [events[0], ...events.slice(events.length - (MAX_EVENTS - 1))] : events
  );
  const hiddenCount = $derived(events.length - shownEvents.length);

  function onKey(e) {
    if (e.key === 'Escape') onclose();
  }
</script>

<svelte:window onkeydown={onKey} />

<div class="panel" role="dialog" bind:this={panel} tabindex="-1" aria-label="{act.title} history">
  <div class="sheet-handle" aria-hidden="true"></div>
  <div class="head">
    <div class="row">
      <span class="wl-label">{lane.label}</span>
      <button class="close wl-mono" onclick={onclose} aria-label="Close panel">✕</button>
    </div>
    <h2 class="wl-disp name">{act.title}</h2>
    {#if act.lifespan_note}
      <div class="wl-mono life">in force {act.lifespan_note}</div>
    {/if}
    {#if act.amendment_count}
      <div class="wl-mono life">{act.amendment_count} amendment events on record</div>
    {/if}
    {#if act.open_note}
      <div class="wl-mono life">{act.open_note}</div>
    {/if}
  </div>

  <div class="body">
    <div class="timeline">
      <div class="spine"></div>
      {#if hiddenCount > 0}
        <p class="wl-mono partial" style="margin:0 0 10px">
          Showing the {MAX_EVENTS - 1} most recent of {events.length} recorded events ({hiddenCount} earlier ones
          omitted for length).
        </p>
      {/if}
      {#each shownEvents as ev, i (i)}
        {@const g = govtFor(ev.date)}
        <div class="ev">
          <span class="dot {g?.party || ''}"></span>
          <div class="evbody">
            <div class="evtop">
              <span class="wl-mono evdate">{dateLabel(ev.date)}</span>
              <span class="wl-mono evop" class:repeal={ev.op === 'Repealed'}>{ev.op}</span>
              {#if g}<span class="wl-mono evgov">{g.label}</span>{/if}
            </div>
            {#if ev.what && ev.what !== act.title}
              <div class="evwhat">{ev.what}</div>
            {/if}
          </div>
        </div>
      {/each}
    </div>

    {#if act.partial !== false && !act.events?.length}
      <p class="wl-mono partial">
        Major amendment acts only. Every amendment to every section — the full picture — lands when the legislation
        pipeline finishes parsing the statute book.
      </p>
    {/if}
  </div>

  <div class="foot">
    <span class="wl-mono fine">
      Source: New Zealand Legislation (PCO) — free of copyright, s 27 Copyright Act 1994.
      {#if act.dlm && act.leg_no}<a href="https://www.legislation.govt.nz/act/public/{act.leg_year}/{act.leg_no}/latest/{act.dlm}.html" target="_blank" rel="noopener">↗ legislation.govt.nz</a>{/if}
    </span>
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
    position: fixed;
    top: 66px;
    right: 14px;
    bottom: 14px;
    width: 380px;
    max-width: calc(100% - 28px);
    background: var(--surface-2);
    border: 1px solid var(--line-2);
    border-radius: 3px;
    display: flex;
    flex-direction: column;
    z-index: 9;
    outline: none;
  }

  .head {
    padding: 16px 18px 12px;
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
    font-size: 19px;
    margin: 9px 0 0;
  }

  .life {
    font-size: 9.5px;
    color: var(--signal);
    margin-top: 6px;
  }

  .body {
    flex: 1;
    overflow-y: auto;
    padding: 14px 18px;
  }

  .timeline {
    position: relative;
    padding-left: 14px;
  }

  .spine {
    position: absolute;
    left: 3px;
    top: 4px;
    bottom: 4px;
    width: 1px;
    background: var(--line-2);
  }

  .ev {
    position: relative;
    padding-bottom: 12px;
  }

  .dot {
    position: absolute;
    left: -14px;
    top: 4px;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--ink-3);
    opacity: 0.9;
  }

  .dot.labour {
    background: var(--gov-lab);
  }

  .dot.national {
    background: var(--gov-nat);
  }

  .evtop {
    display: flex;
    gap: 8px;
    align-items: baseline;
    flex-wrap: wrap;
  }

  .evdate {
    font-size: 9.5px;
    color: var(--ink-3);
  }

  .evop {
    font-size: 10px;
    font-weight: 700;
    color: var(--ink-2);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .evop.repeal {
    color: var(--signal);
  }

  .evgov {
    font-size: 9px;
    color: var(--ink-3);
  }

  .evwhat {
    font-weight: 300;
    font-size: 10.5px;
    color: var(--ink-2);
    line-height: 1.45;
    margin-top: 3px;
  }

  .partial {
    font-size: 9.5px;
    color: var(--ink-3);
    line-height: 1.6;
    border: 1px dashed var(--line-2);
    border-radius: 2px;
    padding: 8px 10px;
    margin: 10px 0 0;
  }

  .foot {
    padding: 10px 18px 12px;
    border-top: 1px solid var(--line-2);
  }

  .fine {
    font-size: 8.5px;
    color: var(--ink-3);
    line-height: 1.5;
  }

  .fine a {
    color: var(--signal);
    text-decoration: none;
  }

  @media (max-width: 560px) {
    .panel {
      top: auto;
      left: 0;
      right: 0;
      bottom: 0;
      width: auto;
      max-width: none;
      max-height: 70%;
      border-radius: 8px 8px 0 0;
    }
  }
</style>
