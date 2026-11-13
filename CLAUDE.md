# MarkOn website

Nyt website for MarkOn A/S (firmatøj, firmagaver og merchandise til erhverv, Lystrup og Ikast). Bygget af OUTHNK Agency. Kunden skrives altid **MarkOn** med stort O.

## Kilder
- `design/pages/` er det godkendte design fra Claude-canvas (desktop-filer, responsive). `design/README.md` forklarer filerne. Designet er facit for udseende og tekst; afvig kun, når en regel herunder siger noget andet.
- `design/images/` er billeder og logo brugt i designet.
- Beslutninger og noter ligger i Claude-projektet "MarkOn" (`claude/markon-noter.md`, `claude/website/drejebog.md`). Ændringer i beslutningerne skrives også her.

## Teknik
- Astro (statisk), ren HTML og CSS, så lidt JavaScript som muligt. Ingen CSS-frameworks; brug CSS-variabler for farver og afstande.
- Fælles komponenter: Topbar (telefon og mail), Header med logo og menu, Mega menu, Mobilmenu, Brødkrummer, Footer, Billedkort med pille, FAQ (details/summary), Proceslinje ("Hele vejen"), "Hvor vil du hen nu?", Kontaktformular.
- Indhold (tekster, FAQ, billeder pr. side) i content collections (Markdown/JSON), ikke hårdkodet i komponenterne, så det senere kan redigeres i et CMS.
- Ét `<h1>` pr. side. Semantisk HTML, `lang="da"`, alt-tekster, synligt fokus, knapper/links mindst 44 px.
- Billeder via Astros billedkomponent (moderne formater, korrekte størrelser, lazy loading under folden).
- `npm run build` skal gå igennem uden fejl før hver commit.
- Sideopbygning: hver side er en JSON-fil i `src/content/sider/` med `url`, `seo`, `breadcrumbs` og en liste af sektioner (`blocks`). Hver sektionstype har et skema i `src/content.config.ts` og en komponent i `src/components/blocks/`. Menu, kontakt og footer ligger i `src/content/site/site.json`.
- `scripts/convert-design.py` lavede sidernes JSON ud fra designfilerne (kræver Python med BeautifulSoup). Kør den kun igen, hvis designet ændres, og tjek forskellen bagefter: den overskriver sidernes JSON. Firmatøj, Inspiration og Tak er skrevet i hånden.
- Formularer (Kontakt og produktsiden) sendes via Netlify Forms og viser `/tak/` bagefter.
- Kontakt: ingen telefon og mail ved siden af formularen; de står i topbar og footer. Ingen løfter om svartid og ingen kvitteringsmail med rådgiverens navn (MarkOns ønske, godkendt af Casper 11. november 2026).
- Muleposerne i toppen af Merchandise skifter hårdt (`step-end`); tempoet sættes med `interval` (sek. pr. billede, nu 0.3) i `merchandise.json`.

