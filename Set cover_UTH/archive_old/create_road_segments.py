
import csv
import json
import math
from pathlib import Path

INPUT = Path("data/osm/roads_near_uth.geojson")
OUTPUT = Path("data/osm/road_segments.csv")

UTH_LAT = 10.804816
UTH_LON = 106.716878
RADIUS = 500.0
MAX_LENGTH = 50.0
EARTH_RADIUS = 6371000.0

COS_LAT = math.cos(math.radians(UTH_LAT))


def to_xy(lon, lat):
    """Chuyen GPS sang toa do met cuc bo."""
    x = math.radians(lon - UTH_LON) * EARTH_RADIUS * COS_LAT
    y = math.radians(lat - UTH_LAT) * EARTH_RADIUS
    return x, y


def to_gps(x, y):
    """Chuyen toa do met cuc bo ve GPS."""
    lon = UTH_LON + math.degrees(
        x / (EARTH_RADIUS * COS_LAT)
    )
    lat = UTH_LAT + math.degrees(y / EARTH_RADIUS)
    return lon, lat


def clip_segment(a, b, radius):
    """
    Cat doan AB theo hinh tron ban kinh radius.
    Tam hinh tron la (0, 0).
    """
    ax, ay = a
    bx, by = b
    dx = bx - ax
    dy = by - ay

    A = dx * dx + dy * dy

    if A == 0:
        return None

    B = 2 * (ax * dx + ay * dy)
    C = ax * ax + ay * ay - radius * radius

    discriminant = B * B - 4 * A * C

    if discriminant < 0:
        return None

    root = math.sqrt(max(0.0, discriminant))
    t1 = (-B - root) / (2 * A)
    t2 = (-B + root) / (2 * A)

    start = max(0.0, min(t1, t2))
    end = min(1.0, max(t1, t2))

    if end <= start:
        return None

    p = (ax + start * dx, ay + start * dy)
    q = (ax + end * dx, ay + end * dy)

    return p, q


with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

rows = []
segment_number = 0

for feature in data["features"]:
    geometry = feature.get("geometry") or {}

    if geometry.get("type") != "LineString":
        continue

    coords = geometry.get("coordinates", [])
    props = feature.get("properties") or {}

    road_name = props.get("name") or "Khong ten"
    road_type = props.get("highway") or "unknown"
    osm_id = str(feature.get("id") or "")

    for i in range(len(coords) - 1):
        a = to_xy(*coords[i][:2])
        b = to_xy(*coords[i + 1][:2])

        clipped = clip_segment(a, b, RADIUS)

        if clipped is None:
            continue

        p, q = clipped
        length = math.dist(p, q)

        if length < 1.0:
            continue

        # Chia doan thanh cac phan dai toi da 50 m
        parts = max(1, math.ceil(length / MAX_LENGTH))

        for k in range(parts):
            t0 = k / parts
            t1 = (k + 1) / parts

            x0 = p[0] + (q[0] - p[0]) * t0
            y0 = p[1] + (q[1] - p[1]) * t0

            x1 = p[0] + (q[0] - p[0]) * t1
            y1 = p[1] + (q[1] - p[1]) * t1

            mx = (x0 + x1) / 2
            my = (y0 + y1) / 2

            start_lon, start_lat = to_gps(x0, y0)
            end_lon, end_lat = to_gps(x1, y1)
            mid_lon, mid_lat = to_gps(mx, my)

            segment_number += 1

            rows.append([
                f"R{segment_number}",
                osm_id,
                road_name,
                road_type,
                round(start_lat, 8),
                round(start_lon, 8),
                round(end_lat, 8),
                round(end_lon, 8),
                round(mid_lat, 8),
                round(mid_lon, 8),
                round(math.dist((x0, y0), (x1, y1)), 2)
            ])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with open(OUTPUT, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)

    writer.writerow([
        "segment_id",
        "osm_id",
        "road_name",
        "highway",
        "start_lat",
        "start_lon",
        "end_lat",
        "end_lon",
        "mid_lat",
        "mid_lon",
        "length_m"
    ])

    writer.writerows(rows)

print("=== TAO ROAD SEGMENTS ===")
print("So duong OSM dau vao:", len(data["features"]))
print("Ban kinh:", RADIUS, "m")
print("Do dai toi da moi doan:", MAX_LENGTH, "m")
print("Tong so doan duong:", len(rows))
print("Da luu:", OUTPUT)
