
def calculate_cover_count(model, selected):
    """
    Dem so camera dang phu moi doi tuong.
    """
    cover_count = [0] * model.m

    for j in selected:
        for i in model.columns[j]:
            cover_count[i] += 1

    return cover_count


def swap_delta(model, remove_camera, add_camera):
    """
    Tinh thay doi chi phi khi Swap.
    """
    return (
        model.costs[add_camera]
        - model.costs[remove_camera]
    )


def swap_feasible_fast(
    model, cover_count, remove_camera, add_camera
):
    """
    Kiem tra do phu cua phep Swap bang cover_count.

    Gia dinh nghiem hien tai hop le.
    Camera bo dang duoc chon.
    Camera them chua duoc chon.
    """
    add_covered = set(model.columns[add_camera])

    for i in model.columns[remove_camera]:
        if cover_count[i] == 1 and i not in add_covered:
            return False

    return True


def swap_camera(model, selected, remove_camera, add_camera):
    """
    Thay mot camera dang chon bang camera chua chon.
    Tra ve None neu nghiem moi khong hop le.
    """
    selected_set = set(selected)

    if remove_camera not in selected_set:
        return None

    if add_camera in selected_set:
        return None

    if not (0 <= remove_camera < model.n):
        return None

    if not (0 <= add_camera < model.n):
        return None

    new_selected = (
        selected_set - {remove_camera}
    ) | {add_camera}

    if not model.is_feasible(new_selected):
        return None

    return sorted(new_selected)


def remove_and_repair(model, selected, remove_camera):
    """
    Bo mot camera, sua nghiem bang Greedy,
    sau do loai camera du thua.
    """
    if remove_camera not in selected:
        raise ValueError("Camera khong nam trong nghiem")

    original = sorted(set(selected))
    new_selected = set(original)
    new_selected.remove(remove_camera)

    uncovered = (
        set(range(model.m))
        - model.get_covered(new_selected)
    )

    while uncovered:
        best_camera = None
        best_ratio = float("inf")

        for j in range(model.n):
            if j in new_selected or j == remove_camera:
                continue

            new_cover = len(
                set(model.columns[j]) & uncovered
            )

            if new_cover == 0:
                continue

            ratio = model.costs[j] / new_cover

            if ratio < best_ratio:
                best_ratio = ratio
                best_camera = j

        if best_camera is None:
            # Khong the sua: tra ve nghiem ban dau
            return original

        new_selected.add(best_camera)
        uncovered.difference_update(
            model.columns[best_camera]
        )

    # Loai camera du thua
    for j in sorted(
        list(new_selected),
        key=lambda x: (-model.costs[x], x)
    ):
        trial = new_selected - {j}

        if model.is_feasible(trial):
            new_selected.remove(j)

    return sorted(new_selected)


def hill_climbing_first(model, initial_solution):
    """
    First Improvement:
    Gap nghiem tot hon dau tien thi chap nhan ngay.
    """
    current = sorted(set(initial_solution))

    if not model.is_feasible(current):
        raise ValueError("Nghiem ban dau khong hop le")

    while True:
        improved = False
        current_cost = model.calculate_cost(current)

        # Lan can 1: Remove & Repair
        for remove_j in current:
            neighbor = remove_and_repair(
                model, current, remove_j
            )

            new_cost = model.calculate_cost(neighbor)

            if new_cost < current_cost:
                current = neighbor
                improved = True
                break

        if improved:
            continue

        # Lan can 2: Swap
        selected_set = set(current)
        cover_count = calculate_cover_count(
            model, current
        )

        for remove_j in current:
            for add_j in range(model.n):
                if add_j in selected_set:
                    continue

                delta = swap_delta(
                    model, remove_j, add_j
                )

                if delta >= 0:
                    continue

                if not swap_feasible_fast(
                    model,
                    cover_count,
                    remove_j,
                    add_j
                ):
                    continue

                current = sorted(
                    (selected_set - {remove_j})
                    | {add_j}
                )

                improved = True
                break

            if improved:
                break

        if not improved:
            break

    return current


def hill_climbing_best(model, initial_solution):
    """
    Best Improvement:
    Xet cac lan can va chon nghiem cai thien tot nhat.
    """
    current = sorted(set(initial_solution))

    if not model.is_feasible(current):
        raise ValueError("Nghiem ban dau khong hop le")

    while True:
        current_cost = model.calculate_cost(current)

        best_neighbor = None
        best_cost = current_cost

        # Lan can 1: Remove & Repair
        for remove_j in current:
            neighbor = remove_and_repair(
                model, current, remove_j
            )

            new_cost = model.calculate_cost(neighbor)

            if new_cost < best_cost:
                best_cost = new_cost
                best_neighbor = neighbor

        # Lan can 2: Swap
        selected_set = set(current)
        cover_count = calculate_cover_count(
            model, current
        )

        for remove_j in current:
            for add_j in range(model.n):
                if add_j in selected_set:
                    continue

                delta = swap_delta(
                    model, remove_j, add_j
                )

                new_cost = current_cost + delta

                # Khong the cai thien nghiem tot nhat
                if new_cost >= best_cost:
                    continue

                if not swap_feasible_fast(
                    model,
                    cover_count,
                    remove_j,
                    add_j
                ):
                    continue

                neighbor = sorted(
                    (selected_set - {remove_j})
                    | {add_j}
                )

                best_cost = new_cost
                best_neighbor = neighbor

        if best_neighbor is None:
            break

        current = best_neighbor

    return current
