<script>
  import { STATUS } from '../lib/status.js';
  import StatusGlyph from './StatusGlyph.svelte';

  let { status, sub = '' } = $props();
  const st = $derived(STATUS[status] || STATUS.underway);
</script>

<span class="wl-status" style="color:{st.color}" title={st.blurb}>
  <StatusGlyph g={st.glyph} size={12} />
  {st.label}{#if sub}<span style="opacity:0.6;font-weight:400">· {sub}</span>{/if}
</span>
