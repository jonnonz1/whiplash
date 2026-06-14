#!/usr/bin/env python3
"""Build `nz-statute-book`: the entire NZ public statute book as one git
mono-repo, where GitHub becomes the free renderer (history / blame / diff).

Every public Act, every electronic consolidation, becomes one commit —
authored by the government of the day — that modifies exactly one file:

    acts/public/<year>/<slug>.md   (content = render_act.render(xml))

so `git log --follow` on that file reads as the act's amendment history, and
the repo's global `git log` reads as NZ's whole legislative timeline. Because
render_act emits one semantic unit per line, a one-section amendment is a
one-line diff and `git blame` attributes each line to a government.

Reuses, does not reimplement:
  - render_act.render()                    — XML → diff-stable markdown
  - export_churn.govt_at / load_governments — government of the day

Two phases (determinism is the contract — same inputs ⇒ identical SHAs):
  1. PARALLEL RENDER every version to a content-addressed cache
     (<cache>/<hash>.md, N workers). The PCO hash in the path IS the content
     address, so the cache is re-runnable and dedups for free.
  2. SERIAL `git fast-import` reading the cache (never a commit/checkout loop —
     15k checkouts of multi-MB files is the trap). One commit per version, in
     global chronological order, + a final README/.gitattributes meta commit.

Usage:
  # full acts build (heavy: minutes + GBs of cache/repo)
  python3 pipeline/build_git_repo.py --out data-raw/nz-statute-book

  # scoped smoke test (a few acts, fast)
  python3 pipeline/build_git_repo.py --out /tmp/nzsb-smoke --checkout \
      --work-id DLM230264 --work-id LMS534585
"""

import argparse
import json
import re
import sqlite3
import subprocess
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, str(Path(__file__).parent))
from render_act import render  # noqa: E402
from export_churn import govt_at, load_governments  # noqa: E402

# The data stamps reprints at noon; we fix +1200 (matching the git-demo and the
# plan) rather than tracking NZDT, so the timestamp is reproducible.
NZ_TZ = timezone(timedelta(hours=12))
GENESIS_ELECTRONIC_YEAR = 2007  # acts older than this start mid-history here
BODY_CAP = 50  # max amendment lines quoted in a commit body
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")  # PCO stamps some consolidations 'nulldate'


