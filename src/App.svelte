<script>
  import { onMount } from 'svelte';
  import { ui, initFromURL, urlQuery } from './lib/state.svelte.js';
  import { db, loadData } from './lib/data.svelte.js';
  import TopBar from './components/TopBar.svelte';
  import MapView from './components/MapView.svelte';
  import ChurnView from './components/ChurnView.svelte';
  import Methodology from './components/Methodology.svelte';
  import NationwideTray from './components/NationwideTray.svelte';
  import Scrubber from './components/Scrubber.svelte';

  onMount(() => {
    initFromURL();
    loadData();
  });

  /* every state is a shareable deep link; debounced so scrubbing doesn't
     hit Safari's replaceState rate limit */
  $effect(() => {
    const q = urlQuery();
    const timer = setTimeout(() => {
      if (location.search !== (q.startsWith('?') ? q : '')) {
        try {
          history.replaceState(null, '', q);
        } catch {
          /* Safari rate limit — next settled state wins */
        }
      }
    }, 150);
    return () => clearTimeout(timer);
  });
</script>

<div class="shell">
  <TopBar />

  {#if !ui.introDismissed && ui.view === 'map'}
    <div class="intro">
      <span class="wl-mono introtext">
        Every cancelled project and reversed law since 2008, with what it cost — and what the churn costs the next
        generation. Drag the timeline to replay history; every number links to its source.
      </span>
      <button class="wl-mono introclose" onclick={() => (ui.introDismissed = true)} aria-label="Dismiss">✕</button>
    </div>
  {/if}

  {#if db.error}
    <div class="err wl-mono">Failed to load data: {db.error}</div>
  {:else if !db.ready}
    <div class="loading wl-label">// loading the receipts…</div>
  {:else if ui.view === 'map'}
    <MapView />
    <NationwideTray />
    <Scrubber />
  {:else if ui.view === 'churn'}
    <ChurnView />
  {:else}
    <Methodology />
  {/if}
</div>

<style>
  .shell {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .intro {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 7px 18px;
    background: var(--surface);
    border-bottom: 1px solid var(--line);
  }

  .introtext {
    font-size: 10px;
    color: var(--ink-2);
    line-height: 1.5;
  }

  .introclose {
    margin-left: auto;
    color: var(--ink-3);
    font-size: 11px;
    flex: none;
  }

  .loading,
  .err {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .err {
    color: var(--st-reversed);
    font-size: 11px;
  }
</style>
