
import json
import math
from pathlib import Path

# Toa do trung tam UTH co so 1
UTH_LAT = 10.804816
UTH_LON = 106.716878

# Ban kinh nghien cuu: 500 met
RADIUS = 500

input_path = Path("data/osm/filtered_roads.geojson")
output_path = Path("data/osm/roads_near_uth.geojson")


def distance_m(lat1, lon1, lat2, lon2):
    """
    Tinh khoang cach giua 2 diem GPS (met).
    Cong thuc Haversine.
    """
    R = 6371000

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = (
        math.sin(dp / 2) ** 2
        + math.cos(p1)
        * math.cos(p2)
        * math.sin(dl / 2) ** 2
    )

    return 2 * R * math.asin(
        min(1.0, math.sqrt(a))
    )


def distance_to_segment_m(point, a, b):
    """
    Khoang cach xap xi tu UTH den doan thang AB.
    Chuyen toa do GPS sang he toa do met cuc bo.
    """
    lat0 = math.radians(UTH_LAT)

    def to_xy(coord):
        lon, lat = coord[:2]

        x = (
            math.radians(lon - UTH_LON)
            * 6371000
            * math.cos(lat0)
        )

        y = (
            math.radians(lat - UTH_LAT)
            * 6371000
        )

        return x, y

    px, py = point
    ax, ay = to_xy(a)
    bx, by = to_xy(b)

    dx = bx - ax
    dy = by - ay

    length_sq = dx * dx + dy * dy

    if length_sq == 0:
        return math.hypot(px - ax, py - ay)

    t = max(
        0.0,
        min(
            1.0,
            ((px - ax) * dx + (py - ay) * dy)
            / length_sq
        )
    )

    closest_x = ax + t * dx
    closest_y = ay + t * dy

    return math.hypot(
        px - closest_x,
        py - closest_y
    )


with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

selected = []

for feature in data["features"]:
    geometry = feature.get("geometry") or {}

    if geometry.get("type") != "LineString":
        continue

    coords = geometry.get("coordinates", [])

    if len(coords) < 2:
        continue

    # Xet tung doan thang cua duong OSM
    min_distance = min(
        distance_to_segment_m(
            (0, 0),
            coords[i],
            coords[i + 1]
        )
        for i in range(len(coords) - 1)
    )

    if min_distance <= RADIUS:
        selected.append(feature)

output = {
    "type": "FeatureCollection",
    "features": selected
}

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(
        output,
        f,
        ensure_ascii=False,
        indent=2
    )

print("=== LOC DUONG QUANH UTH ===")
print("Tam UTH:", UTH_LAT, UTH_LON)
print("Ban kinh:", RADIUS, "met")
print("So duong truoc loc:", len(data["features"]))
print("So duong sau loc:", len(selected))
print("Da luu:", output_path)
