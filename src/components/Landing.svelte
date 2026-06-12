<script>
  /* The story-first front door (the "subtraction" redesign). Scroll once:
     five outcomes in plain language. Scroll twice: the machine chart. Then —
     and only then — the doors to the tool. Outcome first; dollars are evidence.

     Same Seismograph identity, a fraction of the surface: no intro banner, no
     filters, one number, three interactive doors. */
  import { ui } from '../lib/state.svelte.js';
  import { db, hudTotal } from '../lib/data.svelte.js';
  import { TIMELINE } from '../lib/state.svelte.js';
  import { fmtMoney } from '../lib/format.js';
  import { STORY_CARDS } from '../lib/landing.js';
  import WLMark from './WLMark.svelte';

  /* The one headline number: money actually spent on cancelled work, this
     government. Pulled live from the same HUD calc the map uses. */
  const headline = $derived(db.ready ? hudTotal(TIMELINE.to) : { total: 0 });

  /* Seismograph trace for the hero backdrop. */
  const SPIKES = [14, 30, 46, 62, 76, 88];
  function trace(amp = 13) {
    const pts = [];
    for (let i = 0; i <= 160; i++) {
      const x = (i / 160) * 100;
      let y = 20;
      for (let j = 0; j < SPIKES.length; j++) {
        const d = Math.abs(x - SPIKES[j]);
        if (d < 2.2) y += (j % 2 ? -1 : 1) * (2.2 - d) * (amp / 2.2);
      }
      pts.push(`${x.toFixed(2)},${y.toFixed(2)}`);
    }
    return pts.join(' ');
  }

  /* The per-term churn chart — real amendments+repeals per term since 2008,
     joined to the government bands. "It's not red or blue, it's the machine." */
  const terms = $derived.by(() => {
    if (!db.aggregates?.per_term) return [];
    const byId = Object.fromEntries(db.governments.map((g) => [g.id, g]));
    const rows = db.aggregates.per_term
      .map((t) => {
        const g = byId[t.govt];
        if (!g || g.start < '2008') return null;
        const sy = g.start.slice(2, 4);
        const ey = g.end ? g.end.slice(2, 4) : '';
        return { id: t.govt, party: g.party, total: t.amendments + t.repeals, label: `’${sy}–${ey || ''}`, ongoing: !g.end };
      })
      .filter(Boolean)
      .sort((a, b) => a.id.localeCompare(b.id) && 0); // keep input order; per_term is unordered, so sort by start below
    // sort chronologically by government start
    rows.sort((a, b) => byId[a.id].start.localeCompare(byId[b.id].start));
    return rows;
  });
  const termMax = $derived(Math.max(32000, ...terms.map((t) => t.total)));
  const termBand = $derived.by(() => {
    if (!terms.length) return [20000, 30000];
    const vals = terms.filter((t) => !t.ongoing).map((t) => t.total);
    const lo = Math.floor(Math.min(...vals) / 1000) * 1000;
    const hi = Math.ceil(Math.max(...vals) / 1000) * 1000;
    return [lo, hi];
  });

  function openProject(id) {
    ui.selected = id;
    ui.view = 'map';
  }
  function go(view) {
    ui.selectedAct = null;
    ui.view = view;
  }
</script>

