/* App state, shareable via URL params:
   ?view=map|churn|method &t=YYYY-MM &govt= &sector= &status= &min= &p= &act= */

import { dateToFrac, fracToDate, nowFrac, clamp, TIMELINE_FROM } from './format.js';

export const ui = $state({
  view: 'map',
  t: nowFrac(), // fractional year on the scrubber
  govt: '',
  sector: '',
  status: '',
  minCost: 0,
  selected: null, // project id
  selectedAct: null, // act id
  introDismissed: false,
});

export const TIMELINE = { from: TIMELINE_FROM, to: nowFrac() };

const VIEWS = ['map', 'churn', 'method'];

export function initFromURL() {
  const q = new URLSearchParams(location.search);
  const view = q.get('view');
  if (VIEWS.includes(view)) ui.view = view;
  const t = q.get('t');
  if (t && /^\d{4}-\d{2}$/.test(t)) {
    const [y, m] = t.split('-').map(Number);
    ui.t = clamp(dateToFrac(`${y}-${String(m).padStart(2, '0')}-15`), TIMELINE.from, TIMELINE.to);
  }
  ui.govt = q.get('govt') || '';
  ui.sector = q.get('sector') || '';
  ui.status = q.get('status') || '';
  ui.minCost = Number(q.get('min')) || 0;
  ui.selected = q.get('p') || null;
  ui.selectedAct = q.get('act') || null;
}

export function urlQuery() {
  const q = new URLSearchParams();
  if (ui.view !== 'map') q.set('view', ui.view);
  if (TIMELINE.to - ui.t > 1 / 24) {
    const d = fracToDate(ui.t);
    q.set('t', `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}`);
  }
  if (ui.govt) q.set('govt', ui.govt);
  if (ui.sector) q.set('sector', ui.sector);
  if (ui.status) q.set('status', ui.status);
  if (ui.minCost) q.set('min', String(ui.minCost));
  if (ui.selected) q.set('p', ui.selected);
  if (ui.selectedAct) q.set('act', ui.selectedAct);
  const s = q.toString();
  return s ? '?' + s : location.pathname;
}
