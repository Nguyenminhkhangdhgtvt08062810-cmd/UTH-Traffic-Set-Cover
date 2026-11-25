# Giải Bài Toán Set Cover (SCP) Ứng Dụng Bố Trí Camera Giám Sát Giao Thông Khu Vực UTH

## 1. Thông Tin Nhóm & Phân Công Công Việc
* **Môn học:** Phân tích Thiết kế Giải thuật — Đề bài tập lớn: Bài toán NP-khó và Metaheuristic
* **Giảng viên hướng dẫn:** Nguyễn Văn Huy
* **Danh sách thành viên & phân công tóm tắt:**

| STT | Họ và tên | MSSV | Vai trò & Nhiệm vụ chính | Tỷ lệ đóng góp |
| :---: | :--- | :---: | :--- | :---: |
| 1 | **Nguyễn Minh Khang** | 087205008666 | Thiết kế mô hình toán học, cài đặt thuật toán chính xác (B&B), SA, hệ thống chạy thực nghiệm tự động, trực quan hóa web & tổng hợp báo cáo | 34% |
| 2 | **Trần Thùy Linh** | 075305003441 | Cài đặt thuật toán Tabu Search (TS), khảo sát độ nhạy tham số TS, kiểm thử tính hợp lệ nghiệm (`kiemtra.py`) & biên soạn tài liệu | 33% |
| 3 | **Nông Đức Huy** | 070206002093 | Cài đặt thuật toán Genetic Algorithm (GA), tiền xử lý dữ liệu bản đồ thực tế UTH từ OpenStreetMap, khảo sát độ nhạy GA & vẽ biểu đồ | 33% |

---

## 2. Cấu Trúc Thư Mục Dự Án

```text
UTH-Traffic-Set-Cover/
├── README.md                        # Hướng dẫn cài đặt, chạy và tái lập kết quả
├── Set Cover_UTH/
│   ├── algorithms/                  # Mã nguồn các thuật toán (EXACT, GREEDY, SA, TS, GA)
│   │   ├── branch_and_bound.py      # Thuật toán Nhánh cận (EXACT)
│   │   ├── greedy.py                # Giải thuật Tham lam & khử dư thừa (GREEDY)
│   │   ├── simulated_annealing.py   # Thuật toán Luyện kim mô phỏng (SA)
│   │   ├── tabu_search.py           # Thuật toán Tìm kiếm Tabu (TS)
│   │   └── genetic_algorithm.py     # Thuật toán Di truyền (GA)
│   ├── data/                        # Dữ liệu đầu vào theo chuẩn OR-Library
│   │   ├── sample/                  # Ví dụ nhỏ trong đề (vidu.txt)
│   │   ├── generated/               # Dữ liệu tự sinh (sc_10_10 -> sc_30_30)
│   │   ├── osm/                     # Dữ liệu giao thông thực tế khu vực UTH (uth_setcover.txt)
│   │   └── orlib/                   # Bộ dữ liệu chuẩn OR-Library (scp41 -> scp45)
│   ├── results/                     # Kết quả thực nghiệm xuất ra tự động
│   │   ├── raw/                     # Tệp CSV kết quả từng lần chạy
│   │   ├── conv/                    # Log hội tụ (<instance>_<alg>_seed<seed>_conv.csv)
│   │   ├── solutions/               # Tệp lời giải tốt nhất (.sol)
│   │   ├── summary/                 # Bảng tổng hợp thống kê & độ nhạy tham số
│   │   └── figures/                 # Biểu đồ hội tụ và biểu đồ độ nhạy (.png)
│   ├── main.py                      # Chạy đơn lẻ 1 thuật toán trên 1 thể hiện qua dòng lệnh
│   ├── kiemtra.py                   # Chương trình kiểm tra tính hợp lệ lời giải
│   ├── run_exact_benchmark.py       # Chạy đối chứng nghiệm chuẩn xác f*
│   ├── run_experiments.py           # Chạy toàn bộ 330 lượt thực nghiệm chính
│   ├── plot_results.py              # Tổng hợp bảng thống kê & vẽ biểu đồ hội tụ
│   ├── ts_sensitivity.py            # Khảo sát độ nhạy tham số Tabu Search
│   ├── ga_sensitivity.py            # Khảo sát độ nhạy tham số Genetic Algorithm
│   ├── web_app.py                   # Giao diện web trực quan hóa quá trình tìm kiếm (Điểm cộng)
│   └── requirements.txt             # Danh sách thư viện phụ thuộc
```

---

## 3. Môi Trường Thực Nghiệm & Cài Đặt

