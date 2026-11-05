"""Bake the planner's base map (land, borders, lakes, rivers, salt pans) into index.html.

Source data is Natural Earth (public domain), via world-atlas 10m TopoJSON for the
countries and the Natural Earth GeoJSON for lakes, rivers and playas. Download them into
a folder and run:
    python3 tools/build_map.py /path/to/ne-folder
Files expected in the folder: countries-10m.json, ne_10m_lakes.geojson,
ne_10m_rivers_lake_centerlines.geojson, ne_10m_playas.geojson

The result sits between <!--mapbase:start--> and <!--mapbase:end--> inside the planner
SVG, so reruns replace it cleanly. Coordinates are plain lon, -lat (the planner's own
projection), simplified so the page stays light.
"""
import json, math, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
BOX = (2.0, -41.0, 58.0, 13.0)  # lon0, lat0, lon1, lat1: a margin around every map view
TOL = 0.035  # degrees, about one screen pixel at the closest zoom


def dp(pts, tol=TOL):
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]; bx, by = pts[b]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1e-12
        best, bi = 0, None
        for i in range(a + 1, b):
            px, py = pts[i]
            d = abs(dy * px - dx * py + bx * ay - by * ax) / L if (dx or dy) else math.hypot(px - ax, py - ay)
            if d > best:
                best, bi = d, i
        if bi is not None and best > tol:
            keep[bi] = True
            stack += [(a, bi), (bi, b)]
    return [p for p, k in zip(pts, keep) if k]


def clip_poly(pts):
    """Sutherland-Hodgman against BOX. Fine for fills; the cut edges sit outside every view."""
    x0, y0, x1, y1 = BOX
    edges = [(lambda p: p[0] >= x0, lambda a, b: (x0, a[1] + (b[1] - a[1]) * (x0 - a[0]) / (b[0] - a[0]))),
             (lambda p: p[0] <= x1, lambda a, b: (x1, a[1] + (b[1] - a[1]) * (x1 - a[0]) / (b[0] - a[0]))),
             (lambda p: p[1] >= y0, lambda a, b: (a[0] + (b[0] - a[0]) * (y0 - a[1]) / (b[1] - a[1]), y0)),
             (lambda p: p[1] <= y1, lambda a, b: (a[0] + (b[0] - a[0]) * (y1 - a[1]) / (b[1] - a[1]), y1))]
    for inside, cut in edges:
        if not pts:
            break
        out = []
        for i, cur in enumerate(pts):
            prev = pts[i - 1]
            if inside(cur):
                if not inside(prev):
                    out.append(cut(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(cut(prev, cur))
        pts = out
    return pts


def inbox(p, m=0):
    return BOX[0] - m <= p[0] <= BOX[2] + m and BOX[1] - m <= p[1] <= BOX[3] + m


def fmt(p):
    return f"{p[0]:.2f},{-p[1]:.2f}".replace("-0.00", "0.00")


def ring_d(pts):
    out, last = [], None
    for p in pts:
        s = fmt(p)
        if s != last:
            out.append(s)
        last = s
    return ("M" + "L".join(out) + "Z") if len(out) >= 3 else ""


def line_d(pts):
    d, run = "", []
    for p in pts + [None]:
        if p is not None and inbox(p):
            run.append(p)
            continue
        run = dp(run, TOL * 0.8)
        if len(run) >= 2:
            d += "M" + "L".join(fmt(q) for q in run)
        run = []
    return d


def area(pts):
    return abs(sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts)))) / 2


# Countries: simplify each shared arc once, so neighbouring borders stay identical.
topo = json.loads((SRC / "countries-10m.json").read_text())
sx, sy = topo["transform"]["scale"]; tx, ty = topo["transform"]["translate"]
arcs = []
for a in topo["arcs"]:
    x = y = 0; pts = []
    for p in a:
        x += p[0]; y += p[1]
        pts.append((x * sx + tx, y * sy + ty))
    arcs.append(pts)
use = {}
for g in topo["objects"]["countries"]["geometries"]:
    polys = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"] if g["type"] == "MultiPolygon" else []
    for poly in polys:
        for r in poly:
            for i in r:
                use[i if i >= 0 else ~i] = use.get(i if i >= 0 else ~i, 0) + 1
near = {i for i, a in enumerate(arcs) if any(inbox(p, 3) for p in a)}
simp = {i: dp(arcs[i]) for i in near}

