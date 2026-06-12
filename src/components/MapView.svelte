<script>
  /* View 1 — The Map ("the graveyard"). Full-bleed MapLibre NZ, one marker
     per reversal, sized by sunk cost, themed to the Seismograph palette. */
  import { onMount, onDestroy } from 'svelte';
  import maplibregl from 'maplibre-gl';
  import 'maplibre-gl/dist/maplibre-gl.css';
  import { ui } from '../lib/state.svelte.js';
  import { db, projectStateAt, matchesFilters } from '../lib/data.svelte.js';
  import { STATUS } from '../lib/status.js';
  import { markerRadius, fmtMoney } from '../lib/format.js';
  import Hud from './Hud.svelte';
  import FilterBar from './FilterBar.svelte';
  import Legend from './Legend.svelte';
  import DetailPanel from './DetailPanel.svelte';

  let mapEl;
  let map;
  let loaded = $state(false);
  const markers = new Map(); // project id -> { marker, el }

  const NZ_BOUNDS = [
    [165.6, -47.6],
    [179.2, -34.0],
  ];

  onMount(() => {
    map = new maplibregl.Map({
      container: mapEl,
      style: 'https://basemaps.cartocdn.com/gl/dark-matter-nolabels-gl-style/style.json',
      bounds: NZ_BOUNDS,
      fitBoundsOptions: { padding: 30 },
      attributionControl: { compact: true },
      pitchWithRotate: false,
      dragRotate: false,
      touchPitch: false,
    });
    map.touchZoomRotate.disableRotation();
    map.keyboard.enable();

    map.on('load', () => {
      tintBasemap();
      loaded = true;
    });
  });

  onDestroy(() => {
    for (const { marker } of markers.values()) marker.remove();
    markers.clear();
    map?.remove();
  });

  /* Pull the basemap into the Seismograph navy world: land lifts to
     --land navy, sea drops to near-black, per the design. Best-effort —
     if CARTO renames layers a layer silently keeps its dark default. */
  function tintBasemap() {
    for (const layer of map.getStyle().layers) {
      const id = layer.id.toLowerCase();
      try {
        if (layer.type === 'background') {
          // CARTO's background is the land base
          map.setPaintProperty(layer.id, 'background-color', '#1a2738');
        } else if (layer.type === 'fill' && id.includes('water')) {
          map.setPaintProperty(layer.id, 'fill-color', '#081019');
        } else if (layer.type === 'fill' && (id.includes('land') || id.includes('park'))) {
          map.setPaintProperty(layer.id, 'fill-color', '#1a2738');
        } else if (layer.type === 'line' && (id.includes('boundary') || id.includes('admin'))) {
          map.setPaintProperty(layer.id, 'line-color', 'rgba(127,184,168,0.20)');
        }
      } catch {
        /* keep this layer's default */
      }
    }
  }

  function markerSvg(p, state) {
    const st = STATUS[state];
    const r = markerRadius(p.sunk_nzd);
    const s = r * 2 + 10;
    const c = s / 2;
    const dim = state === 'underway';
    const fillOp = state === 'restored' ? 0.16 : dim ? 0.12 : 0.2;
    const dash = state === 'zombie' ? `stroke-dasharray="3 2.2"` : '';
    const cross =
      state === 'cancelled'
        ? `<path d="M${c - r * 0.4} ${c - r * 0.4} L${c + r * 0.4} ${c + r * 0.4} M${c + r * 0.4} ${c - r * 0.4} L${c - r * 0.4} ${c + r * 0.4}" stroke="${st.hex}" stroke-width="1.6" stroke-linecap="round"/>`
        : '';
    /* shape carries status, never colour alone — glyphs match StatusGlyph/legend */
    const GLYPHS = {
      uturn: `<path d="M5 11 V7 a3 3 0 0 1 6 0 v1" fill="none" stroke="${st.hex}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 6 l2 2 2-2" fill="none" stroke="${st.hex}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>`,
      half: `<path d="M8 1.8 A6.2 6.2 0 0 1 8 14.2 Z" fill="${st.hex}" fill-opacity="0.55"/>`,
      loop: `<path d="M12 8 a4 4 0 1 1 -1.4 -3" fill="none" stroke="${st.hex}" stroke-width="2.2" stroke-linecap="round"/><path d="M12.2 2.4 l0.2 2.9 l-2.9 -0.4" fill="none" stroke="${st.hex}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>`,
    };
    const k = (r * 1.3) / 16;
    const inner = ['reversed', 'rescoped', 'restored'].includes(state)
      ? `<g transform="translate(${c - 8 * k} ${c - 8 * k}) scale(${k})">${GLYPHS[st.glyph]}</g>`
      : '';
    const ring =
      ui.selected === p.id
        ? `<circle cx="${c}" cy="${c}" r="${r + 5}" fill="none" stroke="${st.hex}" stroke-width="1" stroke-dasharray="2 3" opacity="0.7"/>`
        : '';
    return `<svg width="${s}" height="${s}" viewBox="0 0 ${s} ${s}" style="filter:drop-shadow(0 0 ${dim ? 0 : 4}px ${st.hex}66)">
      <circle cx="${c}" cy="${c}" r="${r}" fill="${st.hex}" fill-opacity="${fillOp}" stroke="${st.hex}" stroke-width="${ui.selected === p.id ? 2 : 1.4}" ${dash}/>
      ${cross}${inner}${ring}
    </svg>`;
  }

  /* Sync markers with time + filters. */
  $effect(() => {
    if (!loaded || !db.ready) return;
    for (const p of db.projects) {
      if (p.lat == null) continue;
      const state = projectStateAt(p, ui.t);
      const visible = state !== null && matchesFilters(p, ui);
      const existing = markers.get(p.id);
      if (!visible) {
        if (existing) {
          existing.marker.remove();
          markers.delete(p.id);
        }
        continue;
      }
      const label = `${p.name} — ${STATUS[state].label}${p.sunk_nzd ? ', ' + fmtMoney(p.sunk_nzd) + ' sunk' : ''}`;
      if (existing) {
        existing.el.innerHTML = markerSvg(p, state);
        existing.el.setAttribute('aria-label', label);
      } else {
        const el = document.createElement('button');
        el.className = 'wl-marker';
        el.setAttribute('aria-label', label);
        el.innerHTML = markerSvg(p, state);
        el.addEventListener('click', (e) => {
          e.stopPropagation();
          ui.selected = ui.selected === p.id ? null : p.id;
        });
        const marker = new maplibregl.Marker({ element: el }).setLngLat([p.lng, p.lat]).addTo(map);
        markers.set(p.id, { marker, el });
      }
    }
  });

  const selectedProject = $derived(db.projects.find((p) => p.id === ui.selected) || null);
