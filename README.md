# 🚗 Vehicle Tracking & Speed Estimation System

### YOLOv8 · Homography · Real-time Analytics

[![Python](https://img.shields.io/badge/Python-3.9%20|%203.10%20|%203.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![YOLOv8](https://img.shields.io/badge/Model-YOLOv8-00FFFF?logo=ultralytics&logoColor=white)](https://docs.ultralytics.com)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org)
[![License](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)

Hệ thống theo dõi và ước tính tốc độ phương tiện giao thông thời gian thực sử dụng mô hình học sâu YOLOv8 kết hợp thuật toán biến đổi phối cảnh Homography để tính toán chính xác tốc độ (km/h) của từng phương tiện từ camera giám sát hoặc file video.

[Tính năng](#-tính-năng-nổi-bật) · [Cài đặt](#️-cài-đặt) · [Hướng dẫn sử dụng](#-hướng-dẫn-sử-dụng) · [Kiến trúc](#️-kiến-trúc-hệ-thống) · [Thuật toán](#-thuật-toán-ước-tính-tốc-độ)

---

## ✨ Tính Năng Nổi Bật

| Tính năng | Mô tả |
| :--- | :--- |
| 🎯 **Nhận diện & Theo dõi đa đối tượng** | YOLOv8 nhận dạng 4 loại xe (xe buýt, ô tô, xe máy, xe tải) với ID tracking ổn định qua các khung hình. |
| 📐 **Ước tính tốc độ qua Homography** | Ánh xạ pixel từ hệ toạ độ ảnh 2D sang tọa độ mặt đường thực tế 3D (mét), đo khoảng cách di chuyển để tính vận tốc chính xác. |
| 📊 **Bộ lọc EMA làm mượt tốc độ** | Exponential Moving Average giúp triệt tiêu các sai số nhảy vọt/giật lag của bounding box giữa các khung hình liên tiếp. |
| 🧵 **Đa luồng đọc camera** | Thread chuyên biệt đọc dữ liệu video giúp tối ưu hóa luồng ghi nhận hình ảnh, tránh tắc nghẽn bộ đệm OpenCV trên camera RTSP hoặc Webcam. |
| 🚨 **Cảnh báo vượt tốc độ** | Tự động phát hiện vi phạm, đổi màu bounding box sang màu đỏ và xuất cảnh báo chi tiết ra console/giao diện. |
| 📥 **Xuất báo cáo dữ liệu** | Cho phép tải báo cáo định dạng CSV về lịch sử tốc độ và lịch sử vi phạm ngay trên giao diện web. |
| 📹 **Ghi hình kết quả** | Xuất video kết quả với bounding box, ID xe và thông số tốc độ trực quan. |

### Hai phương thức vận hành linh hoạt

1. **Giao diện Web Streamlit**: Dashboard hiện đại (Dark Mode & Glassmorphism), biểu đồ phân tích thời gian thực (phân bố tốc độ, loại xe), cho phép tuỳ chỉnh mọi tham số trực quan.
2. **Giao diện dòng lệnh (CLI/OpenCV)**: Nhẹ nhàng, thích hợp cho việc deploy hệ thống, cấu hình nhanh thông qua tham số dòng lệnh hoặc file YAML cấu hình đa camera.

---

## 🏗️ Kiến Trúc Hệ Thống

```text
Vehicle-Tracking-Speed-Estimation-Yolov8/
│
├── src/                            # Thư mục mã nguồn chính
│   ├── app.py                      # Entrypoint giao diện Web (Streamlit)
│   ├── main.py                     # Entrypoint giao diện dòng lệnh CLI (OpenCV)
│   │
│   ├── core/                       # Logic xử lý chính
│   │   └── speed_estimator.py      # Module tính tốc độ (Homography & lọc mượt EMA)
│   │
│   ├── ui/                         # Thành phần giao diện Streamlit
│   │   ├── dashboard.py            # Hiển thị biểu đồ, thẻ chỉ số, bảng vi phạm
│   │   ├── sidebar.py              # Sidebar điều khiển nguồn video, cài đặt ROI và tham số
│   │   └── styles.py               # CSS tùy chỉnh giao diện (Dark theme & Glassmorphism)
│   │
│   └── utils/                      # Tiện ích bổ trợ
│       ├── drawing_utils.py        # Vẽ nhãn chữ an toàn, chống tràn viền ảnh
│       └── video_stream.py         # Thread đọc camera đa luồng chống trễ
│
├── get_roi_coordinates.py          # Công cụ trực quan chọn 4 điểm ROI bằng chuột
├── best_.pt                        # Trọng số mô hình YOLOv8 đã train
├── data.yaml                       # Định nghĩa class dữ liệu (4 lớp phương tiện)
├── cameras_config.yaml             # File lưu cấu hình đa camera và tọa độ ROI
├── datasets/                       # Thư mục chứa các video test mẫu
└── README.md                       # Tài liệu hướng dẫn sử dụng
```

---

## ⚙️ Cài Đặt

### Yêu cầu hệ thống
- **Python** 3.9, 3.10 hoặc 3.11.
- Khuyến nghị sử dụng **NVIDIA GPU + CUDA** để đạt FPS tốt nhất khi chạy mô hình YOLOv8.

### Các bước cài đặt chi tiết

1. **Clone mã nguồn dự án**:
   ```bash
   git clone https://github.com/Thangp18/Vehicle-Tracking-Speed-Estimation-Yolov8.git
   cd Vehicle-Tracking-Speed-Estimation-Yolov8
   ```

2. **Khởi tạo và kích hoạt môi trường ảo (Virtual Environment)**:
   - **Trên Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Trên Windows (Command Prompt)**:
     ```cmd
     python -m venv venv
     .\venv\Scripts\activate.bat
     ```
   - **Trên Linux/macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Cài đặt các thư viện cần thiết**:
   ```bash
   pip install opencv-python numpy ultralytics pyyaml streamlit pandas plotly
   ```

   > [!TIP]
   > Nếu hệ thống của bạn có card đồ họa NVIDIA và muốn sử dụng GPU để tăng tốc nhận diện, hãy cài đặt PyTorch hỗ trợ CUDA trước:
   > ```bash
   > pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
   > ```

---

## 🚀 Hướng Dẫn Sử Dụng

### Phương thức 1: Giao diện Web (Streamlit)

Chạy câu lệnh dưới đây để khởi động máy chủ giao diện:
```bash
streamlit run src/app.py
```
Sau khi khởi động, trình duyệt sẽ tự động mở trang web giao diện tại địa chỉ `http://localhost:8501`.

**Các bước thực hiện:**
1. **Chọn nguồn video**: Chọn từ danh sách camera cấu hình sẵn (`cameras_config.yaml`), upload video mới từ máy tính, nhập link RTSP camera hoặc Webcam.
2. **Cài đặt thông số**: Tại thanh Sidebar, tuỳ chỉnh toạ độ ROI, giới hạn tốc độ, kích thước thực tế làn đường, độ tin cậy YOLO.
3. **Chạy hệ thống**: Bấm nút **▶ Bắt đầu** để xem trực tiếp quá trình đo tốc độ. Bấm **⏹ Dừng** bất cứ lúc nào để xem báo cáo phân tích tổng hợp.
4. **Tải dữ liệu**: Sau khi quá trình xử lý hoàn tất, chuyển qua tab **Tải xuống báo cáo** để download file CSV thống kê tốc độ, file CSV vi phạm và video kết quả.

---

### Phương thức 2: Chạy qua giao diện CLI (OpenCV)

Nếu muốn chạy trực tiếp bằng cửa sổ OpenCV thông thường từ dòng lệnh:

```bash
# 1. Chạy với Webcam mặc định (ID = 0)
python src/main.py

# 2. Chạy với video cụ thể và giới hạn tốc độ 50 km/h
python src/main.py --source datasets/KQAE7521.MP4 --speed_limit 50

# 3. Chạy cấu hình camera được cấu hình sẵn trong YAML
python src/main.py --config cameras_config.yaml --camera cam_1
```

#### Bảng tham số CLI đầy đủ:
| Tham số đầy đủ | Viết tắt | Kiểu dữ liệu | Giá trị mặc định | Chi tiết |
| :--- | :---: | :---: | :---: | :--- |
| `--config` | `-c` | `str` | `None` | Đường dẫn file cấu hình camera YAML. |
| `--camera` | `-cam` | `str` | `None` | Tên cấu hình camera cụ thể trong file config. |
| `--source` | `-src` | `str/int` | `0` | Đường dẫn video / RTSP URL / ID Webcam. |
| `--model` | `-m` | `str` | `best_.pt` | Đường dẫn tệp trọng số YOLOv8. |
| `--yaml` | `-y` | `str` | `data.yaml` | Tệp cấu hình nhãn lớp phương tiện. |
| `--speed_limit` | `-sl` | `float` | `25.0` | Vận tốc giới hạn cho phép (km/h). |
| `--real_width` | `-rw` | `float` | `4.5` | Chiều rộng thực tế làn đường trong vùng ROI (m). |
| `--real_length` | `-rl` | `float` | `18.0` | Chiều dài thực tế làn đường trong vùng ROI (m). |
| `--cleanup_time` | `-ct` | `float` | `2.0` | Thời gian xóa thông tin xe sau khi rời khung hình (giây). |
| `--save` | `-s` | `bool` | `True` | Cho phép lưu file video kết quả đầu ra. |
| `--output` | `-o` | `str` | `output_speed.mp4` | Đường dẫn lưu video kết quả đầu ra. |

---

## 🖱️ Công Cụ Cấu Hình Vùng ROI Bằng Chuột

Để ước tính tốc độ chính xác, bạn cần lấy tọa độ 4 điểm góc của vùng ROI trên mặt đường. Bạn có thể sử dụng công cụ hỗ trợ `get_roi_coordinates.py` để lấy tọa độ trực quan bằng cách nhấp chuột:

```bash
# Lấy toạ độ từ file video
python get_roi_coordinates.py --source datasets/KQAE7521.MP4

# Lấy toạ độ từ webcam
python get_roi_coordinates.py --source 0

# Tự động chọn camera có sẵn trong file config
python get_roi_coordinates.py
```

**Các thao tác click chuột:**
1. Chọn lần lượt 4 điểm theo thứ tự hình chữ U / vòng tròn:
   - **P1 (Trên-Trái)** $\rightarrow$ **P2 (Trên-Phải)** $\rightarrow$ **P3 (Dưới-Phải)** $\rightarrow$ **P4 (Dưới-Trái)**
2. Nhấn phím **S** trên bàn phím để lưu tọa độ và đặt tên camera trực tiếp vào file `cameras_config.yaml`.
3. Nhấn phím **C** để xoá toàn bộ các điểm đã chọn và thực hiện chọn lại.
4. Nhấn phím **Q** để thoát chương trình.

---

## 📷 Cấu Hình Đa Camera (`cameras_config.yaml`)

File `cameras_config.yaml` lưu trữ thông số của từng camera để tái sử dụng nhanh chóng mà không cần nhập lại tọa độ:

```yaml
cameras:
  cam_1:
    video_source: "rtsp://admin:password@192.168.1.100:554/h264/ch1/main/av_stream"
    src_pts: [[381, 92], [145, 171], [271, 372], [630, 160]]
    real_width: 8.0        # Chiều rộng làn đường thực tế (mét)
    real_length: 15.0      # Chiều dài vùng đo thực tế (mét)
    speed_limit: 25.0      # Tốc độ giới hạn (km/h)
    save_output: false
    output_path: "output_cam_1.mp4"

  cam_2:
    video_source: "datasets/KQAE7521.MP4"
    src_pts: [[281, 146], [179, 180], [295, 429], [556, 304]]
    real_width: 4.5
    real_length: 18.0
    speed_limit: 50.0
    save_output: true
    output_path: "output_cam_2.mp4"
```

---

## 🧮 Thuật Toán Ước Tính Tốc Độ

Vận tốc của xe được tính dựa trên nguyên lý **Phép chiếu phối cảnh (Perspective Transformation / Homography)**.

### 1. Thiết lập ma trận Homography
Chúng ta xác định một hình tứ giác ROI trên ảnh 2D thông qua 4 điểm góc `src_pts` có tọa độ pixel:
$$P_{pixel} = (x_{pixel}, y_{pixel})$$

Mặt đường thực tế tương ứng với một hình chữ nhật có kích thước thực tế: chiều rộng $W$ và chiều dài $L$. Chúng ta định nghĩa các điểm đích lý tưởng `dst_pts` trên mặt phẳng thực tế (mét) tương ứng:
$$P_{real} = (x_{real}, y_{real})$$
Có toạ độ lần lượt là: $\{(0,0),\ (W,0),\ (W,L),\ (0,L)\}$.

Từ đó, ma trận biến đổi phối cảnh $H$ kích thước $3 \times 3$ được xác định sao cho:
$$\begin{bmatrix} x_{real} \\ y_{real} \\ 1 \end{bmatrix} \sim H \begin{bmatrix} x_{pixel} \\ y_{pixel} \\ 1 \end{bmatrix}$$

### 2. Tính vận tốc
- **Điểm neo**: Chúng ta chọn điểm chính giữa cạnh dưới của bounding box làm gốc định vị phương tiện (điểm tiếp đất của bánh xe phía sau hoặc trước).
- Khi xe di chuyển, tọa độ pixel của điểm neo được ánh xạ qua ma trận $H$ thành tọa độ thực $(x_{real}, y_{real})$ theo mét.
- Khoảng cách di chuyển thực tế $\Delta d$ giữa hai lần đo:
$$\Delta d = \sqrt{(x_{real} - x_{real\_old})^2 + (y_{real} - y_{real\_old})^2} \quad \text{(mét)}$$
- Tốc độ tức thời tính bằng:
$$v_{current} = \frac{\Delta d}{\Delta t} \times 3.6 \quad \text{(km/h)}$$

### 3. Làm mượt bằng bộ lọc EMA
Do toạ độ bounding box từ mô hình YOLOv8 có thể bị rung động nhẹ giữa các frame liên tiếp, ta áp dụng bộ lọc mượt **Exponential Moving Average (EMA)** để tránh nhảy vọt tốc độ ảo:
$$v_{smooth} = \alpha \cdot v_{prev} + (1 - \alpha) \cdot v_{current}$$
Với hệ số mượt mặc định $\alpha = 0.7$.

---

## 📦 Bộ Nhãn Dataset (4 Classes)

Mô hình YOLOv8 được huấn luyện trên bộ dữ liệu phát hiện phương tiện giao thông gồm 4 lớp chính:

| ID Lớp | Tên nhãn | Giải nghĩa |
| :---: | :--- | :--- |
| **0** | `xe buyt` | Xe buýt (Bus) |
| **1** | `xe hoi` | Ô tô con (Car) |
| **2** | `xe may` | Xe máy / Xe hai bánh (Motorbike) |
| **3** | `xe tai` | Xe tải (Truck) |

---

## 📄 License

Dự án được phân phối phi thương mại, bộ dữ liệu và trọng số được cấp phép theo chuẩn [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---
<div align="center">

**Phát triển bởi [Thangp18](https://github.com/Thangp18) ❤️**

</div>
