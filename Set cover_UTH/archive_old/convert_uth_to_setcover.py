
import csv
from pathlib import Path

CAMERA_FILE = Path(
    "data/osm/camera_locations.csv"
)

MATRIX_FILE = Path(
    "data/osm/coverage_matrix.csv"
)

OUTPUT_FILE = Path(
    "data/osm/uth_setcover.txt"
)

# Doc camera va chi phi
with open(
    CAMERA_FILE, encoding="utf-8-sig"
) as f:
    cameras = list(csv.DictReader(f))

# Doc ma tran phu
with open(
    MATRIX_FILE, encoding="utf-8-sig"
) as f:
    reader = csv.DictReader(f)
    matrix_rows = list(reader)
    matrix_columns = reader.fieldnames[1:]

m = len(matrix_rows)
n = len(cameras)

camera_ids = [
    camera["camera_id"]
    for camera in cameras
]

assert matrix_columns == camera_ids, (
    "Thu tu camera trong 2 file khong khop"
)

costs = [int(camera["cost"]) for camera in cameras]

assert m > 0 and n > 0
assert all(cost > 0 for cost in costs)

# Dinh dang Set Cover:
# m n
# n chi phi camera
# moi hang: so camera phu va ID camera (1-based)
with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:
    f.write(f"{m} {n}\n")
    f.write(" ".join(map(str, costs)) + "\n")

    for row in matrix_rows:
        covering = [
            j + 1
            for j, camera_id in enumerate(camera_ids)
            if int(row[camera_id]) == 1
        ]

        if not covering:
            raise ValueError(
                f"Doan {row['segment_id']} chua duoc phu"
            )

        f.write(
            str(len(covering))
            + " "
            + " ".join(map(str, covering))
            + "\n"
        )

print("=== CHUYEN DOI DU LIEU UTH ===")
print("So doan duong:", m)
print("So camera ung vien:", n)
print("Chi phi nho nhat:", min(costs))
print("Chi phi lon nhat:", max(costs))
print("Da luu:", OUTPUT_FILE)

# Kiem tra file moi bang mo hinh hien co
from utils.set_cover_model import SetCoverModel

model = SetCoverModel(str(OUTPUT_FILE))

assert model.m == m
assert model.n == n
assert model.is_feasible(range(n))

print("Doc lai bang SetCoverModel: THANH CONG")
print("Tat ca doan duong co the duoc phu: TRUE")
