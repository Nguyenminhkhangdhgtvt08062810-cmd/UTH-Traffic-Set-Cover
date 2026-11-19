
import csv
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from algorithms.greedy import greedy_set_cover
from algorithms.simulated_annealing import simulated_annealing

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'nodes' / 'uth_nodes_setcover.txt'
OUT = ROOT / 'results'


class Model:
    """Read standard OR-Library SCP text: m n, n costs, m row lists (1-based)."""
    def __init__(self, filename):
        tokens = list(map(int, Path(filename).read_text(encoding='utf-8-sig').split()))
        pos = 0
        self.m, self.n = tokens[pos], tokens[pos + 1]
        pos += 2
        if self.m <= 0 or self.n <= 0:
            raise ValueError('Invalid model dimensions')
        self.costs = tokens[pos:pos + self.n]
        if len(self.costs) != self.n:
            raise ValueError('Missing camera costs')
        pos += self.n
        self.rows = []
        self.columns = [[] for _ in range(self.n)]
        for i in range(self.m):
            if pos >= len(tokens):
                raise ValueError(f'Missing data for intersection {i+1}')
            k = tokens[pos]
            pos += 1
            row = [j - 1 for j in tokens[pos:pos + k]]
            if len(row) != k or any(j < 0 or j >= self.n for j in row):
                raise ValueError(f'Invalid camera indices for intersection {i+1}')
            pos += k
            self.rows.append(row)
            for j in row:
                self.columns[j].append(i)
        if pos != len(tokens):
            raise ValueError('Unexpected trailing data; check SCP file format')

    def get_covered(self, selected):
        result = set()
        for j in selected:
            result.update(self.columns[j])
        return result

    def is_feasible(self, selected):
        return len(self.get_covered(selected)) == self.m

    def calculate_cost(self, selected):
        return sum(self.costs[j] for j in selected)


def main():
    if not DATA.exists():
        raise FileNotFoundError(f'Missing input data: {DATA}')
    model = Model(DATA)
    initial = greedy_set_cover(model)
    solution, history = simulated_annealing(
        model, initial,
        initial_temp=10.0,
        cooling_rate=0.99,
        min_temp=0.01,
        max_iterations=5000,
        seed=42,
        return_history=True,
    )
    if not model.is_feasible(solution):
        raise AssertionError('SA returned infeasible solution')
    assert history[-1]['best_cost'] == model.calculate_cost(solution)

    OUT.mkdir(parents=True, exist_ok=True)
    csv_file = OUT / 'sa_convergence_uth.csv'
    png_file = OUT / 'sa_convergence_uth.png'

    with csv_file.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['iteration', 'temperature', 'current_cost', 'best_cost', 'accepted', 'move'])
        writer.writeheader()
        writer.writerows(history)

    x = [r['iteration'] for r in history]
    current = [r['current_cost'] for r in history]
    best = [r['best_cost'] for r in history]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(x, current, alpha=0.55, linewidth=1, label='Current cost')
    ax.plot(x, best, linewidth=2, label='Best cost')
    ax.set_title('Simulated Annealing - UTH convergence')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Total camera cost')
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(png_file, dpi=180)
    plt.close(fig)

    print('=== SA CONVERGENCE ===')
    print('Intersections:', model.m)
    print('Candidate cameras:', model.n)
    print('Greedy initial cost:', model.calculate_cost(initial))
    print('SA selected cameras:', len(solution))
    print('SA best cost:', model.calculate_cost(solution))
    print('Coverage:', f'{len(model.get_covered(solution))}/{model.m}')
    print('Actual iterations:', len(history) - 1)
    print('CSV:', csv_file)
    print('PNG:', png_file)


if __name__ == '__main__':
    main()
