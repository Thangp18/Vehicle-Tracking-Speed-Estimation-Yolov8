<![CDATA[<div align="center">

# 🚗 Vehicle Tracking & Speed Estimation System

### YOLOv8 · Homography · Real-time Analytics

[![Python](https://img.shields.io/badge/Python-3.9%20|%203.10%20|%203.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![YOLOv8](https://img.shields.io/badge/Model-YOLOv8-00FFFF?logo=ultralytics&logoColor=white)](https://docs.ultralytics.com)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org)
[![License](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)

**Hệ thống theo dõi và ước tính tốc độ phương tiện giao thông thời gian thực** sử dụng mô hình học sâu YOLOv8 kết hợp thuật toán biến đổi phối cảnh Homography để tính toán chính xác tốc độ (km/h) của từng phương tiện từ camera giám sát hoặc video.

[Tính năng](#-tính-năng-nổi-bật) · [Cài đặt](#️-cài-đặt) · [Hướng dẫn sử dụng](#-hướng-dẫn-sử-dụng) · [Kiến trúc](#️-kiến-trúc-hệ-thống) · [Thuật toán](#-thuật-toán-ước-tính-tốc-độ)

</div>

---

## ✨ Tính Năng Nổi Bật

| Tính năng | Mô tả |
|:---|:---|
| 🎯 **Nhận diện & Theo dõi đa đối tượng** | YOLOv8 nhận dạng 4 loại xe (xe buýt, ô tô, xe máy, xe tải) với ID tracking ổn định qua các khung hình |
| 📐 **Ước tính tốc độ qua Homography** | Ánh xạ pixel → tọa độ mặt đường thực tế, đo khoảng cách di chuyển để tính vận tốc chính xác |
| 📊 **Bộ lọc EMA làm mượt tốc độ** | Exponential Moving Average triệt tiêu nhiễu dao động bounding box giữa các frame |
| 🧵 **Đa luồng đọc camera** | Luồng đọc nền chuyên biệt chống nghẽn bộ đệm OpenCV khi stream RTSP / webcam |
| 🚨 **Cảnh báo vượt tốc** | Tự động phát hiện vi phạm, đổi màu bounding box đỏ, ghi nhận danh sách vi phạm |
| 📥 **Xuất báo cáo CSV** | Lịch sử tốc độ & vi phạm xuất file CSV trực tiếp từ giao diện |
| 📹 **Lưu video kết quả** | Ghi lại video đã xử lý để tải xuống hoặc xem lại |

### Hai phương thức vận hành

- **🌐 Giao diện Web Streamlit** — Dark Mode & Glassmorphism, thống kê thời gian thực, biểu đồ phân tích, xuất báo cáo
- **⌨️ Giao diện CLI / OpenCV** — Nhẹ nhàng, cấu hình linh hoạt qua tham số dòng lệnh hoặc file YAML

---

## 🏗️ Kiến Trúc Hệ Thống

```
Vehicle-Tracking-Speed-Estimation-Yolov8/
│
├── src/                            # Mã nguồn chính
│   ├── app.py                      # Entry point — Giao diện Web (Streamlit)
│   ├── main.py                     # Entry point — Giao diện CLI (OpenCV)
│   │
│   ├── core/                       # ⚙️ Logic thuật toán lõi
│   │   └── speed_estimator.py      # SpeedEstimator — Homography + EMA filter
│   │
│   ├── ui/                         # 🎨 Giao diện Streamlit
│   │   ├── dashboard.py            # Metrics, bảng biểu, biểu đồ, lịch sử vi phạm
│   │   ├── sidebar.py              # Form cấu hình nguồn, ROI, tham số đầu vào
│   │   └── styles.py               # Custom CSS — Dark Mode & Glassmorphism
│   │
│   └── utils/                      # 🔧 Tiện ích
│       ├── drawing_utils.py        # Vẽ text an toàn tránh khuất mép
│       └── video_stream.py         # VideoStream — Đa luồng đọc camera
│
├── get_roi_coordinates.py          # 🖱️ Công cụ chọn 4 điểm ROI bằng chuột
├── best_.pt                        # 🧠 Trọng số YOLOv8 đã huấn luyện
├── data.yaml                       # 📋 Nhãn lớp phương tiện (4 classes)
├── cameras_config.yaml             # 📷 Cấu hình đa camera & tọa độ ROI
├── datasets/                       # 🎬 Video thử nghiệm mẫu
└── README.md
```

---

## ⚙️ Cài Đặt

### Yêu cầu hệ thống

- **Python** 3.9 — 3.11
- **GPU** (khuyến nghị): NVIDIA GPU + CUDA để tăng tốc inference YOLOv8

### 1. Clone repository

```bash
git clone https://github.com/Thangp18/Vehicle-Tracking-Speed-Estimation-Yolov8.git
cd Vehicle-Tracking-Speed-Estimation-Yolov8
```

### 2. Tạo môi trường ảo

```bash
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (CMD)
.\venv\Scripts\activate.bat

# Linux / macOS
source venv/bin/activate
```

### 3. Cài đặt thư viện

```bash
pip install opencv-python numpy ultralytics pyyaml streamlit pandas
```

> [!TIP]
> Nếu muốn sử dụng GPU, cài đặt PyTorch với CUDA trước:
> ```bash
> pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
> ```

---

## 🚀 Hướng Dẫn Sử Dụng

### Phương thức 1: Giao diện Web Streamlit _(Khuyên dùng)_

```bash
streamlit run src/app.py
```

Truy cập `http://localhost:8501` và thực hiện:

1. **Chọn nguồn đầu vào** từ Sidebar:
   - 📷 **Camera cấu hình sẵn** — chọn trực tiếp từ `cameras_config.yaml`
   - 📁 **Tải lên Video** — file `.mp4`, `.avi`, `.mov`
   - 🌐 **RTSP URL** — `rtsp://username:password@ip:port/path`
   - 🖥️ **Webcam ID** — mặc định `0`

2. **Hiệu chỉnh tham số** — ROI, giới hạn tốc độ, kích thước đường, confidence threshold

3. **Nhấn ▶ Bắt đầu** — theo dõi thời gian thực, nhấn ⏹ Dừng bất kỳ lúc nào

4. **Tải báo cáo** — CSV tốc độ, CSV vi phạm, video kết quả

---

### Phương thức 2: Giao diện CLI / OpenCV

```bash
# Webcam mặc định
python src/main.py

# Video cụ thể
python src/main.py --source datasets/KQAE7521.MP4 --speed_limit 50

# Camera từ file cấu hình YAML
python src/main.py --config cameras_config.yaml --camera cam_1
```

#### Bảng tham số đầy đủ

| Tham số | Rút gọn | Kiểu | Mặc định | Mô tả |
|:---|:---:|:---:|:---:|:---|
| `--config` | `-c` | `str` | `None` | Đường dẫn tệp cấu hình camera YAML |
| `--camera` | `-cam` | `str` | `None` | Tên camera trong file config |
| `--source` | `-src` | `str/int` | `0` | Webcam ID / đường dẫn video / RTSP URL |
| `--model` | `-m` | `str` | `best_.pt` | Đường dẫn trọng số YOLOv8 |
| `--yaml` | `-y` | `str` | `data.yaml` | Tệp nhãn lớp dataset |
| `--speed_limit` | `-sl` | `float` | `25.0` | Giới hạn tốc độ (km/h) |
| `--real_width` | `-rw` | `float` | `4.5` | Chiều rộng thực tế đường trong ROI (m) |
| `--real_length` | `-rl` | `float` | `18.0` | Chiều dài thực tế đường trong ROI (m) |
| `--cleanup_time` | `-ct` | `float` | `2.0` | Thời gian xóa ID xe sau khi biến mất (s) |
| `--save` | `-s` | `bool` | `True` | Lưu video kết quả đầu ra |
| `--output` | `-o` | `str` | `output_speed.mp4` | Đường dẫn file video output |

---

## 🖱️ Công Cụ Chọn Vùng Đo ROI

Sử dụng `get_roi_coordinates.py` để chọn tương tác 4 điểm ROI trên khung hình:

```bash
# Chọn ROI từ video
python get_roi_coordinates.py --source datasets/KQAE7521.MP4

# Chọn ROI từ webcam
python get_roi_coordinates.py --source 0

# Chọn camera từ config có sẵn
python get_roi_coordinates.py
```

**Hướng dẫn:**
1. Click chuột trái lần lượt chọn 4 điểm: `P1 (Trên-Trái)` → `P2 (Trên-Phải)` → `P3 (Dưới-Phải)` → `P4 (Dưới-Trái)`
2. Nhấn `S` để lưu trực tiếp vào `cameras_config.yaml`
3. Nhấn `C` để xóa và chọn lại
4. Nhấn `Q` để thoát

---

## 📷 Cấu Hình Đa Camera

File `cameras_config.yaml` cho phép định nghĩa nhiều camera với tham số riêng biệt:

```yaml
cameras:
  cam_1:
    video_source: "rtsp://admin:password@192.168.1.100:554/h264/ch1/main/av_stream"
    src_pts: [[381, 92], [145, 171], [271, 372], [630, 160]]
    real_width: 8        # Chiều rộng đường (m)
    real_length: 15.0    # Chiều dài đoạn đo (m)
    speed_limit: 25.0    # Giới hạn tốc độ (km/h)
    save_output: false
    output_path: "output_cam_1.mp4"

  cam_2:
    video_source: "rtsp://admin:password@192.168.1.101:554/h264/ch1/main/av_stream"
    src_pts: [[32, 238], [450, 483], [601, 244], [381, 187]]
    real_width: 3.5
    real_length: 15.0
    speed_limit: 50.0
    save_output: false
    output_path: "output_cam_2.mp4"
```

---

## 🧮 Thuật Toán Ước Tính Tốc Độ

Hệ thống dựa trên **phép biến đổi phối cảnh (Perspective Transformation)** để chuyển đổi tọa độ pixel sang tọa độ thế giới thực.

### Bước 1 — Thiết lập vùng đo (ROI)

Xác định đa giác 4 điểm `src_pts` trên mặt đường tương ứng với kích thước thực tế:
- `REAL_WIDTH` ($W$): chiều rộng làn đường (mét)
- `REAL_LENGTH` ($L$): chiều dài đoạn đường (mét)

### Bước 2 — Ma trận Homography

Tính ma trận biến đổi $H$ (3×3) ánh xạ pixel → tọa độ thực:

$$\begin{bmatrix} x_{real} \\ y_{real} \\ 1 \end{bmatrix} \sim H \begin{bmatrix} x_{pixel} \\ y_{pixel} \\ 1 \end{bmatrix}$$

Trong đó `dst_pts` = $\{(0,0),\ (W,0),\ (W,L),\ (0,L)\}$

### Bước 3 — Tính vận tốc tức thời

Điểm neo: trung điểm cạnh dưới bounding box $P = (x_{center},\ y_{bottom})$ — đại diện điểm tiếp đất bánh xe.

$$v_{current} = \frac{\sqrt{(\Delta x_{real})^2 + (\Delta y_{real})^2}}{\Delta t} \times 3.6 \quad \text{(km/h)}$$

### Bước 4 — Bộ lọc EMA làm mượt

Triệt tiêu sai số dao động bounding box:

$$v_{smooth} = \alpha \cdot v_{prev} + (1 - \alpha) \cdot v_{current} \quad (\alpha = 0.7)$$

---

## 📦 Dataset

Mô hình YOLOv8 được huấn luyện trên dataset từ [Roboflow](https://universe.roboflow.com/thng-phm/vehicle-detection-7djne/dataset/7) với 4 lớp phương tiện:

| Lớp | Nhãn |
|:---:|:---|
| 0 | `xe buyt` (Xe buýt) |
| 1 | `xe hoi` (Ô tô) |
| 2 | `xe may` (Xe máy) |
| 3 | `xe tai` (Xe tải) |

---

## 🛠️ Tech Stack

| Thành phần | Công nghệ |
|:---|:---|
| Object Detection & Tracking | [Ultralytics YOLOv8](https://docs.ultralytics.com) |
| Perspective Transform | [OpenCV — `findHomography` + `perspectiveTransform`](https://opencv.org) |
| Web Dashboard | [Streamlit](https://streamlit.io) |
| Video Processing | OpenCV + Threaded VideoStream |
| Data Analysis | Pandas + NumPy |

---

## 📄 License

Dataset được cấp phép theo [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

<div align="center">

**Made with ❤️ by [Thangp18](https://github.com/Thangp18)**

</div>
]]>
