
import json

path = "data/osm/filtered_roads.geojson"

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

lons = []
lats = []

for feature in data["features"]:
    geometry = feature.get("geometry") or {}
    coords = geometry.get("coordinates", [])

    for point in coords:
        lon, lat = point[:2]
        lons.append(lon)
        lats.append(lat)

print("=== PHAM VI DU LIEU OSM ===")
print("So duong:", len(data["features"]))

print("Kinh do nho nhat:", min(lons))
print("Kinh do lon nhat:", max(lons))
print("Vi do nho nhat:", min(lats))
print("Vi do lon nhat:", max(lats))

print("\nTam pham vi du lieu:")
print("Latitude:", (min(lats) + max(lats)) / 2)
print("Longitude:", (min(lons) + max(lons)) / 2)
