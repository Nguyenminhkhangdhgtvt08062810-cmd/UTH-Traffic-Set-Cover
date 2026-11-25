
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
from algorithms.branch_and_bound import branch_and_bound


# Danh sach 9 bo du lieu tu sinh
files = sorted(
    Path("data/tusinh").glob("sc_*.txt")
)

assert len(files) == 9, (
    f"Can 9 bo du lieu, tim thay {len(files)}"
)

results = []

for file_path in files:
    model = SetCoverModel(str(file_path))

    data = {
        "m": model.m,
        "n": model.n,
        "costs": model.costs,
        "rows": model.rows,
        "columns": model.columns
    }

    print(f"\n=== {file_path.stem} ===")

    # 1. Greedy
    start = time.perf_counter()
    greedy = greedy_set_cover(model)
    greedy_time = time.perf_counter() - start

    # 2. Local Search - First
    start = time.perf_counter()
    first = hill_climbing_first(model, greedy)
    first_time = time.perf_counter() - start

    # 3. Local Search - Best
    start = time.perf_counter()
    best = hill_climbing_best(model, greedy)
    best_time = time.perf_counter() - start

    # 4. Simulated Annealing
    start = time.perf_counter()
    sa = simulated_annealing(
        model,
        greedy,
        seed=42
    )
    sa_time = time.perf_counter() - start

    # 5. Branch and Bound (Exact)
    start = time.perf_counter()
    exact, exact_cost = branch_and_bound(model)
    exact_time = time.perf_counter() - start

    algorithms = [
        ("Greedy", greedy, greedy_time),
        ("First Improvement", first, first_time),
        ("Best Improvement", best, best_time),
        ("SA", sa, sa_time),
        ("Exact", exact, exact_time)
    ]

    # Kiem chung va luu ket qua
    for name, solution, elapsed in algorithms:
        valid, cost, message = validate_solution(
            data, solution
        )

        assert valid, (
            f"{file_path.stem} - {name}: {message}"
        )

        if name == "Exact":
            assert cost == exact_cost

        gap = (cost - exact_cost) / exact_cost * 100

        results.append([
            file_path.stem,
            name,
            cost,
            len(solution),
            round(elapsed, 6),
            round(gap, 4)
        ])

        print(
            f"{name:18s} "
            f"Cost={cost:4d} "
            f"Gap={gap:6.2f}% "
            f"Time={elapsed:.4f}s"
        )


# Luu du lieu thuc nghiem
Path("results").mkdir(exist_ok=True)

output = "results/compare_algorithms.csv"

with open(output, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow([
        "instance",
        "algorithm",
        "cost",
        "num_cameras",
        "time_seconds",
        "gap_percent"
    ])

    writer.writerows(results)

print("\n=== HOAN TAT SO SANH ===")
print("So bo du lieu:", len(files))
print("So ket qua:", len(results))
print("Da luu:", output)
