
from utils.data_loader import load_set_cover


class SetCoverModel:
    def __init__(self, path):
        # Doc du lieu Set Cover
        data = load_set_cover(path)

        # So doi tuong can phu
        self.m = data["m"]

        # So vi tri camera ung vien
        self.n = data["n"]

        # Chi phi tung camera
        self.costs = data["costs"]

        # Moi doi tuong duoc nhung camera nao phu
        self.rows = data["rows"]

        # Moi camera phu nhung doi tuong nao
        self.columns = data["columns"]

    def calculate_cost(self, selected):
        # Tinh tong chi phi camera
        return sum(
            self.costs[j] for j in selected
        )

    def get_covered(self, selected):
        # Lay tat ca doi tuong duoc phu
        covered = set()

        for j in selected:
            covered.update(self.columns[j])

        return covered

    def is_feasible(self, selected):
        # Kiem tra tat ca doi tuong duoc phu
        return len(self.get_covered(selected)) == self.m

    def coverage_rate(self, selected):
        # Tinh ty le phu
        covered = self.get_covered(selected)

        return len(covered) / self.m * 100
