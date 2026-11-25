
# Duong dan lam viec: thu muc goc bai nop.
import os as _project_os
from pathlib import Path as _project_Path
_project_os.chdir(_project_Path(__file__).resolve().parent.parent)
import sys

from pathlib import Path

from utils.data_loader import load_set_cover
from utils.validator import validate_solution


def _parse_number(val_str):
    num = float(val_str)
    return int(num) if num.is_integer() else num


def _parse_solution_file(lines):
    # Truong hop 1: Dinh dang chuan de bai (Dong 1: tong chi phi, Dong 2+: cac cot chon)
    first_line = lines[0].strip()
    if ":" not in first_line:
        declared_cost = _parse_number(first_line)
        camera_ids = [int(x) for line in lines[1:] for x in line.split()]
        return declared_cost, camera_ids

    # Truong hop 2: Dinh dang co nhan (Instance: ..., Cost/Best_value: ..., Solution: ...)
    declared_cost = None
    camera_ids = None
    for idx, line in enumerate(lines):
        low = line.lower()
        if any(k in low for k in ("cost", "best_value", "objective", "chi phi")) and ":" in line:
            val_part = line.split(":", 1)[1].split("|", 1)[0].strip()
            declared_cost = _parse_number(val_part)
        elif any(k in low for k in ("solution", "selected", "columns", "loi giai")) and ":" in line:
            rest = line.split(":", 1)[1].strip()
            if rest:
                camera_ids = [int(x) for x in rest.replace(",", " ").split()]
            elif idx + 1 < len(lines):
                camera_ids = [int(x) for x in lines[idx + 1].replace(",", " ").split()]

    if declared_cost is None or camera_ids is None:
        raise ValueError("Khong doc duoc chi phi hoac danh sach vi tri trong tep loi giai")
    return declared_cost, camera_ids


def main():
    if len(sys.argv) != 3:
        print("Cach dung: python kiemtra.py <file_du_lieu> <file_loi_giai>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    solution_path = Path(sys.argv[2])

    try:
        data = load_set_cover(input_path)
        lines = solution_path.read_text(encoding="utf-8").strip().splitlines()
        if not lines:
            raise ValueError("File loi giai rong")

        declared_cost, camera_ids = _parse_solution_file(lines)

        if len(set(camera_ids)) != len(camera_ids):
            raise ValueError("Danh sach vi tri duoc chon bi trung lap")

        selected = [x - 1 for x in camera_ids]
        valid, actual_cost, message = validate_solution(data, selected)

        if not valid:
            print("KHONG HOP LE:", message)
            print("Chi phi khai bao:", declared_cost)
            print("Chi phi tinh lai:", actual_cost)
            sys.exit(1)
        elif abs(declared_cost - actual_cost) > 1e-6:
            print("KHONG HOP LE: Chi phi khai bao khong khop")
            print("Chi phi khai bao:", declared_cost)
            print("Chi phi tinh lai:", actual_cost)
            sys.exit(1)
        else:
            print("HOP LE")
            print("Chi phi khai bao:", declared_cost)
            print("Chi phi tinh lai:", actual_cost)
            sys.exit(0)

    except (OSError, ValueError, IndexError) as e:
        print("KHONG HOP LE:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()