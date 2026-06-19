#!/usr/bin/env python3
"""Export a per-act change-history digest for the Top-change view.

For every act/regulation shown in the Top-10 view (the `top_acts_by_sector`
set in churn-explorer.json, minus the uncategorised bucket), pull its full
amendment history out of the graph and distil a structured digest:

  - totals (churn events, all events), date span
  - operation breakdown (amended / inserted / repealed / …)
  - busiest year
  - the biggest amending Acts (who drove the change)
  - a recent-events timeline (the last N provision-level changes)

This is the deterministic half. The prose `summary` is left null here and
filled by summarise_acts.py (an LLM pass over this digest) — see that script.

Usage:
  python3 pipeline/export_act_history.py pipeline/graph.sqlite public/data
"""

import argparse
import json
import sqlite3
import sys
from collections import Counter
from datetime import date
from pathlib import Path

CHURN_OPS = ("amended", "inserted", "substituted", "replaced")
DEAD_OPS = ("repealed", "revoked")
TIMELINE_N = 24       # most-recent events kept for the inline timeline
TOP_AMENDERS_N = 6    # biggest sources of change


def leg_no(number):
    s = str(number or "").strip()
    return s.zfill(4) if s.isdigit() else s


def target_ids(data_dir):
    """The acts the Top-10 view actually shows: every id in top_acts_by_sector,
    excluding the uncategorised 'other' bucket. Order preserved, de-duped."""
    exp = json.loads((Path(data_dir) / "churn-explorer.json").read_text())
    seen, ids = set(), []
    for sector, acts in exp.get("top_acts_by_sector", {}).items():
        if sector == "other":
            continue
        for a in acts:
            if a["id"] not in seen:
                seen.add(a["id"])
                ids.append(a["id"])
    return ids


def digest(con, work_id):
    meta = con.execute(
        "SELECT id, title, type, year, number, status FROM works WHERE id = ?",
        (work_id,),
    ).fetchone()
    if not meta:
        return None
    wid, title, wtype, year, number, status = meta

    rows = con.execute(
        """SELECT date, op, by_title, by_work_id, provision FROM events
           WHERE work_id = ? AND op != 'editorial' AND date IS NOT NULL
           ORDER BY date""",
        (work_id,),
    ).fetchall()
    if not rows:
        return None

    ops = Counter()
    by_year = Counter()
    amenders = Counter()          # by_title -> churn-op count
    amender_id = {}               # by_title -> by_work_id (for linking)
    churn = repeals = 0
    for d, op, by_title, by_wid, _prov in rows:
        ops[op] += 1
        by_year[d[:4]] += 1
        if op in CHURN_OPS:
            churn += 1
        elif op in DEAD_OPS:
            repeals += 1
        if op in CHURN_OPS + DEAD_OPS and by_title:
            amenders[by_title] += 1
            amender_id.setdefault(by_title, by_wid)

    busiest_year, busiest_count = by_year.most_common(1)[0]
    top_amenders = [
        {"title": t, "id": amender_id.get(t), "count": c}
        for t, c in amenders.most_common(TOP_AMENDERS_N)
    ]
    timeline = [
        {"date": d, "op": op, "by_title": by_title, "provision": prov}
        for d, op, by_title, _wid, prov in rows[-TIMELINE_N:][::-1]
    ]

    return {
        "id": wid,
        "title": title,
        "type": wtype,
        "year": year,
        "number": leg_no(number),
        "status": status,
        "total": churn,
        "repeals": repeals,
        "events_all": len(rows),
        "span": {"first": rows[0][0], "last": rows[-1][0]},
        "ops": dict(ops.most_common()),
        "busiest": {"year": busiest_year, "count": busiest_count},
        "top_amenders": top_amenders,
        "timeline": timeline,
        "summary": None,   # filled by summarise_acts.py
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("db")
    ap.add_argument("data_dir")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    out = {}
    missing = []
    for wid in target_ids(args.data_dir):
        d = digest(con, wid)
        if d:
            out[wid] = d
        else:
            missing.append(wid)

    # Preserve any prose summaries already written, so re-running the digest
    # doesn't wipe the LLM pass.
    path = Path(args.data_dir) / "act-history.json"
    if path.exists():
        prev = json.loads(path.read_text()).get("acts", {})
        for wid, d in out.items():
            if prev.get(wid, {}).get("summary"):
                d["summary"] = prev[wid]["summary"]

    doc = {
        "generated": date.today().isoformat(),
        "note": ("Per-act change history for the Top-change view. Structured fields are "
                 "provision-level events from the PCO legislation XML; `summary` is an LLM "
                 "pass over those fields (summarise_acts.py)."),
        "acts": out,
    }
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print(f"act-history: {len(out)} acts written"
          + (f", {len(missing)} had no events ({missing})" if missing else ""), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
