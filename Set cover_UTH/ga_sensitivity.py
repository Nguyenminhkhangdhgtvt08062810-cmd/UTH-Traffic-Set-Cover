import csv
import math
import os
import matplotlib.pyplot as plt
from algorithms.tabu_search import _parse_orlib_file
from algorithms.genetic_algorithm import solve_genetic_algorithm


def run_ga_sensitivity():
    os.makedirs("results/summary", exist_ok=True)
    os.makedirs("results/figures", exist_ok=True)

    instances = [
        ("uth_setcover", "data/osm/uth_setcover.txt", 3.0),
        ("scp41", "data/orlib/scp41.txt", 3.0),
    ]
    seeds = [42, 100, 2026, 7, 13]

    pop_sizes = [20, 40, 60, 100, 150]
    mut_rates = [0.01, 0.03, 0.05, 0.10, 0.20]

    rows = []

    for inst_name, filepath, t_limit in instances:
        if not os.path.exists(filepath):
            continue
        m, n, costs, row_cols, col_rows = _parse_orlib_file(filepath)
        print(f"\n>>> Dang khao sat do nhay GA tren {inst_name} (m={m}, n={n})...")

        # 1. Khảo sát Kích thước quần thể pop_size (cố định mutation_rate=0.05)
        pop_means, pop_stds = [], []
        for pop in pop_sizes:
            vals, times = [], []
            for s in seeds:
                res = solve_genetic_algorithm(
                    m, n, costs, row_cols, col_rows,
                    time_limit=t_limit, pop_size=pop, mutation_rate=0.05, seed=s
                )
                vals.append(res["best_value"])
                times.append(res["time_s"])
            mean_v = sum(vals) / len(vals)
            std_v = math.sqrt(sum((v - mean_v) ** 2 for v in vals) / (len(vals) - 1))
            mean_t = sum(times) / len(times)
            pop_means.append(mean_v)
            pop_stds.append(std_v)
            rows.append([inst_name, "pop_size", pop, min(vals), round(mean_v, 2), round(std_v, 2), round(mean_t, 4)])
            print(f"  [PopSize={pop:<3}] Best={min(vals)} | Mean={mean_v:.2f} ± {std_v:.2f} | Time={mean_t:.3f}s")

        plt.figure(figsize=(7.5, 4.5))
        plt.errorbar(pop_sizes, pop_means, yerr=pop_stds, marker="o", capsize=5, color="#2a9d8f", linewidth=2)
        plt.title(f"Do nhay kich thuoc quan the (GA) - {inst_name.upper()}")
        plt.xlabel("Kich thuoc quan the (pop_size)")
        plt.ylabel("Chi phi trung binh (Mean Cost ± Std)")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.savefig(f"results/figures/ga_sensitivity_pop_{inst_name}.png", dpi=200)
        plt.close()

        # 2. Khảo sát Tỷ lệ đột biến mutation_rate (cố định pop_size=50)
        mut_means, mut_stds = [], []
        for mr in mut_rates:
            vals, times = [], []
            for s in seeds:
                res = solve_genetic_algorithm(
                    m, n, costs, row_cols, col_rows,
                    time_limit=t_limit, pop_size=50, mutation_rate=mr, seed=s
                )
                vals.append(res["best_value"])
                times.append(res["time_s"])
            mean_v = sum(vals) / len(vals)
            std_v = math.sqrt(sum((v - mean_v) ** 2 for v in vals) / (len(vals) - 1))
            mean_t = sum(times) / len(times)
            mut_means.append(mean_v)
            mut_stds.append(std_v)
            rows.append([inst_name, "mutation_rate", mr, min(vals), round(mean_v, 2), round(std_v, 2), round(mean_t, 4)])
            print(f"  [MutRate={mr:<4}] Best={min(vals)} | Mean={mean_v:.2f} ± {std_v:.2f} | Time={mean_t:.3f}s")

        plt.figure(figsize=(7.5, 4.5))
        plt.errorbar(mut_rates, mut_means, yerr=mut_stds, marker="s", capsize=5, color="#e76f51", linewidth=2)
        plt.title(f"Do nhay ty le dot bien (GA) - {inst_name.upper()}")
        plt.xlabel("Ty le dot bien (mutation_rate)")
        plt.ylabel("Chi phi trung binh (Mean Cost ± Std)")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.savefig(f"results/figures/ga_sensitivity_mut_{inst_name}.png", dpi=200)
        plt.close()

    out_csv = "results/summary/ga_sensitivity_summary.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Instance", "Parameter", "Value", "Best_Cost", "Mean_Cost", "Sample_Std", "Mean_Time_s"])
        writer.writerows(rows)
    print(f"\nHoan tat! Da luu bang do nhay GA tai: {out_csv}")


if __name__ == "__main__":
    run_ga_sensitivity()