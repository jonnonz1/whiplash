<script>
  /* The corrections log. Empty is fine — its existence is the point.
     A public record of being wrong is the cheapest proof the data isn't cooked. */
  const CONTACT = 'jonno.nz@gmail.com';

  const LOG = [
    /* { date: '2026-07-08', where: 'iReX detail panel', was: '…', now: '…', finder: 'Jane Doe, RNZ' } */
  ];
</script>

<div class="corrections">
  <div class="inner">
    <div class="wl-label sig">// The corrections log</div>
    <h1 class="wl-disp big">
      {#if LOG.length === 0}
        Nothing to<br />correct. Yet.
      {:else}
        {LOG.length} correction{LOG.length === 1 ? '' : 's'},<br />on the record.
      {/if}
    </h1>
    <p class="lede">
      Every figure on this tracker links to its source, and some of them will still turn out to be wrong. When one
      does, the fix is handled here, in public. That's the deal that makes the neutrality claim worth anything.
    </p>

    <div class="rules">
      <div class="rule">
        <span class="wl-data num">01</span>
        <p><span class="rh">Acknowledged fast, in public.</span> A reported error is confirmed or disputed on this page, not in a private inbox.</p>
      </div>
      <div class="rule">
        <span class="wl-data num">02</span>
        <p><span class="rh">Every fix leaves a trace.</span> Each correction gets a log entry: what was wrong, what it says now, when it changed. Data fixes also land in the <a href="https://github.com/jonnonz1/whiplash" target="_blank" rel="noopener">public git history</a>.</p>
      </div>
      <div class="rule">
        <span class="wl-data num">03</span>
        <p><span class="rh">Finders get thanked.</span> By name, right here — unless you'd rather not.</p>
      </div>
    </div>

    <div class="block">
      <div class="wl-label sig">// The log</div>
      {#if LOG.length === 0}
        <p class="wl-mono empty">0 entries since launch, 7 July 2026.</p>
      {:else}
        <div class="entries">
          {#each LOG as e (e.date + e.where)}
            <div class="entry">
              <span class="wl-data edate">{e.date}</span>
              <p><span class="rh">{e.where}.</span> Was: {e.was} Now: {e.now}{#if e.finder}&nbsp;<span class="thanks">Thanks: {e.finder}.</span>{/if}</p>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <div class="block">
      <div class="wl-label sig">// Spotted something?</div>
      <a class="wl-mono mail" href="mailto:{CONTACT}?subject=Whiplash%20correction">{CONTACT}</a>
      <p class="fine">
        Check the linked source first — if the receipt doesn't back the number, say which one and why. Journalists:
        same address for anything else, including data requests.
      </p>
    </div>
  </div>
</div>

<style>
  .corrections {
    flex: 1;
    overflow-y: auto;
    min-height: 0;
  }

  .inner {
    max-width: 620px;
    margin: 0 auto;
    padding: 26px 40px 60px;
  }

  .big {
    font-size: 36px;
    margin: 10px 0 0;
  }

  .lede {
    font-weight: 300;
    font-size: 13.5px;
    color: var(--ink-2);
    line-height: 1.6;
    margin: 14px 0 0;
  }

  .rules {
    margin-top: 18px;
    border-top: 1px solid var(--line);
    padding-top: 14px;
  }

  .rule {
    display: flex;
    gap: 12px;
    padding-bottom: 10px;
  }

  .num {
    font-size: 13px;
    color: var(--signal);
    width: 22px;
    flex: none;
  }

  .rule p {
    font-weight: 300;
    font-size: 12.5px;
    color: var(--ink-2);
    line-height: 1.5;
    margin: 0;
  }

  .rh {
    font-family: var(--font-mono);
    font-weight: 700;
    font-size: 11.5px;
    color: var(--ink);
  }

  .block {
    margin-top: 22px;
    border-top: 1px solid var(--line);
    padding-top: 14px;
  }

  .empty {
    font-size: 12px;
    color: var(--ink-3);
    margin: 10px 0 0;
  }

  .entries {
    margin-top: 10px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .entry {
    display: flex;
    gap: 12px;
  }

  .edate {
    font-size: 11px;
    color: var(--signal);
    flex: none;
  }

  .entry p {
    font-weight: 300;
    font-size: 12.5px;
    color: var(--ink-2);
    line-height: 1.5;
    margin: 0;
  }

  .thanks {
    color: var(--ink-3);
  }

  .mail {
    display: inline-block;
    font-size: 17px;
    font-weight: 700;
    color: var(--signal);
    margin-top: 10px;
    word-break: break-all;
  }

  .fine {
    font-family: var(--font-mono);
    font-size: 9.5px;
    color: var(--ink-2);
    line-height: 1.7;
    margin: 10px 0 0;
  }

  @media (max-width: 760px) {
    .inner {
      padding: 22px 18px 48px;
    }

    .big {
      font-size: 28px;
    }
  }
</style>
