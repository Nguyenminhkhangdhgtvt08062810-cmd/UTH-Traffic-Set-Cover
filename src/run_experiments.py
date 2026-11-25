
# Duong dan lam viec: thu muc goc bai nop.
import os as _project_os
from pathlib import Path as _project_Path
_project_os.chdir(_project_Path(__file__).resolve().parent.parent)
import csv
import glob
import importlib
import inspect
import os
import traceback

from algorithms.genetic_algorithm import solve_genetic_algorithm
from algorithms.tabu_search import (
    _parse_orlib_file,
    _validate_solution,
    solve_tabu_search,
)


def load_sa_solver():
    """Tự động dò tìm module và hàm giải SA trong algorithms/simulated_annealing.py."""
    try:
        sa_mod = importlib.import_module("algorithms.simulated_annealing")
    except Exception as e:
        print(f"[Cảnh báo] Không thể import algorithms.simulated_annealing: {e}")
        return None

    for fn_name in [
        "solve_simulated_annealing",
        "simulated_annealing",
        "solve_sa",
        "run_sa",
    ]:
        if hasattr(sa_mod, fn_name):
            return getattr(sa_mod, fn_name)

    print(
        "[Cảnh báo] Không tìm thấy hàm giải SA chuẩn trong algorithms/simulated_annealing.py."
    )
    return None


def call_sa_safely(sa_func, m, n, costs, row_cols, col_rows, time_limit, seed):
    """Gọi hàm SA linh hoạt theo đúng các tham số mà hàm đó hỗ trợ."""
    sig = inspect.signature(sa_func)
    params = sig.parameters
    kwargs = {}

    if "time_limit" in params:
        kwargs["time_limit"] = time_limit
    if "seed" in params:
        kwargs["seed"] = seed
    if "alpha" in params:
        kwargs["alpha"] = 0.99
    elif "cooling_rate" in params:
        kwargs["cooling_rate"] = 0.99
    if "one_indexed_output" in params:
        kwargs["one_indexed_output"] = True

    raw_out = sa_func(m, n, costs, row_cols, col_rows, **kwargs)

    if isinstance(raw_out, dict):
        return raw_out
    if isinstance(raw_out, (tuple, list)) and len(raw_out) >= 2:
        best_val, sol = raw_out[0], raw_out[1]
        return {
            "algorithm": "SA",
            "params": "default",
            "seed": seed,
            "best_value": best_val,
            "solution": list(sol),
            "time_s": raw_out[2] if len(raw_out) > 2 else 0.0,
            "time_to_best_s": raw_out[2] if len(raw_out) > 2 else 0.0,
            "evaluations": raw_out[3] if len(raw_out) > 3 else 0,
            "history": raw_out[4] if len(raw_out) > 4 else [],
        }
    raise ValueError(f"Định dạng trả về của SA không hợp lệ: {type(raw_out)}")


def prepare_clean_dirs():
    """Tạo thư mục kết quả và tự động xóa sạch dữ liệu thực nghiệm cũ để tránh trùng lặp."""
    for sub in ["results/raw", "results/conv", "results/solutions"]:
        os.makedirs(sub, exist_ok=True)
        for old_file in glob.glob(os.path.join(sub, "*")):
            if os.path.isfile(old_file):
                os.remove(old_file)
    print("[Hệ thống] Đã dọn dẹp sạch dữ liệu cũ trong results/raw, results/conv, results/solutions.")


def save_outputs(instance_name, algo_name, seed, m, col_rows, res):
    """Lưu kết quả raw CSV, convergence CSV và tệp nghiệm .sol."""
    raw_file = os.path.join("results", "raw", f"{instance_name}_raw.csv")
    write_header = not os.path.exists(raw_file)

    sol = res.get("solution", [])
    sol_0based = [j - 1 for j in sol]
    feasible, _ = _validate_solution(m, sol_0based, col_rows)

    with open(raw_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                "instance",
                "algorithm",
                "params",
                "seed",
                "best_value",
                "time_s",
                "time_to_best_s",
                "evaluations",
                "feasible",
            ])
        writer.writerow([
            instance_name,
            algo_name,
            res.get("params", ""),
            seed,
            res.get("best_value", ""),
            res.get("time_s", ""),
            res.get("time_to_best_s", ""),
            res.get("evaluations", ""),
            int(feasible),
        ])

    history = res.get("history", [])
    if history:
        conv_file = os.path.join(
            "results", "conv", f"{instance_name}_{algo_name}_seed{seed}_conv.csv"
        )
        with open(conv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["time_s", "iter", "evals", "best_value"])
            writer.writerows(history)

    sol_file = os.path.join(
        "results", "solutions", f"{instance_name}_{algo_name}_seed{seed}.sol"
    )
    with open(sol_file, "w", encoding="utf-8") as f:
        f.write(f"Instance: {instance_name}\n")
        f.write(f"Algorithm: {algo_name} | Seed: {seed}\n")
        f.write(f"Best Cost: {res.get('best_value')} | Feasible: {int(feasible)}\n")
        f.write(
            "Selected columns (1-indexed): " + " ".join(map(str, sol)) + "\n"
        )

    return feasible


