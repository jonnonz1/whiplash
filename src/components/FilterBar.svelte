<script>
  import { ui } from '../lib/state.svelte.js';
  import { db } from '../lib/data.svelte.js';
  import { STATUS, STATUS_KEYS, SECTORS } from '../lib/status.js';

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

  <label class="visually-hidden" for="f-status">Status</label>
  <select id="f-status" class="wl-pill" bind:value={ui.status}>
    <option value="">Status</option>
    {#each STATUS_KEYS as k (k)}
      <option value={k}>{STATUS[k].label}</option>
    {/each}
  </select>

  <label class="visually-hidden" for="f-min">Minimum sunk cost</label>
  <select id="f-min" class="wl-pill" bind:value={ui.minCost}>
    {#each MIN_OPTIONS as o (o.v)}
      <option value={o.v}>{o.label}</option>
    {/each}
  </select>
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

  @media (max-width: 560px) {
    .filters {
      justify-content: flex-start;
    }
  }
</style>
