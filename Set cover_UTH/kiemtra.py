
import sys
from pathlib import Path

from utils.data_loader import load_set_cover
from utils.validator import validate_solution


def main():
    if len(sys.argv) != 3:
        print("Cach dung:")
        print("python kiemtra.py <file_du_lieu> <file_loi_giai>")
        return

    input_path = Path(sys.argv[1])
    solution_path = Path(sys.argv[2])

    try:
        data = load_set_cover(input_path)

        # Dong 1: chi phi khai bao
        # Dong 2: danh sach camera duoc chon (1-based)
        lines = solution_path.read_text(
            encoding="utf-8"
        ).strip().splitlines()

        if not lines:
            raise ValueError("File loi giai rong")

        declared_cost = int(lines[0].strip())

        camera_ids = [
            int(x)
            for line in lines[1:]
            for x in line.split()
        ]

        # Chuyen sang chi so Python (0-based)
        selected = [x - 1 for x in camera_ids]

        valid, actual_cost, message = validate_solution(
            data, selected
        )

        if not valid:
            print("KHONG HOP LE:", message)
        elif declared_cost != actual_cost:
            print("KHONG HOP LE: Chi phi khai bao khong khop")
        else:
            print("HOP LE")

        print("Chi phi khai bao:", declared_cost)
        print("Chi phi tinh lai:", actual_cost)

    except (OSError, ValueError, IndexError) as e:
        print("KHONG HOP LE:", e)


if __name__ == "__main__":
    main()