def main():
    prepare_clean_dirs()
    sa_solver = load_sa_solver()

    # Đầy đủ 11 bộ dữ liệu chuẩn chia theo 3 mức kích thước (Nhỏ - Vừa - Lớn)
    candidate_files = [
        # 1. Dữ liệu nhỏ (Small)
        "data/vidu/vidu.txt",
        "data/tusinh/sc_10_10_s101.txt",
        "data/tusinh/sc_20_20_s101.txt",
        # 2. Dữ liệu vừa (Medium & Thực tế UTH)
        "data/tusinh/sc_30_30_s101.txt",
        "data/tusinh/sc_30_30_s102.txt",
        "data/osm/uth_setcover.txt",
        # 3. Dữ liệu lớn (Large - OR-Library)
        "data/chuan/scp41.txt",
        "data/chuan/scp42.txt",
        "data/chuan/scp43.txt",
        "data/chuan/scp44.txt",
        "data/chuan/scp45.txt",
    ]
    datasets = [p for p in candidate_files if os.path.exists(p)]

    if not datasets:
        print("Không tìm thấy tệp dữ liệu nào trong danh sách.")
        return

    print(f"[Hệ thống] Tìm thấy {len(datasets)}/11 bộ dữ liệu hợp lệ. Bắt đầu chạy thực nghiệm...")

    seeds = [42, 100, 2026, 7, 13, 21, 99, 123, 555, 888]
    errors_log = []

    for filepath in datasets:
        instance_name = os.path.splitext(os.path.basename(filepath))[0]
        m, n, costs, row_cols, col_rows = _parse_orlib_file(filepath)
        time_limit = 1.0 if n <= 50 else 5.0
        tenure = min(15, max(2, n // 3))

        print(
            f"\n>>> Đang chạy bộ dữ liệu: {instance_name} (m={m}, n={n}, time_limit={time_limit}s)"
        )

        for seed in seeds:
            tasks = [
                (
                    "TS",
                    lambda: solve_tabu_search(
                        m,
                        n,
                        costs,
                        row_cols,
                        col_rows,
                        time_limit=time_limit,
                        max_iter=50000,
                        tabu_tenure=tenure,
                        seed=seed,
                    ),
                ),
                (
                    "GA",
                    lambda: solve_genetic_algorithm(
                        m,
                        n,
                        costs,
                        row_cols,
                        col_rows,
                        time_limit=time_limit,
                        pop_size=50,
                        mutation_rate=0.05,
                        seed=seed,
                    ),
                ),
            ]
            if sa_solver is not None:
                tasks.insert(
                    0,
                    (
                        "SA",
                        lambda: call_sa_safely(
                            sa_solver,
                            m,
                            n,
                            costs,
                            row_cols,
                            col_rows,
                            time_limit,
                            seed,
                        ),
                    ),
                )

            for algo_name, runner in tasks:
                try:
                    res = runner()
                    feasible = save_outputs(
                        instance_name, algo_name, seed, m, col_rows, res
                    )
                    print(
                        f"  [OK] {algo_name:<3} | seed={seed:<4} | Cost={res['best_value']:<6} "
                        f"| Time={res['time_s']:<8}s | Feasible={int(feasible)}"
                    )
                except Exception as e:
                    msg = f"{instance_name} - {algo_name} (seed={seed}): {type(e).__name__}: {e}"
                    errors_log.append(msg)
                    print(f"  [LỖI ĐÃ CÔ LẬP] {msg}")
                    traceback.print_exc(limit=2)

    print("\n" + "=" * 60)
    print("HOÀN TẤT CHẠY THỰC NGHIỆM TOÀN BỘ 11 BỘ DỮ LIỆU!")
    print(
        "Kết quả sạch đã lưu tại: results/raw/, results/conv/, results/solutions/"
    )
    if errors_log:
        print(
            f"\nCó {len(errors_log)} lỗi đã được cô lập (không làm sập pipeline):"
        )
        for err in errors_log:
            print(" -", err)


if __name__ == "__main__":
    main()