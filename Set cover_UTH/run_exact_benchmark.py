import csv
import multiprocessing as mp
import os
import time
from pathlib import Path

from algorithms.branch_and_bound import branch_and_bound
from utils.data_loader import load_set_cover

TIME_LIMIT_SEC = 600.0  # Giới hạn 10 phút theo đúng yêu cầu Mục 3.1.1


def _read_mn(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        tokens = f.read().split()
    return int(tokens[0]), int(tokens[1])


class _SetCoverModelAdapter:
    def __init__(self, data_dict):
        self.m = data_dict["m"]
        self.n = data_dict["n"]
        self.costs = data_dict["costs"]
        if "columns" in data_dict:
            self.columns = data_dict["columns"]
        elif "col_rows" in data_dict:
            self.columns = data_dict["col_rows"]
        else:
            cols = [[] for _ in range(self.n)]
            for i, row in enumerate(data_dict["row_cols"]):
                for j in row:
                    cols[j].append(i)
            self.columns = cols

    def get_covered(self, selected):
        covered = set()
        for j in selected:
            covered.update(self.columns[j])
        return covered

    def is_feasible(self, selected):
        return len(self.get_covered(selected)) == self.m

    def calculate_cost(self, selected):
        return sum(self.costs[j] for j in selected)


def _bb_worker(filepath_str, queue):
    try:
        raw_data = load_set_cover(filepath_str)
        model = _SetCoverModelAdapter(raw_data) if isinstance(raw_data, dict) else raw_data
        t0 = time.perf_counter()
        sol, cost = branch_and_bound(model)
        elapsed = time.perf_counter() - t0
        queue.put(("OK", cost, sorted([x + 1 for x in sol]), elapsed))
    except Exception as e:
        queue.put(("ERROR", str(e), [], 0.0))


def collect_small_medium_datasets():
    target_files = [Path("data/sample/vidu.txt")]
    gen_dir = Path("data/generated")
    if gen_dir.exists():
        target_files.extend(sorted(gen_dir.glob("*.txt")))

    sized = []
    for p in target_files:
        if p.exists():
            m, n = _read_mn(p)
            sized.append((n, m, p))
    sized.sort(key=lambda x: (x[0], x[1], x[2].name))
    return sized


def main():
    os.makedirs("results/summary", exist_ok=True)
    datasets = collect_small_medium_datasets()
    if not datasets:
        print("Khong tim thay tep du lieu nho/tu sinh.")
        return

    print(f"Tim thay {len(datasets)} bo du lieu nho/vua. Bat dau chay Nhanh can (gioi han {TIME_LIMIT_SEC}s/bo)...")
    rows = []

    for n, m, path in datasets:
        inst_name = path.stem
        print(f"\n>>> Dang giai {inst_name} (m={m}, n={n})...")
        q = mp.Queue()
        proc = mp.Process(target=_bb_worker, args=(str(path), q))
        proc.start()
        proc.join(timeout=TIME_LIMIT_SEC)

        if proc.is_alive():
            proc.terminate()
            proc.join()
            print(f"  [TIMEOUT > {TIME_LIMIT_SEC}s] Vuot nguong 10 phut!")
            rows.append([inst_name, m, n, "TIMEOUT (>600s)", "N/A", f">{TIME_LIMIT_SEC}"])
            break

        if not q.empty():
            status, cost, sol_1based, elapsed = q.get()
            if status == "OK":
                print(f"  [OPTIMAL] f* = {cost} | Time = {elapsed:.6f}s | Sol = {sol_1based}")
                rows.append([inst_name, m, n, "OPTIMAL", cost, round(elapsed, 6)])
            else:
                print(f"  [ERROR] {cost}")
                rows.append([inst_name, m, n, f"ERROR: {cost}", "N/A", "N/A"])

    out_csv = "results/summary/exact_benchmark.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Instance", "m", "n", "Status", "Optimal_Cost_f*", "Time_s"])
        writer.writerows(rows)

    print(f"\nHoan tat! Bang ket qua Nhanh can da luu tai: {out_csv}")


if __name__ == "__main__":
    mp.freeze_support()
    main()