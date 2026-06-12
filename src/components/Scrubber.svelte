<script>
  /* The signature interaction: a policy seismograph. The trace is
     data-driven — one spike per reversal, amplitude scaled by sunk cost —
     flat between governments, spiking on every U-turn. Drag (or arrow-key)
     the handle to replay history. */
  import { ui, TIMELINE } from '../lib/state.svelte.js';
  import { db, projectStateAt } from '../lib/data.svelte.js';
  import { dateToFrac, fracLabel, clamp } from '../lib/format.js';
  import { STATUS } from '../lib/status.js';
  import GovBand from './GovBand.svelte';
  import StatusGlyph from './StatusGlyph.svelte';

  let { compact = false } = $props();

  let track; // bound element
  let dragging = $state(false);

  const span = TIMELINE.to - TIMELINE.from;
  const pos = $derived(((ui.t - TIMELINE.from) / span) * 100);

  /* Reversal events: when each project ended (= flipped status). */
  const flips = $derived(
    db.projects
      .filter((p) => p.ended)
      .map((p) => ({
        x: ((dateToFrac(p.ended) - TIMELINE.from) / span) * 100,
        amp: 4 + Math.log10((p.sunk_nzd || 0) + 1) * 1.6,
        name: p.name,
        status: p.status,
      }))
      .filter((f) => f.x >= 0 && f.x <= 100)
  );

  /* Seismograph polyline: baseline noise + a spike at each flip. */
  const trace = $derived.by(() => {
    const pts = [];
    const N = 240;
    for (let i = 0; i <= N; i++) {
      const x = (i / N) * 100;
      let y = 23;
      for (let k = 0; k < flips.length; k++) {
        const f = flips[k];
        const d = Math.abs(x - f.x);
        if (d < 1.6) y += (k % 2 ? -1 : 1) * (1.6 - d) * f.amp;
      }
      y += Math.sin(i * 0.9) * 0.9;
      pts.push(`${x.toFixed(2)},${clamp(y, 2, 44).toFixed(2)}`);
    }
    return pts.join(' ');
  });

  /* The "status flip" moment: handle is near a reversal. */
  const nearestFlip = $derived.by(() => {
    let best = null;
    for (const f of flips) {
      if (!best || Math.abs(f.x - pos) < Math.abs(best.x - pos)) best = f;
    }
    return best && Math.abs(best.x - pos) < 0.8 ? best : null;
  });
  const nearFlip = $derived(nearestFlip !== null);

  const atToday = $derived(TIMELINE.to - ui.t < 1 / 24);
  const idle = $derived(atToday && !dragging);

  const visibleCount = $derived(db.projects.filter((p) => projectStateAt(p, ui.t) !== null).length);

  function setFromClientX(clientX) {
    const r = track.getBoundingClientRect();
    const frac = clamp((clientX - r.left) / r.width, 0, 1);
    ui.t = TIMELINE.from + frac * span;
  }

  function onPointerDown(e) {
    if (e.button !== 0 || !e.isPrimary) return;
    dragging = true;
    track.setPointerCapture(e.pointerId);
    setFromClientX(e.clientX);
  }

  function onPointerMove(e) {
    if (dragging) setFromClientX(e.clientX);
  }

  function onPointerUp() {
    dragging = false;
  }

  function onKey(e) {
    const month = 1 / 12;
    if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') ui.t = clamp(ui.t - month, TIMELINE.from, TIMELINE.to);
    else if (e.key === 'ArrowRight' || e.key === 'ArrowUp') ui.t = clamp(ui.t + month, TIMELINE.from, TIMELINE.to);
    else if (e.key === 'PageDown') ui.t = clamp(ui.t - 1, TIMELINE.from, TIMELINE.to);
    else if (e.key === 'PageUp') ui.t = clamp(ui.t + 1, TIMELINE.from, TIMELINE.to);
    else if (e.key === 'Home') ui.t = TIMELINE.from;
    else if (e.key === 'End') ui.t = TIMELINE.to;
    else return;
    e.preventDefault();
  }
</script>