## Design (besluttet)
- Font: Montserrat overalt. Overskrifter Light 300 med nøgleord i Bold 700. Menu Bold 700.
- Farver: baggrund #F7F1EA (alle sider, også topbar), kort/formularer/mobilmenu #FFFFFF, footer og billedpladser #F0E5D9, tynde linjer #EFE5DA, rød #9D5656, tekst #6B3A3A, støvet rosa prik #C29A93. Kundelogoerne på forsiden ("Vi hjælper blandt andre") er dæmpet mørkegrå: #6E6A67 med opacity 0,75 (kundeønske, godkendt af Casper 11. november 2026).
- Logoets røde #AB1A2E bruges kun i selve logoet. Ikke for meget rød.
- Kun to billedformer: kort med hjørne 24 px og cirkel. Ingen buer eller skåle.
- Den rosa prik ligger bag billederne i toppen og titter frem ved kanten, aldrig oven på. Den er falmet, ikke sløret: #C29A93 med 60 % dækning, ren kant og en blød skygge (kundeønske, 11. nov. 2026). Den store cirkel bag collagen på Forsiden er #F0E5D9, ikke hvid. Bløde rød-brune skygger under billederne i toppen.
- Ro på siderne: billeder i gitter har ens format 4:5 og står på linje. Overskrift og brødtekst i én venstrestillet kolonne (max ca. 720 px). Case-bånd: ét billede og én linje (kunde, resultat, "Se casen").
- Billeder flyver eller zoomer ikke. Undtagelse: toppen af Merchandise skifter hårdt (ingen toning) mellem fem muleposer på orange baggrund, ca. 0,3 sek. pr. billede (som på sugarcoat.com). Ved `prefers-reduced-motion` står det første billede stille.
- Proceslinjen: linjen tegnes, prikkerne popper op, trinene toner frem. Vandret på desktop/tablet, lodret på mobil. Respektér `prefers-reduced-motion`.
- Billeder, der leder videre: overskrift i lys pille på billedet; ved hover et rødligt lag med tekst og link; på touch står teksten under billedet.
- Mega menuen skal være let. Under 1100 px bliver menuen til en burger-knap.
- Dropdown i hovedmenuen (kundeønske, godkendt af Casper 12. november 2026): Merchandise og Firmagaver har en let dropdown med undersiderne (hvidt kort, hjørne 24, kun tekstlinks), der åbner ved hover, fokus eller klik på pilen og lukker med Escape. Undersiderne står i `children` (og linket nederst i `allLabel`) i `site.json`; tilføj kun sider, der findes. I mobilmenuen står undersiderne under punktet.
- Ingen "Book et møde" nogen steder. Knapper fører til formularen ("Få et tilbud", "Skriv til os") eller telefonen. "Kun salg til erhverv" vises ikke i topbar, footer eller på produktside.

## Sitemap
- Merchandise: Event merchandise (messer, kick off, firmafester), Onboarding og welcome kits, Employer branding, Re-branding, Special produktion, Den lille ekstra (arbejdstitel, navn afventer)
- Firmagaver: Julegaver (URL `/firmajulegaver/` bevares), Kundegaver, Sæsongaver, Barselsgaver, Jubilæumsgaver, Shopløsninger (placering usikker)
- Firmatøj: Profiltøj, Arbejdstøj, Sport og fritid, Jakker og overtøj, Accessories, Logo og broderi
- Inspiration (cases: Bech-Bruun, Systematic, Norlys Energy, Keepit), Om os (MarkOn og processen, Kataloger, Besøg vores showroom), Kontakt (formular og direkte kontakt)
- URL'er: små bogstaver, danske ord uden æøå (ae, oe, aa), bindestreger. Redirects fra det nuværende site laves efter Sigurds migreringsplan.
- Foreløbige URL'er (afstemmes med migreringsplanen): `/merchandise/`, `/merchandise/messer-og-events/`, `/merchandise/den-lille-ekstra/`, `/merchandise/krus-med-logo/`, `/firmagaver/`, `/firmajulegaver/`, `/firmagaver/kundegaver/`, `/firmagaver/saesongaver/`, `/firmagaver/barselsgaver/`, `/firmagaver/jubilaeumsgaver/`, `/firmatoej/`, `/inspiration/`, `/om-os/`, `/kontakt/`.
- Firmatøj og Inspiration er ikke tegnet endnu og vises som korte "på vej"-sider (besluttet af Casper).
- F-versionerne af Julegaver, Barselsgaver og Jubilæum bruges, ikke V-varianterne (besluttet af Casper).

## Tekst
- Tone: en dygtig, imødekommende og jordnær rådgiver. Du/I og vi/MarkOn. Bestil frem for køb, kan frem for skal. Ingen humor, emojis eller buzzwords.
- Korte afsnit (2-4 sætninger), FAQ på alle sider. Hver side må gerne have sin egen vinkel og opbygning (se `V-*`-filerne).
- Opfind aldrig tal, priser, cases eller citater. Pladsholdere som `[ANTAL]` og `[BILLEDE: ...]` bevares synligt, til MarkOn udfylder dem.

## Arbejdsgang
- Arbejd på en branch og lav pull requests. Push aldrig direkte til `main`, og merge ikke selv.
- Hver PR: hvad er ændret, hvilke sider, skærmbilleder på desktop (1440), tablet (834) og mobil (390), og hvad der mangler.
- Ændringer, der går imod reglerne her, kræver Caspers godkendelse først.
