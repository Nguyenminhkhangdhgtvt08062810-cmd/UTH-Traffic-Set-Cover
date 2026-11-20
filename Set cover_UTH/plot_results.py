import csv
import glob
import math
import os
from collections import defaultdict

import matplotlib.pyplot as plt

# Giá trị tối ưu chuẩn xác f* (từ Nhánh cận) & BKS chuẩn (Beasley 1987 - OR-Library)
BKS_MAP = {
    "vidu": 16,
    "sc_10_10_s101": 22,
    "sc_10_10_s102": 24,
    "sc_10_10_s103": 42,
    "sc_20_20_s101": 85,
    "sc_20_20_s102": 83,
    "sc_20_20_s103": 51,
    "sc_30_30_s101": 103,
    "sc_30_30_s102": 91,
    "sc_30_30_s103": 86,
    "scp41": 429,
    "scp42": 512,
    "scp43": 516,
    "scp44": 494,
    "scp45": 512,
    "scp46": 560,
    "scp47": 430,
    "scp48": 492,
    "scp49": 641,
    "scp410": 514,
}

# Thứ tự hiển thị chuẩn từ Nhỏ -> Vừa -> Lớn trong bảng báo cáo
INSTANCE_ORDER = [
    "vidu",
    "sc_10_10_s101",
    "sc_20_20_s101",
    "sc_30_30_s101",
    "sc_30_30_s102",
    "uth_setcover",
    "scp41",
    "scp42",
    "scp43",
    "scp44",
    "scp45",
]
ALGO_ORDER = ["SA", "TS", "GA"]


def summarize_raw():
    os.makedirs("results/summary", exist_ok=True)
    raw_files = sorted(glob.glob("results/raw/*_raw.csv"))
    if not raw_files:
        print("Khong tim thay tep nao trong results/raw/.")
        return

    groups = defaultdict(list)
    for fpath in raw_files:
        with open(fpath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["instance"].strip(), row["algorithm"].strip())
                groups[key].append((
                    float(row["best_value"]),
                    float(row["time_s"]),
                    int(row["feasible"]),
                ))

    sorted_keys = sorted(
        groups.keys(),
        key=lambda k: (
            INSTANCE_ORDER.index(k[0]) if k[0] in INSTANCE_ORDER else 999,
            ALGO_ORDER.index(k[1]) if k[1] in ALGO_ORDER else 999,
        ),
    )

    summary_rows = []
    for inst, algo in sorted_keys:
        vals = groups[(inst, algo)]
        costs = [v[0] for v in vals]
        times = [v[1] for v in vals]
        feas = sum(v[2] for v in vals)
        best_c = min(costs)
        mean_c = sum(costs) / len(costs)
        std_c = math.sqrt(sum((c - mean_c) ** 2 for c in costs) / max(1, len(costs) - 1))
        mean_t = sum(times) / len(times)

        bks = BKS_MAP.get(inst.lower())
        if bks is not None and bks > 0:
            gap_best = round(abs(best_c - bks) / bks * 100, 2)
            gap_mean = round(abs(mean_c - bks) / bks * 100, 2)
            opt_hits = sum(1 for c in costs if abs(c - bks) < 1e-6)
            opt_rate = f"{opt_hits}/{len(costs)} ({round(opt_hits / len(costs) * 100)}%)"
        else:
            bks = "N/A"
            gap_best = "N/A"
            gap_mean = "N/A"
            opt_rate = "N/A"

        summary_rows.append([
            inst, bks, algo, len(vals), feas,
            round(best_c, 2), round(mean_c, 2), round(std_c, 2),
            gap_best, gap_mean, opt_rate, round(mean_t, 4)
        ])

    out_csv = "results/summary/benchmark_summary.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Instance", "BKS_f*", "Algorithm", "Runs", "Feasible",
            "Best_Cost", "Mean_Cost", "Sample_Std",
            "Gap_Best_%", "Gap_Mean_%", "Optimal_Rate", "Mean_Time_s"
        ])
        writer.writerows(summary_rows)
    print(f"Da xuat bang thong ke day du tai: {out_csv}")


def plot_convergence():
    os.makedirs("results/figures", exist_ok=True)
    conv_files = glob.glob("results/conv/*_conv.csv")
    if not conv_files:
        print("Khong tim thay tep nao trong results/conv/.")
        return

    instances = sorted({
        os.path.basename(p).split("_SA_")[0].split("_GA_")[0].split("_TS_")[0]
        for p in conv_files
    })

    for inst in instances:
        plt.figure(figsize=(8.5, 5))
        has_data = False
        for algo, color in [("SA", "#e63946"), ("GA", "#2a9d8f"), ("TS", "#457b9d")]:
            conv_path = f"results/conv/{inst}_{algo}_seed42_conv.csv"
            if not os.path.exists(conv_path):
                continue
            times, bests = [], []
            with open(conv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    times.append(float(row["time_s"]))
                    bests.append(float(row["best_value"]))
            if times:
                plt.step(times, bests, where="post", label=algo, color=color, linewidth=2)
                has_data = True

        if not has_data:
            plt.close()
            continue

        bks = BKS_MAP.get(inst.lower())
        if bks is not None:
            plt.axhline(y=bks, color="#264653", linestyle=":", linewidth=1.5, label=f"Optimal / BKS ({bks})")

        plt.title(f"Duong hoi tu chi phi (SA vs GA vs TS) - {inst.upper()}")
        plt.xlabel("Thoi gian chay (giay)")
        plt.ylabel("Tong chi phi tot nhat (Best Cost)")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.legend()
        plt.tight_layout()
        fig_path = f"results/figures/{inst}_convergence.png"
        plt.savefig(fig_path, dpi=200)
        plt.close()
        print(f"Da ve bieu do hoi tu: {fig_path}")


if __name__ == "__main__":
    summarize_raw()
    plot_convergence()