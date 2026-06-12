<script>
  /* Seismograph spike that curls into a U-turn — Direction A logo mark. */
  let { size = 22 } = $props();
</script>

<svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true" style="flex:none">
  <path
    d="M1 13 H6 l1.6 -7 2.4 12 1.8 -5 H15"
    stroke="var(--signal)"
    stroke-width="1.8"
    stroke-linecap="round"
    stroke-linejoin="round"
  />
  <path d="M15 13 a4 4 0 1 0 -4 4" stroke="var(--ink-2)" stroke-width="1.8" stroke-linecap="round" />
  <path
    d="M11 17 l-2.4 -0.4 0.6 2.6"
    stroke="var(--ink-2)"
    stroke-width="1.8"
    stroke-linecap="round"
    stroke-linejoin="round"
  />
</svg>
