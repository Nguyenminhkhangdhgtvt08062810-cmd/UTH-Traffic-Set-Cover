
import json
import time
import html
from pathlib import Path

import folium
from branca.element import Element

from utils.set_cover_model import SetCoverModel
from utils.validator import validate_solution
from algorithms.greedy import greedy_set_cover
from algorithms.local_search import (
    hill_climbing_first,
    hill_climbing_best
)
from algorithms.simulated_annealing import simulated_annealing


# ==========================================
# 1. CAU HINH
# ==========================================

UTH_LAT = 10.804816
UTH_LON = 106.716878

MODEL_FILE = "data/osm/uth_setcover.txt"
ROADS_FILE = "data/osm/roads_near_uth.geojson"
CAMERAS_FILE = "data/osm/camera_locations.csv"

OUTPUT_FILE = Path("results/uth_comparison_demo.html")

import csv

with open(CAMERAS_FILE, encoding="utf-8-sig") as f:
    cameras = list(csv.DictReader(f))

with open(ROADS_FILE, encoding="utf-8") as f:
    roads = json.load(f)

model = SetCoverModel(MODEL_FILE)

assert len(cameras) == model.n

data = {
    "m": model.m,
    "n": model.n,
    "costs": model.costs,
    "rows": model.rows,
    "columns": model.columns
}


# ==========================================
# 2. CHAY CAC THUAT TOAN PYTHON
# ==========================================

algorithms = {}

start = time.perf_counter()
greedy = greedy_set_cover(model)
greedy_time = time.perf_counter() - start

algorithms["Greedy"] = (greedy, greedy_time)

start = time.perf_counter()
first = hill_climbing_first(model, greedy)
first_time = time.perf_counter() - start

algorithms["First Improvement"] = (
    first, first_time
)

start = time.perf_counter()
best = hill_climbing_best(model, greedy)
best_time = time.perf_counter() - start

algorithms["Best Improvement"] = (
    best, best_time
)

start = time.perf_counter()
sa = simulated_annealing(
    model,
    greedy,
    initial_temp=10.0,
    cooling_rate=0.99,
    min_temp=0.01,
    max_iterations=5000,
    seed=42
)
sa_time = time.perf_counter() - start

algorithms["SA"] = (sa, sa_time)


# ==========================================
# 3. KIEM TRA VA CHUAN BI KET QUA
# ==========================================

results = {}

for name, (solution, elapsed) in algorithms.items():
    valid, cost, message = validate_solution(
        data, solution
    )

    if not valid:
        raise ValueError(f"{name}: {message}")

    results[name] = {
        "cost": cost,
        "num_cameras": len(solution),
        "coverage": model.coverage_rate(solution),
        "time": round(elapsed, 5),
        "selected": solution
    }

    print(
        f"{name}: {len(solution)} camera, "
        f"cost={cost}, coverage=100%"
    )


# ==========================================
# 4. TAO BAN DO
# ==========================================

m = folium.Map(
    location=[UTH_LAT, UTH_LON],
    zoom_start=16,
    tiles=None,
    control_scale=True
)

folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/ArcGIS/rest/"
        "services/World_Street_Map/MapServer/tile/"
        "{z}/{y}/{x}"
    ),
    attr="Tiles © Esri and contributors",
    name="Esri World Street Map"
).add_to(m)

folium.GeoJson(
    roads,
    style_function=lambda f: {
        "color": "#64748b",
        "weight": 3,
        "opacity": 0.75
    }
).add_to(m)

folium.Circle(
    [UTH_LAT, UTH_LON],
    radius=500,
    color="#2563eb",
    fill=False
).add_to(m)

folium.Marker(
    [UTH_LAT, UTH_LON],
    tooltip="UTH Cơ sở 1",
    icon=folium.Icon(
        color="blue",
        icon="graduation-cap",
        prefix="fa"
    )
).add_to(m)


# ==========================================
# 5. TAO LOP CAMERA THEO THUAT TOAN
# ==========================================

layers = {}

for name, result in results.items():
    layer = folium.FeatureGroup(
        name=name,
        show=(name == "SA"),
        control=False
    )

    for j in result["selected"]:
        camera = cameras[j]

        lat = float(camera["lat"])
        lon = float(camera["lon"])

        popup = (
            f"<b>{html.escape(camera['camera_id'])}</b><br>"
            f"Đường: {html.escape(camera['road_name'])}<br>"
            f"Chi phí: {html.escape(camera['cost'])}<br>"
            f"Thuật toán: {html.escape(name)}"
        )

        folium.Marker(
            [lat, lon],
            popup=folium.Popup(popup, max_width=300),
            tooltip=camera["camera_id"],
            icon=folium.Icon(
                color="red",
                icon="camera",
                prefix="fa"
            )
        ).add_to(layer)

    layer.add_to(m)
    layers[name] = layer.get_name()


