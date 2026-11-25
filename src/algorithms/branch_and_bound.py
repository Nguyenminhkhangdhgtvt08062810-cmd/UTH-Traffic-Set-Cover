from algorithms.greedy import greedy_set_cover


def branch_and_bound(model):
    """Exact Weighted Set Cover using preprocessing and Branch and Bound.

    Returns (selected_camera_indices, total_cost) with zero-based indices.
    Assumes finite, nonnegative camera costs and valid model columns.
    """
    m, n = model.m, model.n
    if m == 0:
        return [], 0

    costs = model.costs
    all_rows = (1 << m) - 1
    covers = [0] * n
    for j in range(n):
        for i in model.columns[j]:
            covers[j] |= 1 << i

    union = 0
    for mask in covers:
        union |= mask
    if union != all_rows:
        raise ValueError('Khong co nghiem phu du tat ca nut giao')
    if any(c < 0 for c in costs):
        raise ValueError('Chi phi camera phai khong am')

    # Greedy is a feasible incumbent, not a proof of optimality.
    initial = greedy_set_cover(model)
    best_solution = sorted(initial)
    best_cost = model.calculate_cost(initial)

    # Drop cameras that cover no required row.
    active = [j for j in range(n) if covers[j]]

    # Dominance: if A's coverage is a subset of B's, and B costs no
    # more, A is unnecessary.  Tie-break equal covers/costs by index.
    kept = []
    for a in active:
        dominated = False
        for b in active:
            if a == b or costs[b] > costs[a]:
                continue
            if covers[a] & ~covers[b]:
                continue
            if covers[a] == covers[b] and costs[a] == costs[b] and b > a:
                continue
            dominated = True
            break
        if not dominated:
            kept.append(a)

    # Forced rows: if exactly one active camera covers a row, select it.
    forced = set()
    forced_mask = 0
    while True:
        missing = all_rows & ~forced_mask
        newly_forced = set()
        bitset = missing
        while bitset:
            bit = bitset & -bitset
            bitset -= bit
            candidates = [j for j in kept if covers[j] & bit]
            if not candidates:
                raise ValueError('Khong the phu het nut giao sau khi giam co')
            if len(candidates) == 1:
                newly_forced.add(candidates[0])
        newly_forced -= forced
        if not newly_forced:
            break
        forced.update(newly_forced)
        for j in newly_forced:
            forced_mask |= covers[j]

    forced_cost = sum(costs[j] for j in forced)
    remaining = all_rows & ~forced_mask
    if not remaining:
        return sorted(forced), forced_cost

    candidates = [j for j in kept if j not in forced and covers[j] & remaining]
    reduced_cover = {j: covers[j] & remaining for j in candidates}

    # Precompute candidate lists for each uncovered row.
    row_options = [tuple(j for j in candidates if reduced_cover[j] & (1 << i))
                   for i in range(m)]

    nodes_visited = 0
    nodes_pruned = 0
    seen = {}

    def lower_bound(uncovered):
        """Valid packing lower bound from disjoint row option sets."""
        row_data = []
        bits = uncovered
        while bits:
            bit = bits & -bits
            bits -= bit
            i = bit.bit_length() - 1
            options = row_options[i]
            if not options:
                return float('inf')
            row_data.append((len(options), min(costs[j] for j in options), options))

        # Rows with pairwise disjoint camera choices require separate
        # cameras, so their cheapest costs can be added safely.
        row_data.sort(key=lambda x: (x[0], -x[1]))
        used_options = set()
        bound = 0
        for _, minimum, options in row_data:
            if all(j not in used_options for j in options):
                bound += minimum
                used_options.update(options)
        return bound

    def dfs(uncovered, selected, extra_cost):
        nonlocal best_solution, best_cost, nodes_visited, nodes_pruned
        nodes_visited += 1
        total_cost = forced_cost + extra_cost

        if not uncovered:
            if total_cost < best_cost:
                best_cost = total_cost
                best_solution = sorted(forced | set(selected))
            return

        if total_cost >= best_cost:
            nodes_pruned += 1
            return

        previous = seen.get(uncovered)
        if previous is not None and previous <= total_cost:
            nodes_pruned += 1
            return
        seen[uncovered] = total_cost

        if total_cost + lower_bound(uncovered) >= best_cost:
            nodes_pruned += 1
            return

        # Choose the most constrained uncovered row (fewest cameras).
        chosen_options = None
        bits = uncovered
        while bits:
            bit = bits & -bits
            bits -= bit
            i = bit.bit_length() - 1
            opts = row_options[i]
            if chosen_options is None or len(opts) < len(chosen_options):
                chosen_options = opts
                if len(opts) == 1:
                    break

        # Cost per new covered row is a useful branch order heuristic.
        order = sorted(chosen_options,
                       key=lambda j: (costs[j] / (uncovered & reduced_cover[j]).bit_count(), j))
        for j in order:
            dfs(uncovered & ~reduced_cover[j], selected + [j], extra_cost + costs[j])

    print('=== BRANCH AND BOUND ===')
    print('Can tren Greedy:', best_cost)
    print('Camera sau dominance:', len(kept), '/', n)
    print('Camera bat buoc:', len(forced))
    dfs(remaining, [], 0)
    print('So nut da duyet:', nodes_visited)
    print('So nut cat tia:', nodes_pruned)
    print('Chi phi toi uu:', best_cost)
    return sorted(best_solution), best_cost
