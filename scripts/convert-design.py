"""
Engangskonvertering: trækker tekster, links og billeder ud af designfilerne i design/pages
og skriver dem som content collection-filer i src/content/sider/. Teksterne kopieres ordret,
så der ikke opstår tastefejl. Kør: python3 scripts/convert-design.py
"""
import json, re, pathlib
from bs4 import BeautifulSoup, NavigableString

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ROOT / 'design' / 'pages'
OUT = ROOT / 'src' / 'content' / 'sider'

URLS = {
    'S-Forside.dc.html': '/',
    'S-Merchandise.dc.html': '/merchandise/',
    'S-Messer.dc.html': '/merchandise/messer-og-events/',
    'S-LilleEkstra.dc.html': '/merchandise/den-lille-ekstra/',
    'S-Produkt.dc.html': '/merchandise/krus-med-logo/',
    'S-Kontakt.dc.html': '/kontakt/',
    'S-OmOs.dc.html': '/om-os/',
    'F-Forside.dc.html': '/firmagaver/',
    'F-Julegaver.dc.html': '/firmajulegaver/',
    'F-Kundegaver.dc.html': '/firmagaver/kundegaver/',
    'F-Saesongaver.dc.html': '/firmagaver/saesongaver/',
    'F-Barselsgaver.dc.html': '/firmagaver/barselsgaver/',
    'F-Jubilaeum.dc.html': '/firmagaver/jubilaeumsgaver/',
}

def url(href):
    if href is None:
        return '#'
    if href.startswith(('tel:', 'mailto:', '#', 'http')):
        return href
    return URLS.get(href, href)

def txt(el):
    """Tekst med <b> som **fed**, mellemrum samlet."""
    out = ''
    for c in el.children:
        if isinstance(c, NavigableString):
            out += str(c)
        elif c.name == 'b':
            out += '**' + c.get_text() + '**'
        elif c.name == 'br':
            out += '\n'
        elif c.get('aria-hidden') == 'true' or 'arr' in (c.get('class') or []):
            continue
        else:
            out += txt(c)
    out = re.sub(r'[ \t\r\f\v]+', ' ', out)
    out = re.sub(r' *\n *', '\n', out).strip()
    out = out.replace('** **', ' ').replace('****', '')
    return out

def plain(el):
    return txt(el).replace('**', '')

def img(el, **extra):
    """<img> eller pladsholder-div -> media."""
    if el.name == 'img':
        src = el['src'].replace('../images/', '../../assets/images/')
        m = {'src': src, 'alt': el.get('alt', '')}
        st = el.get('style', '')
        pos = re.search(r'object-position: ([^;]+)', st)
        if pos:
            m['position'] = pos.group(1).strip()
    else:
        label = el.get_text(strip=True)
        m = {'alt': el.get('aria-label') or label, 'placeholder': label}
        if '#ffffff' in el.get('style', ''):
            m['background'] = 'white'
    m.update(extra)
    return m

def link(a):
    return {'label': plain(a), 'href': url(a.get('href'))}

def paras(container, recursive=False):
    return [txt(p) for p in container.find_all('p', recursive=recursive) if p.get_text(strip=True)]

def is_cta(a):
    return 'background: #9d5656' in (a.get('style') or '')

# ---------- fælles sektioner ----------

def crumbs(soup):
    nav = soup.find('nav', attrs={'aria-label': 'Brødkrummer'})
    if not nav:
        return None
    out = []
    for el in nav.find_all(['a', 'span']):
        if el.name == 'a':
            out.append({'label': plain(el), 'href': url(el['href'])})
        elif el.get('aria-current'):
            out.append({'label': plain(el)})
    return out

