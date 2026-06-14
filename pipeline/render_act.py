#!/usr/bin/env python3
"""Render PCO legislation XML to diff-stable markdown.

Design rules (these decide whether git diffs of legislation are surgical or
useless):

1. ONE SEMANTIC UNIT PER LINE. A subsection, a paragraph, a definition — each
   is exactly one line, however long. Git diffs at line granularity, so the
   diff then IS the legislative change. Never hard-wrap: a one-word amendment
   must touch one line, not reflow a paragraph.
2. DETERMINISTIC OUTPUT. Identical XML → byte-identical markdown, across runs
   and machines. No timestamps, no dict-order dependence. Unchanged provisions
   must produce unchanged lines or every consolidation diffs as noise.
3. STRIP CONSOLIDATION FURNITURE. history-notes, editorial notes and tables of
   contents churn with every reprint and would drown real changes. The
   amendment history lives in the graph (and in commit messages), not in the
   rendered text.
4. KEEP THE LAW'S OWN ADDRESSING. Section/subsection/paragraph labels render
   as (1), (a), (i) prefixes so `git blame act.md | grep "(2)(a)"` works.

Repealed provisions render as their PCO tombstone text ("[Repealed]"), which
makes a repeal diff read exactly like what it is: the body of the law replaced
by a gravestone.
"""

from xml.etree import ElementTree as ET

# elements that become their own output line
UNIT_TAGS = {"subprov", "label-para", "def-para", "proviso"}
# structure containers that become headings
HEAD_TAGS = {"part", "subpart", "schedule", "schedule.group"}
# stripped entirely: consolidation furniture + history (lives in the graph)
SKIP_TAGS = {"history", "history-note", "notes", "contents", "toc", "colspec", "thead.style", "tbody.style"}

def _tag(el):
    return el.tag.split("}")[-1]

def _inline(el, stop):
    """Text of el, skipping descendant subtrees in `stop` (the root element
    itself is never stopped), whitespace-normalised."""
    parts = []

    def walk(e, is_root=False):
        if not is_root and (_tag(e) in stop or _tag(e) in SKIP_TAGS):
            return
        if e.text:
            parts.append(e.text)
        for c in e:
            walk(c)
            if c.tail:
                parts.append(c.tail)

    walk(el, is_root=True)
    return " ".join("".join(parts).split())

def _label_of(el):
    lab = el.find("label")
    return " ".join("".join(lab.itertext()).split()) if lab is not None else ""

def _emit_unit(el, depth, out):
    tag = _tag(el)
    indent = "  " * depth
    stop = UNIT_TAGS | {"label"}
    if tag == "def-para":
        term_el = el.find(".//def-term")
        term = " ".join("".join(term_el.itertext()).split()) if term_el is not None else ""
        body = _inline(el, stop | {"def-term"})
        out.append(f"{indent}- **{term}** {body}".rstrip())
    else:
        label = _label_of(el)
        body = _inline(el, stop)
        prefix = f"({label}) " if label else ""
        if body or label:
            out.append(f"{indent}{prefix}{body}".rstrip())
    for child in el.iter():
        if child is el:
            continue
        # only direct-descendant units not nested inside another unit
        pass
    _emit_child_units(el, depth + 1, out)

def _emit_child_units(el, depth, out):
    """Render unit children in document order, without descending into units
    twice (each unit handles its own children)."""
    for child in el:
        tag = _tag(child)
        if tag in SKIP_TAGS:
            continue
        if tag in UNIT_TAGS:
            _emit_unit(child, depth, out)
        else:
            _emit_child_units(child, depth, out)

def _emit_table(el, out):
    for row in el.iter():
        if _tag(row) == "row":
            cells = [" ".join("".join(e.itertext()).split()) for e in row if _tag(e) == "entry"]
            out.append("| " + " | ".join(cells) + " |")

def _emit_prov(prov, out):
    label = _label_of(prov)
    heading_el = prov.find("heading")
    heading = " ".join("".join(heading_el.itertext()).split()) if heading_el is not None else ""
    out.append("")
    out.append(f"### {label} {heading}".rstrip())
    body = prov.find("prov.body")
    if body is None:
        body = prov
    before = len(out)
    for child in body:
        tag = _tag(child)
        if tag in SKIP_TAGS or tag in ("label", "heading"):
            continue
        if tag in UNIT_TAGS:
            _emit_unit(child, 0, out)
        elif tag == "table":
            _emit_table(child, out)
        else:
            text = _inline(child, UNIT_TAGS)
            if text:
                out.append(text)
            _emit_child_units(child, 0, out)
    if len(out) == before:
        # PCO empties a repealed/spent section to <prov.body/> with no heading
        # and supplies the "[Repealed]" gravestone in its renderer, not the XML.
        # Without this, the section renders as a bare number with nothing under
        # it; emit the tombstone so a repeal reads as a body replaced by a grave.
        out.append("[Repealed]")

def _walk(el, out, depth=1):
    for child in el:
        tag = _tag(child)
        if tag in SKIP_TAGS:
            continue
        if tag == "prov":
            _emit_prov(child, out)
        elif tag in HEAD_TAGS:
            label = _label_of(child)
            heading_el = child.find("heading")
            heading = " ".join("".join(heading_el.itertext()).split()) if heading_el is not None else ""
            out.append("")
            out.append(f"{'#' * min(depth + 1, 4)} {tag.title()} {label} — {heading}".rstrip(" —"))
            _walk(child, out, depth + 1)
        elif tag == "crosshead":
            text = " ".join("".join(child.itertext()).split())
            if text:
                out.append("")
                out.append(f"**{text}**")
        elif tag == "table":
            _emit_table(child, out)
        else:
            _walk(child, out, depth)

def render(xml_path):
    root = ET.parse(xml_path).getroot()
    title_el = root.find(".//cover/title")
    title = " ".join("".join(title_el.itertext()).split()) if title_el is not None else "Untitled"
    as_at = root.get("date.as.at", "")
    out = [f"# {title}", f"_Consolidation as at {as_at}_" if as_at else ""]
    cover = root.find("cover")
    for top in root:
        if top is cover or _tag(top) in SKIP_TAGS:
            continue
        _walk(top, out)
    # collapse runs of blank lines deterministically
    cleaned, prev_blank = [], False
    for line in out:
        blank = line == ""
        if not (blank and prev_blank):
            cleaned.append(line)
        prev_blank = blank
    return "\n".join(cleaned) + "\n"

if __name__ == "__main__":
    import sys

    print(render(sys.argv[1]))
