
# Duong dan lam viec: thu muc goc bai nop.
import os as _project_os
from pathlib import Path as _project_Path
_project_os.chdir(_project_Path(__file__).resolve().parent.parent)

import json
from pathlib import Path

# Duong dan file ban do
file_path = Path("data/osm/roads.geojson")

if not file_path.exists():
    raise FileNotFoundError(
        "Khong tim thay data/osm/roads.geojson"
    )

# Doc du lieu GeoJSON
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

features = data.get("features", [])

print("=== KIEM TRA DU LIEU OSM ===")
print("Loai du lieu:", data.get("type"))
print("Tong so doi tuong:", len(features))

# Thong ke kieu hinh hoc
geometry_counts = {}

for feature in features:
    geometry = feature.get("geometry") or {}
    geometry_type = geometry.get("type", "Unknown")

    geometry_counts[geometry_type] = (
        geometry_counts.get(geometry_type, 0) + 1
    )

print("\nThong ke hinh hoc:")
for name, count in geometry_counts.items():
    print(f"{name}: {count}")

# Hien thi mot doi tuong dau tien
if features:
    first = features[0]
    properties = first.get("properties") or {}
    geometry = first.get("geometry") or {}

    print("\n=== DOI TUONG DAU TIEN ===")
    print("ID:", first.get("id"))
    print("Ten duong:", properties.get("name", "Khong co ten"))
    print("Loai duong:", properties.get("highway", "Khong ro"))
    print("Kieu hinh hoc:", geometry.get("type"))

print("\nKIEM TRA GEOJSON HOAN TAT")
