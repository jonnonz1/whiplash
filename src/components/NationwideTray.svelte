<script>
  /* Non-geographic reversals (tax settings, nationwide laws) get a docked
     tray instead of fake coordinates. */
  import { ui } from '../lib/state.svelte.js';
  import { db, projectStateAt, matchesFilters } from '../lib/data.svelte.js';
  import { STATUS } from '../lib/status.js';
  import StatusGlyph from './StatusGlyph.svelte';

  const items = $derived(
    db.projects
      .filter((p) => p.lat == null)
      .filter((p) => matchesFilters(p, ui))
      .map((p) => ({ p, state: projectStateAt(p, ui.t) }))
      .filter((x) => x.state !== null)
  );

  let open = $state(false);

  /* deep links to a nationwide project should reveal its chip */
  $effect(() => {
    if (ui.selected && items.some((x) => x.p.id === ui.selected)) open = true;
  });
</script>

{#if items.length}
  <div class="tray">
    <button class="head" aria-expanded={open} onclick={() => (open = !open)}>
      <span class="wl-label">// {items.length} nationwide reversal{items.length === 1 ? '' : 's'} — no map pin</span>
      <span class="rule"></span>
      <span class="wl-label chev">{open ? '▾' : '▸'}</span>
    </button>
    {#if open}
      <div class="chips">
        {#each items as { p, state } (p.id)}
          <button
            class="chip"
            class:active={ui.selected === p.id}
            onclick={() => (ui.selected = ui.selected === p.id ? null : p.id)}
            title={p.summary}
          >
            <StatusGlyph g={STATUS[state].glyph} size={11} color={STATUS[state].color} />
            <span class="wl-mono name">{p.name}</span>
          </button>
        {/each}
      </div>
    {/if}
  </div>
{/if}

<style>
  .tray {
    border-top: 1px solid var(--line-2);
    background: var(--surface-2);
    padding: 9px 14px;
  }

  .head {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    text-align: left;
  }

  .head:hover .wl-label {
    color: var(--signal);
  }

  .chev {
    flex: none;
  }

  .rule {
    flex: 1;
    height: 1px;
    background: var(--line);
  }

  .chips {
    display: flex;
    gap: 7px;
    flex-wrap: wrap;
    margin-top: 8px;
  }

  .chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border: 1px solid var(--line-2);
    border-radius: 2px;
    padding: 4px 8px;
  }

  .chip:hover,
  .chip.active {
    border-color: var(--signal);
  }

  .name {
    font-size: 10px;
    color: var(--ink-2);
    white-space: nowrap;
  }

  @media (max-width: 560px) {
    .chips {
      flex-wrap: nowrap;
      overflow-x: auto;
      padding-bottom: 2px;
    }
  }
</style>
