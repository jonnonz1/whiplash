<script>
  /* The running total. Firm figures only — the counting rules are one
     tap away, always. */
  import { ui } from '../lib/state.svelte.js';
  import { hudTotal } from '../lib/data.svelte.js';
  import { fmtMoney } from '../lib/format.js';

  let open = $state(false);

  const hud = $derived(hudTotal(ui.t));

  function onWindowKey(e) {
    if (e.key === 'Escape') open = false;
  }
</script>

<svelte:window onkeydown={onWindowKey} />

<div class="hud">
  <div class="wl-label">// Directly sunk &amp; cancellation costs</div>
  <div class="wl-label gov-line">
    {hud.govt ? hud.govt.label : 'this government'}
    <button
      class="info"
      aria-expanded={open}
      aria-controls={open ? 'counting-pop' : undefined}
      aria-label="How this number is counted"
      onclick={() => (open = !open)}>ⓘ</button
    >
  </div>
  <div class="wl-disp total">{fmtMoney(hud.total)}</div>
  <div class="wl-mono fine">
    money actually spent · never projected costs{hud.count ? ` · ${hud.count} reversal${hud.count === 1 ? '' : 's'} counted` : ''}
  </div>
  {#if hud.consequential}
    <div class="wl-mono redo">
      + {fmtMoney(hud.consequential)} spent redoing &amp; replacing — tracked separately, never added to the number above
    </div>
  {/if}

  {#if open}
    <div class="pop" id="counting-pop" role="note">
      <div class="wl-label sig" style="margin-bottom:6px">// Counting rules</div>
      <p>
        This total adds up only <strong>firm, individually-sourced figures</strong> for money that left the public
        account — sunk costs and contract-exit penalties on projects stopped by the government in power at this point
        on the timeline.
      </p>
      <p>
        Projections ("it would have cost $X"), political estimates and modelled savings are
        <strong>never counted</strong>. They appear on project cards as quarantined, clearly-labelled claims.
      </p>
      <p>
        The "redoing &amp; replacing" line tracks real, cited money spent <strong>because</strong> of a reversal but
        which bought something — replacement ferries, re-established polytechnics. It is shown separately and never
        added to the headline. For scale: the headline total is more than half the cost of the new Dunedin Hospital
        ($1.9b).
      </p>
      <button class="wl-mono more" onclick={() => { ui.view = 'method'; open = false; }}>↗ Full methodology</button>
    </div>
  {/if}
</div>

<style>
  .hud {
    position: absolute;
    top: 14px;
    left: 14px;
    width: 232px;
    background: rgba(12, 21, 32, 0.82);
    border: 1px solid var(--line-2);
    border-radius: 3px;
    padding: 12px 14px;
    backdrop-filter: blur(2px);
    z-index: 5;
  }

  .gov-line {
    margin-top: 1px;
    display: flex;
    align-items: center;
    gap: 5px;
  }

  .info {
    color: var(--ink-3);
    font-size: 11px;
    line-height: 1;
    padding: 7px;
    margin: -7px;
    min-width: 24px;
    min-height: 24px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .info:hover {
    color: var(--signal);
  }

  .total {
    font-size: 38px;
    color: var(--signal);
    margin-top: 6px;
  }

  .fine {
    font-size: 9px;
    color: var(--ink-3);
    margin-top: 4px;
    line-height: 1.5;
  }

  .redo {
    font-size: 9px;
    color: var(--st-reversed);
    margin-top: 6px;
    line-height: 1.5;
    border-top: 1px dotted var(--line);
    padding-top: 5px;
  }

  .pop {
    position: absolute;
    top: calc(100% + 6px);
    left: 0;
    width: 264px;
    background: var(--surface);
    border: 1px solid var(--line-2);
    border-radius: 3px;
    padding: 12px 14px;
    z-index: 6;
  }

  .pop p {
    font-size: 11.5px;
    font-weight: 300;
    line-height: 1.55;
    color: var(--ink-2);
    margin: 0 0 8px;
  }

  .pop strong {
    font-weight: 500;
    color: var(--ink);
  }

  .more {
    font-size: 10px;
    color: var(--signal);
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  @media (max-width: 560px) {
    .hud {
      left: 12px;
      right: 12px;
      width: auto;
      padding: 9px 12px;
    }

    .total {
      font-size: 30px;
      margin-top: 3px;
    }
  }
</style>
