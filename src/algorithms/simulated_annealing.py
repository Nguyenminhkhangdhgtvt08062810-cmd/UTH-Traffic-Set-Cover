import math
import random
import time

from algorithms.local_search import (
    remove_and_repair,
    calculate_cover_count,
    swap_feasible_fast,
)


def simulated_annealing(
    model,
    initial_solution,
    initial_temp=100.0,
    cooling_rate=0.995,
    min_temp=0.01,
    max_iterations=5000,
    seed=42,
    return_history=False,
):
    """Simulated Annealing cho Weighted Set Cover."""
    if not math.isfinite(initial_temp) or initial_temp <= 0:
        raise ValueError("initial_temp phai la so huu han > 0")
    if not math.isfinite(cooling_rate) or not (0 < cooling_rate < 1):
        raise ValueError("cooling_rate phai nam trong (0, 1)")
    if not math.isfinite(min_temp) or min_temp <= 0:
        raise ValueError("min_temp phai la so huu han > 0")
    if not isinstance(max_iterations, int) or max_iterations < 0:
        raise ValueError("max_iterations phai la so nguyen khong am")

    rng = random.Random(seed)
    current = sorted(set(initial_solution))
    if not model.is_feasible(current):
        raise ValueError("Nghiem ban dau khong hop le")

    current_cost = model.calculate_cost(current)
    best = current.copy()
    best_cost = current_cost
    temperature = initial_temp

    history = []
    if return_history:
        history.append({
            "iteration": 0,
            "temperature": temperature,
            "current_cost": current_cost,
            "best_cost": best_cost,
            "accepted": False,
            "move": "initial",
        })

    for iteration in range(1, max_iterations + 1):
        if temperature < min_temp:
            break

        neighbor = None
        move = "none"
        accepted = False

        if rng.random() < 0.5:
            if current:
                remove_j = rng.choice(current)
                neighbor = remove_and_repair(model, current, remove_j)
                move = "remove_repair"
        else:
            if current and len(current) < model.n:
                selected_set = set(current)
                cover_count = calculate_cover_count(model, current)
                for _ in range(30):
                    remove_j = rng.choice(current)
                    add_j = rng.randrange(model.n)
                    if add_j in selected_set:
                        continue
                    if not swap_feasible_fast(model, cover_count, remove_j, add_j):
                        continue
                    neighbor = sorted((selected_set - {remove_j}) | {add_j})
                    move = "swap"
                    break

        if neighbor is not None:
            neighbor_cost = model.calculate_cost(neighbor)
            delta = neighbor_cost - current_cost
            if delta <= 0 or rng.random() < math.exp(-delta / temperature):
                current = neighbor
                current_cost = neighbor_cost
                accepted = True
                if current_cost < best_cost:
                    best = current.copy()
                    best_cost = current_cost

        if return_history:
            history.append({
                "iteration": iteration,
                "temperature": temperature,
                "current_cost": current_cost,
                "best_cost": best_cost,
                "accepted": accepted,
                "move": move,
            })

        temperature *= cooling_rate

    if return_history:
        return best, history
    return best


class _SAProblemAdapter:
    """Adapter tương thích hoàn toàn với SetCoverModel trong local_search.py."""

    def __init__(self, m, n, costs, row_cols, col_rows):
        self.m = m
        self.n = n
        self.num_rows = m
        self.num_cols = n
        self.costs = costs
        self.row_cols = row_cols
        self.col_rows = col_rows
        self.rows = row_cols
        self.columns = col_rows
        self.row_sets = [set(r) for r in row_cols]
        self.col_sets = [set(c) for c in col_rows]

    def get_covered(self, solution):
        covered = set()
        for j in solution:
            covered.update(self.col_rows[j])
        return covered

    def get_uncovered(self, solution):
        return set(range(self.m)) - self.get_covered(solution)

    def is_feasible(self, solution):
        return len(self.get_covered(solution)) == self.m

    def calculate_cost(self, solution):
        return sum(self.costs[j] for j in solution)


def _greedy_initial_solution(m, n, costs, row_cols, col_rows):
    """Tạo nghiệm khởi tạo hợp lệ bằng Greedy chuẩn."""
    uncovered = set(range(m))
    selected = []
    while uncovered:
        best_j = -1
        best_ratio = float("inf")
        for j in range(n):
            gain = len(uncovered.intersection(col_rows[j]))
            if gain > 0:
                ratio = costs[j] / gain
                if ratio < best_ratio:
                    best_ratio = ratio
                    best_j = j
        if best_j == -1:
            break
        selected.append(best_j)
        uncovered.difference_update(col_rows[best_j])
    return sorted(selected)


def solve_simulated_annealing(
    m,
    n,
    costs,
    row_cols,
    col_rows,
    time_limit=5.0,
    initial_temp=100.0,
    cooling_rate=0.995,
    min_temp=0.01,
    max_iterations=5000,
    seed=42,
    one_indexed_output=True,
):
    """Hàm chuẩn hóa SA đồng bộ định dạng đầu vào/đầu ra với TS và GA."""
    start_time = time.perf_counter()
    model = _SAProblemAdapter(m, n, costs, row_cols, col_rows)
    init_sol = _greedy_initial_solution(m, n, costs, row_cols, col_rows)

    best_0based, raw_history = simulated_annealing(
        model=model,
        initial_solution=init_sol,
        initial_temp=initial_temp,
        cooling_rate=cooling_rate,
        min_temp=min_temp,
        max_iterations=max_iterations,
        seed=seed,
        return_history=True,
    )
    total_time = time.perf_counter() - start_time

    n_steps = max(1, len(raw_history))
    history = []
    best_cost = model.calculate_cost(best_0based)
    time_to_best = total_time

    prev_best = None
    for idx, row in enumerate(raw_history):
        it = row["iteration"]
        b_cost = row["best_cost"]
        est_time = round(total_time * (idx / n_steps), 6)
        if prev_best is None or b_cost < prev_best:
            history.append((est_time, it, it + 1, b_cost))
            time_to_best = est_time
            prev_best = b_cost

    if not history or history[-1][1] != raw_history[-1]["iteration"]:
        last_it = raw_history[-1]["iteration"]
        history.append((round(total_time, 6), last_it, last_it + 1, best_cost))

    out_sol = [j + 1 for j in best_0based] if one_indexed_output else best_0based

    return {
        "algorithm": "SA",
        "params": f"T0={initial_temp},rate={cooling_rate},iter={max_iterations}",
        "seed": seed,
        "best_value": best_cost,
        "solution": out_sol,
        "time_s": round(total_time, 6),
        "time_to_best_s": round(time_to_best, 6),
        "evaluations": len(raw_history),
        "history": history,
    }