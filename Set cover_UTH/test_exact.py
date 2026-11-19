
from itertools import combinations

from algorithms.branch_and_bound import branch_and_bound
from algorithms.greedy import greedy_set_cover


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


def brute_force(model):
    best_solution = None
    best_cost = float("inf")

    for r in range(model.n + 1):
        for combo in combinations(range(model.n), r):
            if model.is_feasible(combo):
                cost = model.calculate_cost(combo)

                if cost < best_cost:
                    best_cost = cost
                    best_solution = list(combo)

    return best_solution, best_cost


model = TestModel()

exact_solution, exact_cost = branch_and_bound(model)
brute_solution, brute_cost = brute_force(model)

print("\n=== KET QUA KIEM THU ===")
print("Branch and Bound:", exact_solution, exact_cost)
print("Brute Force     :", brute_solution, brute_cost)

assert model.is_feasible(exact_solution), "Nghiem khong hop le"
assert exact_cost == brute_cost, "Sai chi phi toi uu"

print("PASS: Branch and Bound tim dung chi phi toi uu!")
