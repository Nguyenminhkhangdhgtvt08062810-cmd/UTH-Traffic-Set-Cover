
# Duong dan lam viec: thu muc goc bai nop.
import os as _project_os
from pathlib import Path as _project_Path
_project_os.chdir(_project_Path(__file__).resolve().parent.parent)

import csv
import time
from pathlib import Path

from utils.set_cover_model import SetCoverModel
from utils.validator import validate_solution
from algorithms.greedy import greedy_set_cover
from algorithms.local_search import (
    hill_climbing_first,
    hill_climbing_best
)
from algorithms.simulated_annealing import simulated_annealing


# ============================================
# 1. DUONG DAN DU AN
# ============================================

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "nodes"
RESULTS_DIR = ROOT / "results"

CAMERA_CSV = DATA_DIR / "camera_locations_nodes.csv"
MATRIX_CSV = DATA_DIR / "coverage_matrix_nodes.csv"

MODEL_TXT = DATA_DIR / "uth_nodes_setcover.txt"
OUTPUT_CSV = RESULTS_DIR / "uth_nodes_selected_cameras.csv"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================
# 2. DOC DU LIEU NUT GIAO VA CAMERA
# ============================================

def load_node_data():
    if not CAMERA_CSV.exists():
        raise FileNotFoundError(
            f"Khong tim thay file: {CAMERA_CSV}"
        )

    if not MATRIX_CSV.exists():
        raise FileNotFoundError(
            f"Khong tim thay file: {MATRIX_CSV}"
        )

    with CAMERA_CSV.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        camera_rows = list(csv.DictReader(f))

    if not camera_rows:
        raise ValueError("Danh sach camera rong.")

    costs = []

    for i, camera in enumerate(camera_rows, 1):
        cost = float(camera["cost"])

        if cost <= 0:
            raise ValueError(
                f"Camera {i} co chi phi khong hop le."
            )

        if not cost.is_integer():
            raise ValueError(
                f"Camera {i} co chi phi thap phan: {cost}. "
                "Can kiem tra bo doc SetCoverModel "
                "truoc khi su dung chi phi thap phan."
            )

        costs.append(int(cost))

    matrix = []

    with MATRIX_CSV.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        reader = csv.reader(f)
        header = next(reader, None)

        if not header:
            raise ValueError("Ma tran phu rong.")

        if len(header) - 1 != len(costs):
            raise ValueError(
                "So cot camera trong ma tran "
                "khong khop voi danh sach camera."
            )

        for row in reader:
            if not row:
                continue

            values = [int(x) for x in row[1:]]

            if len(values) != len(costs):
                raise ValueError(
                    "So cot ma tran khong dong nhat."
                )

            if any(x not in (0, 1) for x in values):
                raise ValueError(
                    "Ma tran phu phai chi chua 0 va 1."
                )

            matrix.append(values)

    if not matrix:
        raise ValueError("Khong co nut giao nao.")

    uncovered = [
        i + 1
        for i, row in enumerate(matrix)
        if sum(row) == 0
    ]

    if uncovered:
        raise ValueError(
            "Co nut giao khong duoc camera nao phu: "
            f"{uncovered}"
        )

    return camera_rows, costs, matrix


# ============================================
# 3. CHUYEN SANG DINH DANG SET COVER
# ============================================

def create_setcover_file(costs, matrix):
    """
    Dinh dang OR-Library:
    - Dong dau: so nut giao, so camera
    - Danh sach chi phi camera
    - Moi nut giao: so camera phu duoc nut,
      sau do la danh sach chi so camera tu 1.
    """

    m = len(matrix)
    n = len(costs)

    with MODEL_TXT.open(
        "w", encoding="utf-8"
    ) as f:

        f.write(f"{m} {n}\n")

        f.write(
            " ".join(str(c) for c in costs) + "\n"
        )

        for row in matrix:
            cameras_covering = [
                j + 1
                for j, value in enumerate(row)
                if value == 1
            ]

            f.write(
                str(len(cameras_covering)) + "\n"
            )

            f.write(
                " ".join(
                    str(j) for j in cameras_covering
                ) + "\n"
            )

    print("Da tao du lieu Set Cover:")
    print(MODEL_TXT)


# ============================================
# 4. CHAY CAC THUAT TOAN
# ============================================

def run_algorithm(name, func, model, initial=None, **kwargs):

    start = time.perf_counter()

    if initial is None:
        solution = func(model, **kwargs)
    else:
        solution = func(model, initial, **kwargs)

    elapsed = time.perf_counter() - start

    return name, solution, elapsed


