# Hệ Thống Theo Dõi & Ước Tính Tốc Độ Phương Tiện (YOLOv8 + Homography)

Hệ thống theo dõi và ước tính tốc độ phương tiện giao thông thời gian thực sử dụng mô hình học sâu **YOLOv8** (Object Detection & Multi-Object Tracking) kết hợp thuật toán biến đổi hình học phối cảnh **Homography** (Perspective Transformation) để tính toán chính xác tốc độ (km/h) của từng loại xe từ camera giám sát hoặc video.

Dự án cung cấp hai phương thức chạy:
1. **Giao diện Web Streamlit hiện đại** (`src/app.py`): Thiết kế theo phong cách Dark Mode & Glassmorphism cao cấp, cập nhật thống kê, biểu đồ phân tích và danh sách vi phạm thời gian thực.
2. **Giao diện Dòng lệnh/OpenCV truyền thống** (`src/main.py`): Nhẹ nhàng, hỗ trợ cấu hình linh hoạt qua tham số dòng lệnh hoặc file YAML cho camera RTSP/Webcam.

---

## 🌟 Các Tính Năng Nổi Bật

- **Nhận Diện & Theo Dõi Đa Đối Tượng (MOT):** Sử dụng mô hình YOLOv8 (`best_.pt`) để nhận dạng các loại phương tiện (xe buýt, ô tô, xe máy, xe tải) và gán ID duy nhất (`obj_id`) ổn định trên các khung hình.
- **Ước Tính Tốc Độ Chính Xác Qua Homography:** Ánh xạ tọa độ pixel từ ảnh camera sang tọa độ mặt đường thực tế ($x_{real}, y_{real}$) dựa trên ma trận Homography, đo khoảng cách di chuyển thực tế trên mặt đường để tính vận tốc.
- **Bộ Lọc Làm Mượt Tốc Độ (EMA):** Sử dụng bộ lọc trung bình động lũy thừa (Exponential Moving Average) để loại bỏ nhiễu rung giật tốc độ do bounding box dao động.
- **Xử lý Đa Luồng Đọc Camera (Threaded VideoStream):** Sử dụng luồng đọc camera chạy nền chuyên biệt giúp khắc phục hoàn toàn hiện tượng nghẽn bộ đệm OpenCV và giật hình khi chạy camera trực tiếp hoặc RTSP.
- **Cảnh Báo Vượt Tốc Độ:** Tự động phát hiện phương tiện vượt quá giới hạn tốc độ cấu hình (`speed_limit`), chuyển màu Bounding Box sang màu đỏ và ghi nhận vào danh sách vi phạm.
- **Báo Cáo & Thống Kê Chi Tiết:**
  - Xuất báo cáo lịch sử tốc độ và lịch sử vi phạm ra file CSV trực tiếp từ UI.
  - Vẽ biểu đồ phân tích phương tiện giao thông và phân bố tốc độ tối đa của từng ID xe.
  - Hỗ trợ lưu lại video kết quả đã xử lý để tải xuống.

---

## 📂 Cấu Trúc Thư Mục Dự Án

Dự án được tái cấu trúc thành các module rõ ràng và dễ quản lý:

```text
Vehicle-Tracking-Speed-Estimation-Yolov8/
├── datasets/
│   └── KQAE7521.MP4           # Video thử nghiệm mặc định
├── src/
│   ├── app.py                 # File chính chạy giao diện Web (Streamlit UI)
│   ├── main.py                # File chính chạy giao diện OpenCV (CLI)
│   ├── core/                  # Module logic thuật toán lõi
│   │   ├── __init__.py
│   │   └── speed_estimator.py # Lớp tính toán tốc độ bằng thuật toán Homography
│   ├── ui/                    # Module giao diện Web Streamlit
│   │   ├── dashboard.py       # Hiển thị số liệu, bảng biểu, lịch sử vi phạm
│   │   ├── sidebar.py         # Form cấu hình các tham số đầu vào và bộ lọc
│   │   └── styles.py          # Custom CSS phong cách Dark Mode & Glassmorphism
│   └── utils/                 # Module tiện ích hỗ trợ
│       ├── __init__.py
│       ├── drawing_utils.py   # Vẽ thông tin chữ tiếng Việt (tránh lỗi font OpenCV)
│       └── video_stream.py    # Quản lý luồng đọc camera đa luồng chống nghẽn
├── best_.pt                   # Bộ trọng số mô hình YOLOv8 đã huấn luyện
├── data.yaml                  # Cấu hình nhãn lớp phương tiện giao thông
├── cameras_config.yaml        # Danh sách cấu hình camera và tọa độ ROI mẫu
├── .gitignore                 # Cấu hình bỏ qua tệp tin rác khi commit git
└── README.md                  # Hướng dẫn sử dụng dự án (File này)
```

---

## ⚙️ Cài Đặt Môi Trường

Hệ thống khuyến nghị sử dụng **Python 3.9 - 3.11**.

### 1. Khởi tạo môi trường ảo
```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo
# Trên Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Trên Windows (CMD):
.\venv\Scripts\activate.bat
```

### 2. Cài đặt các thư viện cần thiết
```bash
pip install opencv-python numpy ultralytics pyyaml streamlit pandas
```

---

## 🚀 Hướng Dẫn Chạy Chương Trình

### 1. Giao Diện Web Streamlit (Khuyên Dùng)

