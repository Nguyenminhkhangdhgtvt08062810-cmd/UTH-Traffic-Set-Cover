
from __future__ import annotations

# Duong dan lam viec: thu muc goc bai nop.
import os as _project_os
from pathlib import Path as _project_Path

_project_os.chdir(_project_Path(__file__).resolve().parent.parent)

import csv
import statistics
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from algorithms.greedy import greedy_set_cover
from algorithms.simulated_annealing import simulated_annealing
from plot_sa_convergence import Model


# ============================================================
# 1. DUONG DAN DU LIEU VA KET QUA
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = ROOT / "data" / "nodes" / "uth_nodes_setcover.txt"

OUTPUT_DIR = ROOT / "results"
FIGURES_DIR = OUTPUT_DIR / "figures"
SUMMARY_DIR = OUTPUT_DIR / "summary"


# ============================================================
# 2. CAU HINH THUC NGHIEM
# ============================================================

SEEDS = list(range(1, 11))

BASELINE = {
    "initial_temp": 10.0,
    "cooling_rate": 0.99,
    "max_iterations": 5000,
}

MIN_TEMP = 0.01

PARAMETER_VALUES = {
    "initial_temp": [2.0, 10.0, 50.0],
    "cooling_rate": [0.95, 0.99, 0.995],
    "max_iterations": [100, 400, 1000],
}

DETAIL_FIELDS = [
    "parameter",
    "value",
    "seed",
    "initial_temp",
    "cooling_rate",
    "max_iterations",
    "selected_cameras",
    "cost",
    "coverage_pct",
    "runtime_seconds",
]

SUMMARY_FIELDS = [
    "parameter",
    "value",
    "runs",
    "best_cost",
    "mean_cost",
    "std_cost",
    "worst_cost",
    "mean_cameras",
    "mean_runtime_seconds",
    "feasible_runs",
]


# ============================================================
# 3. CHAY THUC NGHIEM DO NHAY SA
# ============================================================

def run_experiment(model, initial_solution):
    detail_rows = []
    summary_rows = []

    initial_cost = model.calculate_cost(initial_solution)

    for parameter, values in PARAMETER_VALUES.items():
        for value in values:

            config = BASELINE.copy()
            config[parameter] = value

            run_costs = []
            run_counts = []
            run_times = []
            feasible_runs = 0

            print(f"\n[{parameter}={value}]", flush=True)

            for seed in SEEDS:
                start = time.perf_counter()

                selected = simulated_annealing(
                    model,
                    initial_solution,
                    initial_temp=config["initial_temp"],
                    cooling_rate=config["cooling_rate"],
                    min_temp=MIN_TEMP,
                    max_iterations=config["max_iterations"],
                    seed=seed,
                )

                elapsed = time.perf_counter() - start

                if not model.is_feasible(selected):
                    raise AssertionError(
                        f"Nghiem khong hop le: "
                        f"{parameter}={value}, seed={seed}"
                    )

                feasible_runs += 1

                cost = model.calculate_cost(selected)
                covered = len(model.get_covered(selected))
                coverage_pct = 100.0 * covered / model.m

                run_costs.append(cost)
                run_counts.append(len(selected))
                run_times.append(elapsed)

                detail_rows.append({
                    "parameter": parameter,
                    "value": value,
                    "seed": seed,
                    "initial_temp": config["initial_temp"],
                    "cooling_rate": config["cooling_rate"],
                    "max_iterations": config["max_iterations"],
                    "selected_cameras": len(selected),
                    "cost": cost,
                    "coverage_pct": round(coverage_pct, 2),
                    "runtime_seconds": round(elapsed, 6),
                })

                print(
                    f"  seed={seed:2d}  "
                    f"cameras={len(selected):2d} "
                    f"cost={cost:3d}  "
                    f"time={elapsed:.4f}s",
                    flush=True,
                )

            summary_rows.append({
                "parameter": parameter,
                "value": value,
                "runs": len(run_costs),
                "best_cost": min(run_costs),
                "mean_cost": round(
                    statistics.mean(run_costs), 4
                ),
                "std_cost": round(
                    statistics.stdev(run_costs), 4
                ) if len(run_costs) > 1 else 0.0,
                "worst_cost": max(run_costs),
                "mean_cameras": round(
                    statistics.mean(run_counts), 4
                ),
                "mean_runtime_seconds": round(
                    statistics.mean(run_times), 6
                ),
                "feasible_runs": feasible_runs,
            })

    return initial_cost, detail_rows, summary_rows


