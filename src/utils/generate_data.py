
import random
from pathlib import Path


def generate_instance(m, n, seed):
    rng = random.Random(seed)

    # Tao chi phi cho tung camera
    costs = [
        rng.randint(1, 20)
        for _ in range(n)
    ]

    # Tao danh sach camera phu tung doi tuong
    rows = []

    for i in range(m):
        # Moi doi tuong duoc 1 den 5 camera phu
        k = rng.randint(1, min(5, n))

        cameras = sorted(
            rng.sample(range(1, n + 1), k)
        )

        rows.append(cameras)

    return costs, rows


def save_instance(path, m, n, costs, rows):
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{m} {n}\n")
        f.write(" ".join(map(str, costs)) + "\n")

        for cameras in rows:
            f.write(
                str(len(cameras)) + " "
                + " ".join(map(str, cameras))
                + "\n"
            )


if __name__ == "__main__":
    folder = Path("data/tusinh")
    folder.mkdir(parents=True, exist_ok=True)

    # 3 muc kich thuoc
    sizes = [
        (10, 10),
        (20, 20),
        (30, 30)
    ]

    # Moi muc tao 3 bo du lieu
    seeds = [101, 102, 103]

    for m, n in sizes:
        for seed in seeds:
            costs, rows = generate_instance(
                m, n, seed
            )

            filename = f"sc_{m}_{n}_s{seed}.txt"
            path = folder / filename

            save_instance(
                path, m, n, costs, rows
            )

            print("Da tao:", path)