def main():

    print("=" * 55)
    print("BAI TOAN DAT CAMERA GIAM SAT NUT GIAO UTH")
    print("WEIGHTED SET COVER")
    print("=" * 55)

    # Doc du lieu
    camera_rows, costs, matrix = load_node_data()

    print("\n=== DU LIEU DA NAP ===")
    print("So nut giao:", len(matrix))
    print("So camera ung vien:", len(costs))
    print("Kich thuoc ma tran:",
          len(matrix), "x", len(costs))

    # Tao file input tuong thich model cu
    create_setcover_file(costs, matrix)

    # Khoi tao model
    model = SetCoverModel(str(MODEL_TXT))

    data = {
        "m": model.m,
        "n": model.n,
        "costs": model.costs,
        "rows": model.rows,
        "columns": model.columns
    }

    if model.m != len(matrix) or model.n != len(costs):
        raise ValueError(
            "Kich thuoc model khong khop du lieu CSV."
        )

    print("\n=== BAT DAU CHAY THUAT TOAN ===")

    results = []

    # ----------------------------------------
    # GREEDY
    # ----------------------------------------

    greedy_result = run_algorithm(
        "Greedy",
        greedy_set_cover,
        model
    )

    greedy = greedy_result[1]
    results.append(greedy_result)

    # ----------------------------------------
    # LOCAL SEARCH - FIRST
    # ----------------------------------------

    first_result = run_algorithm(
        "First Improvement",
        hill_climbing_first,
        model,
        greedy
    )

    results.append(first_result)

    # ----------------------------------------
    # LOCAL SEARCH - BEST
    # ----------------------------------------

    best_result = run_algorithm(
        "Best Improvement",
        hill_climbing_best,
        model,
        greedy
    )

    results.append(best_result)

    # ----------------------------------------
    # SIMULATED ANNEALING
    # ----------------------------------------

    sa_result = run_algorithm(
        "Simulated Annealing",
        simulated_annealing,
        model,
        greedy,
        initial_temp=10.0,
        cooling_rate=0.99,
        min_temp=0.01,
        max_iterations=5000,
        seed=42
    )

    results.append(sa_result)

    # ========================================
    # 5. KIEM TRA NGHIEM
    # ========================================

    print("\n=== BANG KET QUA ===")

    print(
        f"{'Thuat toan':<23}"
        f"{'Camera':<10}"
        f"{'Chi phi':<12}"
        f"{'Do phu':<12}"
        f"{'Time (s)':<12}"
    )

    print("-" * 69)

    valid_results = []

    for name, solution, elapsed in results:

        solution = sorted(set(solution))

        valid, cost, message = validate_solution(
            data, solution
        )

        coverage = model.coverage_rate(solution)

        if not valid:
            print(
                f"LOI {name}: {message}"
            )
            continue

        print(
            f"{name:<23}"
            f"{len(solution):<10}"
            f"{cost:<12}"
            f"{coverage:<12.2f}"
            f"{elapsed:<12.4f}"
        )

        valid_results.append(
            (name, solution, cost, elapsed)
        )

    if not valid_results:
        raise RuntimeError(
            "Khong co thuat toan nao tao "
            "duoc nghiem hop le."
        )

    # ========================================
    # 6. CHON NGHIEM TOT NHAT TIM DUOC
    # ========================================

    winner = min(
        valid_results,
        key=lambda x: x[2]
    )

    winner_name, selected, cost, elapsed = winner

    print("\n=== NGHIEM TOT NHAT TIM DUOC ===")

    print("Thuat toan:", winner_name)
    print("So camera:", len(selected))
    print("Tong chi phi:", cost)
    print(
        "Ty le phu:",
        model.coverage_rate(selected), "%"
    )
    print("Thoi gian:", round(elapsed, 4), "s")
    print(
        "Danh sach camera:",
        [j + 1 for j in selected]
    )

    # ========================================
    # 7. LUU KET QUA CAMERA DUOC CHON
    # ========================================

    selected_cameras = [
        camera_rows[j]
        for j in selected
    ]

    fieldnames = list(camera_rows[0].keys())

    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(selected_cameras)

    print("\n=== LUU KET QUA ===")
    print("Da luu:", OUTPUT_CSV)
    print("So camera da luu:", len(selected_cameras))

    print("\nHOAN TAT BAI TOAN UTH THEO NUT GIAO")


if __name__ == "__main__":
    main()
