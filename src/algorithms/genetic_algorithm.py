import os
import random
import sys
import time


def _parse_orlib_file(filepath):
    """Đọc tệp chuẩn OR-Library độc lập (trả về dữ liệu chuẩn hóa 0-indexed)."""
    with open(filepath, "r", encoding="utf-8") as f:
        tokens = f.read().split()
    it = iter(tokens)
    m = int(next(it))
    n = int(next(it))
    costs = [float(next(it)) for _ in range(n)]
    costs = [int(c) if c.is_integer() else c for c in costs]
    row_cols = [[] for _ in range(m)]
    col_rows = [[] for _ in range(n)]
    for i in range(m):
        k = int(next(it))
        for _ in range(k):
            col_idx = int(next(it)) - 1
            row_cols[i].append(col_idx)
            col_rows[col_idx].append(i)
    return m, n, costs, row_cols, col_rows


def _validate_solution(m, selected_0based, col_rows):
    """Hàm kiểm tra độc lập tính hợp lệ của lời giải."""
    covered = [False] * m
    for j in selected_0based:
        for i in col_rows[j]:
            covered[i] = True
    uncovered = [i + 1 for i, ok in enumerate(covered) if not ok]
    return len(uncovered) == 0, uncovered


def _repair_and_prune(selected_set, m, costs, row_cols, col_rows):
    """
    Toán tử sửa chữa & xóa cột thừa của Beasley & Chu (1996):
    1. Duyệt các hàng chưa được phủ (ưu tiên hàng khó phủ nhất - ít cột phủ nhất),
       thêm cột có tỉ số (chi phí / số hàng mới phủ) nhỏ nhất.
    2. Loại bỏ các cột thừa theo chi phí giảm dần.
    """
    cover_count = [0] * m
    for j in selected_set:
        for i in col_rows[j]:
            cover_count[i] += 1

    uncovered = {i for i in range(m) if cover_count[i] == 0}

    # Bước 1: Phủ các hàng còn thiếu
    while uncovered:
        target_row = min(uncovered, key=lambda r: len(row_cols[r]))
        best_j = -1
        best_ratio = float("inf")
        for j in row_cols[target_row]:
            newly_covered = sum(1 for r in col_rows[j] if r in uncovered)
            if newly_covered > 0:
                ratio = costs[j] / newly_covered
                if ratio < best_ratio:
                    best_ratio = ratio
                    best_j = j

        selected_set.add(best_j)
        for r in col_rows[best_j]:
            if cover_count[r] == 0:
                uncovered.discard(r)
            cover_count[r] += 1

    # Bước 2: Xóa cột thừa theo chi phí giảm dần
    for j in sorted(selected_set, key=lambda c: costs[c], reverse=True):
        if all(cover_count[r] >= 2 for r in col_rows[j]):
            selected_set.remove(j)
            for r in col_rows[j]:
                cover_count[r] -= 1

    total_cost = sum(costs[j] for j in selected_set)
    return selected_set, total_cost


