#!/usr/bin/env python3
"""Export the amendment graph into the app's data contract.

Two outputs, with an honesty gate between them:

1. Lane enrichment (always): for every act in public/data/churn-acts.json,
   find its work in the graph (by DLM id, else normalised title) and fill
   amendment_count + a real parsed events[] list, each event stamped with the
   government in power.

2. Aggregates (gated): per-term amendment/repeal counts, half-life,
   most-amended. Only written when the acts mirror is complete AND the
   known-facts benchmark passes — partial-corpus aggregates would be lies.
   Run with --force to override the mirror-completeness check (never the
   benchmark).

Usage:
  python3 pipeline/export_churn.py pipeline/graph.sqlite public/data [--force]
"""

import argparse
import json
import re
import sqlite3
import sys
import unicodedata
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from classify import classify  # noqa: E402

CHURN_OPS = ("amended", "inserted", "substituted", "replaced")
DEAD_OPS = ("repealed", "revoked")


def norm_title(t):
    if not t:
        return ""
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z0-9 ]+", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()


def load_governments(data_dir):
    govs = json.loads((Path(data_dir) / "governments.json").read_text())
    out = []
    for g in govs:
        out.append((g["start"], g["end"] or "9999-12-31", g["id"]))
    return sorted(out)


def govt_at(govs, iso):
    if not iso:
        return None
    for start, end, gid in govs:
        if start <= iso < end:
            return gid
    return None


def find_work(con, dlm, title):
    if dlm:
        row = con.execute(
            "SELECT id, title FROM works WHERE id = ?", (dlm,)
        ).fetchone()
        if row:
            return row
    if title:
        row = con.execute(
            "SELECT id, title FROM works WHERE norm_title = ?", (norm_title(title),)
        ).fetchone()
        if row:
            return row
        # try without trailing year noise / subtitle
        base = norm_title(title)
        row = con.execute(
            "SELECT id, title FROM works WHERE norm_title LIKE ? LIMIT 1", (base[:60] + "%",)
        ).fetchone()
        if row:
            return row
    return None


def enrich_lanes(con, data_dir, govs):
    path = Path(data_dir) / "churn-acts.json"
    doc = json.loads(path.read_text())
    matched = 0
    total = 0
    for lane in doc["lanes"]:
        for act in lane["acts"]:
            total += 1
            hit = find_work(con, act.get("dlm"), act.get("full_title") or act.get("title"))
            if not hit:
                continue
            work_id, work_title = hit
            matched += 1
            act["dlm"] = work_id
            n = con.execute(
                "SELECT COUNT(*) FROM events WHERE work_id = ? AND op IN (?,?,?,?)",
                (work_id, *CHURN_OPS),
            ).fetchone()[0]
            act["amendment_count"] = n
            events = []
            for d, op, by_title, provision in con.execute(
                """SELECT date, op, by_title, provision FROM events
                   WHERE work_id = ? AND op != 'editorial' AND date IS NOT NULL
                   ORDER BY date""",
                (work_id,),
            ):
                events.append(
                    {
                        "date": d,
                        "op": op,
                        "by_title": by_title,
                        "provision": provision,
                        "govt": govt_at(govs, d),
                    }
                )
            act["events"] = events
            if events:
                act["partial"] = False
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print(f"lanes: matched {matched}/{total} acts against the graph", flush=True)
    return matched


def benchmark(con):
    """The graph must reproduce documented facts before aggregates publish."""
    checks = []

    def has_work(fragment):
        return con.execute(
            "SELECT COUNT(*) FROM works WHERE norm_title LIKE ?",
            ("%" + norm_title(fragment) + "%",),
        ).fetchone()[0] > 0

    def repeal_event_on(fragment, year):
        return con.execute(
            """SELECT COUNT(*) FROM events e JOIN works w
               ON e.work_id = w.id
               WHERE w.norm_title LIKE ? AND e.op IN ('repealed','revoked')
               AND e.date LIKE ?""",
            ("%" + norm_title(fragment) + "%", f"{year}%"),
        ).fetchone()[0] > 0

    checks.append(("RMA 1991 present", has_work("Resource Management Act 1991")))
    checks.append(("NBA 2023 present", has_work("Natural and Built Environment Act 2023")))
    checks.append(
        ("Water Services Entities Act repeal evidenced 2024",
         repeal_event_on("Water Services Entities Act 2022", 2024) or has_work("Water Services Acts Repeal Act 2024"))
    )
    checks.append(
        ("Smokefree amendment repeal evidenced 2024",
         repeal_event_on("Smokefree Environments and Regulated Products (Smoked Tobacco) Amendment Act", 2024)
         or has_work("Smokefree Environments and Regulated Products Amendment Act 2024"))
    )
    checks.append(("FPA repeal act present", has_work("Fair Pay Agreements Act Repeal Act 2023")))

    ok = True
    for name, passed in checks:
        print(f"  benchmark {'PASS' if passed else 'FAIL'}: {name}", flush=True)
        ok = ok and passed
    return ok