def faq(sec):
    items = []
    for d in sec.find_all('details'):
        items.append({'question': plain(d.find('h3')), 'answer': [txt(p) for p in d.find_all('p')]})
    h2 = sec.find('h2')
    block = {'type': 'faq', 'heading': txt(h2), 'items': items}
    split_layout = 'flex: 1 1 340px' in (h2.parent.get('style') or '')
    pt = re.search(r'padding: (\d+)px', sec.get('style', ''))
    if pt and int(pt.group(1)) != (136 if split_layout else 128):
        block['spaceAbove'] = int(pt.group(1))
    left = h2.parent
    if 'flex: 1 1 340px' in (left.get('style') or ''):
        block['variant'] = 'split'
        p = left.find('p')
        if p:
            block['intro'] = txt(p)
        a = left.find('a')
        if a:
            if 'border: 2px' in (a.get('style') or ''):
                block['cta'] = link(a)
            else:
                block['link'] = link(a)
    else:
        a = sec.find('a', class_='go')
        if a:
            block['link'] = link(a)
    return block

def next_block(sec):
    kicker = plain(sec.find('p'))
    items = []
    for a in sec.find_all('a', recursive=True):
        spans = a.find_all('span', recursive=False)
        items.append({'title': plain(spans[0]), 'text': plain(spans[1]), 'href': url(a['href']),
                      **({'primary': True} if 'background: #9d5656' in a.get('style', '') else {})})
    large = 'border-radius: 40px' in sec.find('a').get('style', '')
    return {'type': 'next', **({'variant': 'large'} if large else {}), 'kicker': kicker, 'items': items}

def hero_standard(sec, variant='standard'):
    text = sec.find('h1').parent
    block = {'type': 'hero', 'variant': variant}
    eb = text.find('p', recursive=False)
    if eb and 'letter-spacing: 3px' in eb.get('style', ''):
        block['eyebrow'] = plain(eb)
    block['heading'] = txt(sec.find('h1')).strip()
    block['body'] = [txt(p) for p in text.find_all('p', recursive=False) if 'letter-spacing: 3px' not in p.get('style', '')]
    block['ctas'] = [link(a) for a in text.find_all('a') if is_cta(a)]
    return block

def cards_section(sec):
    intro = sec.find('h2').parent
    block = {'type': 'cards', 'heading': txt(sec.find('h2')), 'body': paras(intro)}
    cards = sec.find(class_='cards')
    if cards:
        block['cards'] = []
        for c in cards.find_all('div', recursive=False):
            card = {'heading': plain(c.find('h3')), 'body': [txt(p) for p in c.find_all('p', recursive=False) if not p.find('a')]}
            a = c.find('a')
            if a:
                card['link'] = link(a)
            block['cards'].append(card)
    cats = sec.find(class_='cats')
    if cats:
        block['gallery'] = [img(el) for el in cats.find_all(recursive=False)]
    return block

def tiles_section(sec):
    intro = sec.find('h2').parent
    block = {'type': 'tiles', 'heading': txt(sec.find('h2')), 'body': paras(intro), 'tiles': []}
    for lt in sec.find(class_='cats').find_all(class_='lt', recursive=False):
        t = {'title': plain(lt.find(class_='ttl'))}
        swap = lt.find(class_='swap4')
        if swap:
            t['swap'] = {'alt': swap['aria-label'], 'images': [i['src'].replace('../images/', '../../assets/images/') for i in swap.find_all('img')]}
        else:
            pic = lt.find(class_='pic')
            t['image'] = img(pic.find(['img', 'div']))
        ov = lt.find(class_='ov')
        if ov:
            parts = ov.find_all(['p', 'span', 'a'], recursive=False)
            t['text'] = plain(parts[0])
            t['linkLabel'] = plain(parts[1]).rstrip(' →')
            t['href'] = url(lt.get('href') or lt.find('a', class_='cover')['href'])
        block['tiles'].append(t)
    return block