def solve_genetic_algorithm(
    m,
    n,
    costs,
    row_cols,
    col_rows,
    time_limit=30.0,
    pop_size=40,
    max_generations=1000,
    mutation_rate=None,
    seed=42,
    one_indexed_output=True,
):
    """
    Genetic Algorithm (GA) theo Beasley & Chu (1996) cho bài toán Set Cover (Đề 10).
    - Tham số:
        pop_size: kích thước quần thể
        max_generations: số thế hệ tiến hóa tối đa
        mutation_rate: xác suất đột biến mỗi gen (mặc định 2.0 / n)
        time_limit: ngân sách thời gian chạy (giây)
        seed: hạt giống ngẫu nhiên
    - Trả về dict chuẩn hóa để xuất raw CSV, conv CSV và file .sol.
    """
    rng = random.Random(seed)
    start_time = time.perf_counter()

    if mutation_rate is None:
        mutation_rate = min(0.1, 2.0 / max(1, n))

    population = []  # Danh sách các phần tử (cost, frozenset_selected)
    seen_solutions = set()
    evaluations = 0

    # 1. Khởi tạo quần thể ban đầu đa dạng (không trùng lặp cá thể)
    attempts = 0
    while len(population) < pop_size and attempts < pop_size * 6:
        attempts += 1
        if time.perf_counter() - start_time >= time_limit:
            break

        cand = set()
        uncovered = set(range(m))
        while uncovered:
            r = rng.choice(tuple(uncovered))
            j = rng.choice(row_cols[r])
            cand.add(j)
            uncovered.difference_update(col_rows[j])

        cand, cost = _repair_and_prune(cand, m, costs, row_cols, col_rows)
        evaluations += 1
        frozen = frozenset(cand)
        if frozen not in seen_solutions:
            seen_solutions.add(frozen)
            population.append((cost, frozen))

    if not population:
        cand, cost = _repair_and_prune(set(), m, costs, row_cols, col_rows)
        population.append((cost, frozenset(cand)))
        evaluations += 1

    population.sort(key=lambda x: x[0])
    best_cost, best_frozen = population[0]
    time_to_best = time.perf_counter() - start_time
    history = [(round(time_to_best, 6), 0, evaluations, best_cost)]

    # 2. Vòng lặp tiến hóa (Steady-State Replacement)
    gen = 0
    for gen in range(1, max_generations + 1):
        if time.perf_counter() - start_time >= time_limit:
            break

        # Chọn lọc giải đấu nhị phân (Binary Tournament Selection)
        t_size = min(2, len(population))
        p1 = min(rng.sample(population, t_size), key=lambda x: x[0])
        p2 = min(rng.sample(population, t_size), key=lambda x: x[0])

        cost1, set1 = p1
        cost2, set2 = p2

        # Lai ghép hợp nhất (Fusion Crossover - Beasley & Chu 1996)
        prob_p1 = cost2 / (cost1 + cost2) if (cost1 + cost2) > 0 else 0.5
        child = set()
        for j in set1 | set2:
            in1 = j in set1
            in2 = j in set2
            if in1 and in2:
                child.add(j)
            elif in1 and rng.random() < prob_p1:
                child.add(j)
            elif in2 and rng.random() >= prob_p1:
                child.add(j)

        # Đột biến lật bit (Bit-flip Mutation)
        for j in range(n):
            if rng.random() < mutation_rate:
                if j in child:
                    child.remove(j)
                else:
                    child.add(j)

        # Toán tử sửa chữa và xóa cột thừa
        child, child_cost = _repair_and_prune(child, m, costs, row_cols, col_rows)
        evaluations += 1
        child_frozen = frozenset(child)

        # Cập nhật quần thể (thay thế cá thể tệ nhất nếu cá thể con mới và tốt hơn)
        if child_frozen not in seen_solutions:
            worst_cost, worst_frozen = population[-1]
            if child_cost < worst_cost or len(population) < pop_size:
                if len(population) >= pop_size:
                    seen_solutions.remove(worst_frozen)
                    population.pop()
                seen_solutions.add(child_frozen)
                population.append((child_cost, child_frozen))
                population.sort(key=lambda x: x[0])

                if child_cost < best_cost:
                    best_cost = child_cost
                    best_frozen = child_frozen
                    time_to_best = time.perf_counter() - start_time
                    history.append((round(time_to_best, 6), gen, evaluations, best_cost))

    total_time = time.perf_counter() - start_time
    if not history or history[-1][1] != gen:
        history.append((round(total_time, 6), gen, evaluations, best_cost))

    feasible, _ = _validate_solution(m, best_frozen, col_rows)
    out_solution = sorted(j + 1 if one_indexed_output else j for j in best_frozen)

    return {
        "algorithm": "GA",
        "params": f"pop={pop_size};gen={max_generations};mut={mutation_rate:.4f}",
        "seed": seed,
        "best_value": best_cost,
        "solution": out_solution,
        "time_s": round(total_time, 6),
        "time_to_best_s": round(time_to_best, 6),
        "evaluations": evaluations,
        "feasible": int(feasible),
        "history": history,
    }


if __name__ == "__main__":
    # Cho phép chạy test trực tiếp: python algorithms/genetic_algorithm.py data/vidu/vidu.txt
    test_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "vidu", "vidu.txt")
    if os.path.exists(test_file):
        m, n, costs, row_cols, col_rows = _parse_orlib_file(test_file)
        res = solve_genetic_algorithm(m, n, costs, row_cols, col_rows, time_limit=5.0, seed=42)
        print(f"File: {test_file} | Best Cost: {res['best_value']} | Feasible: {res['feasible']}")
        print(f"Selected columns (1-indexed): {res['solution']}")
        print(f"Time: {res['time_s']}s | Time to best: {res['time_to_best_s']}s | Evals: {res['evaluations']}")
    else:
        print(f"Không tìm thấy tệp {test_file}. Hãy truyền đường dẫn tệp dữ liệu làm tham số.")