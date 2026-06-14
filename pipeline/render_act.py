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
    """Render a PCO table as GitHub-flavoured markdown. Markdown needs a header
    separator row to render at all; this also honours the column model so
    colspanned cells (namest/nameend — 57% of tables) stay under the right
    headers, drops the all-empty layout "spacer" columns and rows PCO inserts,
    skips the generic "Column 1/2/3" label row, and escapes pipes."""
    # column order from <colspec colname=...>; entries address columns by name
    colnames = [c.get("colname") for c in el.iter() if _tag(c) == "colspec"]
    col_idx = {n: i for i, n in enumerate(colnames) if n}

    grid = []
    for row in el.iter():
        if _tag(row) != "row":
            continue
        cells, cursor = [""] * len(colnames), 0
        for e in row:
            if _tag(e) != "entry":
                continue
            txt = " ".join("".join(e.itertext()).split()).replace("|", "\\|")
            i = col_idx.get(e.get("namest") or e.get("colname"), cursor)
            if i >= len(cells):
                cells.extend([""] * (i - len(cells) + 1))
            cells[i] = txt
            end = col_idx.get(e.get("nameend"), i)  # span: leave covered cols empty
            cursor = max(i, end) + 1
        grid.append(cells)
    if not grid:
        return
    width = max(len(r) for r in grid)
    grid = [r + [""] * (width - len(r)) for r in grid]
    keep = [c for c in range(width) if any(r[c] for r in grid)]  # drop spacer cols
    grid = [[r[c] for c in keep] for r in grid]

    def noise(r):
        filled = [c for c in r if c]
        return not filled or all(c.startswith("Column ") and c[7:].isdigit() for c in filled)

    grid = [r for r in grid if not noise(r)]  # drop spacer + "Column N" rows
    if not grid:
        return
    out.append("")
    out.append("| " + " | ".join(grid[0]) + " |")
    out.append("| " + " | ".join(["---"] * len(grid[0])) + " |")
    for r in grid[1:]:
        out.append("| " + " | ".join(r) + " |")

def _emit_body(container, out):
    """Emit a provision/preamble body's children as markdown lines; returns the
    number of lines added (0 ⇒ the caller may want a tombstone)."""
    before = len(out)
    for child in container:
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
    return len(out) - before

def _emit_prov(prov, out):
    label = _label_of(prov)
    heading_el = prov.find("heading")
    heading = " ".join("".join(heading_el.itertext()).split()) if heading_el is not None else ""
    out.append("")
    out.append(f"### {label} {heading}".rstrip())
    body = prov.find("prov.body")
    if body is None:
        body = prov
    if _emit_body(body, out) == 0:
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

def _emit_front(front, out):
    """Front matter that isn't furniture: the long title (the act's stated
    purpose) and the preamble (recitals). PCO keeps both in <front>, which the
    body walk would otherwise skip — losing unique, substantive content."""
    lt = front.find("long-title")
    if lt is not None:
        text = _inline(lt, set())
        if text:
            out.append("")
            out.append(f"> {text}")
    pre = front.find("preamble")
    if pre is not None:
        out.append("")
        out.append("## Preamble")
        for block in pre:
            if _tag(block) == "heading" or _tag(block) in SKIP_TAGS:
                continue
            _emit_body(block, out)

def render(xml_path):
    root = ET.parse(xml_path).getroot()
    title_el = root.find(".//cover/title")
    title = " ".join("".join(title_el.itertext()).split()) if title_el is not None else "Untitled"
    as_at = root.get("date.as.at", "")
    out = [f"# {title}", f"_Consolidation as at {as_at}_" if as_at else ""]
    cover = root.find("cover")
    front = root.find("front")
    if front is not None:
        _emit_front(front, out)
    for top in root:
        if top is cover or top is front or _tag(top) in SKIP_TAGS:
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