# ==========================================
# 6. TAO BANG DIEU KHIEN
# ==========================================

map_name = m.get_name()

layer_names_json = json.dumps(layers, ensure_ascii=False)
results_json = json.dumps(results, ensure_ascii=False)

panel = """
<style>
#demo-panel {
    position: fixed;
    top: 20px;
    left: 20px;
    z-index: 9999;
    width: 300px;
    max-width: calc(100vw - 40px);
    background: white;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,.18);
    font-family: Arial, sans-serif;
    color: #1f2937;
}
#demo-panel h3 {
    margin: 0 0 12px;
    color: #1d4ed8;
    font-size: 17px;
}
#demo-panel select {
    width: 100%;
    padding: 9px;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    margin-bottom: 12px;
}
.demo-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid #e5e7eb;
    font-size: 13px;
}
.demo-note {
    margin-top: 12px;
    color: #64748b;
    font-size: 11px;
    line-height: 1.5;
}
</style>

<div id="demo-panel">
    <h3>SO SÁNH THUẬT TOÁN – UTH</h3>

    <label for="algorithm-select">Chọn thuật toán:</label>
    <select id="algorithm-select">
        <option value="Greedy">Greedy</option>
        <option value="First Improvement">
            First Improvement
        </option>
        <option value="Best Improvement">
            Best Improvement
        </option>
        <option value="SA" selected>
            Simulated Annealing
        </option>
    </select>

    <div class="demo-row">
        <span>Đoạn đường:</span>
        <strong>504</strong>
    </div>
    <div class="demo-row">
        <span>Camera ứng viên:</span>
        <strong>64</strong>
    </div>
    <div class="demo-row">
        <span>Camera được chọn:</span>
        <strong id="num-cameras"></strong>
    </div>
    <div class="demo-row">
        <span>Tổng chi phí:</span>
        <strong id="total-cost"></strong>
    </div>
    <div class="demo-row">
        <span>Độ phủ:</span>
        <strong id="coverage"></strong>
    </div>
    <div class="demo-row">
        <span>Thời gian chạy:</span>
        <strong id="runtime"></strong>
    </div>

    <div class="demo-note">
        Kết quả được tính bằng các thuật toán Python
        trước khi tạo bản đồ. Chi phí và phạm vi
        camera là giả định mô phỏng.
    </div>
</div>
"""

m.get_root().html.add_child(Element(panel))

script = """
<script>
(function() {
    const results = RESULTS_JSON;
    const layerNames = LAYER_NAMES_JSON;
    const map = MAP_VARIABLE;

    function updateAlgorithm(name) {
        for (const [algorithm, layerName] of
            Object.entries(layerNames)) {

            const layer = window[layerName];

            if (!layer) continue;

            if (algorithm === name) {
                if (!map.hasLayer(layer)) {
                    map.addLayer(layer);
                }
            } else {
                if (map.hasLayer(layer)) {
                    map.removeLayer(layer);
                }
            }
        }

        const r = results[name];

        document.getElementById("num-cameras")
            .textContent = r.num_cameras;

        document.getElementById("total-cost")
            .textContent = r.cost;

        document.getElementById("coverage")
            .textContent = r.coverage.toFixed(1) + "%";

        document.getElementById("runtime")
            .textContent = r.time.toFixed(5) + " s";
    }

    const select = document.getElementById(
        "algorithm-select"
    );

    select.addEventListener("change", function() {
        updateAlgorithm(this.value);
    });

    updateAlgorithm(select.value);
})();
</script>
"""

script = script.replace(
    "RESULTS_JSON", results_json
).replace(
    "LAYER_NAMES_JSON", layer_names_json
).replace(
    "MAP_VARIABLE", map_name
)

m.get_root().script.add_child(Element(
    script.replace("<script>", "").replace("</script>", "")
))


# ==========================================
# 7. LUU FILE DEMO
# ==========================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

m.save(str(OUTPUT_FILE))

print("\n=== TAO DEMO SO SANH ===")
print("Da luu:", OUTPUT_FILE)
print("TAO DEMO THANH CONG")
