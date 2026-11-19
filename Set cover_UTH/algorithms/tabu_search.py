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
            col_idx = int(next(it)) - 1  # Chuyển về 0-indexed
            row_cols[i].append(col_idx)
            col_rows[col_idx].append(i)
    return m, n, costs, row_cols, col_rows


def _remove_redundant_columns(selected_set, cover_count, col_rows, costs):
    """Hậu xử lý: loại bỏ các cột thừa theo thứ tự chi phí giảm dần."""
    candidates = sorted(selected_set, key=lambda j: costs[j], reverse=True)
    for j in candidates:
        if all(cover_count[i] >= 2 for i in col_rows[j]):
            selected_set.remove(j)
            for i in col_rows[j]:
                cover_count[i] -= 1


def _validate_solution(m, selected_0based, col_rows):
    """Hàm kiểm tra độc lập tính hợp lệ của lời giải."""
    covered = [False] * m
    for j in selected_0based:
        for i in col_rows[j]:
            covered[i] = True
    uncovered = [i + 1 for i, ok in enumerate(covered) if not ok]
    return len(uncovered) == 0, uncovered


def solve_tabu_search(
    m,
    n,
    costs,
    row_cols,
    col_rows,
    initial_solution=None,
    time_limit=30.0,
    max_iter=15000,
    tabu_tenure=15,
    seed=42,
    one_indexed_output=True,
):
    """
    Tabu Search (TS) cho bài toán Set Cover (Đề 10).
    - Tham số:
        m, n: số hàng (nút giao), số cột (vị trí đặt camera)
        costs: danh sách chi phí n cột
        row_cols, col_rows: danh sách kề 2 chiều (0-indexed)
        time_limit: ngân sách thời gian chạy (giây)
        tabu_tenure: độ dài danh sách tabu cơ bản
        seed: hạt giống ngẫu nhiên để tái lập kết quả
    - Trả về dict chuẩn hóa để xuất raw CSV, conv CSV và file .sol.
    """
    rng = random.Random(seed)
    start_time = time.perf_counter()

    # Trọng số phạt khi vi phạm ràng buộc phủ hàng
    penalty_weight = (max(costs) * 2.0 + 1.0) if costs else 100.0

    # 1. Khởi tạo lời giải ban đầu
    selected = set()
    if initial_solution is not None:
        # Tự động nhận diện nếu initial_solution đang ở dạng 1-indexed
        offset = 1 if (initial_solution and max(initial_solution) >= n) else 0
        selected = {j - offset for j in initial_solution}

    cover_count = [0] * m
    for j in selected:
        for i in col_rows[j]:
            cover_count[i] += 1

    # Nếu chưa có lời giải đầu, xây dựng bằng tham lam ngẫu nhiên hóa
    if not selected:
        uncovered = {i for i in range(m) if cover_count[i] == 0}
        while uncovered:
            i = rng.choice(tuple(uncovered))
            best_j = min(row_cols[i], key=lambda j: costs[j] / max(1, len(col_rows[j])))
            selected.add(best_j)
            for r in col_rows[best_j]:
                if cover_count[r] == 0:
                    uncovered.discard(r)
                cover_count[r] += 1

    _remove_redundant_columns(selected, cover_count, col_rows, costs)

    current_cost = sum(costs[j] for j in selected)
    uncovered_count = sum(1 for c in cover_count if c == 0)

    best_selected = set(selected)
    best_cost = current_cost if uncovered_count == 0 else float("inf")
    time_to_best = time.perf_counter() - start_time
    evaluations = 1

    # Lưu log hội tụ: (time_s, iter, evals, best_value)
    history = [(round(time_to_best, 6), 0, evaluations, best_cost)]
    tabu_until = [0] * n
    it = 0

    # 2. Vòng lặp chính của Tabu Search
    for it in range(1, max_iter + 1):
        if time.perf_counter() - start_time >= time_limit:
            break

        best_move_j = -1
        best_move_obj = float("inf")
        best_move_cost = float("inf")
        best_move_uncovered = m

        # Đánh giá lân cận 1-flip bằng kỹ thuật delta evaluation
        for j in range(n):
            evaluations += 1
            if j in selected:
                # Lân cận bỏ cột j
                delta_cost = -costs[j]
                delta_uncov = sum(1 for i in col_rows[j] if cover_count[i] == 1)
            else:
                # Lân cận thêm cột j
                delta_cost = costs[j]
                delta_uncov = -sum(1 for i in col_rows[j] if cover_count[i] == 0)

            cand_cost = current_cost + delta_cost
            cand_uncov = uncovered_count + delta_uncov
            cand_obj = cand_cost + penalty_weight * cand_uncov

            is_tabu = it < tabu_until[j]
            # Tiêu chí mong đợi (Aspiration): phá tabu nếu tìm được lời giải hợp lệ tốt hơn kỷ lục
            aspiration = (cand_uncov == 0) and (cand_cost < best_cost)

            if (not is_tabu or aspiration) and cand_obj < best_move_obj:
                best_move_obj = cand_obj
                best_move_j = j
                best_move_cost = cand_cost
                best_move_uncovered = cand_uncov

        if best_move_j == -1:
            break

        # Cập nhật trạng thái và mảng cover_count
        j = best_move_j
        if j in selected:
            selected.remove(j)
            for i in col_rows[j]:
                cover_count[i] -= 1
        else:
            selected.add(j)
            for i in col_rows[j]:
                cover_count[i] += 1

        current_cost = best_move_cost
        uncovered_count = best_move_uncovered
        # Cập nhật thời hạn cấm (thêm nhiễu ngẫu nhiên nhỏ tránh lặp chu trình)
        tabu_until[j] = it + tabu_tenure + rng.randint(0, max(2, tabu_tenure // 3))

        # Khi lời giải hợp lệ, tối ưu hóa bằng xóa cột thừa và kiểm tra kỷ lục
        if uncovered_count == 0:
            _remove_redundant_columns(selected, cover_count, col_rows, costs)
            current_cost = sum(costs[c] for c in selected)
            if current_cost < best_cost:
                best_cost = current_cost
                best_selected = set(selected)
                time_to_best = time.perf_counter() - start_time
                history.append((round(time_to_best, 6), it, evaluations, best_cost))

    total_time = time.perf_counter() - start_time
    if not history or history[-1][1] != it:
        history.append((round(total_time, 6), it, evaluations, best_cost))

    feasible, _ = _validate_solution(m, best_selected, col_rows)
    out_solution = sorted(j + 1 if one_indexed_output else j for j in best_selected)

    return {
        "algorithm": "TS",
        "params": f"tenure={tabu_tenure};max_iter={max_iter}",
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
    # Cho phép chạy test trực tiếp: python algorithms/tabu_search.py data/sample/vidu.txt
    test_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "sample", "vidu.txt")
    if os.path.exists(test_file):
        m, n, costs, row_cols, col_rows = _parse_orlib_file(test_file)
        res = solve_tabu_search(m, n, costs, row_cols, col_rows, time_limit=5.0, seed=42)
        print(f"File: {test_file} | Best Cost: {res['best_value']} | Feasible: {res['feasible']}")
        print(f"Selected columns (1-indexed): {res['solution']}")
        print(f"Time: {res['time_s']}s | Time to best: {res['time_to_best_s']}s | Evals: {res['evaluations']}")
    else:
        print(f"Không tìm thấy tệp {test_file}. Hãy truyền đường dẫn tệp dữ liệu làm tham số.")