</script>

<div class="wrap">
  <div class="map" bind:this={mapEl}></div>
  <div class="eng-grid"></div>

  <Hud />

  <div class="topright">
    <span class="legend-sm"><Legend /></span>
    <FilterBar />
  </div>

  <div class="bottomleft">
    <Legend />
    {#if db.generated}
      <span class="wl-mono asat">data as at {db.generated}</span>
    {/if}
  </div>

  {#if selectedProject}
    <DetailPanel project={selectedProject} onclose={() => (ui.selected = null)} />
  {/if}
</div>

<style>
  .wrap {
    position: relative;
    flex: 1;
    overflow: hidden;
    background: var(--bg);
    min-height: 0;
  }

  .map {
    position: absolute;
    inset: 0;
  }

  .topright {
    position: absolute;
    top: 14px;
    right: 14px;
    z-index: 5;
    max-width: 60%;
  }

  .legend-sm {
    display: none;
  }

  .bottomleft {
    position: absolute;
    bottom: 12px;
    left: 14px;
    z-index: 5;
    display: flex;
    flex-direction: column;
    gap: 4px;
    align-items: flex-start;
  }

  .asat {
    font-size: 8.5px;
    color: var(--ink-3);
    letter-spacing: 0.06em;
  }

  @media (max-width: 560px) {
    .topright {
      /* under the compact HUD, per the design's mobile frame */
      top: 132px;
      bottom: auto;
      right: 12px;
      left: 12px;
      max-width: none;
      display: flex;
      flex-direction: column;
      gap: 6px;
      align-items: stretch;
    }

    .legend-sm {
      display: block;
    }

    .bottomleft {
      display: none;
    }
  }
</style>
