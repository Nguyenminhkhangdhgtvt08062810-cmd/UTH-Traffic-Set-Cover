
# Duong dan lam viec: thu muc goc bai nop.
import os as _project_os
from pathlib import Path as _project_Path
_project_os.chdir(_project_Path(__file__).resolve().parent.parent)

import time

from utils.set_cover_model import SetCoverModel
from utils.validator import validate_solution
from algorithms.greedy import greedy_set_cover
from algorithms.branch_and_bound import branch_and_bound

# Doc du lieu mau
model = SetCoverModel("data/vidu/vidu.txt")

data = {
    "m": model.m,
    "n": model.n,
    "costs": model.costs,
    "rows": model.rows,
    "columns": model.columns
}

print("=== KIEM TRA BRANCH AND BOUND ===")

# Nghiem Greedy
greedy_solution = greedy_set_cover(model)
greedy_cost = model.calculate_cost(greedy_solution)

print("Chi phi Greedy:", greedy_cost)

# Chay Branch and Bound
start = time.perf_counter()

solution, optimal_cost = branch_and_bound(model)

elapsed = time.perf_counter() - start

# Kiem chung doc lap
valid, verified_cost, message = validate_solution(
    data, solution
)

print("\n=== KET QUA EXACT ===")
print("Camera:", [j + 1 for j in solution])
print("Chi phi toi uu:", optimal_cost)
print("Chi phi Validator:", verified_cost)
print("Ty le phu:", model.coverage_rate(solution), "%")
print("Thoi gian:", round(elapsed, 6), "giay")
print("Validator:", message)

assert valid, "Nghiem khong hop le!"
assert optimal_cost == verified_cost
assert optimal_cost == 16

print("\nKIEM TRA BRANCH AND BOUND THANH CONG")
