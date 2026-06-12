<script>
  /* The credibility of this project lives on this page — kept short enough
     that people actually read it. */
  import { ESSAYS, SERIES_NAME, SERIES_HOME } from '../lib/essays.js';
  import { db } from '../lib/data.svelte.js';
</script>

<div class="method">
  <div class="cols">
    <div class="left">
      <div class="wl-label sig">// How we count</div>
      <h1 class="wl-disp big">Only money<br />actually spent.</h1>
      <p class="lede">
        Whiplash counts dollars that left the public account on things that were then cancelled or reversed. Never
        forecasts, never opportunity costs, never political estimates.
      </p>

      <div class="rules">
        <div class="rule">
          <span class="wl-data num">01</span>
          <p><span class="rh">Sunk costs count.</span> Design, consultants, land, contracts, works.</p>
        </div>
        <div class="rule">
          <span class="wl-data num">02</span>
          <p><span class="rh">Exit costs count.</span> Penalties paid to walk away — like iReX's $144m.</p>
        </div>
        <div class="rule">
          <span class="wl-data num">03</span>
          <p><span class="rh">Projections never count.</span> "It would have cost $X" appears only as a labelled claim.</p>
        </div>
        <div class="rule">
          <span class="wl-data num">04</span>
          <p><span class="rh">Attribution is factual.</span> Who started it, who stopped it. Party colours are timeline bands, never verdicts.</p>
        </div>
      </div>

      <div class="block">
        <div class="wl-label sig">// What the churn costs</div>
        <p class="lede tight">
          Decisions that need 30-year horizons — hospitals, water, retirement — keep being re-decided on a 3-year
          clock. The bill compounds onto people who can't vote yet.
        </p>
        <div class="impacts">
          <div class="impact">
            <span class="wl-disp ival">$25.5b</span>
            <span class="itext">the Super Fund's own estimate of what pausing contributions for eight years cost the next generation</span>
          </div>
          <div class="impact">
            <span class="wl-disp ival">8 yrs</span>
            <span class="itext">of rescoping Dunedin Hospital while its price climbed from $1.2b to $1.9b</span>
          </div>
          <div class="impact">
            <span class="wl-disp ival">Bottom 10%</span>
            <span class="itext">NZ's rank among rich countries for what each infrastructure dollar delivers — while being the OECD's biggest investor, 2010–19 (Te Waihanga)</span>
          </div>
        </div>
      </div>

      <div class="block">
        <div class="wl-label sig">// The essays</div>
        <div class="essaylist">
          {#each ESSAYS as e (e.part)}
            <div class="essayrow">
              <span class="wl-data epart">0{e.part}</span>
              {#if e.url}
                <a class="wl-mono etitle" href={e.url}>{e.title} ↗</a>
              {:else}
                <span class="wl-mono etitle soon">{e.title} <span class="chip-claimed">coming soon</span></span>
              {/if}
            </div>
          {/each}
        </div>
        <p class="fine" style="margin-top:8px">
          {SERIES_NAME}, on <a href={SERIES_HOME}>jonno.nz</a>: what the reversals cost, why New Zealand swings harder
          than anyone, and what would fix it.
        </p>
      </div>
    </div>

    <div class="right">
      <div class="wl-label" style="margin-bottom:8px">// The three kinds of money</div>
      <div class="spec">
        <div class="specbox solid">
          <span class="fig-firm" style="font-size:18px">$507.3m <a class="src" style="font-size:9px" href="https://www.rnz.co.nz/news/political/560273" target="_blank" rel="noopener">↗ KiwiRail / RNZ</a></span>
          <div class="wl-mono speccap">FIRM — sourced, one click to the receipt. The only money that enters totals.</div>
        </div>
        <div class="specbox dashed">
          <span class="fig-contested" style="font-size:14px">[ ~$1.16b ]</span>
          <span class="chip-claimed">⚠ claimed</span>
          <div class="wl-mono speccap">CLAIMED — projections and political estimates. Quarantined, attributed, never summed.</div>
        </div>
        <div class="specbox solid">
          <span class="fig-firm" style="font-size:16px;color:var(--st-reversed)">$1.86b</span>
          <div class="wl-mono speccap">THE DO-OVER — real, cited money spent redoing or replacing (new ferries, re-merged polytechs). Shown on its own line, never added to the headline.</div>
        </div>
      </div>

      <div class="wl-label" style="margin:20px 0 8px">// Worked example — iReX ferries</div>
      <div class="wl-grid eg">
        <div class="wl-cell">
          <div class="wl-label">Sunk</div>
          <div class="wl-data" style="font-size:15px;margin-top:3px">$507.3m</div>
        </div>
        <div class="wl-cell">
          <div class="wl-label">Contract exit</div>
          <div class="wl-data" style="font-size:15px;margin-top:3px">$144.0m</div>
        </div>
        <div class="wl-cell">
          <div class="wl-label">Counted total</div>
          <div class="wl-data" style="font-size:15px;margin-top:3px;color:var(--signal)">$651.3m</div>
        </div>
        <div class="wl-cell">
          <div class="wl-label">"Total incl. maintenance"</div>
          <div class="fig-contested" style="font-size:12px;margin-top:4px">[ excluded ]</div>
        </div>
      </div>

      <div class="block">
        <div class="wl-label" style="margin-bottom:6px">// Sources &amp; licence</div>
        <p class="fine">
          Projects are hand-curated from the public record — Treasury and agency disclosures, OIA releases, reporting
          by RNZ, NZ Herald, 1News, Newsroom and The Spinoff — and every figure links to its source. Legislation data
          is the Parliamentary Counsel Office's XML of the entire statute book, parsed into 241,456 amendment events;
          urgency stats from <a href="https://nzpt.cjs.nz" target="_blank" rel="noopener">nzpt.cjs.nz</a>.
        </p>
        <p class="fine">
          Legislation is free of copyright (s 27 Copyright Act 1994; CC BY 4.0 reuse statement). Basemap ©
          OpenStreetMap contributors, © CARTO. Independent, non-commercial project by
          <a href="https://jonno.nz" target="_blank" rel="noopener">John Gregoriadis</a> — no party, no funder. Data as
          at {db.generated}. Pipeline and data:
          <a href="https://github.com/jonnonz1/whiplash" target="_blank" rel="noopener">github.com/jonnonz1/whiplash</a>.
        </p>
      </div>
    </div>
  </div>
</div>

<style>
  .method {
    flex: 1;
    overflow-y: auto;
    min-height: 0;
  }

  .cols {
    display: grid;
    grid-template-columns: 1.15fr 1fr;
    gap: 34px;
    padding: 26px 40px 40px;
    max-width: 1020px;
    margin: 0 auto;
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

  .lede.tight {
    font-size: 12.5px;
    margin-top: 8px;
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

  .impacts {
    margin-top: 12px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .impact {
    display: flex;
    gap: 14px;
    align-items: baseline;
  }

  .ival {
    font-size: 20px;
    color: var(--signal);
    min-width: 110px;
    flex: none;
  }

  .itext {
    font-weight: 300;
    font-size: 11.5px;
    color: var(--ink-2);
    line-height: 1.5;
  }

  .essaylist {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 10px;
  }

  .essayrow {
    display: flex;
    gap: 12px;
    align-items: baseline;
  }

  .epart {
    font-size: 12px;
    color: var(--signal);
    flex: none;
  }

  .etitle {
    font-size: 12px;
    font-weight: 700;
    color: var(--ink);
    text-decoration: none;
  }

  a.etitle:hover {
    color: var(--signal);
  }

  .etitle.soon {
    color: var(--ink-2);
  }

  .spec {
    display: flex;
    flex-direction: column;
    gap: 9px;
  }

  .specbox {
    border: 1px solid var(--line-2);
    border-radius: 3px;
    padding: 11px 13px;
  }

  .specbox.dashed {
    border-style: dashed;
  }

  .speccap {
    font-size: 9.5px;
    color: var(--ink-3);
    margin-top: 7px;
    line-height: 1.5;
  }

  .eg {
    grid-template-columns: 1fr 1fr;
  }

  .fine {
    font-family: var(--font-mono);
    font-size: 9.5px;
    color: var(--ink-2);
    line-height: 1.7;
    margin: 0 0 8px;
  }

  @media (max-width: 760px) {
    .cols {
      grid-template-columns: 1fr;
      padding: 22px 18px 36px;
      gap: 24px;
    }

    .big {
      font-size: 28px;
    }

    .ival {
      min-width: 90px;
      font-size: 17px;
    }
  }
</style>
