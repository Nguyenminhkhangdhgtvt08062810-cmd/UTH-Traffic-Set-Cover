
import inspect

from algorithms.greedy import greedy_set_cover
from algorithms.simulated_annealing import simulated_annealing


class TestModel:
    def __init__(self):
        self.m = 5
        self.n = 5
        self.costs = [4, 6, 3, 5, 7]
        self.columns = [
            [0, 1],
            [1, 2, 3],
            [2, 4],
            [0, 3, 4],
            [1, 4],
        ]

    def get_covered(self, selected):
        covered = set()
        for j in selected:
            covered.update(self.columns[j])
        return covered

    def is_feasible(self, selected):
        return len(self.get_covered(selected)) == self.m

    def calculate_cost(self, selected):
        return sum(self.costs[j] for j in selected)


model = TestModel()
initial = greedy_set_cover(model)

print("=== KIEM TRA SIMULATED ANNEALING ===")

# Kiem tra SA co ho tro ghi log hay khong
signature = inspect.signature(simulated_annealing)

if "return_history" not in signature.parameters:
    raise RuntimeError(
        "SA chua co return_history. "
        "Can cap nhat simulated_annealing.py truoc."
    )

params = {
    "initial_temp": 10.0,
    "cooling_rate": 0.99,
    "max_iterations": 500,
    "seed": 42,
}

# Chay theo cach cu
normal_solution = simulated_annealing(
    model, initial, **params
)

# Chay voi log hoi tu
logged_solution, history = simulated_annealing(
    model,
    initial,
    return_history=True,
    **params
)

assert model.is_feasible(normal_solution), "Nghiem SA khong hop le"
assert normal_solution == logged_solution, "Bat log lam thay doi nghiem"
assert history, "Lich su hoi tu rong"

print("Nghiem:", logged_solution)
print("Chi phi:", model.calculate_cost(logged_solution))
print("So ban ghi hoi tu:", len(history))
print("PASS: SA hoat dong va ghi log hoi tu!")
