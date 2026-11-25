# BỐ TRÍ CAMERA GIÁM SÁT GIAO THÔNG KHU VỰC UTH BẰNG BÀI TOÁN SET COVER

**Bài tập lớn – Đề tài 10: Bài toán NP-khó và Metaheuristic**  
**Giảng viên hướng dẫn:** Nguyễn Văn Huy

## 1. Giới thiệu đề tài

Dự án giải quyết bài toán lựa chọn vị trí lắp đặt camera giám sát giao thông tại khu vực Trường Đại học Giao thông vận tải Thành phố Hồ Chí Minh (UTH). Các nút giao hoặc đoạn đường cần quan sát được mô hình hóa thành những phần tử cần bao phủ; mỗi vị trí lắp camera ứng viên có phạm vi quan sát và chi phí tương ứng.

Bài toán được biểu diễn dưới dạng **Weighted Set Cover (bài toán phủ tập có trọng số)**, với mục tiêu tìm tập camera có **tổng chi phí nhỏ nhất có thể** và vẫn **bao phủ 100% các vị trí cần giám sát**. Dự án triển khai các thuật toán giải, thực hiện thực nghiệm trên nhiều bộ dữ liệu và xây dựng giao diện Web để minh họa kết quả trên bản đồ.

## 2. Thành viên và phân công công việc

| STT | Họ và tên | MSSV | Nội dung công việc | Mức độ tham gia |
|:---:|---|:---:|---|:---:|
| 1 | **Nguyễn Minh Khang** | 087205008666 | Xây dựng mô hình toán học Weighted Set Cover; triển khai Greedy, Branch and Bound và **Tabu Search (TS)**; thực nghiệm và khảo sát độ nhạy TS; xây dựng hệ thống chạy thực nghiệm; phụ trách **Backend**, kết nối thuật toán với giao diện Web. | **100%** |
| 2 | **Trần Thùy Linh** | 075305003441 | Triển khai **Simulated Annealing (SA)**; chạy thực nghiệm, khảo sát độ nhạy tham số và xây dựng biểu đồ hội tụ SA; thu thập, xử lý dữ liệu **OpenStreetMap (OSM)** khu vực UTH; xây dựng dữ liệu nút giao, vị trí camera ứng viên, ma trận bao phủ và **trực quan hóa bản đồ giao thông**. | **100%** |
| 3 | **Nông Đức Huy** | 070206002093 | Triển khai **Genetic Algorithm (GA)**; chạy thực nghiệm, khảo sát độ nhạy và xây dựng biểu đồ GA; phụ trách **Frontend**, hiển thị thông tin camera và kết quả giải, xây dựng chức năng so sánh thuật toán trên Web; hỗ trợ kiểm thử và đánh giá kết quả. | **100%** |

**Công việc chung:** Các thành viên phối hợp kiểm tra tính hợp lệ của nghiệm, phân tích kết quả, hoàn thiện báo cáo và chuẩn bị thuyết trình.

## 3. Các thuật toán được triển khai

| Thuật toán | Mục đích |
|---|---|
| **Greedy (tham lam)** | Tạo nghiệm ban đầu nhanh; dùng làm phương án tham chiếu. |
| **Branch and Bound (B&B)** | Tìm nghiệm tối ưu đối với các trường hợp có quy mô phù hợp. |
| **First Improvement** | Cải thiện nghiệm bằng cách nhận phương án tốt hơn đầu tiên tìm được. |
| **Best Improvement** | Tìm phương án cải thiện tốt nhất trong lân cận được xét. |
| **Simulated Annealing (SA)** | Khám phá không gian nghiệm bằng cơ chế chấp nhận có kiểm soát những bước đi kém hơn. |
| **Genetic Algorithm (GA)** | Tìm kiếm nghiệm dựa trên quần thể và các phép toán di truyền. |
| **Tabu Search (TS)** | Sử dụng bộ nhớ Tabu để hạn chế lặp lại và mở rộng tìm kiếm. |

**SA, GA và TS** là ba thuật toán Metaheuristic chính được thực nghiệm và so sánh. Giao diện Web hỗ trợ sáu phương pháp: Greedy, First Improvement, Best Improvement, SA, GA và TS; B&B được kiểm tra bằng chương trình riêng.

## 4. Cấu trúc thư mục

```text
UTH-Traffic-Set-Cover/
├── README.md
├── requirements.txt
├── src/
│   ├── algorithms/           # Các thuật toán
│   ├── utils/                # Đọc dữ liệu, mô hình, kiểm tra nghiệm
│   ├── templates/            # Giao diện HTML
│   ├── main.py               # Kiểm tra B&B trên bài toán mẫu
│   ├── web_app.py            # Ứng dụng Web
│   ├── run_experiments.py    # Chạy thực nghiệm
│   ├── plot_results.py       # Tổng hợp và vẽ biểu đồ
│   ├── plot_sa_convergence.py
│   └── sa_sensitivity_uth.py
├── data/
│   ├── vidu/                 # Bộ dữ liệu ví dụ
│   ├── chuan/                # Bộ dữ liệu chuẩn OR-Library
│   ├── tusinh/               # Bộ dữ liệu tự sinh
│   ├── osm/                  # Dữ liệu đường giao thông OSM
│   └── nodes/                # Nút giao và mô hình camera UTH
├── results/
│   ├── raw/                  # Kết quả thực nghiệm thô
│   ├── conv/                 # Dữ liệu hội tụ CSV
│   ├── solutions/            # Nghiệm .sol
│   ├── figures/              # Biểu đồ PNG
│   └── summary/              # Bảng thống kê tổng hợp
└── report/                   # Báo cáo và slide
```

