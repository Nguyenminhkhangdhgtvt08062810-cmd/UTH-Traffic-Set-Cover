
def greedy_set_cover(model):
    # Cac doi tuong chua duoc phu
    uncovered = set(range(model.m))

    # Camera da chon
    selected = []

    # Camera chua chon
    available = set(range(model.n))

    # Giai doan 1: Greedy
    while uncovered:
        best_camera = None
        best_ratio = float("inf")

        for j in sorted(available):
            # Chuyen list thanh set
            covered_by_camera = set(model.columns[j])

            # Tinh so doi tuong moi duoc phu
            new_covered = len(
                covered_by_camera & uncovered
            )

            if new_covered == 0:
                continue

            ratio = model.costs[j] / new_covered

            if ratio < best_ratio:
                best_ratio = ratio
                best_camera = j

        if best_camera is None:
            raise ValueError(
                "Khong the phu het doi tuong"
            )

        selected.append(best_camera)
        available.remove(best_camera)

        uncovered.difference_update(
            model.columns[best_camera]
        )

    # Giai doan 2: Loai camera du thua
    for j in sorted(
        selected.copy(),
        key=lambda x: model.costs[x],
        reverse=True
    ):
        trial = [x for x in selected if x != j]

        if model.is_feasible(trial):
            selected.remove(j)

    selected.sort()
    return selected
