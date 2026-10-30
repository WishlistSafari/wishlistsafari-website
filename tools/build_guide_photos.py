"""Insert a credited hero photo into each species guide that has one.

For each entry in img/guides/credits.json -> photos, e.g.
  "shoebill": {"alt": "A shoebill standing in papyrus", "credit": "Photo: Jane Guide, Shoebill Island Camp",
               "link": "https://...", "licence": "Used with permission"}
and an image at img/guides/shoebill.jpg, the photo is placed under the guide's quick-answer box,
between <!--photo:start--> and <!--photo:end--> markers (reruns replace it).
Only use photos we have permission or a free licence for, and always credit the photographer.
"""
import json, html, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
cfg = json.loads((ROOT / 'img/guides/credits.json').read_text())['photos']
CSS = ('<style id="photo-css">.guide-photo{margin:32px 0 0}.guide-photo img{display:block;width:100%;height:auto;'
       'aspect-ratio:3/2;object-fit:cover;border-radius:4px;background:var(--tint)}'
       '.guide-photo figcaption{margin-top:8px;font-size:13px;color:var(--muted)}</style>')
for f in sorted(ROOT.glob('*.html')):
    s = f.read_text()
    s = re.sub(r'\n?<!--photo:start-->.*?<!--photo:end-->', '', s, flags=re.S)
    p = cfg.get(f.stem)
    img = ROOT / 'img/guides' / (f.stem + '.jpg')
    if p and img.exists():
        cap = html.escape(p.get('credit', ''))
        if p.get('link'): cap = '<a href="%s">%s</a>' % (html.escape(p['link']), cap)
        if p.get('licence'): cap += ', ' + html.escape(p['licence'])
        fig = ('<!--photo:start--><figure class="guide-photo"><img src="img/guides/%s.jpg" alt="%s" '
               'width="1600" height="1067" loading="lazy"><figcaption>%s</figcaption></figure><!--photo:end-->'
               % (f.stem, html.escape(p.get('alt', '')), cap))
        m = re.search(r'<div class="answer">.*?</div>', s, re.S)
        if m:
            s = s[:m.end()] + '\n' + fig + s[m.end():]
            if 'id="photo-css"' not in s: s = s.replace('</head>', CSS + '\n</head>', 1)
            print('photo added:', f.name)
    f.write_text(s)