Cung cấp giao diện trực quan đầy đủ tính năng cấu hình động, hiển thị thời gian thực và xuất báo cáo.

```bash
streamlit run src/app.py
```
- **Cách sử dụng:**
  1. Truy cập đường dẫn hiển thị trên Terminal (ví dụ: `http://localhost:8501`).
  2. Chọn nguồn đầu vào từ Sidebar:
     - **Tải lên Video:** Chọn tệp video `.mp4` từ máy của bạn.
     - **Nhập RTSP URL:** Nhập link luồng stream camera mạng (ví dụ: `rtsp://username:password@ip:port/h264`).
     - **Webcam ID:** Nhập ID webcam tích hợp hoặc cắm ngoài (mặc định là `0`).
     - **Cấu hình có sẵn:** Chọn camera cấu hình sẵn trực tiếp từ danh sách nếu phát hiện tệp `cameras_config.yaml`.
  3. Hiệu chỉnh vùng đo (ROI), giới hạn tốc độ và các tham số lọc ở Sidebar. Nhấn **👁 Xem trước Vùng đo** để kiểm tra vị trí ROI.
  4. Nhấn **▶ Bắt đầu** để chạy xử lý. Nhấn **⏹ Dừng** bất kỳ lúc nào để dừng lại và tải về báo cáo CSV hoặc video kết quả.

### 2. Giao Diện Dòng Lệnh CLI / OpenCV

Phù hợp cho việc chạy tự động, lưu trực tiếp video ra file hoặc kiểm tra nhanh thuật toán qua màn hình OpenCV.

```bash
# Chạy mặc định với camera 0 (Webcam)
python src/main.py

# Chạy với nguồn video cụ thể và cấu hình vùng ROI tùy chỉnh
python src/main.py --source datasets/KQAE7521.MP4 --speed_limit 50 --save True

# Chạy với cấu hình camera định nghĩa sẵn từ file YAML
python src/main.py --config cameras_config.yaml --camera cam_1
```

**Các tham số dòng lệnh hỗ trợ (`python src/main.py -h`):**

| Tham số | Rút gọn | Kiểu dữ liệu | Mặc định | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `--config` | `-c` | `str` | `None` | Đường dẫn tới tệp cấu hình camera YAML. |
| `--camera` | `-cam` | `str` | `None` | Tên camera cụ thể trong tệp cấu hình để áp dụng nhanh. |
| `--source` | `-src` | `str/int` | `0` | Chỉ số webcam (0, 1) hoặc đường dẫn file video / link RTSP. |
| `--model` | `-m` | `str` | `best_.pt` | Đường dẫn tới tệp trọng số YOLOv8. |
| `--yaml` | `-y` | `str` | `data.yaml` | Tệp cấu hình nhãn lớp của dataset. |
| `--speed_limit` | `-sl` | `float` | `25.0` | Giới hạn tốc độ cho phép (km/h) trên làn đường này. |
| `--real_width` | `-rw` | `float` | `4.5` | Chiều rộng thực tế của đường trong vùng ROI (mét). |
| `--real_length`| `-rl` | `float` | `18.0` | Chiều dài thực tế của đoạn đường trong vùng ROI (mét). |
| `--cleanup_time`| `-ct` | `float` | `2.0` | Thời gian (giây) để xóa ID xe khỏi bộ nhớ sau khi biến mất. |
| `--save` | `-s` | `bool` | `True` | Lưu video kết quả đầu ra thành file. |
| `--output` | `-o` | `str` | `output_speed.mp4` | Đường dẫn lưu tệp video kết quả đầu ra. |

---

## 📊 Phương Pháp Ước Tính Tốc Độ (Homography)

Hệ thống ước tính tốc độ dựa trên việc chuyển đổi không gian 2D từ hình ảnh phối cảnh của camera sang mặt đường thế giới thực phẳng:

1. **Thiết lập vùng đo (ROI):** Xác định đa giác gồm 4 điểm ảnh phối cảnh `SRC_PTS` trên mặt đường tương ứng với chiều rộng làn đường thật `REAL_WIDTH` ($W$) và chiều dài đoạn đường thực tế `REAL_LENGTH` ($L$).
2. **Biến đổi phối cảnh (Homography):** Tính toán ma trận biến đổi phối cảnh $H$ kích thước $3 \times 3$ ánh xạ điểm pixel $(x_{pixel}, y_{pixel})$ về tọa độ thực tế $(x_{real}, y_{real})$:
   $$\begin{bmatrix} x_{real} \\ y_{real} \\ 1 \end{bmatrix} \sim H \begin{bmatrix} x_{pixel} \\ y_{pixel} \\ 1 \end{bmatrix}$$
3. **Tính vận tốc di chuyển:** Điểm neo của xe được chọn là trung điểm cạnh dưới của hộp giới hạn $P = (x_{center}, y_{bottom})$ đại diện cho điểm tiếp đất của bánh xe. Vận tốc tức thời được tính qua khoảng cách di chuyển thực tế trên giây:
   $$v_{current} = \left(\frac{\Delta d}{\Delta t}\right) \times 3.6 \quad (\text{km/h})$$
4. **Bộ lọc làm mượt tốc độ:** Để triệt tiêu sai số dao động bounding box giữa các frame, chúng tôi dùng bộ lọc Exponential Moving Average (EMA):
   $$v_{smooth} = \alpha \times v_{prev} + (1 - \alpha) \times v_{current} \quad (\text{với } \alpha = 0.7)$$
