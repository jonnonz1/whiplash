#!/usr/bin/env python3
"""LLM pass: write a prose `summary` for each act in act-history.json.

export_act_history.py produces the structured digest (totals, busiest year,
biggest amending Acts, recent timeline) with `summary: null`. This script reads
that digest and asks Claude to turn each act's numbers into two grounded
sentences — what changed, and the headline story — strictly from the supplied
fields (no outside knowledge, no invented detail).

Idempotent: acts that already have a summary are skipped unless --force.
Needs ANTHROPIC_API_KEY in the environment.

Usage:
  python3 pipeline/summarise_acts.py public/data/act-history.json [--force] [--model claude-sonnet-4-6]
"""

import argparse
import json
import os
import sys
from pathlib import Path

SYSTEM = (
    "You summarise the amendment history of a New Zealand law for a data viz. "
    "Write two or three sentences that say WHAT changed, not just how much. "
    "Your only source of substance is the titles of the biggest amending Acts: "
    "the parenthetical themes in those titles (e.g. '(Vaping)', '(Closely Held "
    "Companies)', '(Emissions Trading Reform)') are the topics — name them in "
    "plain words. Mention the repeal/replacement if the digest shows one. Stay "
    "grounded ONLY in the digest: never invent facts, motives, or numbers not "
    "present, and where an amending Act's title carries no theme, don't guess "
    "what it did. No preamble, no quotes, no markdown — just the sentences."
)


def prompt_for(a):
    fields = {
        "title": a["title"], "type": a["type"], "year": a["year"],
        "total_changes": a["total"], "repeals": a["repeals"],
        "span": a["span"], "busiest": a["busiest"],
        "operations": a["ops"],
        "biggest_amending_acts": a["top_amenders"],
        "recent_events": a["timeline"][:6],
    }
    return "Digest:\n" + json.dumps(fields, ensure_ascii=False, indent=2)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path")
    ap.add_argument("--force", action="store_true", help="rewrite summaries that already exist")
    ap.add_argument("--model", default="claude-sonnet-4-6")
    args = ap.parse_args()

    try:
        from anthropic import Anthropic
    except ImportError:
        print("pip install anthropic", file=sys.stderr)
        return 1
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("set ANTHROPIC_API_KEY", file=sys.stderr)
        return 1

    client = Anthropic()
    path = Path(args.path)
    doc = json.loads(path.read_text())
    acts = doc["acts"]

    todo = [k for k, a in acts.items() if args.force or not a.get("summary")]
    print(f"summarising {len(todo)}/{len(acts)} acts with {args.model}", flush=True)
    for i, k in enumerate(todo, 1):
        msg = client.messages.create(
            model=args.model, max_tokens=300, system=SYSTEM,
            messages=[{"role": "user", "content": prompt_for(acts[k])}],
        )
        acts[k]["summary"] = msg.content[0].text.strip()
        print(f"  [{i}/{len(todo)}] {acts[k]['title']}", flush=True)
        # write through after each so a crash doesn't lose progress
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

    print("done", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
