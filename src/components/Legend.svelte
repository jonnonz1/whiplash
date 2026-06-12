<script>
  import { STATUS, STATUS_KEYS } from '../lib/status.js';
  import StatusGlyph from './StatusGlyph.svelte';
</script>

<div class="legend">
  {#each STATUS_KEYS as k (k)}
    <span class="item" title={STATUS[k].blurb}>
      <StatusGlyph g={STATUS[k].glyph} size={12} color={STATUS[k].color} />
      <span class="wl-label" style="font-size:9px">{STATUS[k].label}</span>
    </span>
  {/each}
</div>

<style>
  .legend {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 14px;
    background: rgba(12, 21, 32, 0.7);
    border-radius: 3px;
    padding: 5px 8px;
  }

  .item {
    display: inline-flex;
    align-items: center;
    gap: 5px;
  }
</style>
