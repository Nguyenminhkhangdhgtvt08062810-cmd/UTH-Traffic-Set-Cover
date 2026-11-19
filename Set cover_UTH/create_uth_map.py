
import csv
import json
import html
from pathlib import Path

import folium

# ==================================================
# 1. CAU HINH DU AN
# ==================================================

UTH_LAT = 10.804816
UTH_LON = 106.716878

STUDY_RADIUS = 500
CAMERA_RADIUS = 120

ROADS_FILE = Path("data/osm/roads_near_uth.geojson")
CAMERAS_FILE = Path("data/osm/camera_locations.csv")
SELECTED_FILE = Path("results/uth_selected_cameras.csv")
OUTPUT_FILE = Path("results/uth_camera_map.html")


# ==================================================
# 2. DOC DU LIEU
# ==================================================

with open(ROADS_FILE, "r", encoding="utf-8") as f:
    roads = json.load(f)

with open(CAMERAS_FILE, "r", encoding="utf-8-sig") as f:
    cameras = list(csv.DictReader(f))

with open(SELECTED_FILE, "r", encoding="utf-8-sig") as f:
    selected = list(csv.DictReader(f))

selected_ids = {
    camera["camera_id"] for camera in selected
}

total_cost = sum(
    int(camera["cost"]) for camera in selected
)

# Du lieu ket qua da kiem chung tu run_uth.py
TOTAL_SEGMENTS = 504
COVERAGE_PERCENT = 100.0


# ==================================================
# 3. TAO BAN DO VOI NEN ESRI
# ==================================================

m = folium.Map(
    location=[UTH_LAT, UTH_LON],
    zoom_start=16,
    tiles=None,
    control_scale=True,
    prefer_canvas=True
)

# Su dung Esri World Street Map
folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/ArcGIS/rest/"
        "services/World_Street_Map/MapServer/tile/"
        "{z}/{y}/{x}"
    ),
    attr="Tiles &copy; Esri and contributors",
    name="Esri World Street Map",
    overlay=False,
    control=True
).add_to(m)


# ==================================================
# 4. LOP DUONG GIAO THONG OSM
# ==================================================

road_layer = folium.FeatureGroup(
    name="Đường giao thông OSM",
    show=True
)

folium.GeoJson(
    roads,
    name="Roads",
    style_function=lambda feature: {
        "color": "#64748b",
        "weight": 3,
        "opacity": 0.8
    }
).add_to(road_layer)

road_layer.add_to(m)


# ==================================================
# 5. CAMERA UNG VIEN CHUA CHON
# ==================================================

candidate_layer = folium.FeatureGroup(
    name="Camera ứng viên chưa chọn",
    show=False
)

for camera in cameras:
    camera_id = camera["camera_id"]

    if camera_id in selected_ids:
        continue

    folium.CircleMarker(
        location=[
            float(camera["lat"]),
            float(camera["lon"])
        ],
        radius=5,
        color="#64748b",
        weight=1,
        fill=True,
        fill_color="#94a3b8",
        fill_opacity=0.85,
        tooltip=f"Camera ứng viên {camera_id}"
    ).add_to(candidate_layer)

candidate_layer.add_to(m)


# ==================================================
# 6. PHAM VI PHU CUA CAMERA DUOC CHON
# ==================================================

coverage_layer = folium.FeatureGroup(
    name="Phạm vi phủ camera 120 m",
    show=False
)

for camera in selected:
    lat = float(camera["lat"])
    lon = float(camera["lon"])
    camera_id = camera["camera_id"]

    folium.Circle(
        location=[lat, lon],
        radius=CAMERA_RADIUS,
        color="#16a34a",
        weight=1,
        fill=True,
        fill_color="#22c55e",
        fill_opacity=0.07,
        tooltip=(
            f"{camera_id}: bán kính phủ "
            f"{CAMERA_RADIUS} m"
        )
    ).add_to(coverage_layer)

coverage_layer.add_to(m)


# ==================================================
# 7. CAMERA DUOC THUAT TOAN SA CHON
# ==================================================

selected_layer = folium.FeatureGroup(
    name="Camera được SA chọn",
    show=True
)