def export_aggregates(con, data_dir, govs):
    path = Path(data_dir) / "churn-aggregates.json"
    doc = json.loads(path.read_text())

    per_term = {}
    for d, op, work_title in con.execute(
        "SELECT date, op, work_title FROM events WHERE date IS NOT NULL AND date >= '2008'"
    ):
        gid = govt_at(govs, d)
        if not gid:
            continue
        bucket = per_term.setdefault(gid, {"govt": gid, "amendments": 0, "repeals": 0, "by_sector": {}})
        sector = classify(work_title)
        if op in CHURN_OPS:
            bucket["amendments"] += 1
            bucket["by_sector"][sector] = bucket["by_sector"].get(sector, 0) + 1
        elif op in DEAD_OPS:
            bucket["repeals"] += 1
            bucket["by_sector"][sector] = bucket["by_sector"].get(sector, 0) + 1
    # honesty flags: the 2008 timeline-start truncates Clark's term, and the
    # current term is still running — neither bucket is comparable as-is
    for bucket in per_term.values():
        g = next((x for x in govs if x[2] == bucket["govt"]), None)
        if g and (g[0] < "2008-01-01" or g[1] == "9999-12-31"):
            bucket["partial"] = True
    doc["per_term"] = list(per_term.values())

    top = con.execute(
        f"""SELECT work_id, work_title, COUNT(*) c FROM events
            WHERE op IN {CHURN_OPS!r} AND work_title IS NOT NULL
            GROUP BY work_id ORDER BY c DESC LIMIT 10"""
    ).fetchall()
    doc["most_amended"] = [{"id": i, "title": t, "count": c} for i, t, c in top]

    # "half-life": median age of the host act at the moment one of its
    # provisions is repealed/revoked. Provision-level, NOT whole-instrument
    # lifespan (a provision inserted later than enactment biases the span
    # upward) — the labels below must say exactly what this is.
    spans = []
    for (y, d) in con.execute(
        """SELECT w.year, e.date FROM events e JOIN works w ON e.work_id = w.id
           WHERE e.op IN ('repealed','revoked') AND w.year IS NOT NULL AND e.date IS NOT NULL"""
    ):
        try:
            span = int(d[:4]) - int(y)
            if 0 <= span < 200:
                spans.append(span)
        except (ValueError, TypeError):
            continue
    if spans:
        spans.sort()
        doc["half_life_years"] = spans[len(spans) // 2]
        doc["half_life_note"] = (
            "median age of an act when one of its provisions is repealed or revoked; "
            "provision-level, not whole-act lifespan"
        )

    # flip the pending stat cards to sourced-by-pipeline
    for card in doc.get("stat_cards", []):
        if card["id"] == "half-life" and spans:
            card.update(status="sourced", value=f"{doc['half_life_years']} yrs",
                        label="Age of a law when part of it gets struck out",
                        sub=f"median age of an act when one of its provisions is repealed — across {len(spans):,} repeal events in the statute book",
                        source="Whiplash pipeline — PCO legislation XML")
        if card["id"] == "most-amended" and top:
            card.update(status="sourced", value=f"{top[0][2]:,}×",
                        label="Most-amended statute",
                        sub=f"{top[0][1]} — provision-level amendment events on record",
                        source="Whiplash pipeline — PCO legislation XML")

    doc["generated"] = date.today().isoformat()
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print(f"aggregates: {len(per_term)} terms, top act = {top[0][1] if top else 'n/a'}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("db")
    ap.add_argument("data_dir")
    ap.add_argument("--force", action="store_true",
                    help="skip the mirror-completeness check (benchmark still applies)")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    govs = load_governments(args.data_dir)

    enrich_lanes(con, args.data_dir, govs)

    log = Path("data-raw/mirror.log")
    acts_done = log.exists() and "ACTS DONE" in log.read_text()
    if not (acts_done or args.force):
        print("aggregates SKIPPED: acts mirror not complete (gate; --force to override)", flush=True)
        return 0
    if not benchmark(con):
        print("aggregates BLOCKED: known-facts benchmark failed — fix the graph first", flush=True)
        return 1
    export_aggregates(con, args.data_dir, govs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
