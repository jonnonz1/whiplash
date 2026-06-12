# Whiplash — whiplash.jonno.nz

New Zealand's policy whiplash, on the record. An interactive, open-data record
of reversed projects and churned legislation: the project graveyard map, the
statute-book churn timeline, and a running total that counts **only money
actually spent**.

Sibling of [crimemap.jonno.nz](https://crimemap.jonno.nz). Publishes alongside
the three-part **Policy Whiplash** essay series on [jonno.nz](https://jonno.nz).

## Stack

Vite + Svelte 5 + MapLibre GL. Static build, no backend — all data is
precomputed JSON in `public/data/`.

```sh
npm install
npm run dev        # local dev server
npm run build      # static build to dist/
```

## Data contract (`public/data/`)

Specced in the jonno.nz repo at `specs/whiplash/02-app-spec.md`.

| File                    | What                                                                                                                                      |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `governments.json`      | Hand-keyed government terms (the spine everything joins to)                                                                               |
| `projects.json`         | Hand-curated reversals with the firm/contested split. Extends the spec contract with a `firm[]` breakdown that the detail panel renders  |
| `churn-acts.json`       | Hand-curated act lanes (documented enactment/repeal facts only) — also the pipeline's acceptance benchmark                                |
| `churn-aggregates.json` | Aggregate stat cards; `pending` cards wait for the pipeline and never show invented numbers                                               |

**Counting rules (non-negotiable):** `sunk_nzd`/`firm[]` hold only
individually-cited, directly sunk or cancellation/exit costs. Projections and
political estimates live in `contested[]` and are never summed. The
methodology page in the app is the canonical statement of these rules.

## Pipeline

`pipeline/` holds the legislation mirror → `<history-note>` parser →
amendment graph (see `specs/whiplash/03-data-pipeline.md` in the jonno.nz
repo). `data-raw/` (multi-GB XML mirror) is machine-local and gitignored.

**Treat `data-raw/legislation/` as an archive, not a cache.** It is mirrored
from classic.legislation.govt.nz, which faces decommission with no announced
date — once that site goes, a full re-mirror may be impossible. Keep it,
back it up outside git, and reuse it freely (legislation is free of copyright,
s 27 Copyright Act 1994). The SQLite graph (`pipeline/graph.sqlite`) is
regenerable from the mirror at any time.

## TODO before launch

- [ ] Consequential-cost attribution nuance: zombie revivals (e.g. charter
      schools' $153m reinstatement) currently bucket under the government that
      *ended* the project, not the later one that paid for the do-over —
      correct for same-government reversals, imprecise for multi-government
      zombies. Add a `spent_by` field if more zombie cases accumulate.

- [ ] Verify the pending figures flagged in `projects.json` (Lake Onslow spend)
- [ ] og.png — render the OG card (1200×630, seismograph trace + the two big
      numbers) and drop it in `public/`
- [ ] Fill essay URLs in `src/lib/essays.js` as each part publishes
- [ ] Pipeline integration: replace hand-curated churn JSON with generated
      output once the graph reproduces the known-facts benchmark
- [ ] DNS + deploy to whiplash.jonno.nz

## Licence & attribution

Legislation data: Parliamentary Counsel Office — free of copyright under s 27
Copyright Act 1994; reuse statement CC BY 4.0. Basemap © OpenStreetMap
contributors, © CARTO. Project cost figures are cited per-source in the data
files and the UI. Independent, non-commercial project by John Gregoriadis —
not affiliated with any government agency, party or campaign.
