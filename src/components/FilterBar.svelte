<script>
  import { ui } from '../lib/state.svelte.js';
  import { db } from '../lib/data.svelte.js';
  import { STATUS, STATUS_KEYS, SECTORS } from '../lib/status.js';
  import StatusGlyph from './StatusGlyph.svelte';

  const sectorsInUse = $derived([...new Set(db.projects.map((p) => p.sector))]);

  const MIN_OPTIONS = [
    { v: 0, label: 'Any sunk cost' },
    { v: 50_000_000, label: '$50m+' },
    { v: 100_000_000, label: '$100m+' },
    { v: 250_000_000, label: '$250m+' },
  ];
</script>

<div class="filters">
  <label class="visually-hidden" for="f-govt">Government</label>
  <select id="f-govt" class="wl-pill" bind:value={ui.govt}>
    <option value="">Government</option>
    {#each db.governments.filter((g) => g.parliament >= 49) as g (g.id)}
      <option value={g.id}>{g.label}</option>
    {/each}
  </select>

  <label class="visually-hidden" for="f-sector">Sector</label>
  <select id="f-sector" class="wl-pill" bind:value={ui.sector}>
    <option value="">Sector</option>
    {#each sectorsInUse as s (s)}
      <option value={s}>{SECTORS[s] || s}</option>
    {/each}
  </select>

  <label class="visually-hidden" for="f-min">Minimum sunk cost</label>
  <select id="f-min" class="wl-pill" bind:value={ui.minCost}>
    {#each MIN_OPTIONS as o (o.v)}
      <option value={o.v}>{o.label}</option>
    {/each}
  </select>

  <!-- status chips double as the legend: glyph + label, tap to filter -->
  <div class="statuschips" role="group" aria-label="Filter by status">
    {#each STATUS_KEYS as k (k)}
      <button
        class="schip"
        class:on={ui.status === k}
        aria-pressed={ui.status === k}
        title={STATUS[k].blurb}
        onclick={() => (ui.status = ui.status === k ? '' : k)}
      >
        <StatusGlyph g={STATUS[k].glyph} size={11} color={STATUS[k].color} />
        <span>{STATUS[k].label}</span>
      </button>
    {/each}
  </div>
</div>

<style>
  .filters {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    justify-content: flex-end;
  }

  .visually-hidden {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0 0 0 0);
  }

  .statuschips {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
    justify-content: flex-end;
    width: 100%;
  }

  .schip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-family: var(--font-mono);
    font-size: 9px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--ink-3);
    border: 1px solid var(--line-2);
    border-radius: 2px;
    padding: 4px 7px;
    background: rgba(12, 21, 32, 0.82);
    min-height: 24px;
  }

  .schip:hover {
    color: var(--ink-2);
    border-color: var(--ink-3);
  }

  .schip.on {
    color: var(--ink);
    border-color: var(--signal);
    background: rgba(212, 168, 83, 0.14);
  }

  @media (max-width: 560px) {
    .filters {
      justify-content: flex-start;
    }
  }
</style>