# --------------------------------------------------------------------------- #
# slugs
# --------------------------------------------------------------------------- #
def slugify(title):
    """Lowercased title, non-alphanumerics collapsed to '-'. Macrons folded to
    ASCII so Māori titles get clean URL-safe slugs. The title already carries
    the year, so this yields e.g. 'resource-management-act-1991'."""
    t = unicodedata.normalize("NFKD", title or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    return t or "untitled"


def read_root_attrs(path):
    """Just the root <act> attributes — stop at the first start event so even a
    70 MB file is read in milliseconds (the full parse happens once, in the
    parallel render phase)."""
    for _ev, el in ET.iterparse(path, events=("start",)):
        a = el.attrib
        return {"id": a.get("id"), "date": a.get("date.as.at"),
                "year": a.get("year"), "no": a.get("act.no")}
    return {}


def read_title(path):
    """Fallback canonical title for an id absent from the works table: the
    cover title, read by stopping at the first </title>."""
    for _ev, el in ET.iterparse(path, events=("end",)):
        if el.tag.split("}")[-1] == "title":
            return " ".join("".join(el.itertext()).split())
    return None


# --------------------------------------------------------------------------- #
# phase 0 — gather versions + resolve slugs
# --------------------------------------------------------------------------- #
def gather(leg_root, only_ids):
    """Every act/public consolidation as a version dict, keyed by the XML root
    id (= the works/DLM id)."""
    base = Path(leg_root) / "act" / "public"
    versions = []
    skipped_nodate = 0
    for xml in base.glob("*/*/*/*.xml"):  # <year>/<no>/<reprint>/<hash>.xml
        a = read_root_attrs(xml)
        wid, date = a.get("id"), a.get("date")
        if not wid:
            continue
        if only_ids and wid not in only_ids:
            continue
        if not date or not DATE_RE.match(date):
            # 'nulldate' & friends have no orderable consolidation date —
            # date.as.at is the repo's ordering truth, so skip, don't guess
            skipped_nodate += 1
            continue
        reprint = xml.parent.name  # "62.0" verbatim
        try:
            reprint_f = float(reprint)
        except ValueError:
            reprint_f = 0.0
        versions.append({
            "id": wid,
            "date": date,
            "year": a.get("year") or xml.parts[-4],
            "no": (a.get("no") or xml.parts[-3]).lstrip("0") or "0",
            "reprint": reprint,
            "reprint_f": reprint_f,
            "xml": str(xml),
            "hash": xml.stem,
        })
    if skipped_nodate:
        print(f"  skipped {skipped_nodate} versions with no/invalid date.as.at (e.g. 'nulldate')", flush=True)
    return versions


def resolve_slugs(versions, works):
    """work id → (title, slug). Slugs collide on (year, slug); the plan's one
    known collision is disambiguated with a -no<act.no> suffix applied to the
    whole colliding group (order-independent ⇒ deterministic)."""
    title_of, year_of, no_of = {}, {}, {}
    for v in versions:
        wid = v["id"]
        if wid not in title_of:
            title_of[wid] = works.get(wid, {}).get("title") or read_title(v["xml"]) or wid
            year_of[wid] = v["year"]
            no_of[wid] = v["no"]

    groups = {}
    for wid, title in title_of.items():
        groups.setdefault((year_of[wid], slugify(title)), []).append(wid)

    slug_of = {}
    for (year, base_slug), ids in groups.items():
        for wid in ids:
            slug_of[wid] = base_slug if len(ids) == 1 else f"{base_slug}-no{no_of[wid]}"
    return title_of, slug_of


# --------------------------------------------------------------------------- #
# phase 1 — parallel render to a content-addressed cache
# --------------------------------------------------------------------------- #
def _render_one(job):
    xml, out = job
    out = Path(out)
    if out.exists():
        return out.stat().st_size
    md = render(xml)
    out.write_text(md, encoding="utf-8")
    return len(md.encode())


def render_cache(versions, cache_dir, workers):
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    jobs = {}  # hash -> (xml, cache_path); dedups identical content addresses
    for v in versions:
        jobs.setdefault(v["hash"], (v["xml"], str(cache_dir / f"{v['hash']}.md")))
    jobs = list(jobs.values())
    print(f"phase 1: rendering {len(jobs)} unique versions → {cache_dir} ({workers} workers)", flush=True)
    biggest = 0
    done = 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for size in ex.map(_render_one, jobs, chunksize=8):
            biggest = max(biggest, size)
            done += 1
            if done % 1000 == 0:
                print(f"  rendered {done}/{len(jobs)}", flush=True)
    print(f"phase 1 done: largest rendered .md = {biggest/1e6:.2f} MB", flush=True)
    if biggest > 50_000_000:
        print(f"  WARNING: a rendered file exceeds 50 MB ({biggest/1e6:.1f} MB)", flush=True)
    return biggest


# --------------------------------------------------------------------------- #
# phase 2 — serial fast-import
# --------------------------------------------------------------------------- #
def ts_of(date_iso):
    y, m, d = map(int, date_iso.split("-"))
    return int(datetime(y, m, d, 12, 0, 0, tzinfo=NZ_TZ).timestamp())


def author_for(gid, gov_meta):
    """Government of the day → (name, email). Email buckets by party so
    `git shortlog -sne` and `git blame` group by government. Pre-electoral-data
    dates fall back to a generic parliament identity."""
    g = gov_meta.get(gid)
    if not g:
        return "New Zealand Parliament", "parliament@parliament.nz"
    return g["label"], f"{g['party']}@parliament.nz"


def commit_body(con, work_id, date_iso, is_genesis, year):
    """Amendments effective exactly on this consolidation's date — the
    exact-date fence validated against the known acts. Capped, then an honest
    note on genesis commits of acts older than the electronic-consolidation era."""
    rows = con.execute(
        """SELECT op, provision, by_title FROM events
           WHERE work_id = ? AND date = ? AND op != 'editorial'
           ORDER BY provision, op, by_title""",
        (work_id, date_iso),
    ).fetchall()
    lines = []
    for op, prov, by in rows[:BODY_CAP]:
        seg = f"- {op}"
        if prov:
            seg += f" {prov}"
        if by:
            seg += f" — {by}"
        lines.append(seg)
    if len(rows) > BODY_CAP:
        lines.append(f"…and {len(rows) - BODY_CAP} more")
    if is_genesis and year and year.isdigit() and int(year) < GENESIS_ELECTRONIC_YEAR:
        if lines:
            lines.append("")
        lines.append(
            "(History in this repo starts at the first electronic consolidation; "
            "amendments predating NZ Legislation's published XML aren't represented "
            "as commits.)"
        )
    return "\n".join(lines)


def _write_commit(stream, mark, author, email, ts, message, path, content):
    ident = f"{author} <{email}>".encode("utf-8")
    msg = message.encode("utf-8")
    body = content.encode("utf-8")
    w = stream.write
    w(b"commit refs/heads/main\n")
    w(f"mark :{mark}\n".encode())
    w(b"author "); w(ident); w(f" {ts} +1200\n".encode())
    w(b"committer "); w(ident); w(f" {ts} +1200\n".encode())
    w(f"data {len(msg)}\n".encode()); w(msg); w(b"\n")
    w(f"M 100644 inline {path}\n".encode())
    w(f"data {len(body)}\n".encode()); w(body); w(b"\n")


def fast_import(con, versions, title_of, slug_of, gov_meta, govs, cache_dir, out_dir):
    """One commit per version in global chronological order, then a meta commit
    for README + .gitattributes (dated to the max consolidation date, for
    reproducibility)."""
    cache_dir = Path(cache_dir)
    versions = sorted(versions, key=lambda v: (v["date"], v["reprint_f"], slug_of[v["id"]]))
    seen_work = set()
    n_acts = len({v["id"] for v in versions})
    max_date = versions[-1]["date"]

    proc = subprocess.Popen(
        ["git", "fast-import", "--date-format=raw", "--quiet"],
        cwd=out_dir, stdin=subprocess.PIPE,
    )
    s = proc.stdin
    mark = 0
    for i, v in enumerate(versions, 1):
        wid = v["id"]
        is_genesis = wid not in seen_work
        seen_work.add(wid)
        title = title_of[wid]
        gid = govt_at(govs, v["date"])
        name, email = author_for(gid, gov_meta)
        govt_label = gov_meta.get(gid, {}).get("label", "New Zealand Parliament")
        subject = f"{v['date']} · {govt_label} · {title} (v{v['reprint']})"
        body = commit_body(con, wid, v["date"], is_genesis, v["year"])
        message = f"{subject}\n\n{body}" if body else subject
        content = (cache_dir / f"{v['hash']}.md").read_text(encoding="utf-8")
        path = f"acts/public/{v['year']}/{slug_of[wid]}.md"
        mark += 1
        _write_commit(s, mark, name, email, ts_of(v["date"]), message, path, content)
        if i % 2000 == 0:
            print(f"  fast-import: {i}/{len(versions)} commits streamed", flush=True)

    # meta commit: README + .gitattributes, dated to the last consolidation
    readme = render_readme(n_acts, len(versions), max_date)
    mark += 1
    ts = ts_of(max_date)
    ident = "Whiplash pipeline <pipeline@whiplash.nz>".encode("utf-8")
    s.write(b"commit refs/heads/main\n")
    s.write(f"mark :{mark}\n".encode())
    s.write(b"author "); s.write(ident); s.write(f" {ts} +1200\n".encode())
    s.write(b"committer "); s.write(ident); s.write(f" {ts} +1200\n".encode())
    msg = b"Add repository README and .gitattributes"
    s.write(f"data {len(msg)}\n".encode()); s.write(msg); s.write(b"\n")
    rb = readme.encode("utf-8")
    s.write(b"M 100644 inline README.md\n")
    s.write(f"data {len(rb)}\n".encode()); s.write(rb); s.write(b"\n")
    ga = b"*.md text eol=lf\n"
    s.write(b"M 100644 inline .gitattributes\n")
    s.write(f"data {len(ga)}\n".encode()); s.write(ga); s.write(b"\n")

    s.close()
    if proc.wait() != 0:
        raise SystemExit("git fast-import failed")
    print(f"phase 2 done: {len(versions)} version commits + 1 meta commit over {n_acts} acts", flush=True)
    return n_acts, len(versions), max_date


def render_readme(n_acts, n_versions, max_date):
    return f"""# The New Zealand statute book, in git

Every public Act of the New Zealand Parliament, every electronic consolidation,
as a commit authored by the government of the day. GitHub renders the history,
blame and diffs for free.

- **{n_acts:,} acts** · **{n_versions:,} consolidations** (one commit each)
- Current through consolidations as at **{max_date}**
- One file per act: `acts/public/<year>/<slug>.md`

## How to read it

```sh
git log --follow acts/public/1991/resource-management-act-1991.md   # an act's life
git blame      acts/public/1991/resource-management-act-1991.md   # which govt wrote each line
git show <commit>                                                  # a single amendment as a diff
git shortlog -sne                                                  # commits bucketed by government
```

Each commit modifies exactly one file. The markdown renders one semantic unit
(subsection, paragraph, definition) per line, so a one-section amendment is a
one-line diff. The commit subject is `DATE · GOVERNMENT · TITLE (vREPRINT)`;
the body lists the amendments effective that day. Author identity is the
government in power, bucketed by party email — never a verdict, just the record.

## Provenance

Rendered deterministically from the New Zealand Legislation (PCO) XML — free of
copyright under s 27 Copyright Act 1994; reuse statement CC BY 4.0. Consolidation
furniture (history notes, tables of contents) is stripped so diffs show real
legislative change; the amendment graph lives in the Whiplash pipeline. Repealed
provisions render as their PCO `[Repealed]` tombstone. Regenerable from the same
inputs — identical inputs produce identical commit SHAs.

_Generated by the Whiplash pipeline (`pipeline/build_git_repo.py`)._
"""


# --------------------------------------------------------------------------- #
def load_works(db):
    con = sqlite3.connect(db)
    works = {}
    for wid, title, year, number in con.execute(
        "SELECT id, title, year, number FROM works WHERE type = 'act'"
    ):
        works[wid] = {"title": title, "year": year, "number": number}
    con.close()
    return works


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default="pipeline/graph.sqlite")
    ap.add_argument("--legislation", default="data-raw/legislation")
    ap.add_argument("--data-dir", default="public/data", help="for governments.json")
    ap.add_argument("--out", default="data-raw/nz-statute-book", help="output repo dir")
    ap.add_argument("--cache", default="data-raw/git-build-cache")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--work-id", action="append", default=[], help="restrict to these work ids (repeatable; smoke test)")
    ap.add_argument("--no-repack", action="store_true")
    ap.add_argument("--checkout", action="store_true", help="checkout the working tree after import (inspection)")
    args = ap.parse_args()

    only = set(args.work_id)
    works = load_works(args.db)
    gov_meta = {g["id"]: g for g in json.loads((Path(args.data_dir) / "governments.json").read_text())}
    govs = load_governments(args.data_dir)

    print("phase 0: gathering versions…", flush=True)
    versions = gather(args.legislation, only)
    if not versions:
        raise SystemExit("no versions gathered — check --legislation path / --work-id filters")
    title_of, slug_of = resolve_slugs(versions, works)
    print(f"phase 0 done: {len(versions)} versions over {len({v['id'] for v in versions})} acts", flush=True)

    render_cache(versions, args.cache, args.workers)

    out = Path(args.out)
    if out.exists():
        raise SystemExit(f"refusing to overwrite existing {out} — remove it first")
    out.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=out, check=True)

    con = sqlite3.connect(args.db)
    fast_import(con, versions, title_of, slug_of, gov_meta, govs, args.cache, out)
    con.close()

    if not args.no_repack:
        print("repacking…", flush=True)
        subprocess.run(["git", "repack", "-adf", "--depth=250", "--window=250"], cwd=out, check=True)
    if args.checkout:
        subprocess.run(["git", "checkout", "-q", "main"], cwd=out, check=True)

    size = subprocess.run(["git", "count-objects", "-vH"], cwd=out, capture_output=True, text=True).stdout
    print("\n=== git count-objects -vH ===")
    print(size.strip())
    print(f"\nrepo ready at {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
