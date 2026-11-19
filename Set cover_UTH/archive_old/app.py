
import csv
import json
import time
import html

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from utils.set_cover_model import SetCoverModel
from utils.validator import validate_solution

from algorithms.greedy import greedy_set_cover
from algorithms.local_search import (
    hill_climbing_first,
    hill_climbing_best
)
from algorithms.simulated_annealing import simulated_annealing


# ==================================================
# 1. CAU HINH UNG DUNG
# ==================================================

st.set_page_config(
    page_title="UTH Camera Optimization",
    page_icon="📷",
    layout="wide"
)

UTH_LAT = 10.804816
UTH_LON = 106.716878

MODEL_FILE = "data/osm/uth_setcover.txt"
ROADS_FILE = "data/osm/roads_near_uth.geojson"
CAMERA_FILE = "data/osm/camera_locations.csv"

STUDY_RADIUS = 500
CAMERA_RADIUS = 120


# ==================================================
# 2. DOC DU LIEU
# ==================================================

@st.cache_data
def load_files():

    with open(
        CAMERA_FILE,
        encoding="utf-8-sig"
    ) as f:
        cameras = list(csv.DictReader(f))

    with open(
        ROADS_FILE,
        encoding="utf-8"
    ) as f:
        roads = json.load(f)

    return cameras, roads


cameras, roads = load_files()

model = SetCoverModel(MODEL_FILE)

data = {
    "m": model.m,
    "n": model.n,
    "costs": model.costs,
    "rows": model.rows,
    "columns": model.columns
}

if len(cameras) != model.n:
    st.error(
        "So camera trong CSV va mo hinh khong khop."
    )
    st.stop()


# ==================================================
# 3. TIEU DE UNG DUNG
# ==================================================

st.title("📷 UTH – Traffic Camera Optimization")

st.caption(
    "Mô phỏng tối ưu vị trí đặt camera giao thông "
    "bằng bài toán Weighted Set Cover."
)


# ==================================================
# 4. THANH DIEU KHIEN
# ==================================================

st.sidebar.header("⚙️ Điều khiển")

algorithm = st.sidebar.selectbox(
    "Chọn thuật toán",
    [
        "Greedy",
        "First Improvement",
        "Best Improvement",
        "Simulated Annealing"
    ],
    index=3
)

st.sidebar.divider()

st.sidebar.subheader("Hiển thị bản đồ")

show_candidates = st.sidebar.checkbox(
    "Hiện camera ứng viên chưa chọn",
    value=False
)

show_coverage = st.sidebar.checkbox(
    "Hiện bán kính phủ 120 m",
    value=False
)

st.sidebar.divider()


# ==================================================
# 5. THAM SO SIMULATED ANNEALING
# ==================================================

# Gia tri mac dinh
temperature = 10.0
cooling_rate = 0.99
seed = 42
max_iterations = 5000

# Chi hien khi chon SA
if algorithm == "Simulated Annealing":

    st.sidebar.subheader(
        "🌡️ Tham số Simulated Annealing"
    )

    temperature = st.sidebar.number_input(
        "Nhiệt độ ban đầu",
        min_value=0.1,
        value=10.0,
        step=1.0
    )

    cooling_rate = st.sidebar.number_input(
        "Cooling rate",
        min_value=0.001,
        max_value=0.999,
        value=0.99,
        step=0.001,
        format="%.3f"
    )

    seed = st.sidebar.number_input(
        "Random seed",
        min_value=0,
        value=42,
        step=1
    )

    max_iterations = st.sidebar.number_input(
        "Số vòng lặp tối đa",
        min_value=1,
        value=5000,
        step=500
    )

    st.sidebar.caption(
        "Thay đổi tham số để quan sát "
        "kết quả tìm kiếm của SA."
    )


# ==================================================
# 6. NUT CHAY THUAT TOAN
# ==================================================

run_button = st.sidebar.button(
    "▶ Chạy thuật toán",
    type="primary",
    width="stretch"
)


# ==================================================
# 7. CHAY THUAT TOAN BANG PYTHON
# ==================================================

current_config = (
    algorithm,
    float(temperature) if algorithm == "Simulated Annealing" else None,
    float(cooling_rate) if algorithm == "Simulated Annealing" else None,
    int(seed) if algorithm == "Simulated Annealing" else None,
    int(max_iterations) if algorithm == "Simulated Annealing" else None
)

if run_button or "result" not in st.session_state:

    with st.spinner("Đang chạy thuật toán..."):

        start = time.perf_counter()

        # Greedy tao nghiem ban dau
        greedy = greedy_set_cover(model)

        if algorithm == "Greedy":

            solution = greedy

        elif algorithm == "First Improvement":

            solution = hill_climbing_first(
                model,
                greedy
            )

        elif algorithm == "Best Improvement":

            solution = hill_climbing_best(
                model,
                greedy
            )

        elif algorithm == "Simulated Annealing":

            solution = simulated_annealing(
                model,
                greedy,
                initial_temp=float(temperature),
                cooling_rate=float(cooling_rate),
                min_temp=0.01,
                max_iterations=int(max_iterations),
                seed=int(seed)
            )

        elapsed = time.perf_counter() - start

        # Kiem tra nghiem
        valid, cost, message = validate_solution(
            data,
            solution
        )

        if not valid:
            st.error(
                f"Nghiem khong hop le: {message}"
            )
            st.stop()

        # Luu ket qua
        st.session_state.result = {
            "algorithm": algorithm,
            "solution": list(solution),
            "cost": cost,
            "time": elapsed,
            "coverage": model.coverage_rate(solution),
            "config": current_config
        }


result = st.session_state.result
solution = result["solution"]

