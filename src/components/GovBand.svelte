<script>
  /* Party colours appear ONLY here: factual, muted government bands. */
  import { db } from '../lib/data.svelte.js';
  import { TIMELINE } from '../lib/state.svelte.js';
  import { dateToFrac, clamp } from '../lib/format.js';

  let { height = 4 } = $props();

  const segs = $derived(
    db.governments
      .map((g) => {
        const s = clamp(dateToFrac(g.start), TIMELINE.from, TIMELINE.to);
        const e = clamp(g.end ? dateToFrac(g.end) : TIMELINE.to, TIMELINE.from, TIMELINE.to);
        return { g, flex: e - s };
      })
      .filter((x) => x.flex > 0)
  );
</script>

<div class="gov-band" style="height:{height}px" role="img" aria-label="Governments in power, 2008 to today">
  {#each segs as { g, flex } (g.id)}
    <div class="seg {g.party}" style="flex:{flex}" title="{g.label} · {g.start.slice(0, 4)}–{g.end ? g.end.slice(0, 4) : 'now'}"></div>
  {/each}
</div>
