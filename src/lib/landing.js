/* Plain-language reversal stories — "what you didn't get", per project.

   Outcome-first: every figure is real and sourced in projects.json. Surfaced
   as per-sector examples in the Churn Explorer (ChurnExplorer.svelte); the
   `project` id ties each story to the map's detail panel — keep these in sync
   with public/data/projects.json. (Formerly the landing front door.) */

export const STORY_CARDS = [
  {
    project: 'auckland-light-rail',
    kicker: '// 01 · the train',
    title: 'A train to the airport.',
    rows: [
      { k: 'Promised', t: '2017 — light rail, downtown to Auckland Airport' },
      { k: 'Stopped', t: 'January 2024', sub: 'started under Labour · stopped under National' },
      { k: 'Cost', t: '$228m on plans, consultants and land', strong: true, src: 'Treasury / MoT' },
    ],
    got: 'Nothing. Zero metres of track.',
  },
  {
    project: 'irex-ferries',
    kicker: '// 02 · the ferries',
    title: 'New Cook Strait ferries.',
    rows: [
      { k: 'Promised', t: '2021 — two rail-enabled ships, ordered' },
      { k: 'Stopped', t: 'December 2023', sub: 'started under Labour · stopped under National' },
      { k: 'Cost', t: '$144m paid just to walk away', strong: true, src: 'KiwiRail' },
    ],
    got: 'Different ferries — ordered anyway, due 2029.',
  },
  {
    project: 'three-waters',
    kicker: '// 03 · the water',
    title: 'Water you can drink.',
    rows: [
      { k: 'Why', t: '5,500 people poisoned — Havelock North, 2016' },
      { k: 'Built', t: '2020–22 — the water reform, end to end' },
      { k: 'Stopped', t: '2024 — repealed, restarted under a new name', sub: 'built under Labour · repealed under National' },
    ],
    got: 'The same pipes.',
  },
  {
    project: 'dunedin-hospital',
    kicker: '// 04 · the hospital',
    title: 'A new Dunedin hospital.',
    rows: [
      { k: 'Promised', t: '2017 — in full' },
      { k: 'Rescoped', t: 'eight years of redrawing, both governments' },
      { k: 'Marched', t: '35,000 people, September 2024', strong: true },
    ],
    got: 'A smaller hospital. Still unbuilt.',
  },
  {
    project: 'super-fund-suspension',
    kicker: '// 05 · the retirement',
    title: 'A funded retirement.',
    rows: [
      { k: 'Paused', t: '2009–17 — Super Fund contributions halted' },
      { k: 'The hole', t: "$25.5b — by the fund's own estimate", strong: true, src: 'NZ Super Fund' },
    ],
    got: 'The bill, passed to people too young to vote.',
  },
];
