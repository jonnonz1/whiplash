<script>
  /* The credibility of this project lives on this page. */
  import { ESSAYS, SERIES_NAME, SERIES_HOME } from '../lib/essays.js';
  import { db } from '../lib/data.svelte.js';
</script>

<div class="method">
  <div class="cols">
    <div class="left">
      <div class="wl-label sig">// How we count</div>
      <h1 class="wl-disp big">Only money<br />actually spent.</h1>
      <p class="lede">
        Whiplash counts dollars that left the public account on projects that were then cancelled, reversed or
        rescoped. Never forecasts, never opportunity cost, never political estimates. The credibility of this project
        lives on this page.
      </p>

      <div class="rules">
        <div class="rule">
          <span class="wl-data num">01</span>
          <div>
            <div class="wl-mono rh">Directly sunk costs count</div>
            <p>Cash spent on design, consultants, land, contracts and works before the decision to stop.</p>
          </div>
        </div>
        <div class="rule">
          <span class="wl-data num">02</span>
          <div>
            <div class="wl-mono rh">Cancellation &amp; exit costs count</div>
            <p>Penalties and settlements paid to walk away — e.g. iReX's $144m shipbuild contract exit.</p>
          </div>
        </div>
        <div class="rule">
          <span class="wl-data num">03</span>
          <div>
            <div class="wl-mono rh">Projected costs never count</div>
            <p>
              "It would have cost $X to finish" is excluded entirely. Those figures appear only as contested claims,
              never in a total.
            </p>
          </div>
        </div>
        <div class="rule">
          <span class="wl-data num">04</span>
          <div>
            <div class="wl-mono rh">Attribution is factual</div>
            <p>
              Each project shows the government that started it and the one that stopped it. Party colours are
              descriptive bands on timelines, never a verdict. Reversals by every government, red and blue, are on the
              record here.
            </p>
          </div>
        </div>
      </div>

      <div class="essays">
        <div class="wl-label sig" style="margin-bottom:8px">// Why this matters — the generational bill</div>
        <p class="lede" style="margin-top:0">
          The point of this record is bigger than any one cancelled project. The decisions that matter most —
          hospitals, water, retirement savings, public health — need 10-to-30-year horizons, and New Zealand keeps
          re-deciding them on a 3-year clock. The cost of that compounds onto people who can't vote yet.
        </p>
        <p class="lede" style="margin-top:8px">
          Healthcare shows it plainest. The new Dunedin Hospital was re-scoped for eight years while its price climbed
          from $1.2b toward $1.9b. A national Māori health agency was stood up and shut down inside 24 months. A
          world-first smoking law was repealed before a single clause took effect — modelling (van der Deen et al.)
          had projected ~8,150 preventable deaths and ~$1.3b of health-system savings over 20 years. Those last figures
          are modelled, so they never enter a total here; the churn that triggered them is on the public record.
        </p>
        <p class="lede" style="margin-top:8px">
          The cleanest generational specimen isn't a building at all. Contributions to the NZ Super Fund — the fund
          that pre-pays the pensions of people now at school — were suspended from 2009 to 2017. The Guardians' own
          estimate of the cost: roughly <strong>$25.5 billion</strong> in missed contributions, forgone returns and
          forgone tax. One reversal, compounding for a generation.
        </p>
        <p class="lede" style="margin-top:8px">
          And the backdrop: from 2010 to 2019 New Zealand was the OECD's biggest infrastructure investor as a share of
          GDP, while ranking near the bottom 10% of high-income countries for what each dollar delivers (Te Waihanga,
          2022), against a $100–210b, 30-year infrastructure deficit. The problem isn't how much gets spent. It's that
          nothing is allowed to stay decided.
        </p>
      </div>

      <div class="essays">
        <div class="wl-label sig" style="margin-bottom:8px">// The essays</div>
        <p class="lede" style="margin-top:0">
          This tracker publishes alongside <strong>{SERIES_NAME}</strong>, a three-part series on
          <a href={SERIES_HOME}>jonno.nz</a> — what the reversals cost, why New Zealand swings harder than anyone, and
          what would fix it.
        </p>
        <div class="essaylist">
          {#each ESSAYS as e (e.part)}
            <div class="essayrow">
              <span class="wl-data epart">0{e.part}</span>
              <div>
                {#if e.url}
                  <a class="wl-mono etitle" href={e.url}>{e.title} ↗</a>
                {:else}
                  <span class="wl-mono etitle soon">{e.title} <span class="chip-claimed">coming soon</span></span>
                {/if}
                <div class="eblurb">{e.blurb}</div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    </div>

    <div class="right">
      <div class="wl-label" style="margin-bottom:8px">// Firm vs contested</div>
      <div class="spec">
        <div class="specbox solid">
          <span class="fig-firm" style="font-size:18px">$507.3m <a class="src" style="font-size:9px" href="https://www.rnz.co.nz/news/political/560273" target="_blank" rel="noopener">↗ KiwiRail / RNZ</a></span>
          <div class="wl-mono speccap">FIRM — bold, monospaced, one click to its source. Enters totals.</div>
        </div>
        <div class="specbox dashed">
          <span class="fig-contested" style="font-size:14px">[ ~$1.16b ]</span>
          <span class="chip-claimed">⚠ claimed</span>
          <div class="wl-mono speccap">CONTESTED — hatched, bracketed, quarantined, attributed to whoever claimed it. Never enters a total.</div>
        </div>
      </div>

      <div class="wl-label" style="margin:22px 0 8px">// Worked example — iReX ferries</div>
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

      <div class="wl-label" style="margin:22px 0 8px">// Where the data comes from</div>
      <ul class="srcs">
        <li>
          <span class="wl-mono key">Projects:</span> hand-curated from the public record — Treasury and agency
          disclosures, OIA releases, and reporting by RNZ, NZ Herald, 1News, The Post, Newsroom, BusinessDesk and The
          Spinoff. Every figure links to its source.
        </li>
        <li>
          <span class="wl-mono key">Legislation:</span> the Parliamentary Counsel Office's XML of the entire statute
          book. Hand-curated highlights today; a full amendment/repeal graph of ~26,000 documents is in the pipeline.
        </li>
        <li>
          <span class="wl-mono key">Urgency:</span> the community tracker at
          <a href="https://nzpt.cjs.nz" target="_blank" rel="noopener">nzpt.cjs.nz</a> and analysis by David Farrar and
          Newsroom.
        </li>
      </ul>

      <div class="licence">
        <div class="wl-label" style="margin-bottom:6px">// Data &amp; licence</div>
        <p class="wl-mono fine">
          Legislation data: Parliamentary Counsel Office — free of copyright under s 27 Copyright Act 1994; reuse
          statement CC BY 4.0 with attribution. Basemap © OpenStreetMap contributors, © CARTO. Whiplash is an
          independent, non-commercial project by
          <a href="https://jonno.nz" target="_blank" rel="noopener">John Gregoriadis</a> (sibling of
          <a href="https://crimemap.jonno.nz" target="_blank" rel="noopener">crimemap.jonno.nz</a>). It is not
          affiliated with any government agency, party or campaign. Data as at {db.generated}.
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
    max-width: 1060px;
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
    margin-top: 14px;
  }

  .lede strong {
    font-weight: 500;
    color: var(--ink);
  }

  .rules {
    margin-top: 20px;
    border-top: 1px solid var(--line);
    padding-top: 18px;
  }

  .rule {
    display: flex;
    gap: 12px;
    padding-bottom: 14px;
  }

  .num {
    font-size: 13px;
    color: var(--signal);
    width: 22px;
    flex: none;
  }

  .rh {
    font-size: 12px;
    font-weight: 700;
    color: var(--ink);
    letter-spacing: 0.01em;
  }

  .rule p {
    font-weight: 300;
    font-size: 12.5px;
    color: var(--ink-2);
    line-height: 1.55;
    margin: 3px 0 0;
  }

  .essays {
    margin-top: 26px;
    border-top: 1px solid var(--line);
    padding-top: 18px;
  }

  .essaylist {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 12px;
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

  .eblurb {
    font-weight: 300;
    font-size: 11px;
    color: var(--ink-3);
    margin-top: 2px;
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

  .srcs {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .srcs li {
    font-weight: 300;
    font-size: 11.5px;
    color: var(--ink-2);
    line-height: 1.6;
    margin-bottom: 10px;
  }

  .key {
    font-size: 9.5px;
    color: var(--signal);
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }

  .licence {
    margin-top: 20px;
    border-top: 1px solid var(--line);
    padding-top: 12px;
  }

  .fine {
    font-size: 9.5px;
    color: var(--ink-2);
    line-height: 1.7;
    margin: 0;
  }

  @media (max-width: 760px) {
    .cols {
      grid-template-columns: 1fr;
      padding: 22px 18px 36px;
      gap: 26px;
    }

    .big {
      font-size: 28px;
    }
  }
</style>
