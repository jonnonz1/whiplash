/* Links out to where a law's change history actually lives. nz-statute-book is
   a git mirror of the statute book, so an act's commit history *is* its diff
   trail; regulations and any act missing from the repo fall back to
   legislation.govt.nz. Shared by the Explore drill-down and the Top-change view. */

export const STATUTE_BOOK_REPO = 'https://github.com/jonnonz1/nz-statute-book';

export function slug(title) {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

export function linkFor(a) {
  if (STATUTE_BOOK_REPO && a.type === 'act')
    return `${STATUTE_BOOK_REPO}/commits/main/acts/public/${a.year}/${slug(a.title)}.md`;
  // legislation.govt.nz builds the page from year/number in the path (the DLM is
  // only an anchor), so all three are required — the bare /public/latest/<DLM>
  // form 404s.
  return `https://www.legislation.govt.nz/${a.type}/public/${a.year}/${a.number}/latest/${a.id}.html`;
}

export function linkLabel(a) {
  if (STATUTE_BOOK_REPO && a.type === 'act') return 'git history ↗';
  return 'legislation.govt.nz ↗';
}
