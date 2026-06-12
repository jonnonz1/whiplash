#!/usr/bin/env python3
"""Resumable mirror of the NZ legislation bulk XML directory.

Walks the classic.legislation.govt.nz/subscribe/ HTML directory listings and
downloads every .xml file, preserving the URL path on disk. Safe to stop and
re-run: completed files are skipped, so it can resume on another machine given
the partial mirror (interrupted writes use .part temp files and are redone).

Requirements discovered during live verification (2026-06-10):
- A browser User-Agent is mandatory (plain curl/wget UAs get Azure WAF 403).
- The WAF can also serve a JS-challenge page as HTTP 200 — every payload is
  validated as XML before being written, and challenge pages trigger backoff.
- Directory links in the listings have NO trailing slash (and trailing-slash
  URLs are served the wrong page) — directories are requested slash-less.
- Stay under 2,000 requests / 5 min / IP (0.7s gap ≈ 430 req / 5 min).
- XML only; PDFs roughly double the volume for no analytical value.

Usage:
    python3 mirror-legislation.py OUTPUT_DIR [--base URL] [--subtree act/public regulation/public]
    python3 mirror-legislation.py ~/workspace/whiplash/data-raw/legislation
"""

import argparse
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
DEFAULT_BASE = "https://classic.legislation.govt.nz/subscribe/"
DEFAULT_SUBTREES = ["act/public", "regulation/public"]
REQUEST_GAP = 0.7  # seconds between requests (override with --gap)
MAX_RETRIES = 5
# version directories ("1.0", "21.0") are the only dotted names that are dirs;
# any other dotted last segment is a file (pdf/svg/gif/...) and skipped
VERSION_DIR = re.compile(r"^\d+(\.\d+)?$")
SKIP_DIR_NAMES = {"images"}  # asset folders, never contain XML


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    self.hrefs.append(value)


def looks_like_html(data):
    head = data[:512].lstrip().lower()
    return head.startswith(b"<!doctype html") or head.startswith(b"<html") or b"<html" in head


def is_xml_payload(data):
    head = data[:512].lstrip()
    if not head.startswith(b"<"):
        return False
    return not looks_like_html(data)


def fetch(url):
    """GET with browser UA, retry/backoff on WAF and transient errors."""
    for attempt in range(1, MAX_RETRIES + 1):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code in (403, 429, 500, 502, 503, 504) and attempt < MAX_RETRIES:
                wait = min(300, 15 * (2 ** (attempt - 1)))
                print(f"  HTTP {e.code} on {url} — backing off {wait}s (attempt {attempt})", flush=True)
                time.sleep(wait)
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < MAX_RETRIES:
                wait = min(300, 15 * (2 ** (attempt - 1)))
                print(f"  {e} on {url} — retrying in {wait}s (attempt {attempt})", flush=True)
                time.sleep(wait)
                continue
            raise


def fetch_xml(url):
    """Fetch a document that must be XML; challenge pages count as retryable."""
    for attempt in range(1, 4):
        data = fetch(url)
        if is_xml_payload(data):
            return data
        wait = 30 * attempt
        print(f"  non-XML payload (WAF challenge?) for {url} — waiting {wait}s", flush=True)
        time.sleep(wait)
    raise RuntimeError(f"persistent non-XML payload for {url}")


def child_links(page_url, html_bytes):
    """(directories, xml_files) strictly below page_url, slash-normalised."""
    parser = LinkParser()
    parser.feed(html_bytes.decode("utf-8", errors="replace"))
    page = urllib.parse.urlparse(page_url)
    base_path = page.path.rstrip("/")
    dirs, files = set(), set()
    for href in parser.hrefs:
        absolute = urllib.parse.urljoin(page_url.rstrip("/") + "/", href)
        absolute = absolute.split("?", 1)[0].split("#", 1)[0]
        parsed = urllib.parse.urlparse(absolute)
        if parsed.netloc != page.netloc:
            continue
        path = parsed.path.rstrip("/")
        if not path.startswith(base_path + "/"):
            continue  # parent links, sort toggles, off-tree links
        clean = f"{parsed.scheme}://{parsed.netloc}{path}"
        last = path.rsplit("/", 1)[-1].lower()
        if last.endswith(".xml"):
            files.add(clean)
        elif "." not in last and last not in SKIP_DIR_NAMES:
            dirs.add(clean)
        elif VERSION_DIR.match(last):
            dirs.add(clean)
        # anything else: non-XML file or asset folder — skip
    return sorted(dirs), sorted(files)


def main():
    global REQUEST_GAP
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("output", help="directory to mirror into")
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--subtree", nargs="*", default=DEFAULT_SUBTREES,
                    help="subtrees under base to mirror (default: act/public regulation/public)")
    ap.add_argument("--gap", type=float, default=REQUEST_GAP,
                    help="seconds between requests per worker (default %(default)s)")
    ap.add_argument("--workers", type=int, default=1,
                    help="parallel file downloads (keep total req rate well under 2000/5min)")
    args = ap.parse_args()
    REQUEST_GAP = args.gap

    base = args.base if args.base.endswith("/") else args.base + "/"
    base_path = urllib.parse.urlparse(base).path
    out_root = Path(args.output).expanduser()
    out_root.mkdir(parents=True, exist_ok=True)

    queue = [urllib.parse.urljoin(base, s.strip("/")) for s in args.subtree] or [base.rstrip("/")]
    seen_dirs, downloaded, skipped, errors = set(), 0, 0, 0
    started = time.time()

    while queue:
        dir_url = queue.pop()
        if dir_url in seen_dirs:
            continue
        seen_dirs.add(dir_url)
        try:
            html = fetch(dir_url)
        except Exception as e:
            errors += 1
            print(f"DIR FAIL {dir_url}: {e}", flush=True)
            continue
        time.sleep(REQUEST_GAP)
        dirs, files = child_links(dir_url, html)
        if not dirs and not files and looks_like_html(html) is False:
            print(f"  empty/odd listing at {dir_url} (no children found)", flush=True)
        queue.extend(d for d in dirs if d not in seen_dirs)

        lock = threading.Lock()

        def grab(file_url):
            nonlocal downloaded, skipped, errors
            rel = urllib.parse.urlparse(file_url).path
            rel = rel[len(base_path):] if rel.startswith(base_path) else rel.lstrip("/")
            dest = out_root / rel
            if dest.exists() and dest.stat().st_size > 0:
                with lock:
                    skipped += 1
                return
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                data = fetch_xml(file_url)
            except Exception as e:
                with lock:
                    errors += 1
                print(f"FILE FAIL {file_url}: {e}", flush=True)
                return
            tmp = Path(str(dest) + ".part")
            tmp.write_bytes(data)
            tmp.rename(dest)
            time.sleep(REQUEST_GAP)
            with lock:
                downloaded += 1
                if downloaded % 100 == 0:
                    rate = downloaded / max(1.0, time.time() - started)
                    print(f"{downloaded} downloaded, {skipped} skipped, {errors} errors, "
                          f"{len(queue)} dirs queued, {rate:.2f} files/s", flush=True)

        if args.workers > 1 and files:
            with ThreadPoolExecutor(max_workers=args.workers) as ex:
                list(ex.map(grab, files))
        else:
            for file_url in files:
                grab(file_url)

    elapsed = time.time() - started
    print(f"DONE: {downloaded} downloaded, {skipped} already present, {errors} errors, "
          f"{len(seen_dirs)} directories walked, {elapsed:.0f}s", flush=True)
    if errors or (downloaded == 0 and skipped == 0):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
