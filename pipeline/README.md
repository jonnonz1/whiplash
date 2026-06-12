# Pipeline (placeholder)

The legislation pipeline lives here once built:

```
mirror (XML) ──► parse history-notes ──► amendment graph (SQLite)
                                              │
governments.json (hand-keyed) ────────────────┤ stamp govt-in-power per event
sector classifier (agency+LLM+overrides) ─────┤
                                              ▼
                                   churn-acts.json / churn-aggregates.json
```

Full design: `specs/whiplash/03-data-pipeline.md` in the jonno.nz repo.
Key facts:

- The bulk XML mirror script is at `specs/whiplash/scripts/mirror-legislation.py`
  (jonno.nz repo). Mirror output goes to `../data-raw/legislation/` (gitignored,
  machine-local, ~4–6GB).
- Amendment history is element-encoded in `<history-note>` blocks — NOT the
  XML attributes an early research dossier claimed (verified 2026-06-10).
- Acceptance benchmark before publishing any number: the graph must reproduce
  the hand-curated facts in `public/data/churn-acts.json` (RMA/NBA/SPA, Water
  Services, bright-line, Smokefree, FPA, Three Strikes).
