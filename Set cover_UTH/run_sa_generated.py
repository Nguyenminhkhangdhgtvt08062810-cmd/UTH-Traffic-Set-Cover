
import csv
import time
import statistics
from pathlib import Path

from utils.set_cover_model import SetCoverModel
from utils.validator import validate_solution
from algorithms.greedy import greedy_set_cover
from algorithms.simulated_annealing import simulated_annealing

files = sorted(
    Path("data/generated").glob("sc_*.txt")
)

if len(files) != 9:
    raise ValueError(
        f"Can 9 instance, hien co {len(files)}"
    )

results = []

for file_path in files:
    name = file_path.stem
    model = SetCoverModel(str(file_path))

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

    print(f"\n=== {name} ===")

    for seed in range(1, 11):
        start = time.perf_counter()

        solution = simulated_annealing(
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
            data, solution
        )

        assert valid, f"{name} - seed {seed}: {message}"
        assert cost <= greedy_cost

        costs.append(cost)
        times.append(elapsed)

        results.append([
            name,
            seed,
            greedy_cost,
            cost,
            round(elapsed, 6)
        ])

    print("Greedy:", greedy_cost)
    print("SA Best:", min(costs))
    print("SA Worst:", max(costs))
    print("SA Mean:", round(statistics.mean(costs), 2))
    print("SA Std:", round(statistics.stdev(costs), 2))
    print("Mean Time:", round(statistics.mean(times), 4), "s")

Path("results").mkdir(exist_ok=True)

output = "results/sa_generated_experiments.csv"

with open(output, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow([
        "instance",
        "seed",
        "greedy_cost",
        "sa_cost",
        "time_seconds"
    ])

    writer.writerows(results)

print("\n=== HOAN TAT ===")
print("So instance:", len(files))
print("Tong so lan chay:", len(results))
print("Da luu:", output)