<div class="landing">
  <!-- ============ HERO = the 5-second screenshot ============ -->
  <section class="hero">
    <svg class="seis" viewBox="0 0 100 40" preserveAspectRatio="none" aria-hidden="true">
      <polyline points={trace()} fill="none" stroke="var(--signal)" stroke-width="1" vector-effect="non-scaling-stroke" />
    </svg>

    <header class="hero-top">
      <span class="wl-logo">
        <WLMark size={20} />
        <span class="word">WHIP<span class="dot">·</span>LASH</span>
      </span>
    </header>

    <div class="hero-body">
      <div class="wl-label sig">// the public record of reversals</div>
      <h1 class="wl-disp headline">WHAT YOU<br />DIDN’T GET.</h1>
      <p class="lede">A train to the airport. New ferries. Drinkable water. A hospital.</p>
      <p class="sub">
        New Zealand keeps cancelling its own future — under both parties. The bill lands on people too young to vote.
      </p>
    </div>

    <div class="hero-number">
      <div>
        <div class="wl-disp big-num">{db.ready ? fmtMoney(headline.total).toUpperCase() : '…'}</div>
        <div class="wl-label">spent, then thrown away — this government alone</div>
        <div class="count-note wl-mono">
          only money actually spent ·
          <button class="link" onclick={() => go('method')}>how we count ↗</button>
        </div>
      </div>
      <span class="scroll-cue wl-mono" aria-hidden="true">↓</span>
    </div>
  </section>

  <!-- ============ five story cards ============ -->
  <section class="cards">
    <div class="wl-label">// five things, in plain language</div>
    {#each STORY_CARDS as c (c.project)}
      <button class="card" onclick={() => openProject(c.project)} aria-label="{c.title} — open the full story">
        <div class="wl-label sig">{c.kicker}</div>
        <div class="wl-disp card-title">{c.title}</div>
        <div class="rows">
          {#each c.rows as r}
            <div class="crow">
              <span class="wl-label rk">{r.k}</span>
              <span class="rt">
                <span class="wl-mono" class:strong={r.strong}>{r.t}</span>
                {#if r.src}<span class="wl-mono src">↗ {r.src}</span>{/if}
                {#if r.sub}<span class="rsub wl-mono">{r.sub}</span>{/if}
              </span>
            </div>
          {/each}
        </div>
        <div class="got">
          <span class="wl-label sig gk">You got</span>
          <span class="gt">{c.got}</span>
        </div>
      </button>
    {/each}
  </section>

  <!-- ============ the machine band ============ -->
  <section class="machine">
    <div class="wl-label sig">// every government does this</div>
    <div class="wl-disp machine-title">IT’S NOT RED OR BLUE.<br />IT’S THE MACHINE.</div>
    <p class="machine-sub">
      Every term since 2008 has rewritten the statute book
      {#if termBand[0]}between {termBand[0].toLocaleString()} and {termBand[1].toLocaleString()} times{/if}
      — amendments and repeals, whoever governs.
    </p>

    <div class="chart" role="img" aria-label="Amendments and repeals per parliamentary term since 2008 — every term lands in a similar band regardless of party">
      <div class="bars">
        {#each [termBand[1], termBand[0]] as b}
          {#if b}
            <div class="gridline" style="bottom:{(b / termMax) * 100}%">
              <span class="wl-label gl">{Math.round(b / 1000)}K</span>
            </div>
          {/if}
        {/each}
        {#each terms as t (t.id)}
          <div class="bar-col">
            <div class="bar" class:ongoing={t.ongoing} style="height:{(t.total / termMax) * 100}%">
              <div class="party {t.party}"></div>
            </div>
          </div>
        {/each}
      </div>
      <div class="bar-labels">
        {#each terms as t (t.id)}
          <span class="wl-label tl">{t.label}{t.ongoing ? '·' : ''}</span>
        {/each}
      </div>
    </div>
    <div class="machine-src wl-mono">source: Parliamentary Counsel Office · party shown as fact, not fault · · = term in progress</div>
  </section>

  <!-- ============ end cap: the only doors to the tool ============ -->
  <section class="endcap">
    <div class="wl-label">// go as deep as you want</div>
    <button class="door" onclick={() => go('map')}>
      <span class="dglyph wl-mono">↺</span>
      <span class="dbody">
        <span class="wl-mono dtitle">The map</span>
        <span class="wl-label dsub">{db.ready ? db.projects.length : 30} reversals · 2008 → today · drag the scrubber</span>
      </span>
      <span class="wl-mono dchev">▸</span>
    </button>
    <button class="door" onclick={() => go('churn')}>
      <span class="dglyph wl-mono">≣</span>
      <span class="dbody">
        <span class="wl-mono dtitle">The law, rewritten</span>
        <span class="wl-label dsub">three statutes’ stories · every act behind them</span>
      </span>
      <span class="wl-mono dchev">▸</span>
    </button>
    <p class="neutral wl-mono">
      Both parties’ reversals carried at equal weight. Every figure links to its source.
      <button class="link" onclick={() => go('method')}>How we count ↗</button>
    </p>
  </section>
</div>

<style>
  .landing {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
  }

  /* ---------------- hero ---------------- */
  .hero {
    position: relative;
    display: flex;
    flex-direction: column;
    min-height: min(620px, calc(100svh - 1px));
    border-bottom: 1px solid var(--line);
    overflow: hidden;
  }

  .seis {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 128px;
    width: 100%;
    height: 90px;
    display: block;
    opacity: 0.28;
    pointer-events: none;
  }

  .hero-top {
    display: flex;
    align-items: center;
    padding: 16px 20px 0;
    position: relative;
  }

  .word {
    font-family: var(--font-sans);
    font-weight: 900;
    font-size: 14px;
    letter-spacing: -0.03em;
    text-transform: uppercase;
    color: var(--ink);
  }
  .word .dot {
    color: var(--signal);
  }

  .hero-body {
    padding: 40px 20px 0;
    position: relative;
  }

  .headline {
    font-size: clamp(44px, 13vw, 96px);
    margin: 12px 0 0;
  }

  .lede {
    font-family: var(--font-sans);
    font-weight: 400;
    font-size: clamp(15.5px, 4.5vw, 22px);
    color: var(--ink);
    line-height: 1.5;
    margin: 18px 0 0;
    max-width: 580px;
  }

  .sub {
    font-family: var(--font-sans);
    font-weight: 300;
    font-size: clamp(13px, 3.6vw, 15.5px);
    color: var(--ink-2);
    line-height: 1.6;
    margin: 12px 0 0;
    max-width: 540px;
  }

  .hero-number {
    margin-top: auto;
    padding: 28px 20px 18px;
    position: relative;
    display: flex;
    align-items: flex-end;
    gap: 12px;
  }

  .big-num {
    font-size: clamp(40px, 11vw, 56px);
    color: var(--signal);
  }

  .count-note {
    font-size: 9px;
    color: var(--ink-3);
    margin-top: 4px;
  }

  .link {
    color: var(--signal);
    cursor: pointer;
    font: inherit;
  }
  .link:hover {
    text-decoration: underline;
  }

  .scroll-cue {
    margin-left: auto;
    font-size: 17px;
    color: var(--ink-3);
    animation: bob 1.8s ease-in-out infinite;
  }
  @keyframes bob {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(4px); }
  }

  /* ---------------- story cards ---------------- */
  .cards {
    display: flex;
    flex-direction: column;
    gap: 13px;
    padding: 26px 20px;
    max-width: 700px;
    margin: 0 auto;
    width: 100%;
  }

  .card {
    display: block;
    text-align: left;
    border: 1px solid var(--line-2);
    border-radius: 3px;
    background: var(--surface);
    padding: 16px 18px;
    cursor: pointer;
    transition: border-color 0.15s ease, transform 0.15s ease;
  }
  .card:hover {
    border-color: rgba(212, 168, 83, 0.5);
    transform: translateY(-2px);
  }

  .card-title {
    font-size: 22px;
    margin: 8px 0 12px;
  }

  .rows {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .crow {
    display: grid;
    grid-template-columns: 82px 1fr;
    gap: 10px;
    align-items: baseline;
  }
  .rk {
    font-size: 9px;
  }
  .rt .wl-mono {
    font-size: 11.5px;
    line-height: 1.45;
    color: var(--ink);
  }
  .rt .strong {
    font-weight: 700;
  }
  .src {
    font-size: 9px;
    color: var(--signal);
    margin-left: 7px;
    white-space: nowrap;
  }
  .rsub {
    display: block;
    font-size: 9px;
    color: var(--ink-3);
    margin-top: 2px;
  }

  .got {
    border-top: 1px solid var(--line);
    margin-top: 13px;
    padding-top: 11px;
    display: grid;
    grid-template-columns: 82px 1fr;
    gap: 10px;
    align-items: baseline;
  }
  .gk {
    font-size: 9px;
  }
  .gt {
    font-family: var(--font-sans);
    font-weight: 500;
    font-size: 14.5px;
    color: var(--ink);
    line-height: 1.4;
  }

  /* ---------------- machine band ---------------- */
  .machine {
    background: var(--surface-2);
    border-top: 1px solid var(--line-2);
    border-bottom: 1px solid var(--line-2);
    padding: 28px 20px 26px;
  }
  .machine-title {
    font-size: clamp(28px, 8vw, 44px);
    margin: 10px 0 0;
  }
  .machine-sub {
    font-family: var(--font-sans);
    font-weight: 300;
    font-size: clamp(12.5px, 3.4vw, 14.5px);
    color: var(--ink-2);
    line-height: 1.6;
    margin: 12px 0 0;
    max-width: 560px;
  }

  .chart {
    max-width: 580px;
    margin-top: 22px;
  }
  .bars {
    position: relative;
    height: 150px;
    display: flex;
    align-items: flex-end;
    gap: 8px;
  }
  .gridline {
    position: absolute;
    left: 0;
    right: 0;
    border-top: 1px dashed var(--line-2);
    pointer-events: none;
  }
  .gl {
    position: absolute;
    right: 0;
    top: -13px;
    font-size: 8px;
  }
  .bar-col {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    height: 100%;
  }
  .bar {
    background: rgba(127, 150, 170, 0.26);
    border-top: 2px solid var(--ink-2);
    position: relative;
    min-height: 2px;
  }
  .bar.ongoing {
    background: repeating-linear-gradient(
      -45deg,
      rgba(127, 150, 170, 0.26),
      rgba(127, 150, 170, 0.26) 4px,
      transparent 4px,
      transparent 7px
    );
  }
  .party {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 3px;
    opacity: 0.5;
  }
  .party.labour {
    background: var(--gov-lab);
  }
  .party.national {
    background: var(--gov-nat);
  }
  .bar-labels {
    display: flex;
    gap: 8px;
    margin-top: 5px;
  }
  .tl {
    flex: 1;
    text-align: center;
    font-size: 8.5px;
  }
  .machine-src {
    font-size: 9px;
    color: var(--ink-3);
    margin-top: 12px;
  }

  /* ---------------- end cap ---------------- */
  .endcap {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 26px 20px 40px;
    max-width: 680px;
    margin: 0 auto;
    width: 100%;
  }
  .door {
    display: flex;
    align-items: center;
    gap: 13px;
    border: 1px solid var(--line-2);
    border-radius: 3px;
    padding: 14px 16px;
    background: var(--surface);
    cursor: pointer;
    text-align: left;
    transition: border-color 0.15s ease;
  }
  .door:hover {
    border-color: rgba(212, 168, 83, 0.5);
  }
  .dglyph {
    font-size: 16px;
    color: var(--signal);
    flex: none;
  }
  .dbody {
    display: flex;
    flex-direction: column;
    gap: 3px;
  }
  .dtitle {
    font-size: 12.5px;
    font-weight: 700;
    color: var(--ink);
  }
  .dsub {
    font-size: 9px;
  }
  .dchev {
    margin-left: auto;
    color: var(--ink-3);
  }
  .neutral {
    font-size: 9.5px;
    color: var(--ink-3);
    line-height: 1.7;
    margin: 9px 0 0;
  }

  /* ---------------- desktop polish ---------------- */
  @media (min-width: 760px) {
    .hero-top {
      padding: 24px 64px 0;
    }
    .hero-body {
      padding: 58px 64px 0;
    }
    .hero-number {
      padding: 0 64px 28px;
    }
    .seis {
      height: 140px;
      bottom: 110px;
    }
    .cards,
    .endcap {
      padding-left: 64px;
      padding-right: 64px;
    }
    .machine {
      padding: 46px 64px 40px;
    }
  }
</style>
