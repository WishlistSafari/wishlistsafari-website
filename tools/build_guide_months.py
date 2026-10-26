"""Add a 'Month by month' grid to each species guide from the planner's SEASON and OPEN data.

Rerun after tools/build_seasons.py changes SEASON in index.html:
    python3 tools/build_guide_months.py
The grid sits between <!--months:start--> and <!--months:end--> markers, right after
the guide's 'When to go' table, so reruns replace it cleanly.

Levels shown publicly are deliberately conservative:
  3 -> Best (only when the next or previous month is also 3, so one-off spikes in the
  records are not oversold), 1 or 2 -> Good, 0 -> Not in season, park closure -> Closed.
We never label a month as poor, because a quieter month in the records is not proof
the species is absent.
"""
import json, re, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
idx = (ROOT / "index.html").read_text()
SEASON = json.loads(re.search(r"var SEASON *= *(\{[^}]*\})", idx).group(1))
OPEN = json.loads(re.search(r"var OPEN *= *(\{[^}]*\})", idx).group(1).replace("'", '"'))

MONTHS = "J F M A M J J A S O N D".split()
MONTH_NAMES = "January February March April May June July August September October November December".split()
MAX_ROWS = 8

CSS = """<style id="months-css">
.months{width:100%;border-collapse:collapse;margin-top:12px;font-size:14px;table-layout:fixed}
.months th,.months td{padding:6px 0;text-align:center;border-bottom:1px solid var(--line)}
.months th{font-size:11px;letter-spacing:.1em;color:var(--muted);font-weight:500}
.months th.pl,.months td.pl{text-align:left;width:34%;padding-right:10px;font-size:14px;letter-spacing:0;color:var(--green)}
.months td span{display:block;height:18px;margin:0 2px;border-radius:3px}
.m3{background:var(--green)}.m2{background:var(--mist)}.m0{background:transparent;border:1px dashed var(--line)}.mx{background:repeating-linear-gradient(45deg,var(--tint),var(--tint) 3px,var(--line) 3px,var(--line) 5px)}
@media(max-width:600px){.months th.pl,.months td.pl{width:30%;font-size:12px}.months td span{margin:0 1px;height:16px}.months th{font-size:10px;letter-spacing:0}}
.months-key{display:flex;flex-wrap:wrap;gap:6px 18px;margin:12px 0 0;font-size:13px;color:var(--muted)}
.months-key i{display:inline-block;width:14px;height:12px;border-radius:2px;margin-right:6px;vertical-align:-1px}
</style>"""


def level(place, i, v, row=""):
    o = OPEN.get(place)
    if o and o[i] == "0":
        return "mx", "camps closed"
    if v == "0":
        return "m0", "not in season"
    if v == "3" and (row[i - 1] == "3" or row[(i + 1) % 12] == "3"):
        return "m3", "best"
    return "m2", "good"


def grid(species):
    rows = [(k.split("|")[0], v) for k, v in SEASON.items() if k.split("|")[1] == species]
    if not rows:
        return None
    rows.sort(key=lambda r: (-r[1].count("3"), r[0]))
    rows = rows[:MAX_ROWS]
    has0 = any("0" in v for _, v in rows)
    hasx = any(p in OPEN for p, _ in rows)
    head = '<tr><th class="pl">Place</th>' + "".join(f'<th scope="col" title="{MONTH_NAMES[i]}">{m}</th>' for i, m in enumerate(MONTHS)) + "</tr>"
    body = ""
    for p, v in rows:
        cells = ""
        for i, c in enumerate(v):
            cls, word = level(p, i, c, v)
            cells += f'<td><span class="{cls}" title="{MONTH_NAMES[i]}: {word}" aria-label="{MONTH_NAMES[i]}: {word}"></span></td>'
        body += f'<tr><th scope="row" class="pl">{html.escape(p)}</th>{cells}</tr>'
    key = '<i class="m3"></i>Best</span><span><i class="m2"></i>Good</span>'
    key = '<span>' + key
    if has0:
        key += '<span><i class="m0"></i>Not in season</span>'
    if hasx:
        key += '<span><i class="mx"></i>Most camps closed for the rains</span>'
    return (
        "<!--months:start-->\n"
        "<h3>Month by month, place by place</h3>\n"
        f'<div class="table-wrap"><table class="months"><thead>{head}</thead><tbody>{body}</tbody></table></div>\n'
        f'<p class="months-key">{key}</p>\n'
        "<p style=\"font-size:14px;color:var(--muted)\">Shaded from a year of wildlife records at each place, adjusted for how many people were out looking, checked against known seasons such as denning and the dry months, and refined as our partner camps share their sightings. "
        "A lighter month is still a good month; it just has fewer records. "
        f'<a href="index.html?add={species.replace(" ", "%20").replace(chr(39), "%27")}#planner">Pick your month in the planner</a> to see how it changes your matches.</p>\n'
        "<!--months:end-->"
    )


GUIDES = {}
for f in sorted(ROOT.glob("*.html")):
    m = re.search(r'index\.html\?add=([^#"]+)#planner', f.read_text())
    if m:
        from urllib.parse import unquote
        GUIDES[f.name] = unquote(m.group(1))

done, skipped = [], []
for name, species in GUIDES.items():
    p = ROOT / name
    s = p.read_text()
    s = re.sub(r"\n?<!--months:start-->.*?<!--months:end-->", "", s, flags=re.S)
    g = grid(species)
    if not g:
        skipped.append(name)
        p.write_text(s)
        continue
    m = re.search(r"<h2>When to go</h2>\s*<div class=\"table-wrap\">.*?</table></div>", s, re.S)
    if not m:
        skipped.append(name + " (no When to go table)")
        continue
    s = s[: m.end()] + "\n" + g + s[m.end():]
    if 'id="months-css"' not in s:
        s = s.replace("</head>", CSS + "\n</head>", 1)
    p.write_text(s)
    done.append(name)

print("updated:", len(done), done)
print("skipped:", skipped)