Các tệp mã nguồn bổ sung phục vụ xử lý OSM, thực nghiệm và phân tích tham số cũng được đặt trong `src/`.

## 5. Cài đặt và hướng dẫn chạy

**Yêu cầu:** Python và các thư viện trong `requirements.txt`.

Mở Terminal tại **thư mục gốc của repository**, sau đó cài đặt thư viện:

```bash
python -m pip install -r requirements.txt
```

### 5.1. Kiểm tra bài toán mẫu và Branch and Bound

```bash
python src/main.py
```

Chương trình in tập camera được chọn, chi phí, tỷ lệ bao phủ, thời gian và kết quả kiểm tra tính hợp lệ. Trong bài toán mẫu đã kiểm thử, B&B tìm được tập camera `[1, 2, 4]`, chi phí **16**, độ phủ **100%**.

### 5.2. Tổng hợp kết quả thực nghiệm và vẽ biểu đồ

```bash
python src/plot_results.py
```

Bảng tổng hợp được ghi vào `results/summary/benchmark_summary.csv`, các biểu đồ hội tụ được xuất vào `results/figures/`.

### 5.3. Biểu đồ hội tụ SA trên dữ liệu nút giao UTH

```bash
python src/plot_sa_convergence.py
```

Kết quả được lưu tại:

- `results/conv/sa_convergence_uth.csv`
- `results/figures/sa_convergence_uth.png`

### 5.4. Chạy giao diện Web

```bash
python src/web_app.py
```

Truy cập **http://127.0.0.1:5000** bằng trình duyệt. Giao diện cho phép chạy từng thuật toán, hiển thị kết quả lựa chọn camera và so sánh các phương pháp trên mô hình UTH.

> **Lưu ý:** Những chương trình chạy thực nghiệm hàng loạt hoặc khảo sát tham số có thể tạo lại/ghi đè các tệp trong `results/`. Nên sao lưu kết quả hiện có trước khi chạy lại toàn bộ thí nghiệm.

## 6. Dữ liệu và phương pháp đánh giá

Dự án sử dụng các nhóm dữ liệu:

- **Ví dụ (`data/vidu/`)**: Kiểm tra cách đọc dữ liệu, thuật toán và tính hợp lệ của nghiệm.
- **Chuẩn (`data/chuan/`)**: Các bộ `scp41`–`scp45` từ OR-Library.
- **Tự sinh (`data/tusinh/`)**: Các trường hợp có quy mô khác nhau để khảo sát hiệu quả giải.
- **UTH (`data/osm/`, `data/nodes/`)**: Dữ liệu mô phỏng mạng lưới giao thông, nút giao, vị trí camera và quan hệ bao phủ lấy từ quá trình xử lý OSM.

Bộ kết quả thực nghiệm hiện có ghi nhận **330 lượt chạy** của **SA, GA và TS** trên **11 bộ dữ liệu**, với **10 seed** cho mỗi cặp thuật toán – bộ dữ liệu. Các tiêu chí đánh giá bao gồm chi phí nghiệm, tính hợp lệ và tỷ lệ bao phủ, thời gian thực thi, đặc điểm hội tụ và độ nhạy tham số.

## 7. Kết quả minh họa

Trên bộ dữ liệu mô hình **104 nút giao, 64 camera ứng viên** được dùng trong giao diện Web, một lần kiểm thử cho kết quả:

| Phương pháp | Số camera | Tổng chi phí | Độ phủ |
|---|---:|---:|---:|
| Greedy | 17 | 87 | 100% |
| First Improvement | 16 | 86 | 100% |
| Best Improvement | 16 | 86 | 100% |
| SA | 14 | 80 | 100% |
| GA | 14 | 80 | 100% |
| TS | 16 | 82 | 100% |

Đây là **kết quả của một lần kiểm thử**, không phải cam kết rằng thuật toán luôn cho cùng kết quả hoặc chứng minh chi phí 80 là tối ưu toàn cục. Các thống kê đầy đủ và hình ảnh được lưu trong thư mục `results/`.

## 8. Kết luận

Dự án kết hợp mô hình Weighted Set Cover, các thuật toán giải chính xác và gần đúng, dữ liệu giao thông UTH, hệ thống thực nghiệm và giao diện trực quan. Kết quả giúp đánh giá sự khác biệt giữa các phương pháp lựa chọn camera theo chi phí, tỷ lệ bao phủ và hiệu quả tính toán, đồng thời cung cấp nền tảng để mở rộng bài toán sang các điều kiện triển khai thực tế.
