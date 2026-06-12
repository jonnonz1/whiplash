/* Status system — shape always carries meaning alongside colour. */

export const STATUS = {
  cancelled: {
    label: 'Cancelled',
    color: 'var(--st-cancelled)',
    hex: '#d4a853',
    glyph: 'cross',
    blurb: 'Killed outright. Money already spent is gone.',
  },
  reversed: {
    label: 'Reversed',
    color: 'var(--st-reversed)',
    hex: '#e0894f',
    glyph: 'uturn',
    blurb: 'Policy flipped back or undone by a later government.',
  },
  rescoped: {
    label: 'Rescoped',
    color: 'var(--st-rescoped)',
    hex: '#c98a3a',
    glyph: 'half',
    blurb: 'Repeatedly redrawn — smaller, later, or somewhere else.',
  },
  restored: {
    label: 'Restored',
    color: 'var(--st-restored)',
    hex: '#7eb8a8',
    glyph: 'loop',
    blurb: 'Banned or scrapped, then brought back.',
  },
  zombie: {
    label: 'Zombie',
    color: 'var(--st-zombie)',
    hex: '#b07cc6',
    glyph: 'zombie',
    blurb: 'Repealed or cancelled, then revived in near-identical form.',
  },
  underway: {
    label: 'Under way',
    color: 'var(--st-underway)',
    hex: '#647a8e',
    glyph: 'half',
    blurb: 'Not yet reversed at this point on the timeline.',
  },
};

export const STATUS_KEYS = ['cancelled', 'reversed', 'rescoped', 'restored', 'zombie'];

export const SECTORS = {
  transport: 'Transport',
  water: 'Water',
  environment: 'Environment / RMA',
  health: 'Health',
  education: 'Education',
  energy: 'Energy',
  tax: 'Tax',
  economy: 'Economy',
  justice: 'Justice / Work',
};
