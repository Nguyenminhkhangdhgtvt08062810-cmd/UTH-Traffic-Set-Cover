
def load_set_cover(path):
    with open(path, "r", encoding="utf-8") as f:
        numbers = list(map(int, f.read().split()))

    # So doi tuong can phu va so camera
    m, n = numbers[0], numbers[1]

    # Chi phi cua tung camera
    costs = numbers[2:2 + n]

    pos = 2 + n
    rows = []

    # Doc danh sach camera phu tung doi tuong
    for i in range(m):
        k = numbers[pos]
        pos += 1

        cameras = [
            x - 1 for x in numbers[pos:pos + k]
        ]

        rows.append(cameras)
        pos += k

    # Tao danh sach doi tuong ma moi camera phu
    columns = [[] for _ in range(n)]

    for row_id, cameras in enumerate(rows):
        for camera in cameras:
            columns[camera].append(row_id)

    return {
        "m": m,
        "n": n,
        "costs": costs,
        "rows": rows,
        "columns": columns
    }