# ============================================================
# 4. XUAT FILE CSV
# ============================================================

def export_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as handle:

        writer = csv.DictWriter(
            handle,
            fieldnames=fields
        )

        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# 5. VE BIEU DO DO NHAY SA
# ============================================================

def draw_plots(summary_rows):
    filenames = []

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    for parameter, label in [
        ("initial_temp", "Initial temperature"),
        ("cooling_rate", "Cooling rate"),
        ("max_iterations", "Max iterations"),
    ]:

        rows = [
            r for r in summary_rows
            if r["parameter"] == parameter
        ]

        x = [float(r["value"]) for r in rows]
        means = [float(r["mean_cost"]) for r in rows]
        stds = [float(r["std_cost"]) for r in rows]
        bests = [float(r["best_cost"]) for r in rows]

        fig, ax = plt.subplots(figsize=(8, 5))

        ax.errorbar(
            x,
            means,
            yerr=stds,
            marker="o",
            capsize=4,
            label="Mean cost +/- sample std",
        )

        ax.plot(
            x,
            bests,
            marker="s",
            linestyle="--",
            label="Best cost",
        )

        ax.set_xticks(x)
        ax.set_xlabel(label)
        ax.set_ylabel(
            "Total camera cost (lower is better)"
        )

        ax.set_title(
            f"SA sensitivity - {label} "
            f"(UTH, {len(SEEDS)} seeds)"
        )

        ax.grid(True, alpha=0.25)
        ax.legend()

        fig.tight_layout()

        # Luu tat ca anh SA vao results/figures/
        path = FIGURES_DIR / f"sa_sensitivity_{parameter}.png"

        fig.savefig(path, dpi=180)
        plt.close(fig)

        filenames.append(path)

    return filenames


# ============================================================
# 6. CHUONG TRINH CHINH
# ============================================================

def main():

    if not DATA_FILE.is_file():
        raise FileNotFoundError(
            f"Khong tim thay du lieu: {DATA_FILE}"
        )

    if len(SEEDS) < 10:
        raise ValueError(
            "Can it nhat 10 seeds cho thuc nghiem nay"
        )

    # Tao thu muc luu ket qua
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

    model = Model(DATA_FILE)
    initial = greedy_set_cover(model)

    if not model.is_feasible(initial):
        raise AssertionError(
            "Greedy tra ve nghiem khong hop le"
        )

    print("=== PHAN TICH DO NHAY SA - UTH ===")

    print(
        f"Nut giao: {model.m} | "
        f"Camera ung vien: {model.n}"
    )

    print(
        f"Greedy initial cost: "
        f"{model.calculate_cost(initial)}"
    )

    print(f"Seeds: {SEEDS}")
    print(f"Baseline: {BASELINE}")

    initial_cost, detail, summary = run_experiment(
        model, initial
    )

    # Luu CSV vao results/summary/
    detail_path = (
        SUMMARY_DIR / "sa_sensitivity_uth_detail.csv"
    )

    summary_path = (
        SUMMARY_DIR / "sa_sensitivity_uth_summary.csv"
    )

    export_csv(
        detail_path,
        detail,
        DETAIL_FIELDS
    )

    export_csv(
        summary_path,
        summary,
        SUMMARY_FIELDS
    )

    # Luu bieu do PNG vao results/figures/
    images = draw_plots(summary)

    print("\n=== TONG HOP ===")

    print(f"Greedy cost: {initial_cost}")

    print(
        f"So cau hinh: {len(summary)} | "
        f"So lan chay: {len(detail)}"
    )

    for r in summary:
        print(
            f"{r['parameter']:15s}="
            f"{str(r['value']):8s} "
            f"best={r['best_cost']:3d} "
            f"mean={r['mean_cost']:7.2f} "
            f"std={r['std_cost']:6.2f} "
            f"avg_time={r['mean_runtime_seconds']:.4f}s "
            f"feasible={r['feasible_runs']}/{r['runs']}"
        )

    print("\nDA XUAT:")

    for path in [detail_path, summary_path, *images]:
        print(path)

    print(
        "\nLuu y: Do nhay mot tham so tai mot thoi diem "
        "(one-factor-at-a-time)."
    )

    print(
        "Chi phi 80 da tim thay truoc do "
        "KHONG phai toi uu duoc chung minh."
    )


if __name__ == "__main__":
    main()
