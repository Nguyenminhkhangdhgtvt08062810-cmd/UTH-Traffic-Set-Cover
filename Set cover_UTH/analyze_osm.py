
import json
from collections import Counter

with open(
    "data/osm/roads.geojson",
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)

features = data["features"]

# Dem theo loai duong
highway_counts = Counter()

# Dem theo ten duong
road_names = Counter()

for feature in features:
    properties = feature.get("properties") or {}

    highway = properties.get("highway", "unknown")
    name = properties.get("name")

    highway_counts[highway] += 1

    if name:
        road_names[name] += 1

print("=== THONG KE DU LIEU OSM ===")
print("Tong so doi tuong:", len(features))

print("\n=== LOAI DUONG ===")
for highway, count in highway_counts.most_common():
    print(f"{highway}: {count}")

print("\n=== 20 TEN DUONG XUAT HIEN NHIEU NHAT ===")
for name, count in road_names.most_common(20):
    print(f"{name}: {count}")

print("\nSO DOI TUONG CO TEN:", sum(road_names.values()))
print("SO TEN DUONG KHAC NHAU:", len(road_names))