land = ""
for g in topo["objects"]["countries"]["geometries"]:
    polys = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"] if g["type"] == "MultiPolygon" else []
    for poly in polys:
        for r in poly:
            if not all((i if i >= 0 else ~i) in near for i in r):
                ids = [(i if i >= 0 else ~i) for i in r]
                if not any(j in near for j in ids):
                    continue
            pts = []
            for i in r:
                j = i if i >= 0 else ~i
                a = simp.get(j) or dp(arcs[j])
                a = a if i >= 0 else a[::-1]
                pts += a if not pts else a[1:]
            c = clip_poly(pts)
            if len(c) >= 3 and area(c) > 0.004:
                land += ring_d(c)

# Internal borders: arcs used by two countries.
borders = ""
for i in near:
    if use.get(i, 0) >= 2:
        borders += line_d(simp[i])

# Lakes and pans.
def polys_of(geo):
    g = geo["geometry"]
    if not g:
        return []
    return [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"] if g["type"] == "MultiPolygon" else []

lakes = ""
for f in json.loads((SRC / "ne_10m_lakes.geojson").read_text())["features"]:
    for poly in polys_of(f):
        outer = [tuple(p[:2]) for p in poly[0]]
        if not any(inbox(p) for p in outer) or area(outer) < 0.02:
            continue
        lakes += ring_d(dp(clip_poly(outer), TOL * 0.7))

pans = ""
for f in json.loads((SRC / "ne_10m_playas.geojson").read_text())["features"]:
    for poly in polys_of(f):
        outer = [tuple(p[:2]) for p in poly[0]]
        if any(inbox(p) for p in outer) and area(outer) > 0.01:
            pans += ring_d(dp(outer, TOL * 0.6))

# The Okavango Delta is not in Natural Earth as a polygon; a generalised outline of the
# permanent and seasonal swamps, traced from published maps.
OKAVANGO = [(21.78, -18.27), (22.05, -18.62), (22.12, -19.05), (22.25, -19.45), (22.45, -19.85),
            (22.85, -19.98), (23.25, -20.0), (23.55, -19.82), (23.68, -19.5), (23.55, -19.2),
            (23.3, -18.95), (22.95, -18.75), (22.55, -18.55), (22.2, -18.35), (21.95, -18.22)]
swamp = ring_d(OKAVANGO)

# Rivers: the big systems plus the rivers our places are named after.
KEEP = {"Luangwa", "Great Ruaha", "Olifants", "Chambeshi", "Luapula", "Kafue", "Okavango", "Cubango",
        "Cuando", "Linyanti", "Chobe", "Limpopo", "Save", "Rufiji", "Kunene", "Cunene", "Zambezi",
        "Shire", "Tana", "Pangani", "Victoria Nile", "Albert Nile", "Kagera", "Semliki", "Rusizi",
        "Orange", "Vaal", "Kabompo", "Lungwebungu", "Shangani", "Gwayi", "Cuito", "Malagarasi"}
riv = {1: "", 2: ""}
for f in json.loads((SRC / "ne_10m_rivers_lake_centerlines.geojson").read_text())["features"]:
    p = f["properties"]; g = f["geometry"]
    if not g or p.get("featurecla") != "River":
        continue
    rank = p.get("scalerank") or 9
    if p.get("name") not in KEEP and rank > 4:
        continue
    lines = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
    for ln in lines:
        pts = [tuple(q[:2]) for q in ln]
        if any(inbox(q) for q in pts):
            riv[1 if rank <= 4 else 2] += line_d(pts)

svg = (
    "<!--mapbase:start-->\n"
    f'<path id="map-land" d="{land}"/>\n'
    f'<path class="map-borders" d="{borders}"/>\n'
    f'<path class="map-pan" d="{pans}"/>\n'
    f'<path class="map-swamp" d="{swamp}"/>\n'
    f'<path class="map-river" d="{riv[2]}"/>\n'
    f'<path class="map-river major" d="{riv[1]}"/>\n'
    f'<path class="map-lake" d="{lakes}"/>\n'
    "<!--mapbase:end-->"
)
p = ROOT / "index.html"
s = p.read_text()
s, n = re.subn(r"<!--mapbase:start-->.*?<!--mapbase:end-->", lambda m: svg, s, flags=re.S)
if not n:
    sys.exit("No <!--mapbase:start--> marker in index.html")
p.write_text(s)
print("map bytes:", len(svg), {k: len(v) for k, v in [("land", land), ("borders", borders), ("lakes", lakes), ("rivers", riv[1] + riv[2]), ("pans", pans)]})
