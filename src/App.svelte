<script>
  import { onMount } from 'svelte';
  import { ui, initFromURL, urlQuery } from './lib/state.svelte.js';
  import { db, loadData } from './lib/data.svelte.js';
  import { trackView } from './lib/analytics.js';
  import TopBar from './components/TopBar.svelte';
  import MapView from './components/MapView.svelte';
  import ChurnView from './components/ChurnView.svelte';
  import ChurnExplorer from './components/ChurnExplorer.svelte';
  import TopChangeView from './components/TopChangeView.svelte';
  import Methodology from './components/Methodology.svelte';
  import NationwideTray from './components/NationwideTray.svelte';
  import Scrubber from './components/Scrubber.svelte';

  onMount(() => {
    initFromURL();
    loadData();
  });

  /* One GA pageview per view change (SPA — no real page loads). */
  $effect(() => {
    trackView(ui.view);
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
  {:else if ui.view === 'explore'}
    <ChurnExplorer />
  {:else if ui.view === 'top'}
    <TopChangeView />
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