<div class="scrub" class:compact>
  <div class="row">
    <span class="wl-label">// {TIMELINE.from}</span>
    <span class="wl-label sig">{idle ? '▎scrub to replay history' : fracLabel(ui.t)}</span>
    <span class="wl-label">{atToday ? 'Today' : 'Today →'}</span>
  </div>

  <!-- state readout: idle count · replay count · the status-flip moment -->
  <div class="readout" aria-live="polite">
    {#if idle}
      <span class="wl-mono quiet">{flips.length} reversals on the record · drag the handle to replay</span>
    {:else if nearestFlip}
      <StatusGlyph g="half" size={14} color="var(--ink-3)" />
      <span class="wl-mono quiet">under way</span>
      <span class="wl-mono arrow">→</span>
      <StatusGlyph g={STATUS[nearestFlip.status].glyph} size={14} color="var(--signal)" />
      <span class="wl-mono flipname">{nearestFlip.name} · {STATUS[nearestFlip.status].label.toUpperCase()}</span>
    {:else}
      <span class="wl-mono quiet">{visibleCount} of {db.projects.length} projects visible at this date</span>
    {/if}
  </div>

  <!-- pointer affordance only; keyboard semantics live on the slider handle -->
  <div
    class="track"
    role="presentation"
    bind:this={track}
    onpointerdown={onPointerDown}
    onpointermove={onPointerMove}
    onpointerup={onPointerUp}
    onpointercancel={onPointerUp}
    onlostpointercapture={onPointerUp}
  >
    <svg viewBox="0 0 100 46" preserveAspectRatio="none" aria-hidden="true">
      <polyline points={trace} fill="none" stroke="var(--signal)" stroke-width="0.7" opacity={dragging ? 0.9 : 0.7} />
    </svg>
    {#if nearFlip && !idle}
      <div class="flash" style="left:{pos}%"></div>
    {/if}
    <div
      class="handle"
      class:dragging
      class:flip={nearFlip && dragging}
      style="left:{pos}%"
      role="slider"
      tabindex="0"
      aria-label="Timeline — drag or use arrow keys to replay history"
      aria-valuemin={TIMELINE.from}
      aria-valuemax={Math.round(TIMELINE.to * 100) / 100}
      aria-valuenow={Math.round(ui.t * 100) / 100}
      aria-valuetext={fracLabel(ui.t)}
      onkeydown={onKey}
    >
      <div class="knob"></div>
    </div>
  </div>

  <GovBand height={compact ? 3 : 4} />
</div>

<style>
  .scrub {
    padding: 10px 16px 14px;
    background: var(--surface-2);
    border-top: 1px solid var(--line-2);
    user-select: none;
  }

  .scrub.compact {
    padding: 8px 14px 12px;
  }

  .row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
  }

  .readout {
    display: flex;
    align-items: center;
    gap: 6px;
    min-height: 16px;
    margin-bottom: 4px;
  }

  .quiet {
    font-size: 10px;
    color: var(--ink-3);
  }

  .arrow {
    font-size: 13px;
    color: var(--signal);
  }

  .flipname {
    font-size: 10px;
    color: var(--signal);
    font-weight: 700;
  }

  .flash {
    position: absolute;
    top: -4px;
    bottom: -4px;
    width: 34px;
    transform: translateX(-50%);
    background: radial-gradient(ellipse, rgba(212, 168, 83, 0.22), transparent 70%);
    pointer-events: none;
  }

  .track {
    position: relative;
    height: 38px;
    margin-bottom: 7px;
    cursor: ew-resize;
    touch-action: none;
  }

  .compact .track {
    height: 30px;
  }

  .track svg {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
  }

  .handle {
    position: absolute;
    top: -3px;
    bottom: -3px;
    width: 2px;
    background: var(--signal);
    transform: translateX(-1px);
  }

  .knob {
    position: absolute;
    top: -6px;
    left: -8px;
    width: 18px;
    height: 18px;
    background: var(--signal);
    border-radius: 50%;
    transition: box-shadow 0.15s ease;
  }

  .handle.dragging .knob {
    box-shadow: 0 0 0 5px rgba(212, 168, 83, 0.16);
  }

  .handle.flip {
    box-shadow: 0 0 14px 2px var(--signal);
  }

  @media (max-width: 560px) {
    .knob {
      /* one-handed thumb target */
      top: -8px;
      left: -10px;
      width: 22px;
      height: 22px;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .handle.flip {
      box-shadow: none;
    }

    .flash {
      display: none;
    }
  }
</style>
