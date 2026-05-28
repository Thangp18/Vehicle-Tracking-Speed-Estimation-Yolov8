# Hệ Thống Theo Dõi & Ước Tính Tốc Độ Phương Tiện (YOLOv8 + Homography)

Hệ thống theo dõi và ước tính tốc độ phương tiện giao thông thời gian thực sử dụng mô hình học sâu **YOLOv8** (Object Detection & Multi-Object Tracking) kết hợp thuật toán biến đổi hình học phối cảnh **Homography** (Perspective Transformation) để tính toán chính xác tốc độ (km/h) của từng loại xe từ camera/video giám sát.

Dự án cung cấp hai giao diện hoạt động: Giao diện dòng lệnh/OpenCV truyền thống (`main.py`) và Ứng dụng Web hiện đại, trực quan xây dựng trên nền tảng **Streamlit** với phong cách thiết kế **Dark Mode & Glassmorphism** cao cấp.

---

## 🌟 Các Tính Năng Nổi Bật

- **Nhận Diện & Theo Dõi Đa Đối Tượng (MOT):** Sử dụng mô hình YOLOv8 (`best_.pt`) được tối ưu hóa để nhận diện chính xác các loại phương tiện đặc trưng (xe buýt, xe hơi, xe máy, xe tải) và gán ID duy nhất (`obj_id`) ổn định qua từng khung hình.
- **Ước Tính Tốc Độ Chính Xác Qua Homography:** Ánh xạ tọa độ pixel từ camera sang tọa độ mét thế giới thực ($x_{real}, y_{real}$) dựa trên ma trận Homography, đo khoảng cách di chuyển thực tế trên mặt đường để tính vận tốc.
- **Bộ Lọc Làm Mượt Tốc Độ (EMA):** Sử dụng bộ lọc thông thấp (Exponential Moving Average) giảm thiểu hiện tượng nhảy số, giật khung hình do nhiễu bounding box.
- **Giao Diện Web Streamlit Hiện Đại (Premium UI):**
  - **Chỉ số thời gian thực (Metric Cards):** Tổng số xe phát hiện, tốc độ trung bình, tốc độ cao nhất và FPS xử lý.
  - **Tùy chỉnh tham số động:** Thay đổi trực tiếp độ tự tin (Confidence Threshold), kích thước frame xử lý, và thời gian dọn dẹp bộ nhớ đệm (Cleanup Time) từ Sidebar.
  - **Bảng tổng hợp chi tiết:** Hiển thị danh sách phương tiện kèm ID, chủng loại và tốc độ tối đa tương ứng dưới dạng Pandas DataFrame, hỗ trợ sắp xếp và trích xuất dữ liệu dễ dàng.
- **Cảnh Báo Vượt Quá Tốc Độ:** Tự động chuyển đổi màu sắc Bounding Box và văn bản chỉ số sang **màu đỏ** cảnh báo nếu phương tiện di chuyển vượt quá tốc độ giới hạn cấu hình (`SPEED_LIMIT = 50 km/h`).
- **Quản Lý Bộ Nhớ Đệm Thông Minh:** Tự động dọn dẹp (`Cleanup`) các ID phương tiện đã di chuyển ra ngoài vùng đo sau một khoảng thời gian chờ để tối ưu hóa tài nguyên RAM.

---

## ⚙️ Yêu Cầu Hệ Thống & Cài Đặt

### 1. Chuẩn bị môi trường Python
Hệ thống khuyến nghị sử dụng **Python 3.9 - 3.11**. Bạn nên tạo môi trường ảo để cài đặt:

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
Cài đặt các thư viện phụ thuộc bằng lệnh sau:

```bash
pip install opencv-python numpy ultralytics pyyaml streamlit pandas
```

---

## 🚀 Hướng Dẫn Sử Dụng

### Giao Diện Web Streamlit (Khuyên Dùng)
Ứng dụng Web cung cấp trải nghiệm điều khiển trực quan, trực tiếp xem video đầu ra và bảng tổng hợp vi phạm tốc độ.

