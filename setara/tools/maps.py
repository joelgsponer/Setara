#!/usr/bin/env python3
"""Draw the map pictures of the geography pack from real map data.

  python3 tools/maps.py

Writes content/pictures/scene_map_*.svg, map_*.svg and globe.svg in the
library's style. The outlines come from Natural Earth (naturalearthdata.com,
public domain), downloaded once into builder/.cache/ne. Needs shapely.

Country borders are not drawn. A map shows land and sea, and at most the one
or two countries a lesson is about.
"""
import json
import math
import urllib.request
from pathlib import Path

from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "builder" / ".cache" / "ne"
OUT = ROOT / "content" / "pictures"
BASE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"

INK, SEA, LAND, MARK = "#3b2f2f", "#bfe3f0", "#e8d2a6", "#f2b705"
ORANGE, GREEN, PURPLE, WATER, GREY = "#e07a3f", "#9ccb7a", "#b79ad6", "#5da9d6", "#b9ae9b"


def load(name):
    path = CACHE / f"{name}.geojson"
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        local = Path("/opt/tools/ne") / path.name
        path.write_bytes(local.read_bytes() if local.exists() else urllib.request.urlopen(BASE + path.name).read())
    return json.loads(path.read_text("utf-8"))["features"]


def parts(geom):
    return list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom] if isinstance(geom, Polygon) else []


def continents(features):
    """Land by continent. Russia is cut at the Urals; far-off parts of European countries go where they lie."""
    by = {}
    for f in features:
        cont = f["properties"]["CONTINENT"]
        if cont.startswith("Seven"):
            continue
        for part in parts(shape(f["geometry"]).buffer(0)):
            pieces = [(cont, part)]
            if f["properties"]["ADM0_A3"] == "RUS":
                pieces = [("Europe", part.intersection(box(-30, 0, 60, 90))), ("Asia", part.intersection(box(60, 0, 180, 90))),
                          ("Asia", part.intersection(box(-180, 0, -30, 90)))]
            for c, piece in pieces:
                if piece.is_empty:
                    continue
                x, y = piece.centroid.x, piece.centroid.y
                if c == "Europe" and x < -30 and y < 15:
                    c = "South America"
                by.setdefault(c, []).append(piece)
    return {c: unary_union(g) for c, g in by.items()}


