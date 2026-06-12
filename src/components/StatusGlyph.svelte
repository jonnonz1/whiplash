<script>
  /* Shape carries status meaning — never colour alone. */
  let { g, size = 13, color = 'currentColor' } = $props();
  const sw = 1.7;
</script>

<svg
  width={size}
  height={size}
  viewBox="0 0 16 16"
  fill="none"
  aria-hidden="true"
  style="display:inline-block;flex:none"
>
  {#if g === 'cross'}
    <circle cx="8" cy="8" r="6.2" stroke={color} stroke-width={sw} />
    <path d="M5.6 5.6 L10.4 10.4 M10.4 5.6 L5.6 10.4" stroke={color} stroke-width={sw} stroke-linecap="round" />
  {:else if g === 'uturn'}
    <path d="M5 11 V7 a3 3 0 0 1 6 0 v1" stroke={color} stroke-width={sw} stroke-linecap="round" stroke-linejoin="round" />
    <path d="M9 6 l2 2 2-2" stroke={color} stroke-width={sw} stroke-linecap="round" stroke-linejoin="round" />
  {:else if g === 'half'}
    <circle cx="8" cy="8" r="6.2" stroke={color} stroke-width={sw} />
    <path d="M8 1.8 A6.2 6.2 0 0 1 8 14.2 Z" fill={color} />
  {:else if g === 'loop'}
    <path d="M12 8 a4 4 0 1 1 -1.4 -3" stroke={color} stroke-width={sw} stroke-linecap="round" />
    <path d="M12.2 2.4 l0.2 2.9 l-2.9 -0.4" stroke={color} stroke-width={sw} stroke-linecap="round" stroke-linejoin="round" />
  {:else if g === 'zombie'}
    <circle cx="8" cy="8" r="6.2" stroke={color} stroke-width={sw} stroke-dasharray="2.4 2" />
    <circle cx="8" cy="8" r="2.4" fill={color} />
  {/if}
</svg>