def band(sec, variant='standard'):
    inner = sec.find('div')
    h2 = inner.find('h2')
    block = {'type': 'band', 'variant': variant, 'heading': txt(h2)}
    intro = h2.parent
    if intro is inner:  # S-stil: h2 og p direkte i containeren
        block['body'] = [txt(h2.find_next_sibling('p'))]
    else:
        ps = intro.find_all('p', recursive=False)
        block['body'] = [txt(p) for p in ps if 'font-weight: 600' not in p.get('style', '')]
        lead = [p for p in ps if 'font-weight: 600' in p.get('style', '')]
        if lead:
            block['lead'] = plain(lead[0])
    lead = inner.find('p', recursive=False)
    if lead and 'font-weight: 600' in lead.get('style', '') and 'lead' not in block:
        block['lead'] = plain(lead)
    steps = inner.find(class_='steps')
    if steps:
        block['steps'] = []
        for li in steps.find_all(recursive=False):
            ps = li.find_all('p')
            st = {}
            if len(ps) == 3:
                st['kicker'] = plain(ps[0]); ps = ps[1:]
            st.update({'title': plain(ps[0]), 'text': plain(ps[1])})
            block['steps'].append(st)
        after = steps.find_next_sibling('div')
        if after:
            block['after'] = [txt(p) for p in after.find_all('p', recursive=False) if not p.find('a')]
            block['links'] = [link(a) for a in after.find_all('a', class_='go')]
            cta = [a for a in after.find_all('a') if is_cta(a)]
            if cta:
                block['cta'] = link(cta[0])
        nxt = steps.find_next_sibling('a')
        if nxt:
            block['link'] = link(nxt)
    else:
        cta = [a for a in inner.find_all('a') if is_cta(a)]
        if cta:
            block['cta'] = link(cta[0])
        block['links'] = [link(a) for a in inner.find_all('a', class_='go')]
    return block

def sections(soup):
    main = soup.find('x-dc')
    return [s for s in main.find_all('section') if s.find_parent('section') is None]

# ---------- sider ----------

def page_f(name, soup, title, description):
    secs = sections(soup)
    blocks = []
    for s in secs:
        if s.find('h1'):
            b = hero_standard(s)
            media = s.find('h1').parent.find_next_sibling('div')
            swap = media.find(class_='swap')
            if swap:
                bg = re.search(r'background: (#[0-9a-f]+)', swap['style']).group(1)
                b['media'] = {'kind': 'swap', 'alt': swap['aria-label'], 'background': bg,
                              'images': [i['src'].replace('../images/', '../../assets/images/') for i in swap.find_all('img')]}
            elif media.find(class_='dot'):
                items = []
                for el in media.find_all('img'):
                    wrap = el.parent if el.parent is not media else el
                    st = wrap.get('style', '') + el.get('style', '')
                    circle = 'border-radius: 50%' in el.get('style', '')
                    mb = re.search(r'margin-bottom: (\d+)px', el.get('style', ''))
                    grow = re.search(r'flex: ([\d.]+)', wrap.get('style', '') if wrap is not el else el.get('style', ''))
                    items.append({'image': img(el), 'shape': 'circle' if circle else 'tall', 'grow': float(grow.group(1)) if grow else 1,
                                  'offsetBottom': int(mb.group(1)) if mb else 0, 'dot': bool(wrap.find(class_='dot')) if wrap is not el else False,
                                  'shadow': 'box-shadow' in el.get('style', '')})
                mw = re.search(r'max-width: (\d+)px', media.get('style', ''))
                b['media'] = {'kind': 'pair', 'align': 'end', **({'maxWidth': int(mw.group(1))} if mw else {}), 'items': items}
            else:
                el = media.find(['img']) or media.find('div', attrs={'role': 'img'})
                b['media'] = {'kind': 'image', 'image': img(el)}
            blocks.append(b)
        elif s.get('aria-label') == 'Inspiration':
            a = s.find('a')
            spans = a.find('span').find_all('span', recursive=False)
            blocks.append({'type': 'case', 'variant': 'strip', 'kicker': plain(s.find('p')), 'title': plain(spans[0]),
                           'href': url(a['href']), 'linkLabel': plain(spans[1]), 'image': img(a.find('img'))})
        elif s.get('aria-label') == 'Videre herfra':
            blocks.append(next_block(s))
        elif s.find('details'):
            blocks.append(faq(s))
        elif 'border-top: 1px solid #efe5da' in s.get('style', ''):
            blocks.append(band(s))
        elif s.find(class_='lt') and s.find(class_='cats'):
            blocks.append(tiles_section(s))
        else:
            blocks.append(cards_section(s))
    return blocks

