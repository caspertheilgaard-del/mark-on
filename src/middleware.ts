import { defineMiddleware } from 'astro:middleware';

/*
 * Midlertidig markering af pladsholdere (ønske oe-20261123072150-vhsm, godkendt af Emma 23. nov. 2026).
 * Al synlig tekst i firkantede klammer med stort begyndelsesbogstav, fx [ANTAL], [MANGLER: ...],
 * [BILLEDE: ...] og [KUNDECITAT ...], pakkes ind i <mark class="mangler"> og vises skriggrøn,
 * så det er let at se, hvad der mangler. Attributter (alt, aria-label, meta) røres ikke.
 * Slå fra: sæt MARKER_MANGLER til false (eller slet filen og .mangler i global.css).
 */
const MARKER_MANGLER = true;

const PLADSHOLDER = /\[[A-ZÆØÅ][^\[\]<>]{0,300}\]/g;
const HAR_PLADSHOLDER = /\[[A-ZÆØÅ][^\[\]<>]{0,300}\]/;
const SPRING_OVER = /(<(script|style|textarea|title)\b[\s\S]*?<\/\2>)/gi;

function marker(html: string): string {
  const start = html.search(/<body\b/i);
  if (start < 0) return html;
  const head = html.slice(0, start);
  const body = html
    .slice(start)
    .split(SPRING_OVER)
    .map((del, i) => {
      // split med to grupper giver: tekst, hele blokken, tagnavn, tekst, ...
      if (i % 3 === 1) return del;
      if (i % 3 === 2) return '';
      // Kun tekst mellem tags (efter '>' og før '<'), aldrig inde i et tag.
      return del.replace(/(^|>)([^<>]+)(?=<|$)/g, (m, før: string, tekst: string) =>
        HAR_PLADSHOLDER.test(tekst)
          ? før + tekst.replace(PLADSHOLDER, (p) => `<mark class="mangler">${p}</mark>`)
          : m,
      );
    })
    .join('');
  return head + body;
}

export const onRequest = defineMiddleware(async (_ctx, next) => {
  const res = await next();
  if (!MARKER_MANGLER || !(res.headers.get('content-type') ?? '').includes('text/html')) return res;
  const html = await res.text();
  return new Response(marker(html), { status: res.status, statusText: res.statusText, headers: res.headers });
});
