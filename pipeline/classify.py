#!/usr/bin/env python3
"""Sector classifier for NZ legislation — v1: overrides + title keywords.

No official sector taxonomy exists, so this is the spec's hybrid (specs/
whiplash/03-data-pipeline.md §3) minus the LLM tier for now:

  1. manual override table (the acts readers will actually click — publishable,
     auditable, and the most likely public-criticism vector, so it lives in
     the repo, not in code)
  2. keyword classifier on the title (good enough for aggregate stacking;
     anything unmatched stays 'other' rather than guessing)

The LLM tier for ambiguous/multi-sector acts can slot in later without
changing the interface: classify(title) -> sector key.
"""

import json
import re
from pathlib import Path

OVERRIDES_PATH = Path(__file__).parent / "sector-overrides.json"

KEYWORDS = [
    ("environment", r"resource management|environment|climate|conservation|biodiversity|emissions|carbon|freshwater|fisheries|wildlife|hazardous"),
    ("water", r"\bwater\b|drinking water|wastewater|stormwater|three waters"),
    ("transport", r"transport|railways?|roads?|land transport|civil aviation|maritime|shipping|vehicle"),
    ("health", r"health|smokefree|medicines?|mental|hospital|pae ora|cancer|disability|therapeutic"),
    ("education", r"education|school|university|polytechnic|training|teaching|student|pukenga|tertiary"),
    ("energy", r"energy|electricity|gas\b|crown minerals|petroleum|mining"),
    ("tax", r"taxation|income tax|gst|goods and services tax|customs|excise|revenue"),
    ("justice", r"sentencing|crimes?|criminal|justice|courts?|police|corrections|parole|evidence|employment|fair pay|industrial relations"),
    ("economy", r"finance|public finance|appropriation|reserve bank|commerce|companies|securities|overseas investment|state sector|public service"),
]

_COMPILED = [(sector, re.compile(rx, re.I)) for sector, rx in KEYWORDS]


def load_overrides():
    if OVERRIDES_PATH.exists():
        return json.loads(OVERRIDES_PATH.read_text())
    return {}


_OVERRIDES = load_overrides()


def classify(title):
    if not title:
        return "other"
    for fragment, sector in _OVERRIDES.items():
        if fragment.lower() in title.lower():
            return sector
    for sector, rx in _COMPILED:
        if rx.search(title):
            return sector
    return "other"


if __name__ == "__main__":
    import sys

    for t in sys.argv[1:]:
        print(f"{classify(t)}\t{t}")