```bash
streamlit run src/app.py
```
> **Hướng dẫn sử dụng Web:**
> 1. Truy cập vào đường link Local URL hiển thị trên terminal (thường là `http://localhost:8501`).
> 2. Tại thanh điều khiển Sidebar, chọn nguồn đầu vào là **Video** (và upload file video từ máy) hoặc **Camera (Webcam)**.
> 3. Cấu hình các tham số ngưỡng tin cậy, kích thước frame nếu cần.
> 4. Nhấn nút **▶ Bắt đầu** để chạy hệ thống. Nhấn **⏹ Dừng** để kết thúc quá trình xử lý bất kỳ lúc nào và xem báo cáo bảng tốc độ chi tiết.

### Giao Diện CLI / OpenCV
Để chạy trực tiếp xử lý lưu video ra file hoặc kiểm tra nhanh thuật toán qua OpenCV GUI:

```bash
python src/implement/main.py
```
> **Lưu ý:** Giao diện này sẽ đọc tệp video cấu hình mặc định trong thư mục `datasets/KQAE7521.MP4`, vẽ trực tiếp thông tin lên màn hình và xuất file kết quả tại `output_speed.mp4`. Nhấn phím `Q` trên bàn phím để dừng chương trình.

---

## 📊 Giải Thuật Ước Tính Tốc Độ (Homography)

Hệ thống hoạt động dựa trên việc ánh xạ không gian 2D từ ảnh Camera sang mặt phẳng thế giới thực:

1. **Thiết lập vùng đo (ROI):** Xác định đa giác gồm 4 điểm ảnh phối cảnh `SRC_PTS` trên mặt đường tương ứng với chiều rộng làn đường thật `REAL_WIDTH` ($4.5m$) và chiều dài đoạn đường thực tế `REAL_LENGTH` ($18m$).
2. **Biến đổi Homography:** Tính toán ma trận biến đổi phối cảnh $H$:
   $$\begin{bmatrix} x_{real} \\ y_{real} \\ 1 \end{bmatrix} = H \begin{bmatrix} x_{pixel} \\ y_{pixel} \\ 1 \end{bmatrix}$$
3. **Tính vận tốc:** Lấy điểm neo là trung điểm cạnh dưới của hộp giới hạn $P = (x_{center}, y_{bottom})$ đại diện cho điểm bánh xe tiếp xúc mặt đường. Sử dụng khoảng cách Euclid di chuyển thực tế trên giây để quy ra tốc độ $km/h$:
   $$v_{current} = \left(\frac{\text{Khoảng cách (mét)}}{\text{Thời gian (giây)}}\right) \times 3.6$$
4. **Lọc thông thấp làm mượt:**
   $$v_{smooth} = 0.7 \times v_{prev} + 0.3 \times v_{current}$$

---

## 📂 Cấu Trúc Thư Mục Dự Án

```text
Vehicle-Tracking-Speed-Estimation-Yolov8/
├── datasets/
│   ├── KQAE7521.MP4           # Video đầu vào thử nghiệm mặc định
│   └── ...                    # Các video thử nghiệm khác
├── src/
│   ├── app.py                 # Mã nguồn Giao diện Web (Streamlit UI)
│   └── implement/
│       └── main.py            # Core engine xử lý thuật toán & Giao diện OpenCV
├── .gitignore                 # Cấu hình bỏ qua các tệp không cần thiết khi git commit
├── best_.pt                   # Bộ trọng số YOLOv8 đã được huấn luyện phát hiện phương tiện
├── data.yaml                  # File cấu hình nhãn lớp phương tiện giao thông
├── README.md                  # Tài liệu hướng dẫn sử dụng (File này)
└── output_speed.mp4           # Video đầu ra ghi nhận kết quả ước tính tốc độ
```

---

## 🛠️ Các Tham Số Cấu Hình Quan Trọng (`main.py`)

- `SRC_PTS`: Tọa độ 4 điểm góc tạo thành vùng đo tốc độ trên màn hình.
- `REAL_WIDTH` (mặc định `4.5` mét): Độ rộng thực tế của làn đường đo.
- `REAL_LENGTH` (mặc định `18.0` mét): Chiều dài thực tế của phân đoạn đường đo.
- `SPEED_LIMIT` (mặc định `50` km/h): Ngưỡng giới hạn tốc độ. Bounding box của phương tiện vượt ngưỡng này sẽ tự động đổi sang màu đỏ.
- `CLEANUP_TIME` (mặc định `2.0` giây): Khoảng thời gian không phát hiện thấy xe trước khi hệ thống giải phóng ID xe khỏi bộ nhớ đệm.
