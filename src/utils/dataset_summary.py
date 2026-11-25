
import csv
from pathlib import Path
from data_loader import load_set_cover


def create_summary():
    # Thu muc chua du lieu
    folders = [
        Path("data/chuan"),
        Path("data/tusinh")
    ]

    results = []

    for folder in folders:
        for path in sorted(folder.glob("*.txt")):
            data = load_set_cover(path)

            m = data["m"]
            n = data["n"]

            # Tong so quan he phu
            relations = sum(
                len(row) for row in data["rows"]
            )

            # Ty le phan tu bang 1
            density = relations / (m * n) * 100

            # Thong ke chi phi
            total_cost = sum(data["costs"])
            min_cost = min(data["costs"])
            max_cost = max(data["costs"])

            results.append({
                "Dataset": path.name,
                "Source": folder.name,
                "Rows": m,
                "Columns": n,
                "Coverage_Relations": relations,
                "Density_Percent": round(density, 2),
                "Min_Cost": min_cost,
                "Max_Cost": max_cost,
                "Total_Cost": total_cost
            })

    # Tao thu muc ket qua
    output_folder = Path("results")
    output_folder.mkdir(exist_ok=True)

    output_path = output_folder / "dataset_summary.csv"

    with open(
        output_path, "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    print("Da tao file:", output_path)
    print("Tong so bo du lieu:", len(results))


if __name__ == "__main__":
    create_summary()