def write(fname, slug, data):
    (OUT / f'{slug}.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print('skrev', slug)

def soup_of(f):
    return BeautifulSoup((PAGES / f).read_text(), 'html.parser')

SEO = {
    'F-Forside.dc.html': ('firmagaver', 'Firmagaver til medarbejdere og kunder | MarkOn', 'Firmagaver til jul, jubilæer, barsel og kunder. MarkOn hjælper med gavevalg, indpakning, personlig hilsen og levering.'),
    'F-Julegaver.dc.html': ('firmajulegaver', 'Firmajulegaver til medarbejdere og kunder | MarkOn', 'Julegaver til medarbejdere, kunder og samarbejdspartnere. MarkOn hjælper med fællesgaver, gaveshop, indpakning, julehilsen og levering.'),
    'F-Kundegaver.dc.html': ('kundegaver', 'Kundegaver med logo og personlig hilsen | MarkOn', 'Kundegaver, der siger tak for samarbejdet. Få rådgivning om gavevalg, logo, indpakning og levering hos MarkOn.'),
    'F-Saesongaver.dc.html': ('saesongaver', 'Påskegaver og sommergaver til medarbejdere | MarkOn', 'Sæsongaver til påske og sommer til medarbejdere, kunder og samarbejdspartnere. MarkOn hjælper med gave, hilsen og levering.'),
    'F-Barselsgaver.dc.html': ('barselsgaver', 'Barselsgaver til medarbejdere | MarkOn', 'Barselsgaver til medarbejdere med indpakning og en personlig hilsen fra kollegerne. Få forslag hos MarkOn.'),
    'F-Jubilaeum.dc.html': ('jubilaeumsgaver', 'Jubilæumsgaver til medarbejdere og virksomheder | MarkOn', 'Jubilæumsgaver til medarbejdere og virksomhedsjubilæer. MarkOn hjælper med gavevalg, kort, indpakning og levering.'),
    'S-Merchandise.dc.html': ('merchandise', 'Merchandise med logo | MarkOn', 'Merchandise med logo til events, onboarding, employer branding og rebranding. MarkOn hjælper fra idé til levering.'),
    'S-LilleEkstra.dc.html': ('den-lille-ekstra', 'Den lille ekstra | MarkOn', '[MANGLER: beskrivelse af kategorien]'),
}


# ---------- S-sider med egne sektioner ----------

def split_head(sec):
    """Overskrift til venstre og tekst til højre (Forside, Om os)."""
    h2 = sec.find('h2')
    p = h2.find_next_sibling('p')
    return txt(h2), txt(p)

def page_forside(soup):
    secs = sections(soup)
    blocks = []
    hero = secs[0]
    b = hero_standard(hero, 'front')
    col = hero.find(class_='collage')
    imgs = col.find_all('img')
    b['media'] = {'kind': 'collage', 'images': [img(i) for i in imgs]}
    blocks.append(b)
    logos = secs[1].find('div')
    spans = logos.find_all('span', recursive=False)
    blocks.append({'type': 'logos', 'label': plain(spans[0]), 'names': [plain(x) for x in spans[1:]]})
    cat = secs[2]
    heading, text = split_head(cat)
    items = []
    for lt in cat.find(class_='three').find_all(class_='lt', recursive=False):
        im = lt.find('img'); ov = lt.find(class_='ov'); ttl = lt.find(class_='ttl')
        mt = re.search(r'margin-top: (\d+)px', lt.get('style', ''))
        items.append({'title': plain(ttl), 'href': url(lt.find('a', class_='cover')['href']), 'text': plain(ov.find('p')),
                      'links': [link(a) for a in ov.find('div').find_all('a')], 'more': plain(ov.find(class_='more')).rstrip(' →'),
                      'image': img(im), 'ratio': 'tall' if '4 / 5' in im.get('style', '') else 'portrait',
                      'offset': int(mt.group(1)) if mt else 0, 'pill': 'top' if 'top:' in ttl.get('style', '') else 'bottom'})
    aud = []
    for a in cat.find_all('a', class_='go', recursive=True):
        if a.find_parent(class_='lt'):
            continue
        sp = a.find('span').find_all('span', recursive=False)
        aud.append({'kicker': plain(sp[0]), 'title': plain(sp[1]), 'href': url(a['href'])})
    blocks.append({'type': 'categories', 'heading': heading, 'text': text, 'items': items, 'audiences': aud})
    blocks.append(band(secs[3], 'large'))
    cs = secs[4]
    head = cs.find('div')
    items = []
    for a in cs.find(class_='cases').find_all('a', recursive=False):
        st = a.get('style', '')
        size = 'large' if 'grid-row: span 2' in st else ('wide' if 'grid-column: span 2' in st else 'small')
        ov = a.find(class_='ov')
        items.append({'title': plain(a.find(class_='ttl')), 'text': plain(ov.find('span')), 'href': url(a['href']),
                      'image': img(a.find('img')), 'size': size})
    blocks.append({'type': 'cases', 'heading': txt(head.find('p')), 'link': link(head.find('a')), 'items': items})
    q = secs[5].find_all('p')
    blocks.append({'type': 'quote', 'text': plain(q[0]), 'author': plain(q[1])})
    blocks.append(faq(secs[6]))
    blocks.append(next_block(secs[7]))
    return blocks

def pair_media(container, align):
    items = []
    for el in container.find_all(['img', 'div'], recursive=False):
        st = el.get('style', '')
        circle = 'border-radius: 50%' in st
        mt = re.search(r'margin-top: (\d+)px', st); mb = re.search(r'margin-bottom: (\d+)px', st)
        grow = re.search(r'flex: ([\d.]+)', st)
        items.append({'image': img(el), 'shape': 'circle' if circle else 'portrait', 'grow': float(grow.group(1)) if grow else 1,
                      'offsetTop': int(mt.group(1)) if mt else 0, 'offsetBottom': int(mb.group(1)) if mb else 0})
    return {'kind': 'pair', 'align': align, 'items': items}

def page_messer(soup):
    secs = sections(soup)
    b = hero_standard(secs[0], 'large')
    b['media'] = pair_media(secs[0].find('h1').parent.find_next_sibling('div'), 'start')
    blocks = [b]
    f = secs[1]
    items = []
    for c in f.find(class_='three').find_all('div', recursive=False):
        items.append({'image': img(c.find('img')), 'title': plain(c.find('h3')), 'text': plain(c.find('h3').find_next_sibling('p')),
                      'label': plain(c.find('h4')), 'value': plain(c.find('h4').find_next_sibling('p'))})
    blocks.append({'type': 'features', 'heading': txt(f.find('h2')), 'text': txt(f.find('h2').find_next_sibling('p')), 'items': items})
    blocks.append(band(secs[2], 'large'))
    c = secs[3]; box = c.find('div')
    ps = box.find_all('p')
    blocks.append({'type': 'case', 'variant': 'banner', 'kicker': plain(ps[0]), 'title': plain(ps[1]), 'href': url(box.find('a')['href']),
                   'linkLabel': plain(box.find('a')), 'image': img(c.find('img'))})
    blocks.append(faq(secs[4]))
    blocks.append(next_block(secs[5]))
    return blocks

def page_produkt(soup):
    secs = sections(soup)
    h = secs[0]
    gal = h.find('div')
    gallery = []
    for el in gal.find_all(['img', 'div'], recursive=False):
        gallery.append(img(el, shape='circle' if 'border-radius: 50%' in el.get('style', '') else 'square'))
    text = h.find('h1').parent
    facts = []
    for d in text.find('div', recursive=False).find_all('div', recursive=False):
        dd = d.find_all('div')
        facts.append({'label': plain(dd[0]), 'value': plain(dd[1])})
    blocks = [{'type': 'product', 'heading': txt(h.find('h1')), 'body': txt(text.find('p')), 'gallery': gallery, 'facts': facts,
               'formHeading': plain(h.find('form').find('p'))}]
    pr = secs[1]
    items = []
    for c in pr.find(class_='three').find_all('div', recursive=False):
        first = c.find(['img', 'div'])
        items.append({'image': img(first), 'title': plain(c.find('h3')), 'text': plain(c.find('h3').find_next_sibling('p')), 'meta': plain(c.find('h4'))})
    blocks.append({'type': 'products', 'heading': txt(pr.find('h2')), 'text': txt(pr.find('h2').find_next_sibling('p')), 'items': items})
    sp = secs[2]
    cards = [{'title': plain(c.find_all('p')[0]), 'text': plain(c.find_all('p')[1])} for c in sp.find(class_='two').find_all('div', recursive=False)]
    blocks.append({'type': 'split', 'heading': txt(sp.find('h2')), 'text': txt(sp.find('h2').find_next_sibling('p')), 'cards': cards})
    blocks.append(faq(secs[3]))
    blocks.append(next_block(secs[4]))
    return blocks

def page_kontakt(soup):
    secs = sections(soup)
    h = secs[0]; text = h.find('h1').parent
    channels = []
    for a in text.find('div').find_all('a'):
        sp = a.find_all('span', recursive=False)[1].find_all('span')
        channels.append({'icon': 'phone' if a['href'].startswith('tel') else 'mail', 'label': plain(sp[0]), 'value': plain(sp[1]), 'href': a['href']})
    form = h.find('form')
    needs = [{'label': plain(l), **({'checked': True} if l.find('input').has_attr('checked') else {})} for l in form.find_all(class_='chk')]
    blocks = [{'type': 'quoteForm', 'heading': txt(h.find('h1')), 'body': txt(text.find('p')), 'channels': channels, 'needs': needs,
               'note': plain(form.find_all('p')[-1])}]
    loc = secs[1]
    items = []
    for d in loc.find(class_='three').find_all('div', recursive=False):
        p = d.find('p'); lines = [l for l in txt(p).split('\n') if l and '@' not in l]
        a = p.find('a')
        items.append({'name': plain(d.find('h3')), 'lines': lines, **({'email': plain(a)} if a else {})})
    a = loc.find('a', class_='go'); sp = a.find_all('span', recursive=False)
    blocks.append({'type': 'locations', 'items': items, 'card': {'kicker': plain(sp[0]), 'title': plain(sp[1]), 'href': url(a['href'])}})
    blocks.append(faq(secs[2]))
    blocks.append(next_block(secs[3]))
    return blocks

def page_omos(soup):
    secs = sections(soup)
    h = secs[0]
    b = hero_standard(h, 'large')
    stats = []
    for d in h.find('h1').parent.find('div', recursive=False).find_all('div', recursive=False):
        dd = d.find_all('div'); stats.append({'value': plain(dd[0]), 'label': plain(dd[1])})
    b['stats'] = stats
    b['media'] = pair_media(h.find('h1').parent.find_next_sibling('div'), 'end')
    blocks = [b]
    v = secs[1]; left = v.find('h2').parent
    h3s = v.find_all('h3')
    steps = []
    for li in v.find('ol').find_all('li'):
        t = li.find_all('span')[1]
        title = plain(t.find('b')).rstrip('.')
        steps.append({'title': title, 'text': plain(t).replace(plain(t.find('b')), '', 1).strip()})
    blocks.append({'type': 'values', 'heading': txt(v.find('h2')), 'text': txt(v.find('h2').find_next_sibling('p')),
                   'storyHeading': plain(h3s[0]), 'story': txt(h3s[0].find_next_sibling('p')), 'processHeading': plain(h3s[1]), 'steps': steps})
    t = secs[2]; heading, text = split_head(t)
    members = []
    for d in t.find(class_='four').find_all('div', recursive=False):
        members.append({'photo': img(d.find('div')), 'name': plain(d.find('h4')), 'role': plain(d.find('p')), 'link': link(d.find('a'))})
    blocks.append({'type': 'team', 'heading': heading, 'text': text, 'members': members})
    cards = []
    for c in secs[3].find(class_='two').find_all('div', recursive=False):
        ps = c.find_all('p', recursive=False)
        card = {'heading': plain(c.find('h3')), 'text': txt(ps[0])}
        if len(ps) > 1:
            card['extra'] = txt(ps[1])
        cta = [a for a in c.find_all('a') if is_cta(a)]
        if cta:
            card['cta'] = link(cta[0])
        lk = [a for a in c.find_all('a', class_='go')]
        if lk:
            card['links'] = [{'label': plain(a.find('span')), 'href': url(a['href'])} for a in lk]
        cards.append(card)
    blocks.append({'type': 'info', 'cards': cards})
    blocks.append(faq(secs[4]))
    blocks.append(next_block(secs[5]))
    return blocks

S_PAGES = {
    'S-Forside.dc.html': ('forside', 'Firmatøj, firmagaver og merchandise med logo | MarkOn', 'MarkOn leverer firmatøj, firmagaver og merchandise med jeres logo. Én kontakt fra idé og design til tryk, pakning og levering.', page_forside),
    'S-Messer.dc.html': ('messer-og-events', 'Merchandise til messer og events | MarkOn', 'Giveaways, tøj til standen og merchandise til kick off og firmafester. MarkOn samler det hele, så alt er klar til tiden.', page_messer),
    'S-Produkt.dc.html': ('krus-med-logo', 'Krus med logo | MarkOn', 'Krus med logo til kontoret, velkomstpakken og messen. Vælg mellem stålkrus, termokrus og kaffekopper i keramik.', page_produkt),
    'S-Kontakt.dc.html': ('kontakt', 'Kontakt og få et tilbud | MarkOn', 'Fortæl kort, hvad I har brug for, så vender en rådgiver tilbage med forslag og pris. Ring på 86 19 86 86 eller skriv til salg@markon.as.', page_kontakt),
    'S-OmOs.dc.html': ('om-os', 'Om MarkOn | MarkOn', 'MarkOn er rådgivere, designere og lagerfolk i Lystrup og Ikast. Besøg vores showroom eller bladr i vores kataloger.', page_omos),
}

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for f, (slug, title, desc) in SEO.items():
        soup = soup_of(f)
        data = {'url': URLS[f], 'seo': {'title': title, 'description': desc}}
        cr = crumbs(soup)
        data['menu'] = cr[1]['label'] if cr and len(cr) > 1 and cr[1].get('href') else (cr[-1]['label'] if cr else None)
        data['breadcrumbs'] = cr
        data['blocks'] = page_f(f, soup, title, desc)
        write(f, slug, data)
    for f, (slug, title, desc, fn) in S_PAGES.items():
        soup = soup_of(f)
        data = {'url': URLS[f], 'seo': {'title': title, 'description': desc}, 'scale': 'large'}
        cr = crumbs(soup)
        if cr:
            data['menu'] = cr[1]['label'] if len(cr) > 2 else cr[-1]['label']
            data['breadcrumbs'] = cr
        data['blocks'] = fn(soup)
        write(f, slug, data)
