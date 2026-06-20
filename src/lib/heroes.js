/* Per-sector "hero" reversals — one emblematic cancelled/reversed thing per
   sector, surfaced at the top of the Churn Explorer. Outcome-first, party shown
   as fact (never fault). The four project-backed heroes open the map's detail
   panel (`project`); the rest link to a primary/neutral source (`href`). Every
   figure is real and sourced. (Formerly the landing page's STORY_CARDS.) */

export const SECTOR_HEROES = {
  transport: {
    tag: 'the train',
    title: 'A train to the airport.',
    rows: [
      { k: 'Promised', t: '2017 — light rail, downtown to Auckland Airport' },
      { k: 'Stopped', t: 'January 2024', sub: 'started under Labour · stopped under National' },
      { k: 'Cost', t: '$228m on plans, consultants and land', strong: true, src: 'Treasury / MoT' },
    ],
    got: 'Nothing. Zero metres of track.',
    project: 'auckland-light-rail',
  },
  water: {
    tag: 'the water',
    title: 'Water you can drink.',
    rows: [
      { k: 'Why', t: '5,500 people poisoned — Havelock North, 2016' },
      { k: 'Built', t: '2020–22 — the water reform, end to end' },
      { k: 'Stopped', t: '2024 — repealed, restarted under a new name', sub: 'built under Labour · repealed under National' },
    ],
    got: 'The same pipes.',
    project: 'three-waters',
  },
  health: {
    tag: 'the hospital',
    title: 'A new Dunedin hospital.',
    rows: [
      { k: 'Promised', t: '2017 — in full' },
      { k: 'Rescoped', t: 'eight years of redrawing, both governments' },
      { k: 'Marched', t: '35,000 people, September 2024', strong: true },
    ],
    got: 'A smaller hospital. Still unbuilt.',
    project: 'dunedin-hospital',
  },
  economy: {
    tag: 'the retirement',
    title: 'A funded retirement.',
    rows: [
      { k: 'Paused', t: '2009–17 — Super Fund contributions halted', sub: 'under National' },
      { k: 'The hole', t: "$27.5b — by the fund's own estimate", strong: true, src: 'NZ Super Fund' },
    ],
    got: 'The bill, passed to people too young to vote.',
    project: 'super-fund-suspension',
  },
  environment: {
    tag: 'the planning law',
    title: 'A replacement for the RMA.',
    rows: [
      { k: 'Passed', t: 'Aug 2023 — Natural & Built Environment + Spatial Planning Acts', sub: 'under Labour' },
      { k: 'Repealed', t: 'Dec 2023 — gone in about four months', sub: 'under National', strong: true },
    ],
    got: 'The Resource Management Act 1991 — still in force.',
    href: 'https://www.beehive.govt.nz/release/nba-and-spa-successfully-repealed',
    hrefLabel: 'Beehive ↗',
  },
  justice: {
    tag: 'three strikes',
    title: 'Three-strikes sentencing.',
    rows: [
      { k: 'Enacted', t: '2010 — Sentencing and Parole Reform Act', sub: 'under National' },
      { k: 'Repealed', t: '2022', sub: 'under Labour' },
      { k: 'Reinstated', t: '2024 — back again', sub: 'under National', strong: true },
    ],
    got: 'The same regime it started as — a round trip.',
    href: 'https://www.justice.govt.nz/justice-sector-policy/key-initiatives/three-strikes-law/',
    hrefLabel: 'Justice.govt.nz ↗',
  },
  education: {
    tag: 'charter schools',
    title: 'Charter schools.',
    rows: [
      { k: 'Set up', t: '2014 — partnership schools open', sub: 'under National' },
      { k: 'Abolished', t: '2018', sub: 'under Labour' },
      { k: 'Reinstated', t: '2024 — $153m for up to 50 schools', sub: 'under National', strong: true, src: 'Treasury' },
    ],
    got: 'Back, a decade later.',
    href: 'https://en.wikipedia.org/wiki/Charter_schools_in_New_Zealand',
    hrefLabel: 'Wikipedia ↗',
  },
  energy: {
    tag: 'the gas fields',
    title: 'An offshore oil & gas exploration ban.',
    rows: [
      { k: 'Banned', t: '2018 — no new offshore exploration', sub: 'under Labour' },
      { k: 'Reversed', t: '2025 — ban lifted', sub: 'under National', strong: true },
    ],
    got: 'Back to square one, seven years on.',
    href: 'https://www.beehive.govt.nz/release/government-reverse-oil-and-gas-exploration-ban',
    hrefLabel: 'Beehive ↗',
  },
  tax: {
    tag: 'the property tax',
    title: 'A capital-gains brake on housing.',
    rows: [
      { k: 'Extended', t: '2021 — bright-line test stretched to 10 years', sub: 'under Labour' },
      { k: 'Cut', t: '1 Jul 2024 — back to 2 years', sub: 'under National', strong: true },
    ],
    got: 'Roughly where it started in 2015.',
    href: 'https://www.ird.govt.nz/property/buying-and-selling/when-you-need-to-pay/the-brightline-test',
    hrefLabel: 'IRD ↗',
  },
  other: {
    tag: 'public media',
    title: 'A merged public broadcaster.',
    rows: [
      { k: 'Built', t: '2022 — RNZ + TVNZ merger legislated', sub: 'under Labour' },
      { k: 'Scrapped', t: 'Feb 2023 — weeks before launch', sub: 'under Labour', strong: true },
      { k: 'Cost', t: '~$19m spent before it was canned', src: 'RNZ' },
    ],
    got: 'Two separate broadcasters — the status quo.',
    href: 'https://en.wikipedia.org/wiki/Aotearoa_New_Zealand_Public_Media',
    hrefLabel: 'Wikipedia ↗',
  },
};
