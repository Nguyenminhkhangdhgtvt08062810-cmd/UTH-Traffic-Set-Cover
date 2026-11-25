
def validate_solution(data, selected):
    # Kiem tra camera trung lap
    if len(selected) != len(set(selected)):
        return False, 0, "Camera bi trung lap"

    # Kiem tra chi so camera
    for camera in selected:
        if camera < 0 or camera >= data["n"]:
            return False, 0, "Camera khong hop le"

    # Tinh cac doi tuong duoc phu
    covered = set()

    for camera in selected:
        covered.update(data["columns"][camera])

    # Tinh tong chi phi
    total_cost = sum(
        data["costs"][camera]
        for camera in selected
    )

    # Kiem tra phu day du
    if len(covered) != data["m"]:
        return False, total_cost, "Chua phu het doi tuong"

    return True, total_cost, "HOP LE"