class Map:
    """An equirectangular map of a lon/lat window, fitted into a picture."""

    def __init__(self, w, h, lon0, lon1, lat0, lat1, pad=0):
        k = math.cos(math.radians((lat0 + lat1) / 2))
        sx = (w - 2 * pad) / ((lon1 - lon0) * k)
        sy = (h - 2 * pad) / (lat1 - lat0)
        self.s = min(sx, sy)
        self.k, self.w, self.h = k, w, h
        self.window = box(lon0, lat0, lon1, lat1)
        self.cx, self.cy = (lon0 + lon1) / 2, (lat0 + lat1) / 2
        self.body = []

    def xy(self, lon, lat):
        return (self.w / 2 + (lon - self.cx) * self.k * self.s, self.h / 2 - (lat - self.cy) * self.s)

    def path(self, geom, min_area=6):
        geom = geom.intersection(self.window.buffer(3))
        d = []
        for part in parts(geom):
            for ring in [part.exterior] + list(part.interiors):
                pts = [self.xy(x, y) for x, y in ring.coords]
                # a coastline can touch itself once drawn this small: mend it rather than lose the land
                for poly in parts(Polygon(pts).buffer(0)):
                    if poly.area < min_area:
                        continue
                    pts2 = list(poly.simplify(0.5).exterior.coords)
                    d.append("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts2[:-1]) + "Z")
        return "".join(d)

    def land(self, geom, fill, width=2.4, min_area=6):
        d = self.path(geom, min_area)
        if d:
            self.body.append(f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="{width}" stroke-linejoin="round"/>')

    def line(self, geom, colour, width):
        geom = geom.intersection(self.window)
        lines = list(geom.geoms) if hasattr(geom, "geoms") else [geom]
        for ln in lines:
            if ln.is_empty or ln.geom_type != "LineString":
                continue
            pts = [self.xy(x, y) for x, y in LineString(ln.coords).simplify(0.002).coords]
            self.body.append('<path d="M' + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) +
                             f'" fill="none" stroke="{colour}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')

    def dot(self, lon, lat, r, fill=INK):
        x, y = self.xy(lon, lat)
        self.body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>')

    def ring(self, lon, lat, r):
        x, y = self.xy(lon, lat)
        self.body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="none" stroke="{MARK}" stroke-width="5"/>')
        self.body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r + 3.5}" fill="none" stroke="{INK}" stroke-width="2"/>')

    def save(self, name, sea=SEA):
        back = f'<rect width="{self.w}" height="{self.h}" fill="{sea}"/>' if sea else ""
        (OUT / f"{name}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}">\n{back}\n' + "\n".join(self.body) + "\n</svg>\n")
        print("  " + name)


KABUL, BASEL, BERN = (69.17, 34.53), (7.59, 47.56), (7.45, 46.95)


def main():
    c110 = load("ne_110m_admin_0_countries")
    c50 = load("ne_50m_admin_0_countries")
    c10 = load("ne_10m_admin_0_countries")
    cont = continents(c110)
    country50 = {f["properties"]["ADM0_A3"]: shape(f["geometry"]).buffer(0) for f in c50}
    country10 = {f["properties"]["ADM0_A3"]: shape(f["geometry"]).buffer(0) for f in c10}
    land50 = unary_union(list(country50.values()))
    names = {"Asia": "asia", "Africa": "africa", "Europe": "europe", "North America": "north_america",
             "South America": "south_america", "Oceania": "oceania", "Antarctica": "antarctica"}

    def world(highlight=None, mark=None, name="scene_map_world"):
        m = Map(400, 300, -180, 180, -90, 90)
        m.k, m.s = 1.0, 400 / 360 * 1.0   # the whole world, stretched a little in height to fill the picture
        m.xy = lambda lon, lat: (200 + lon * 400 / 360, 150 - lat * 300 / 180 * 0.98)
        m.land(unary_union(list(cont.values())), LAND, min_area=3)   # one land, no lines between continents
        m.land(cont["Antarctica"], "#ffffff", min_area=3)            # ice
        if highlight:
            m.land(cont[highlight], ORANGE, min_area=3)
        if mark:
            code, at, r = mark
            m.land(country50[code], ORANGE, width=1.5, min_area=0.5)
            m.ring(at[0], at[1], r)
        m.save(name)

    world()
    for c, n in names.items():
        world(highlight=c, name=f"scene_map_{n}")
    world(mark=("AFG", (66, 34), 16), name="scene_map_world_afghanistan")
    world(mark=("CHE", (8.2, 46.8), 12), name="scene_map_world_switzerland")

    # each continent alone, as a square picture
    for c, n in names.items():
        geom = cont[c]
        if c == "Asia":
            geom = geom.intersection(box(20, -15, 180, 85))
        if c == "Oceania":
            geom = geom.intersection(box(105, -50, 180, 5))
        if c == "North America":
            geom = geom.intersection(box(-170, 5, -50, 84))
        if c == "Europe":
            geom = geom.intersection(box(-25, 34, 62, 72))
        if c == "Antarctica":
            # seen from above the pole, the way it looks on a globe
            m = Map(128, 128, -1, 1, -1, 1)
            rings = []
            for part in parts(geom):
                pts = [((90 + y) * math.sin(math.radians(x)), (90 + y) * math.cos(math.radians(x))) for x, y in part.exterior.coords if y > -89.5]
                if len(pts) > 3:
                    rings.append(Polygon(pts).buffer(0))
            shape_ = unary_union(rings)
            x0, y0, x1, y1 = shape_.bounds
            s = 112 / max(x1 - x0, y1 - y0)
            d = ""
            for part in parts(shape_):
                if part.area * s * s < 20:
                    continue
                pts = [(64 + (x - (x0 + x1) / 2) * s, 64 - (y - (y0 + y1) / 2) * s) for x, y in part.simplify(0.3).exterior.coords]
                d += "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts[:-1]) + "Z"
            m.body.append(f'<path d="{d}" fill="#ffffff" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
            m.save(f"map_{n}", sea=None)
            continue
        x0, y0, x1, y1 = geom.bounds
        m = Map(128, 128, x0, x1, y0, y1, pad=8)
        m.land(geom, LAND, width=4, min_area=14)
        m.save(f"map_{n}", sea=None)

    for code, n in (("AFG", "afghanistan"), ("CHE", "switzerland")):
        geom = country10[code]
        x0, y0, x1, y1 = geom.bounds
        m = Map(128, 128, x0, x1, y0, y1, pad=9)
        m.land(geom, ORANGE, width=5, min_area=30)
        m.save(f"map_{n}", sea=None)

    m = Map(400, 300, 24, 150, -12, 78)
    m.land(land50, LAND)
    m.land(country50["AFG"], ORANGE, width=3)
    m.save("scene_map_asia_afghanistan")

    m = Map(400, 300, -26, 46, 33, 72)
    m.land(land50, LAND)
    m.land(country50["CHE"], ORANGE, width=3, min_area=1)
    m.ring(8.2, 46.8, 14)
    m.save("scene_map_europe_switzerland")

    m = Map(400, 300, -14, 82, 18, 66)
    m.land(land50, LAND)
    m.land(country50["AFG"], ORANGE, width=3)
    m.land(country50["CHE"], ORANGE, width=3, min_area=1)
    (x1, y1), (x2, y2) = m.xy(*KABUL), m.xy(*BASEL)
    m.body.append(f'<path d="M{x1:.1f} {y1:.1f}Q{(x1 + x2) / 2:.1f} {min(y1, y2) - 46:.1f} {x2:.1f} {y2:.1f}" fill="none" stroke="{INK}" '
                  f'stroke-width="4" stroke-dasharray="3 9" stroke-linecap="round"/>')
    m.dot(*KABUL, 6, MARK)
    m.dot(*BASEL, 6, MARK)
    m.save("scene_map_route")

    rivers = [shape(f["geometry"]) for f in load("ne_10m_rivers_lake_centerlines")
              if (f["properties"].get("name") or "") in ("Rhein", "Rhine", "Rhin")]
    rhine = unary_union(rivers)
    lakes = unary_union([shape(f["geometry"]).buffer(0) for f in load("ne_10m_lakes")])
    land10 = unary_union([g for g in country10.values() if g.intersects(box(3, 43, 14, 51))])

    m = Map(400, 300, 5.3, 11.1, 45.45, 48.25)
    m.land(land10, LAND)
    m.land(country10["CHE"], ORANGE, width=3.5)
    m.land(lakes.intersection(box(5.3, 45.45, 11.1, 48.25)), WATER, width=1.5, min_area=4)
    m.line(rhine, WATER, 4)
    for lon, lat in ((7.2, 46.2), (7.9, 46.1), (8.6, 46.35), (9.4, 46.5), (10.0, 46.6), (8.1, 46.55)):   # the Alps
        x, y = m.xy(lon, lat)
        m.body.append(f'<path d="M{x - 11:.1f} {y + 8:.1f}L{x:.1f} {y - 10:.1f}L{x + 11:.1f} {y + 8:.1f}Z" fill="#ffffff" stroke="{INK}" '
                      f'stroke-width="2.5" stroke-linejoin="round"/>')
    m.dot(*BERN, 5, "#ffffff")
    m.dot(*BASEL, 8, MARK)
    m.save("scene_map_switzerland")

    w = (7.22, 7.98, 47.36, 47.78)
    m = Map(400, 300, *w)
    win = box(w[0] - 0.2, w[2] - 0.2, w[1] + 0.2, w[3] + 0.2)
    for code, colour in (("FRA", GREEN), ("DEU", PURPLE), ("CHE", ORANGE)):
        m.land(country10[code].intersection(win), colour, width=3.5)
    m.line(rhine, WATER, 9)
    m.line(rhine, "#8fc6e8", 4)
    x, y = m.xy(*BASEL)
    for dx, dy in ((-16, 6), (-4, -12), (10, 4), (-2, 12), (18, -10)):   # the city: a cluster of roofs
        m.body.append(f'<path d="M{x + dx - 8:.1f} {y + dy + 6:.1f}v-9l8-7 8 7v9z" fill="#fff6dc" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')
    m.save("scene_map_basel")

    # a globe on a stand, turned so that Asia, Africa and Europe show
    lon0, lat0, R, cx, cy = math.radians(55), math.radians(22), 44, 64, 54
    body = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{WATER}" stroke="{INK}" stroke-width="5"/>']
    d = ""
    for geom in cont.values():
        for part in parts(geom.simplify(0.8)):
            pts, seen = [], 0
            for lon, lat in part.exterior.coords:
                lam, phi = math.radians(lon) - lon0, math.radians(lat)
                cosc = math.sin(lat0) * math.sin(phi) + math.cos(lat0) * math.cos(phi) * math.cos(lam)
                x = math.cos(phi) * math.sin(lam)
                y = math.cos(lat0) * math.sin(phi) - math.sin(lat0) * math.cos(phi) * math.cos(lam)
                if cosc < 0:           # behind the globe: pull the point to the edge
                    n = math.hypot(x, y) or 1
                    x, y = x / n, y / n
                else:
                    seen += 1
                pts.append((cx + R * x, cy - R * y))
            if seen >= 3 and Polygon(pts).buffer(0).area > 12:
                d += "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts[:-1]) + "Z"
    body.append(f'<path d="{d}" fill="{GREEN}" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round"/>')
    body.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{INK}" stroke-width="5"/>')
    body.append(f'<path d="M{cx - 30} {cy + 38}a48 48 0 0 0 60 0" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>')
    body.append(f'<path d="M{cx} {cy + 47}v10" stroke="{INK}" stroke-width="5"/>')
    body.append(f'<path d="M{cx - 26} 120h52l-8-10h-36z" fill="#9a6b3f" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
    (OUT / "globe.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">\n' + "\n".join(body) + "\n</svg>\n")
    print("  globe")


if __name__ == "__main__":
    main()