# Canh bao neu thay doi thuat toan
# hoac tham so nhung chua bam chay
if result["config"] != current_config:

    st.info(
        "Các thiết lập đã được thay đổi. "
        "Nhấn 'Chạy thuật toán' để xem kết quả mới."
    )


# ==================================================
# 8. HIEN THI THONG KE
# ==================================================

st.subheader(
    f"📊 Kết quả: {result['algorithm']}"
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Đoạn đường",
    model.m
)

c2.metric(
    "Camera được chọn",
    len(solution)
)

c3.metric(
    "Tổng chi phí",
    result["cost"]
)

c4.metric(
    "Độ phủ",
    f"{result['coverage']:.1f}%"
)

st.write(
    f"**Thời gian chạy:** "
    f"{result['time']:.4f} giây"
)

st.success(
    "Nghiệm hợp lệ – đã kiểm tra bằng Validator."
)


# ==================================================
# 9. TAO BAN DO FOLIUM
# ==================================================

m = folium.Map(
    location=[UTH_LAT, UTH_LON],
    zoom_start=16,
    tiles=None,
    control_scale=True
)

# Nen ban do Esri
folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/ArcGIS/rest/"
        "services/World_Street_Map/MapServer/tile/"
        "{z}/{y}/{x}"
    ),
    attr="Tiles © Esri and contributors",
    name="Esri World Street Map"
).add_to(m)


# ==================================================
# 10. DUONG GIAO THONG
# ==================================================

folium.GeoJson(
    roads,
    name="Đường giao thông OSM",
    style_function=lambda feature: {
        "color": "#64748b",
        "weight": 3,
        "opacity": 0.75
    }
).add_to(m)


# ==================================================
# 11. PHAM VI NGHIEN CUU
# ==================================================

folium.Circle(
    location=[UTH_LAT, UTH_LON],
    radius=STUDY_RADIUS,
    color="#2563eb",
    weight=2,
    fill=False,
    tooltip="Phạm vi nghiên cứu 500 m"
).add_to(m)


# ==================================================
# 12. DANH DAU UTH
# ==================================================

folium.Marker(
    location=[UTH_LAT, UTH_LON],
    tooltip="UTH - Cơ sở 1",
    popup="Trường Đại học Giao thông vận tải TP.HCM",
    icon=folium.Icon(
        color="blue",
        icon="graduation-cap",
        prefix="fa"
    )
).add_to(m)


# ==================================================
# 13. CAMERA UNG VIEN CHUA CHON
# ==================================================

selected_set = set(solution)

if show_candidates:

    for j, camera in enumerate(cameras):

        if j in selected_set:
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
            fill_opacity=0.8,
            tooltip=(
                f"Ứng viên {camera['camera_id']}"
            )
        ).add_to(m)


# ==================================================
# 14. CAMERA DUOC THUAT TOAN CHON
# ==================================================

for j in solution:

    camera = cameras[j]

    lat = float(camera["lat"])
    lon = float(camera["lon"])

    camera_id = html.escape(camera["camera_id"])
    road_name = html.escape(camera["road_name"])
    road_type = html.escape(camera["highway"])
    cost = html.escape(str(camera["cost"]))

    popup_html = f"""
    <div style="
        font-family:Arial;
        min-width:200px;
        line-height:1.7;
    ">
        <h3>Camera {camera_id}</h3>
        <b>Đường:</b> {road_name}<br>
        <b>Loại đường:</b> {road_type}<br>
        <b>Chi phí:</b> {cost}<br>
        <b>Bán kính phủ:</b> {CAMERA_RADIUS} m<br>
        <b>Thuật toán:</b>
        {html.escape(result['algorithm'])}
    </div>
    """

    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(
            popup_html,
            max_width=320
        ),
        tooltip=f"Camera {camera_id}",
        icon=folium.Icon(
            color="red",
            icon="camera",
            prefix="fa"
        )
    ).add_to(m)

    # Hien thi pham vi phu neu duoc bat
    if show_coverage:

        folium.Circle(
            location=[lat, lon],
            radius=CAMERA_RADIUS,
            color="#16a34a",
            weight=1,
            fill=True,
            fill_color="#22c55e",
            fill_opacity=0.07,
            tooltip=(
                f"Phạm vi phủ {CAMERA_RADIUS} m"
            )
        ).add_to(m)


# ==================================================
# 15. HIEN THI BAN DO
# ==================================================

st.subheader("🗺️ Bản đồ vị trí camera")

st_folium(
    m,
    height=620,
    width=1100,
    returned_objects=[],
    key="uth_map"
)


# ==================================================
# 16. DANH SACH CAMERA
# ==================================================

st.subheader("📋 Danh sách camera được lựa chọn")

selected_rows = []

for j in solution:

    camera = cameras[j]

    selected_rows.append({
        "Camera": camera["camera_id"],
        "Tên đường": camera["road_name"],
        "Loại đường": camera["highway"],
        "Chi phí": int(camera["cost"]),
        "Vĩ độ": float(camera["lat"]),
        "Kinh độ": float(camera["lon"])
    })

df = pd.DataFrame(selected_rows)

st.dataframe(
    df,
    width="stretch",
    hide_index=True
)


# ==================================================
# 17. TAI KET QUA CSV
# ==================================================

csv_data = df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    "⬇ Tải danh sách camera CSV",
    data=csv_data,
    file_name="uth_selected_cameras.csv",
    mime="text/csv",
    width="stretch"
)


# ==================================================
# 18. GHI CHU
# ==================================================

st.divider()

st.caption(
    "Dữ liệu đường giao thông được xử lý từ OpenStreetMap. "
    "Chi phí và bán kính phủ là giả định mô phỏng. "
    "Kết quả chưa xét đầy đủ góc quan sát, "
    "vật cản và điều kiện lắp đặt camera thực tế."
)
