#!/usr/bin/env python3
"""Parse the NZ legislation XML mirror into an amendment/repeal graph.

Design: specs/whiplash/03-data-pipeline.md (jonno.nz repo). The amendment
history is element-encoded in <history-note> blocks (NOT XML attributes —
that early research claim was verified false on 2026-06-10):

  <history-note>
    <amended-provision>…</amended-provision>     which provision was touched
    <amending-operation>…</amending-operation>   free text: amended/inserted/…
    <amendment-date>2 July 2001</amendment-date> PROSE date
    <amending-provision href="DLM…">             machine id when present
    <amending-leg>Title of Act 2001</amending-leg>  title only, no id
  </history-note>

Two passes:
  1. index every document  -> works table (id, title, year, number, type, status)
  2. extract history-note tuples, resolve the amending act (href id first,
     title+year fallback against the index) -> events table; unresolved -> queue

Usage:
  python3 pipeline/parse_history.py data-raw/legislation pipeline/graph.sqlite
  python3 pipeline/parse_history.py data-raw/legislation pipeline/graph.sqlite --stats-only
"""

import argparse
import json
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path
from xml.etree import ElementTree as ET

MONTHS = {
    m.lower(): i + 1
    for i, m in enumerate(
        ["January", "February", "March", "April", "May", "June",
         "July", "August", "September", "October", "November", "December"]
    )
}
for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
    MONTHS.setdefault(m.lower(), i + 1)

DATE_RE = re.compile(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})")
YEAR_RE = re.compile(r"\b(1[89]\d\d|20\d\d)\b")
TITLE_YEAR_RE = re.compile(r"\b(1[89]\d\d|20\d\d)\b")

OP_MAP = [
    ("editorial", "editorial"),  # PCO editorial changes are not churn
    ("insert", "inserted"),
    ("substitut", "substituted"),
    ("replac", "replaced"),
    ("repeal", "repealed"),
    ("revok", "revoked"),
    ("amend", "amended"),
    ("add", "inserted"),
    ("omit", "repealed"),
]


def norm_op(raw):
    if not raw:
        return "other"
    low = raw.lower()
    for needle, op in OP_MAP:
        if needle in low:
            return op
    return "other"


def parse_prose_date(raw):
    """'2 July 2001' -> '2001-07-02'; tolerate noise; fall back to year only."""
    if not raw:
        return None
    m = DATE_RE.search(raw)
    if m:
        day, mon, year = m.groups()
        mm = MONTHS.get(mon.lower())
        if mm:
            return f"{year}-{mm:02d}-{int(day):02d}"
    y = YEAR_RE.search(raw)
    if y:
        return f"{y.group(1)}-01-01"
    return None


def norm_title(t):
    """Normalised title key for fallback matching."""
    if not t:
        return ""
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z0-9 ]+", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()


def text_of(el):
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip() if el is not None else None


class Doc:
    __slots__ = ("path", "id", "title", "year", "number", "type", "status", "version")

    def __init__(self, path):
        self.path = path
        self.id = None
        self.title = None
        self.year = None
        self.number = None
        self.type = None
        self.status = None
        self.version = None


def parse_doc_header(path, root):
    """Pull identity off the root element + cover block, defensively."""
    d = Doc(str(path))
    d.type = root.tag
    d.id = root.get("id") or root.get("Id")
    d.year = root.get("year")
    d.status = root.get("status") or root.get("stage")
    d.number = (root.get("act.no") or root.get("sr.no") or root.get("no")
                or root.get("number"))
    cover = root.find(".//cover")
    title_el = (cover.find("title") if cover is not None else None)
    if title_el is None:
        title_el = root.find(".//title")
    d.title = text_of(title_el)
    if d.year is None and d.title:
        m = TITLE_YEAR_RE.search(d.title)
        if m:
            d.year = m.group(1)
    # path fallback: …/act/public/1991/0069/<version>/<file>.xml
    parts = Path(path).parts
    for i, p in enumerate(parts):
        if p in ("act", "regulation") and i + 2 < len(parts):
            d.year = d.year or parts[i + 2]
            if i + 3 < len(parts):
                d.number = d.number or parts[i + 3].lstrip("0")
            break
    try:
        d.version = float(Path(path).parent.name)
    except ValueError:
        d.version = None
    return d


def iter_xml(mirror_dir):
    for p in sorted(Path(mirror_dir).rglob("*.xml")):
        yield p


def latest_versions(mirror_dir):
    """Keep only the highest version dir per work directory."""
    best = {}
    for p in iter_xml(mirror_dir):
        workdir = p.parent.parent  # …/1991/0069
        try:
            v = float(p.parent.name)
        except ValueError:
            workdir, v = p.parent, 0.0
        cur = best.get(workdir)
        if cur is None or v > cur[0]:
            best[workdir] = (v, p)
    return [p for _, p in best.values()]


