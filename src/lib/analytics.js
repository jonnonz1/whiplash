/* Google Analytics 4. The production property ID is baked in as the default
   so prod builds report out of the box; VITE_GA_ID overrides it (e.g. a
   different property), and dev builds stay clean unless VITE_GA_ID is set.
   A GA4 measurement ID is public — it ships in the client bundle regardless.

   This is a client-side SPA: there are no real page loads, so automatic
   page_view is disabled and we send one per view change via trackView(). */

const GA_PROD_ID = 'G-3RNHN0YX3X';
const GA_ID = import.meta.env.VITE_GA_ID || (import.meta.env.PROD ? GA_PROD_ID : '');

export function initAnalytics() {
  if (!GA_ID || typeof window === 'undefined') return;

  const s = document.createElement('script');
  s.async = true;
  s.src = `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`;
  document.head.appendChild(s);

  window.dataLayer = window.dataLayer || [];
  window.gtag = function gtag() {
    window.dataLayer.push(arguments);
  };
  window.gtag('js', new Date());
  window.gtag('config', GA_ID, { send_page_view: false });
}

export function trackView(view) {
  if (!GA_ID || typeof window === 'undefined' || !window.gtag) return;
  const path = view === 'explore' ? '/' : `/${view}`;
  window.gtag('event', 'page_view', {
    page_path: path,
    page_title: `Whiplash — ${view}`,
    page_location: location.origin + path,
  });
}
