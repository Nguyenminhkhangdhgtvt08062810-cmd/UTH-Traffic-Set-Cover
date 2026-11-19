
import csv
import math
from pathlib import Path

INPUT = Path("data/osm/road_segments.csv")
OUTPUT = Path("data/osm/camera_locations.csv")

UTH_LAT = 10.804816
UTH_LON = 106.716878

MIN_DISTANCE = 80.0
EARTH_RADIUS = 6371000.0


def distance_m(lat1, lon1, lat2, lon2):
    """Tinh khoang cach giua hai vi tri GPS."""
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

    return 2 * EARTH_RADIUS * math.asin(
        min(1.0, math.sqrt(a))
    )


with open(INPUT, "r", encoding="utf-8-sig") as f:
    segments = list(csv.DictReader(f))

# Sap xep theo ID de ket qua co the tai lap
segments.sort(
    key=lambda row: int(row["segment_id"][1:])
)

cameras = []

for segment in segments:
    lat = float(segment["mid_lat"])
    lon = float(segment["mid_lon"])

    # Khong tao camera qua gan camera da co
    too_close = any(
        distance_m(
            lat, lon,
            camera["lat"], camera["lon"]
        ) < MIN_DISTANCE
        for camera in cameras
    )

    if too_close:
        continue

    # Chi phi mo phong dua theo loai duong
    highway = segment["highway"]

    cost_by_type = {
        "residential": 5,
        "tertiary": 7,
        "secondary": 9,
        "primary": 11,
        "trunk": 13
    }

    cost = cost_by_type.get(highway, 8)

    cameras.append({
        "camera_id": f"C{len(cameras) + 1}",
        "lat": lat,
        "lon": lon,
        "cost": cost,
        "road_name": segment["road_name"],
        "highway": highway
    })


OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with open(
    OUTPUT, "w",
    newline="",
    encoding="utf-8-sig"
) as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "camera_id",
            "lat",
            "lon",
            "cost",
            "road_name",
            "highway"
        ]
    )

    writer.writeheader()
    writer.writerows(cameras)


print("=== TAO VI TRI CAMERA UNG VIEN ===")
print("So doan duong:", len(segments))
print("Khoang cach toi thieu:", MIN_DISTANCE, "m")
print("So vi tri camera:", len(cameras))
print("Da luu:", OUTPUT)