def build(mirror_dir, db_path, stats_only=False):
    files = latest_versions(mirror_dir)
    print(f"{len(files)} work documents (latest versions) under {mirror_dir}", flush=True)

    con = sqlite3.connect(db_path)
    con.executescript(
        """
        DROP TABLE IF EXISTS works;
        DROP TABLE IF EXISTS events;
        DROP TABLE IF EXISTS unresolved;
        CREATE TABLE works(
            id TEXT, title TEXT, norm_title TEXT, year INT, number TEXT,
            type TEXT, status TEXT, path TEXT
        );
        CREATE TABLE events(
            work_id TEXT, work_title TEXT, date TEXT, op TEXT, raw_op TEXT,
            by_work_id TEXT, by_title TEXT, provision TEXT, raw TEXT
        );
        CREATE TABLE unresolved(
            work_id TEXT, date TEXT, op TEXT, amending_leg TEXT, raw TEXT
        );
        """
    )

    # ---- pass 1: stream every doc once — index header + extract raw events.
    # Roots are NOT retained (a full corpus of parsed DOMs would exhaust RAM);
    # title resolution happens against SQLite in pass 2.
    n_docs = n_notes = n_resolved_href = parse_errors = 0
    for i, p in enumerate(files):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            parse_errors += 1
            continue
        d = parse_doc_header(p, root)
        n_docs += 1
        con.execute(
            "INSERT INTO works VALUES (?,?,?,?,?,?,?,?)",
            (d.id, d.title, norm_title(d.title), d.year, d.number, d.type, d.status, d.path),
        )
        for note in root.iter("history-note"):
            n_notes += 1
            provision = text_of(note.find("amended-provision"))
            raw_op = text_of(note.find("amending-operation"))
            date = parse_prose_date(text_of(note.find("amendment-date")))
            amending_prov = note.find("amending-provision")
            href = amending_prov.get("href") if amending_prov is not None else None
            amending_leg = text_of(note.find("amending-leg"))
            raw = re.sub(r"\s+", " ", "".join(note.itertext())).strip()[:400]
            by_id = href.lstrip("#/") if href else None
            if by_id:
                n_resolved_href += 1
            con.execute(
                "INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?)",
                (d.id, d.title, date, norm_op(raw_op), raw_op, by_id, amending_leg, provision, raw),
            )
        if (i + 1) % 1000 == 0:
            con.commit()
            print(f"  …{i + 1}/{len(files)} docs, {n_notes} events so far", flush=True)
    con.commit()
    print(f"pass 1: indexed {n_docs} docs ({parse_errors} XML parse errors), {n_notes} history-notes", flush=True)

    # ---- pass 2: resolve amending-leg titles against the index (pure SQL) ----
    con.execute("CREATE INDEX IF NOT EXISTS idx_works_norm ON works(norm_title)")
    title_index = dict(
        con.execute("SELECT norm_title, id FROM works WHERE norm_title != '' GROUP BY norm_title")
    )
    n_resolved_title = n_unresolved = 0
    pending = con.execute(
        "SELECT rowid, work_id, date, op, by_title, raw FROM events WHERE by_work_id IS NULL AND by_title IS NOT NULL"
    ).fetchall()
    for rowid, work_id, date, op, by_title, raw in pending:
        hit = title_index.get(norm_title(by_title))
        if hit:
            con.execute("UPDATE events SET by_work_id = ? WHERE rowid = ?", (hit, rowid))
            n_resolved_title += 1
        else:
            n_unresolved += 1
            con.execute("INSERT INTO unresolved VALUES (?,?,?,?,?)", (work_id, date, op, by_title, raw))
    con.commit()
    print(
        f"pass 2: resolved by href {n_resolved_href}, by title {n_resolved_title}, unresolved {n_unresolved}",
        flush=True,
    )

    # quick shape report
    for row in con.execute(
        "SELECT op, COUNT(*) FROM events GROUP BY op ORDER BY 2 DESC LIMIT 10"
    ):
        print(f"  op {row[0]}: {row[1]}", flush=True)

    if stats_only:
        con.close()
        return

    con.close()
    print(f"graph written to {db_path}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mirror_dir")
    ap.add_argument("db", nargs="?", default="pipeline/graph.sqlite")
    ap.add_argument("--stats-only", action="store_true")
    args = ap.parse_args()
    build(args.mirror_dir, args.db, args.stats_only)
    return 0


if __name__ == "__main__":
    sys.exit(main())
