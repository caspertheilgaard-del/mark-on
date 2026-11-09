# Designfiler fra Claude-canvas

Eksporteret 9. november 2026 fra artifactet "MarkOn website". Kun desktop-filerne er med; tablet- og mobilvisningerne i canvas var de samme filer vist i 834 og 390 px bredde, så siderne er responsive i sig selv (se `@media`-reglerne i hver fil).

| Fil | Side |
| --- | --- |
| S-Forside | Forside |
| S-Merchandise | Merchandise (områdeside) |
| S-Messer | Messer og events |
| S-Produkt | Produktside (eksempel: krus med logo) |
| S-Kontakt | Kontakt: Få et tilbud |
| S-OmOs | Om os |
| S-LilleEkstra | Den lille ekstra (navn mangler) |
| F-Forside | Firmagaver (områdeside) |
| F-Julegaver, F-Kundegaver, F-Saesongaver, F-Barselsgaver, F-Jubilaeum | Firmagavesiderne |
| V-Julegaver, V-Barselsgaver, V-Jubilaeum | Ny tekststruktur (Carlas varianter med hver sin vinkel; endnu ikke valgt i stedet for F-versionerne) |

Om filformatet:
- `<x-dc>`, `<helmet>` og `support.js` hører til canvas-værktøjet. Indholdet i `<helmet>` er sidens `<head>` (font og CSS); resten er markup.
- `<sc-if value="{{ menu }}">` og scriptet `text/x-dc` styrer kun mobilmenuen (åben/lukket). Erstat med en lille knap-toggle.
- Links som `S-Merchandise.dc.html` peger på de andre designfiler; `#` betyder siden ikke er tegnet endnu.
- Billeder ligger i `../images/` med deres id fra canvas. Logo: `65329b41fce4aac70a33a76ab86b8ff5.png`.
- Inline-styles er designets værdier; flyt dem til komponenter og CSS-variabler.