for camera in selected:
    camera_id = camera["camera_id"]

    lat = float(camera["lat"])
    lon = float(camera["lon"])

    safe_id = html.escape(camera_id)
    road_name = html.escape(camera["road_name"])
    road_type = html.escape(camera["highway"])
    cost = html.escape(str(camera["cost"]))

    popup_html = f"""
    <div style="
        font-family: Arial, sans-serif;
        min-width: 210px;
        line-height: 1.7;
    ">
        <h3 style="
            margin: 0 0 8px;
            color: #1e3a5f;
        ">
            Camera {safe_id}
        </h3>

        <b>Tên đường:</b> {road_name}<br>
        <b>Loại đường:</b> {road_type}<br>
        <b>Chi phí mô phỏng:</b> {cost}<br>
        <b>Bán kính phủ:</b> {CAMERA_RADIUS} m<br>
        <b>Thuật toán:</b> Simulated Annealing
    </div>
    """

    folium.Marker(
        location=[lat, lon],
        tooltip=f"Camera {camera_id}",
        popup=folium.Popup(
            popup_html,
            max_width=320
        ),
        icon=folium.Icon(
            color="red",
            icon="camera",
            prefix="fa"
        )
    ).add_to(selected_layer)

selected_layer.add_to(m)


# ==================================================
# 8. DANH DAU UTH CO SO 1
# ==================================================

folium.Marker(
    location=[UTH_LAT, UTH_LON],
    tooltip="UTH - Cơ sở 1",
    popup=folium.Popup(
        "Trường Đại học Giao thông vận tải TP.HCM"
        " - Cơ sở 1",
        max_width=300
    ),
    icon=folium.Icon(
        color="blue",
        icon="graduation-cap",
        prefix="fa"
    )
).add_to(m)


# ==================================================
# 9. RANH GIOI KHU VUC NGHIEN CUU
# ==================================================

folium.Circle(
    location=[UTH_LAT, UTH_LON],
    radius=STUDY_RADIUS,
    color="#2563eb",
    weight=2,
    fill=False,
    tooltip="Khu vực nghiên cứu - bán kính 500 m"
).add_to(m)


# ==================================================
# 10. BANG THONG KE GON GANG
# ==================================================

info_html = f"""
<style>
    .uth-info {{
        position: fixed;
        left: 16px;
        bottom: 28px;
        z-index: 9999;

        box-sizing: border-box;
        width: 280px;
        max-width: calc(100vw - 32px);

        background: rgba(255,255,255,0.97);
        border: 1px solid #e2e8f0;
        border-radius: 12px;

        padding: 14px 16px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.15);

        font-family: Arial, sans-serif;
        font-size: 13px;
        color: #1f2937;
    }}

    .uth-info h3 {{
        margin: 0 0 10px;
        font-size: 15px;
        color: #1d4ed8;
        line-height: 1.4;
    }}

    .uth-info .uth-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 8px;
        padding: 4px 0;
        border-bottom: 1px solid #f1f5f9;
    }}

    .uth-info .uth-row strong {{
        white-space: nowrap;
        color: #0f172a;
    }}

    .uth-info .uth-note {{
        margin-top: 9px;
        font-size: 11px;
        line-height: 1.5;
        color: #64748b;
    }}

    @media (max-width: 600px) {{
        .uth-info {{
            width: 230px;
            padding: 10px 12px;
            font-size: 11px;
            bottom: 22px;
        }}

        .uth-info h3 {{
            font-size: 13px;
        }}
    }}
</style>

<div class="uth-info">
    <h3>MÔ PHỎNG CAMERA – UTH</h3>

    <div class="uth-row">
        <span>Đoạn đường</span>
        <strong>{TOTAL_SEGMENTS}</strong>
    </div>

    <div class="uth-row">
        <span>Camera ứng viên</span>
        <strong>{len(cameras)}</strong>
    </div>

    <div class="uth-row">
        <span>Camera được chọn</span>
        <strong>{len(selected)}</strong>
    </div>

    <div class="uth-row">
        <span>Tổng chi phí</span>
        <strong>{total_cost}</strong>
    </div>

    <div class="uth-row">
        <span>Độ phủ mô hình</span>
        <strong>{COVERAGE_PERCENT:.0f}%</strong>
    </div>

    <div class="uth-row">
        <span>Thuật toán</span>
        <strong>SA</strong>
    </div>

    <div class="uth-note">
        Dữ liệu đường từ OpenStreetMap.
        Chi phí và phạm vi phủ là giả định mô phỏng.
    </div>
</div>
"""

m.get_root().html.add_child(
    folium.Element(info_html)
)


# ==================================================
# 11. BAT TAT CAC LOP
# ==================================================

folium.LayerControl(
    collapsed=False,
    position="topright"
).add_to(m)


# ==================================================
# 12. LUU BAN DO HTML
# ==================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

m.save(str(OUTPUT_FILE))

print("=== TAO BAN DO CAMERA UTH ===")
print("So doan duong:", TOTAL_SEGMENTS)
print("So camera ung vien:", len(cameras))
print("So camera SA chon:", len(selected))
print("Tong chi phi:", total_cost)
print("Nen ban do: Esri World Street Map")
print("Da luu:", OUTPUT_FILE)
print("TAO BAN DO THANH CONG")
