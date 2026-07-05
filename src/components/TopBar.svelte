<script>
  import WLMark from './WLMark.svelte';
  import { ui, urlQuery } from '../lib/state.svelte.js';
  import { SERIES_HOME } from '../lib/essays.js';

  const taglines = {
    map: 'the graveyard',
    churn: 'the statute book, moving',
    explore: 'the whole statute book',
    top: 'where the churn lands',
    method: 'how we count',
    corrections: 'when we get it wrong',
  };

  const CONTACT = 'jonno.nz@gmail.com';

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
    <button class="wl-tab" class:on={ui.view === 'top'} onclick={() => go('top')} aria-current={ui.view === 'top' ? 'page' : undefined}>↟ Top 10</button>
    <button class="wl-tab" class:on={ui.view === 'method'} onclick={() => go('method')} aria-current={ui.view === 'method' ? 'page' : undefined}>Method</button>
    <button class="wl-tab" class:on={ui.view === 'corrections'} onclick={() => go('corrections')} aria-current={ui.view === 'corrections' ? 'page' : undefined}>Corrections</button>
    <a class="wl-tab ext" href={SERIES_HOME} target="_blank" rel="noopener">↗ jonno.nz</a>
  </nav>
  <a class="wl-pill contact" href="mailto:{CONTACT}?subject=Whiplash" title="Email {CONTACT}">✉ <span class="word">Contact</span></a>
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

  .contact {
    flex: none;
    text-decoration: none;
    color: var(--signal);
    border-color: var(--signal);
  }

  .ext {
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    margin-left: 4px;
    padding-left: 14px;
    border-left: 1px solid var(--line-2);
  }

  @media (max-width: 560px) {
    .tagline {
      display: none;
    }

    .ext {
      display: none;
    }

    .contact .word {
      display: none;
    }

    /* tabs scroll; logo and the contact/share pills stay pinned */
    .nav {
      flex: 1;
      min-width: 0;
      overflow-x: auto;
      scrollbar-width: none;
    }

    .nav::-webkit-scrollbar {
      display: none;
    }

    .nav :global(.wl-tab) {
      flex: none;
    }

    :global(.wl-top) {
      padding: 0 12px;
      gap: 8px;
    }
  }
</style>
