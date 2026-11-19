
import csv
import math
from pathlib import Path

SEGMENTS = Path("data/osm/road_segments.csv")
CAMERAS = Path("data/osm/camera_locations.csv")
OUTPUT = Path("data/osm/coverage_matrix.csv")

COVERAGE_RADIUS = 120.0
EARTH_RADIUS = 6371000.0


def distance_m(lat1, lon1, lat2, lon2):
    """Khoang cach GPS giua hai diem, don vi met."""
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = (
        math.sin(dp / 2) ** 2
        + math.cos(p1) * math.cos(p2)
        * math.sin(dl / 2) ** 2
    )

    return 2 * EARTH_RADIUS * math.asin(
        min(1.0, math.sqrt(a))
    )


with open(SEGMENTS, encoding="utf-8-sig") as f:
    segments = list(csv.DictReader(f))

with open(CAMERAS, encoding="utf-8-sig") as f:
    cameras = list(csv.DictReader(f))

matrix = []
uncovered = []

for segment in segments:
    row = []

    for camera in cameras:
        distance = distance_m(
            float(segment["mid_lat"]),
            float(segment["mid_lon"]),
            float(camera["lat"]),
            float(camera["lon"])
        )

        row.append(
            1 if distance <= COVERAGE_RADIUS else 0
        )

    matrix.append(row)

    if sum(row) == 0:
        uncovered.append(segment["segment_id"])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with open(
    OUTPUT, "w", newline="", encoding="utf-8-sig"
) as f:
    writer = csv.writer(f)

    writer.writerow([
        "segment_id",
        *[camera["camera_id"] for camera in cameras]
    ])

    for segment, row in zip(segments, matrix):
        writer.writerow([
            segment["segment_id"], *row
        ])

print("=== TAO MA TRAN PHU CAMERA ===")
print("So doan duong:", len(segments))
print("So camera ung vien:", len(cameras))
print("Ban kinh phu:", COVERAGE_RADIUS, "m")
print("Kich thuoc ma tran:", len(matrix), "x", len(cameras))
print("So doan duong chua co camera phu:", len(uncovered))

if uncovered:
    print("Mot so doan chua phu:", uncovered[:15])
    print("CAN DIEU CHINH MO HINH TRUOC KHI GIAI.")
else:
    print("Tat ca doan duong deu co it nhat 1 ung vien phu.")

print("Da luu:", OUTPUT)
