/* Google Analytics 4 — loaded only when VITE_GA_ID is set (so dev and
   un-configured builds stay clean). Set it as a build-time env var, e.g. on
   Railway add a service variable VITE_GA_ID=G-XXXXXXXXXX. See .env.example.

   This is a client-side SPA: there are no real page loads, so automatic
   page_view is disabled and we send one per view change via trackView(). */

const GA_ID = import.meta.env.VITE_GA_ID;

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
  const path = view === 'landing' ? '/' : `/${view}`;
  window.gtag('event', 'page_view', {
    page_path: path,
    page_title: `Whiplash — ${view}`,
    page_location: location.origin + path,
  });
}
