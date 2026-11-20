# Giải Bài Toán Set Cover (SCP) Ứng Dụng Bố Trí Camera Giao Thông Khu Vực UTH

Dự án nghiên cứu, cài đặt và đánh giá thực nghiệm các thuật toán tối ưu tổ hợp (Chính xác & Metaheuristics) cho bài toán **Set Cover Problem (SCP)** trên cả bộ dữ liệu chuẩn quốc tế OR-Library, dữ liệu sinh ngẫu nhiên và dữ liệu bản đồ giao thông thực tế khu vực Đại học Giao thông Vận tải TP.HCM (UTH).

---

## 1. Cấu Trúc Thư Mục Dự Án

```text
Set Cover_UTH/
├── algorithms/                  # Mã nguồn các thuật toán giải bài toán SCP
│   ├── simulated_annealing.py   # Thuật toán Luyện kim mô phỏng (SA)
│   ├── tabu_search.py           # Thuật toán Tìm kiếm Tabu (TS)
│   ├── genetic_algorithm.py     # Thuật toán Di truyền (GA)
│   └── exact_solver.py          # Thuật toán Nhánh cận (Branch & Bound) đối chứng f*
├── data/                        # Dữ liệu đầu vào theo chuẩn OR-Library
│   ├── sample/                  # Dữ liệu mẫu (vidu.txt)
│   ├── generated/               # Dữ liệu tự sinh kích thước nhỏ & vừa (sc_10_10 -> sc_30_30)
│   ├── osm/                     # Dữ liệu bản đồ giao thông thực tế UTH (uth_setcover.txt)
│   └── orlib/                   # Bộ dữ liệu chuẩn Beasley OR-Library (scp41 -> scp45)
├── results/                     # Kết quả thực nghiệm tự động xuất ra
│   ├── raw/                     # Kết quả thô từng lần chạy (10 seeds/thuật toán)
│   ├── conv/                    # Lịch sử hội tụ chi phí theo thời gian
│   ├── solutions/               # Nghiệm tối ưu tìm được (.sol)
│   ├── summary/                 # Bảng tổng hợp thống kê & độ nhạy tham số (.csv)
│   └── figures/                 # Biểu đồ đường hội tụ & biểu đồ độ nhạy (.png)
├── run_exact_benchmark.py       # Chạy thuật toán Nhánh cận tìm nghiệm chuẩn xác f*
├── run_experiments.py           # Chạy thực nghiệm tự động 11 bộ dữ liệu x 3 thuật toán x 10 seeds
├── plot_results.py              # Tổng hợp benchmark_summary.csv & vẽ biểu đồ hội tụ gộp
├── ts_sensitivity.py            # Phân tích độ nhạy tham số cho Tabu Search
├── ga_sensitivity.py            # Phân tích độ nhạy tham số cho Genetic Algorithm
├── kiemtra.py                   # Kiểm tra tính hợp lệ (feasibility) của toàn bộ nghiệm .sol
└── requirements.txt             # Danh sách thư viện Python cần thiết
```

---

## 2. Môi Trường Thực Nghiệm & Cài Đặt

* **Hệ điều hành:** Microsoft Windows 11 Home Single Language (64-bit)
* **Vi xử lý (CPU):** AMD Ryzen 5 6600H with Radeon Graphics[cite: 17]
* **Bộ nhớ (RAM):** 16 GB (15,677 MB khả dụng)
* **Ngôn ngữ lập trình:** Python 3.15.1
* **Thư viện cần cài đặt:**
  ```bash
  pip install matplotlib
  ```
  *(Hoặc cài đặt đầy đủ cho cả ứng dụng web trực quan hóa: `pip install -r requirements.txt`)*

---

## 3. Tham Số Mặc Định Các Thuật Toán

| Thuật toán | Tham số chính | Giá trị mặc định |
| :--- | :--- | :--- |
| **Simulated Annealing (SA)** | Hệ số làm nguội (`alpha`), Giới hạn thời gian (`time_limit`) | `alpha = 0.99`, `1.0s` ($n \le 50$) / `5.0s` ($n > 50$) |
| **Tabu Search (TS)** | Độ dài danh sách cấm (`tabu_tenure`), Số vòng lặp tối đa (`max_iter`) | `min(15, max(2, n // 3))`, `max_iter = 50000` |
| **Genetic Algorithm (GA)** | Kích thước quần thể (`pop_size`), Tỷ lệ đột biến (`mutation_rate`) | `pop_size = 50`, `mutation_rate = 0.05` |
| **Chung** | Bộ 10 hạt giống ngẫu nhiên (`seeds`) | `[42, 100, 2026, 7, 13, 21, 99, 123, 555, 888]` |

---

## 4. Hướng Dẫn Chạy Tái Lập Kết Quả (Reproducibility)

Thực hiện tuần tự các lệnh sau trong thư mục `Set Cover_UTH`:

1. **Chạy đối chứng nghiệm tối ưu chuẩn xác $f^*$ (Nhánh cận):**
   ```bash
   python run_exact_benchmark.py
   ```
2. **Chạy toàn bộ thực nghiệm chính (11 bộ dữ liệu $\times$ 3 thuật toán $\times$ 10 seeds):**
   ```bash
   python run_experiments.py
   ```
3. **Tổng hợp bảng thống kê (`Gap%`, `Optimal_Rate`, `Mean ± Std`) và vẽ biểu đồ hội tụ:**
   ```bash
   python plot_results.py
   ```
4. **Chạy khảo sát độ nhạy tham số cho TS và GA:**
   ```bash
   python ts_sensitivity.py
   python ga_sensitivity.py
   ```
5. **Kiểm tra độc lập tính hợp lệ của toàn bộ nghiệm đầu ra:**
   ```bash
   python kiemtra.py
   ```