"""Rebuild the SEASON table in index.html from tools/seasons-source.txt.
Run from the repo root: python3 tools/build_seasons.py"""
import json, re
src = open('tools/seasons-source.txt', encoding='utf-8').read().splitlines()
s = open('index.html', encoding='utf-8').read()
d = json.loads(re.search(r'const DATA = (\{.*?\});\n', s).group(1))
valid = {r['name'] + '|' + sp for r in d['regions'] for sp in r['species']}
season, bad = {}, []
for line in src:
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    if line.startswith('FLAT '):
        k, v = line[5:], '3' * 12
    else:
        line = line.replace('CURATED ', '', 1)
        k, v = line.rsplit('=', 1)
    if k not in valid or not re.fullmatch(r'[0-3]{12}', v):
        bad.append(k); continue
    season[k] = v
js = '  var SEASON = ' + json.dumps(season, ensure_ascii=False, separators=(',', ':')) + ';'
s, n = re.subn(r'^  var SEASON = .*;$', lambda m: js, s, count=1, flags=re.M)
assert n == 1
open('index.html', 'w', encoding='utf-8').write(s)
print(len(season), 'pairs; skipped:', bad)
