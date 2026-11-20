import csv
import math
import os
import matplotlib.pyplot as plt
from algorithms.tabu_search import _parse_orlib_file, solve_tabu_search


def run_ts_sensitivity():
    os.makedirs("results/summary", exist_ok=True)
    os.makedirs("results/figures", exist_ok=True)

    # Khảo sát trên bộ dữ liệu thực tế UTH và một bộ OR-Library đại diện (scp41)
    instances = [
        ("uth_setcover", "data/osm/uth_setcover.txt", 3.0),
        ("scp41", "data/orlib/scp41.txt", 3.0),
    ]
    seeds = [42, 100, 2026, 7, 13]

    tenures = [3, 7, 15, 25, 40]
    max_iters = [500, 2000, 10000, 30000, 50000]

    rows = []

    for inst_name, filepath, t_limit in instances:
        if not os.path.exists(filepath):
            continue
        m, n, costs, row_cols, col_rows = _parse_orlib_file(filepath)
        print(f"\n>>> Dang khao sat do nhay TS tren {inst_name} (m={m}, n={n})...")

        # 1. Khảo sát Tabu Tenure (cố định max_iter=30000)
        tenure_means, tenure_stds = [], []
        for ten in tenures:
            vals, times = [], []
            for s in seeds:
                res = solve_tabu_search(
                    m, n, costs, row_cols, col_rows,
                    time_limit=t_limit, max_iter=30000, tabu_tenure=ten, seed=s
                )
                vals.append(res["best_value"])
                times.append(res["time_s"])
            mean_v = sum(vals) / len(vals)
            std_v = math.sqrt(sum((v - mean_v) ** 2 for v in vals) / (len(vals) - 1))
            mean_t = sum(times) / len(times)
            tenure_means.append(mean_v)
            tenure_stds.append(std_v)
            rows.append([inst_name, "tabu_tenure", ten, min(vals), round(mean_v, 2), round(std_v, 2), round(mean_t, 4)])
            print(f"  [Tenure={ten:<2}] Best={min(vals)} | Mean={mean_v:.2f} ± {std_v:.2f} | Time={mean_t:.3f}s")

        plt.figure(figsize=(7.5, 4.5))
        plt.errorbar(tenures, tenure_means, yerr=tenure_stds, marker="o", capsize=5, color="#457b9d", linewidth=2)
        plt.title(f"Do nhay tham so Tabu Tenure (TS) - {inst_name.upper()}")
        plt.xlabel("Do dai danh sach Tabu (tabu_tenure)")
        plt.ylabel("Chi phi trung binh (Mean Cost ± Std)")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.savefig(f"results/figures/ts_sensitivity_tenure_{inst_name}.png", dpi=200)
        plt.close()

        # 2. Khảo sát Max Iterations (cố định tabu_tenure=15)
        iter_means, iter_stds = [], []
        for it in max_iters:
            vals, times = [], []
            for s in seeds:
                res = solve_tabu_search(
                    m, n, costs, row_cols, col_rows,
                    time_limit=t_limit, max_iter=it, tabu_tenure=15, seed=s
                )
                vals.append(res["best_value"])
                times.append(res["time_s"])
            mean_v = sum(vals) / len(vals)
            std_v = math.sqrt(sum((v - mean_v) ** 2 for v in vals) / (len(vals) - 1))
            mean_t = sum(times) / len(times)
            iter_means.append(mean_v)
            iter_stds.append(std_v)
            rows.append([inst_name, "max_iter", it, min(vals), round(mean_v, 2), round(std_v, 2), round(mean_t, 4)])
            print(f"  [MaxIter={it:<5}] Best={min(vals)} | Mean={mean_v:.2f} ± {std_v:.2f} | Time={mean_t:.3f}s")

        plt.figure(figsize=(7.5, 4.5))
        plt.errorbar(max_iters, iter_means, yerr=iter_stds, marker="s", capsize=5, color="#1d3557", linewidth=2)
        plt.title(f"Do nhay so vong lap toi da (TS) - {inst_name.upper()}")
        plt.xlabel("So vong lap toi da (max_iter)")
        plt.ylabel("Chi phi trung binh (Mean Cost ± Std)")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.savefig(f"results/figures/ts_sensitivity_iter_{inst_name}.png", dpi=200)
        plt.close()

    out_csv = "results/summary/ts_sensitivity_summary.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Instance", "Parameter", "Value", "Best_Cost", "Mean_Cost", "Sample_Std", "Mean_Time_s"])
        writer.writerows(rows)
    print(f"\nHoan tat! Da luu bang do nhay TS tai: {out_csv}")


if __name__ == "__main__":
    run_ts_sensitivity()