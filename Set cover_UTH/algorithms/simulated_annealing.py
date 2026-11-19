import math
import random

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
    """Simulated Annealing cho Weighted Set Cover.

    Mac dinh tra ve danh sach camera tot nhat (tuong thich code/Web cu).
    Neu return_history=True, tra ve (best, history).

    history la danh sach dict voi cac cot:
    iteration, temperature, current_cost, best_cost, accepted, move.
    Co dong iteration=0 cho trang thai ban dau.
    """
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
                    if not swap_feasible_fast(
                        model, cover_count, remove_j, add_j
                    ):
                        continue
                    neighbor = sorted(
                        (selected_set - {remove_j}) | {add_j}
                    )
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
