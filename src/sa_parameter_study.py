
# Duong dan lam viec: thu muc goc bai nop.
import os as _project_os
from pathlib import Path as _project_Path
_project_os.chdir(_project_Path(__file__).resolve().parent.parent)

import csv
import time
import statistics
from pathlib import Path

from utils.set_cover_model import SetCoverModel
from utils.validator import validate_solution
from algorithms.greedy import greedy_set_cover
from algorithms.simulated_annealing import simulated_annealing


# 1. Chon bo du lieu chuan
model = SetCoverModel("data/chuan/scp41.txt")

data = {
    "m": model.m,
    "n": model.n,
    "costs": model.costs,
    "rows": model.rows,
    "columns": model.columns
}

initial = greedy_set_cover(model)
greedy_cost = model.calculate_cost(initial)

# 2. Cac tham so can thu
temperatures = [10.0, 50.0, 100.0]
cooling_rates = [0.95, 0.99, 0.995]
seeds = range(1, 11)

results = []
summary = []

print("=== PHAN TICH THAM SO SA - SCP41 ===")
print("Chi phi Greedy:", greedy_cost)

# 3. Thu tung cap tham so
for temp in temperatures:
    for cooling in cooling_rates:
        costs = []
        times = []

        print(
            f"\nTemp={temp}, Cooling={cooling}"
        )

        for seed in seeds:
            start = time.perf_counter()

            solution = simulated_annealing(
                model,
                initial,
                initial_temp=temp,
                cooling_rate=cooling,
                min_temp=0.01,
                max_iterations=5000,
                seed=seed
            )

            elapsed = time.perf_counter() - start

            valid, cost, message = validate_solution(
                data, solution
            )

            assert valid, (
                f"Temp={temp}, Cooling={cooling}, "
                f"Seed={seed}: {message}"
            )

            costs.append(cost)
            times.append(elapsed)

            results.append([
                "scp41",
                temp,
                cooling,
                seed,
                cost,
                round(elapsed, 6)
            ])

        mean_cost = statistics.mean(costs)
        std_cost = statistics.stdev(costs)
        mean_time = statistics.mean(times)

        summary.append([
            temp,
            cooling,
            min(costs),
            round(mean_cost, 2),
            round(std_cost, 2),
            round(mean_time, 4)
        ])

        print("Best:", min(costs))
        print("Mean:", round(mean_cost, 2))
        print("Std:", round(std_cost, 2))
        print("Mean time:", round(mean_time, 4), "s")


# 4. Luu ket qua
Path("results").mkdir(exist_ok=True)

with open(
    "results/sa_parameter_detail.csv",
    "w",
    newline="",
    encoding="utf-8"
) as f:
    writer = csv.writer(f)
    writer.writerow([
        "instance",
        "initial_temp",
        "cooling_rate",
        "seed",
        "cost",
        "time_seconds"
    ])
    writer.writerows(results)


with open(
    "results/sa_parameter_summary.csv",
    "w",
    newline="",
    encoding="utf-8"
) as f:
    writer = csv.writer(f)
    writer.writerow([
        "initial_temp",
        "cooling_rate",
        "best_cost",
        "mean_cost",
        "std_cost",
        "mean_time"
    ])
    writer.writerows(summary)


# 5. Tim cau hinh co mean cost nho nhat
best_config = min(
    summary,
    key=lambda row: (row[3], row[5])
)

print("\n=== CAU HINH TOT NHAT THEO MEAN COST ===")
print("Initial Temp:", best_config[0])
print("Cooling Rate:", best_config[1])
print("Best Cost:", best_config[2])
print("Mean Cost:", best_config[3])
print("Mean Time:", best_config[5], "s")

print("\n=== HOAN TAT ===")
print("Tong so lan chay:", len(results))
print("Da luu: results/sa_parameter_detail.csv")
print("Da luu: results/sa_parameter_summary.csv")
