
# Duong dan lam viec: thu muc goc bai nop.
import os as _project_os
from pathlib import Path as _project_Path
_project_os.chdir(_project_Path(__file__).resolve().parent.parent)

import csv
import os
import time
import statistics

from utils.set_cover_model import SetCoverModel
from utils.validator import validate_solution
from algorithms.greedy import greedy_set_cover
from algorithms.simulated_annealing import simulated_annealing


instances = [
    "scp42",
    "scp43",
    "scp44",
    "scp45"
]

os.makedirs("results", exist_ok=True)

all_results = []

for instance in instances:
    print(f"\n=== DANG CHAY {instance} ===")

    model = SetCoverModel(
        f"data/chuan/{instance}.txt"
    )

    data = {
        "m": model.m,
        "n": model.n,
        "costs": model.costs,
        "rows": model.rows,
        "columns": model.columns
    }

    initial = greedy_set_cover(model)
    greedy_cost = model.calculate_cost(initial)

    costs = []
    times = []

    for seed in range(1, 11):
        start = time.perf_counter()

        result = simulated_annealing(
            model,
            initial,
            initial_temp=100.0,
            cooling_rate=0.995,
            min_temp=0.01,
            max_iterations=5000,
            seed=seed
        )

        elapsed = time.perf_counter() - start

        valid, cost, message = validate_solution(
            data, result
        )

        assert valid, (
            f"{instance} seed {seed}: "
            f"nghiem khong hop le"
        )

        assert cost <= greedy_cost

        costs.append(cost)
        times.append(elapsed)

        all_results.append([
            instance,
            "SA",
            seed,
            greedy_cost,
            cost,
            round(elapsed, 6)
        ])

        print(
            f"Seed {seed:2d}: "
            f"Cost = {cost}, "
            f"Time = {elapsed:.4f}s"
        )

    print(f"\nTHONG KE {instance}")
    print("Greedy:", greedy_cost)
    print("Best:", min(costs))
    print("Worst:", max(costs))
    print("Mean:", round(statistics.mean(costs), 2))
    print("Std:", round(statistics.stdev(costs), 2))
    print("Mean time:", round(statistics.mean(times), 4), "s")


output_path = "results/sa_orlib_experiments.csv"

with open(
    output_path,
    "w",
    newline="",
    encoding="utf-8"
) as f:
    writer = csv.writer(f)

    writer.writerow([
        "instance",
        "algorithm",
        "seed",
        "greedy_cost",
        "sa_cost",
        "time_seconds"
    ])

    writer.writerows(all_results)

print("\n=== HOAN TAT THUC NGHIEM ===")
print("Da luu:", output_path)
