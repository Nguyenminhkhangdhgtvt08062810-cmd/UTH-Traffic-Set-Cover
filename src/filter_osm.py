
# Duong dan lam viec: thu muc goc bai nop.
import os as _project_os
from pathlib import Path as _project_Path
_project_os.chdir(_project_Path(__file__).resolve().parent.parent)

import json
from pathlib import Path
from collections import Counter

input_path = Path("data/osm/roads.geojson")
output_path = Path("data/osm/filtered_roads.geojson")

# Cac loai duong giu lai
allowed_highways = {
    "residential",
    "tertiary",
    "secondary",
    "primary",
    "trunk"
}

with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

filtered_features = []

for feature in data["features"]:
    properties = feature.get("properties") or {}
    geometry = feature.get("geometry") or {}

    highway = properties.get("highway")

    # Chi giu duong dung loai va co toa do
    if highway not in allowed_highways:
        continue

    if geometry.get("type") != "LineString":
        continue

    if len(geometry.get("coordinates", [])) < 2:
        continue

    filtered_features.append(feature)

filtered_data = {
    "type": "FeatureCollection",
    "features": filtered_features
}

output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(
        filtered_data,
        f,
        ensure_ascii=False,
        indent=2
    )

print("=== LOC DU LIEU OSM ===")
print("Ban dau:", len(data["features"]))
print("Sau khi loc:", len(filtered_features))

counts = Counter(
    f["properties"]["highway"]
    for f in filtered_features
)

print("\nThong ke sau loc:")
for name, count in counts.most_common():
    print(f"{name}: {count}")

print("\nDa luu:", output_path)