* **Hệ điều hành:** Microsoft Windows 11 Home Single Language (64-bit)
* **Phần cứng:** CPU AMD Ryzen 5 6600H with Radeon Graphics, RAM 16 GB (15,677 MB khả dụng)
* **Ngôn ngữ & Trình thông dịch:** Python 3.15.1
* **Thư viện phụ thuộc (`requirements.txt`):**
  * `matplotlib >= 3.8.0` (vẽ biểu đồ hội tụ và phân tích độ nhạy)
  * `flask >= 3.0.0` (tùy chọn, dùng cho giao diện trực quan hóa `web_app.py`)
* **Lệnh cài đặt môi trường:**
  ```bash
  cd "Set Cover_UTH"
  pip install -r requirements.txt
  ```

---

## 4. Hướng Dẫn Chạy Đơn Lẻ & Kiểm Tra Lời Giải

### 4.1. Chạy một thuật toán trên một thể hiện
Cú pháp dòng lệnh chuẩn trong thư mục `Set Cover_UTH`:
```bash
python main.py --instance <duong_dan_tep_vao> --alg <SA|TS|GA|EXACT|GREEDY> --seed <so_nguyen> --time_limit <giay> --out <tep_loi_giai_ra>
```
**Ví dụ cụ thể chạy được ngay** (giải dữ liệu thực tế giao thông UTH bằng thuật toán Simulated Annealing với `seed=42`, ngân sách thời gian `3.0s`):
```bash
python main.py --instance data/osm/uth_setcover.txt --alg SA --seed 42 --time_limit 3.0 --out results/solutions/uth_setcover_SA_s42.sol
```

### 4.2. Chạy chương trình kiểm tra lời giải (`kiemtra`)
Cú pháp kiểm tra tính hợp lệ (ràng buộc bao phủ toàn bộ phần tử $U$ và đối chiếu tổng chi phí):
```bash
python kiemtra.py <tep_vao> <tep_loi_giai>
```
**Ví dụ cụ thể chạy được ngay:**
```bash
python kiemtra.py data/osm/uth_setcover.txt results/solutions/uth_setcover_SA_s42.sol
```

---

## 5. Hướng Dẫn Chạy Toàn Bộ Thực Nghiệm & Tái Lập Kết Quả

* **Danh sách 10 hạt giống ngẫu nhiên (seeds) cố định:** `[42, 100, 2026, 7, 13, 21, 99, 123, 555, 888]`
* **Tổng thời gian chạy ước tính cho toàn bộ bộ thực nghiệm:** Khoảng **12 – 15 phút** trên CPU AMD Ryzen 5 6600H.

Thực hiện tuần tự các lệnh sau trong thư mục `Set Cover_UTH`:
1. **Chạy đối chứng nghiệm tối ưu chính xác $f^*$ (Branch & Bound):** *(~15 giây)*
   ```bash
   python run_exact_benchmark.py
   ```
2. **Chạy toàn bộ thực nghiệm chính (11 thể hiện $\times$ 3 thuật toán $\times$ 10 seeds = 330 lượt chạy):** *(~10 phút)*
   ```bash
   python run_experiments.py
   ```
3. **Tổng hợp bảng số liệu thống kê (`Gap_b%`, `Gap_a%`, `Mean ± Std`) và sinh 11 biểu đồ hội tụ:** *(~10 giây)*
   ```bash
   python plot_results.py
   ```
4. **Chạy khảo sát độ nhạy tham số cho TS và GA (sinh 8 biểu đồ độ nhạy):** *(~3 phút)*
   ```bash
   python ts_sensitivity.py
   python ga_sensitivity.py
   ```

---

## 6. Tham Số Mặc Định Các Thuật Toán (Trùng Khớp Báo Cáo)

| Thuật toán | Ký hiệu | Tham số chính | Giá trị mặc định |
| :--- | :---: | :--- | :--- |
| **Branch & Bound** | `EXACT` | Chiến lược phân nhánh & cắt tỉa | Cận dưới tham lam phân số, giới hạn thời gian `60s` |
| **Greedy + Prune** | `GREEDY` | Tiêu chí chọn cột & hậu xử lý | $\min \frac{c_j}{|S_j \cap U_{\text{rem}}|}$ kết hợp khử cột dư thừa |
| **Simulated Annealing** | `SA` | Nhiệt độ đầu $T_0$, hệ số nguội $\alpha$, ngân sách | $T_0$ tự động theo $\Delta_{\text{avg}}$, $\alpha = 0.99$, `1.0s` ($n \le 50$) / `5.0s` ($n > 50$) |
| **Tabu Search** | `TS` | Độ dài danh sách cấm (`tabu_tenure`), vòng lặp tối đa | $\min(15, \max(2, \lfloor n/3 \rfloor))$, `max_iter = 50000` |
| **Genetic Algorithm** | `GA` | Kích thước quần thể (`pop_size`), tỷ lệ đột biến $p_m$ | `pop_size = 50`, `mutation_rate = 0.05`, Tournament $k=3$ |