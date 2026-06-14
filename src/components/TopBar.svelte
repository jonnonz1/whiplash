<script>
  import WLMark from './WLMark.svelte';
  import { ui, urlQuery } from '../lib/state.svelte.js';

  const taglines = {
    map: 'the graveyard',
    churn: 'the statute book, moving',
    explore: 'the whole statute book',
    method: 'how we count',
  };

  let copied = $state(false);

  async function share() {
    const url = location.origin + location.pathname + (urlQuery().startsWith('?') ? urlQuery() : '');
    try {
      await navigator.clipboard.writeText(url);
      copied = true;
      setTimeout(() => (copied = false), 1600);
    } catch {
      prompt('Copy this link:', url);
    }
  }

  function go(view) {
    ui.view = view;
    ui.selectedAct = null;
    ui.exploreSector = null;
  }
</script>

<header class="wl-top">
  <button class="wl-logo" onclick={() => go('explore')} aria-label="Whiplash home">
    <WLMark />
    <span class="word">WHIP<span class="dot">·</span>LASH</span>
  </button>
  <span class="wl-label tagline">{taglines[ui.view]}</span>
  <nav class="nav" aria-label="Views">
    <button class="wl-tab" class:on={ui.view === 'map'} onclick={() => go('map')} aria-current={ui.view === 'map' ? 'page' : undefined}>↺ Map</button>
    <button class="wl-tab" class:on={ui.view === 'explore'} onclick={() => go('explore')} aria-current={ui.view === 'explore' ? 'page' : undefined}>⊞ Explore</button>
    <button class="wl-tab" class:on={ui.view === 'method'} onclick={() => go('method')} aria-current={ui.view === 'method' ? 'page' : undefined}>Method</button>
  </nav>
  <button class="wl-pill share" onclick={share}>{copied ? '✓ copied' : '⤴ Share'}</button>
  <span class="sr-only" role="status">{copied ? 'Link copied to clipboard' : ''}</span>
</header>

<style>
  .tagline {
    margin-left: 4px;
  }

  .share {
    flex: none;
  }

  @media (max-width: 560px) {
    .tagline {
      display: none;
    }

    :global(.wl-top) {
      padding: 0 12px;
      gap: 8px;
    }
  }
</style>
