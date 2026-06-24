# KỊCH BẢN HỎI ĐÁP BẢO VỆ ĐỒ ÁN
## Đề tài: Hệ Thống Giám Sát, Theo Dõi và Ước Tính Tốc Độ Phương Tiện Giao Thông Bằng YOLOv8 & Homography

Tài liệu này tổng hợp các câu hỏi tiềm năng mà Hội đồng/Giáo viên hướng dẫn có thể đặt ra liên quan đến **Mô hình AI**, **Thuật toán thị giác máy tính**, và **Logic xử lý toán học** trong dự án, đi kèm với câu trả lời chi tiết và liên kết trực tiếp tới mã nguồn của bạn.

---

## MỤC LỤC
1. [PHẦN 1: CÁC CÂU HỎI VỀ MÔ HÌNH NHẬN DIỆN & THEO DÕI (YOLOv8 & TRACKING)](#phan-1-cac-cau-hoi-ve-mo-hinh-nhan-dien--theo-doi-yolov8--tracking)
2. [PHẦN 2: CÁC CÂU HỎI VỀ PHÉP BIẾN ĐỔI PHỐI CẢNH HOMOGRAPHY (TRỌNG TÂM)](#phan-2-cac-cau-hoi-ve-phep-bien-doi-phoi-canh-homography-trong-tam)
3. [PHẦN 3: CÁC CÂU HỎI VỀ TÍNH TOÁN TỐC ĐỘ & BỘ LỌC LÀM MƯỢT EMA](#phan-3-cac-cau-hoi-ve-tinh-toan-toc-do--bo-loc-lam-muot-ema)
4. [PHẦN 4: CÁC CÂU HỎI VỀ LOGIC CODE & THIẾT KẾ HỆ THỐNG](#phan-4-cac-cau-hoi-ve-logic-code--thiet-ke-he-thong)

---

## PHẦN 1: CÁC CÂU HỎI VỀ MÔ HÌNH NHẬN DIỆN & THEO DÕI (YOLOv8 & TRACKING)

### Câu 1: Tại sao em lại chọn mô hình YOLOv8 cho bài toán này mà không phải các phiên bản trước (YOLOv5, YOLOv7) hay các mô hình khác (Faster R-CNN, SSD)?
* **Trả lời:**
  * **Tốc độ và độ chính xác (Real-time Performance):** YOLOv8 là mô hình *Anchor-free* (không sử dụng neo trước), giúp giảm thiểu số lượng hộp neo cần dự đoán, từ đó tăng tốc độ suy luận đáng kể và đạt độ chính xác (mAP) cao hơn YOLOv5 và YOLOv7 trên tập dữ liệu COCO.
  * **Thiết kế thân thiện với lập trình viên (Developer-friendly API):** Thư viện `ultralytics` tích hợp sẵn cả ba tác vụ: Nhận diện (Detection), Phân vùng (Segmentation) và Theo dõi (Tracking) trong cùng một giao diện lập trình, giúp việc tích hợp vào ứng dụng Python rất dễ dàng.
  * **Hỗ trợ Tracking tối ưu:** YOLOv8 hỗ trợ cơ chế lưu vết tích hợp sẵn rất mạnh mẽ (`model.track()`), giúp giảm thiểu việc phải cài đặt thêm các thư viện tracking bên thứ ba phức tạp.

### Câu 2: Cơ chế theo dõi (Tracking) trong mã nguồn hoạt động như thế nào? Em đang sử dụng thuật toán tracking nào?
* **Trả lời:**
  * Trong dự án này, cơ chế theo dõi được kích hoạt qua dòng code:
    ```python
    # Tại file src/main.py:116
    results = model.track(frame, persist=True, verbose=False)
    ```
  * Tham số `persist=True` báo hiệu cho mô hình biết cần duy trì định danh (ID) của vật thể qua các khung hình liên tiếp.
  * **Thuật toán ngầm định:** YOLOv8 sử dụng mặc định thuật toán **BoT-SORT** (hoặc **ByteTrack** tùy cấu hình). Các thuật toán này hoạt động dựa trên hai yếu tố chính:
    1. **Kalman Filter (Bộ lọc Kalman):** Dự đoán vị trí tiếp theo của xe ở khung hình sau dựa trên vận tốc và hướng di chuyển ở khung hình trước.
    2. **Cực đại hóa độ tương đồng (Hungarian Algorithm/Intersection over Union - IoU):** Khớp các bounding box nhận diện được ở khung hình hiện tại với các vị trí dự đoán từ Kalman Filter để gán cùng một `ID` duy nhất cho xe.

### Câu 3: File mô hình `best_.pt` trong thư mục gốc được huấn luyện như thế nào?
* **Trả lời:**
  * File [best_.pt](file:///d:/AI/Deeplearning/CVPROJECT/best_.pt) là trọng số (weights) của mô hình YOLOv8 sau khi được huấn luyện (fine-tune) trên tập dữ liệu xe cộ.
  * Cấu trúc các class nhận diện được định nghĩa trong file [data.yaml](file:///d:/AI/Deeplearning/CVPROJECT/data.yaml), bao gồm các loại phương tiện như: `car`, `truck`, `bus`, `motorbike`,...
  * Việc huấn luyện tùy biến giúp mô hình nhận diện chính xác các phương tiện giao thông đặc thù trong các điều kiện ánh sáng và góc quay của camera trong dự án.

---

## PHẦN 2: CÁC CÂU HỎI VỀ PHÉP BIẾN ĐỔI PHỐI CẢNH HOMOGRAPHY (TRỌNG TÂM)

### Câu 4: Bản chất vật lý của Phép biến đổi Homography là gì? Tại sao camera góc nghiêng lại không thể tính tốc độ trực tiếp bằng pixel?
* **Trả lời:**
  * **Vấn đề của Camera Góc Nghiêng (Perspective Distortion):** Khi camera đặt nghiêng, xuất hiện hiện tượng "gần to, xa nhỏ". Một pixel ở vùng gần camera tương ứng với khoảng cách thực tế rất ngắn (ví dụ: $1\text{ px} \approx 2\text{ cm}$), nhưng một pixel ở vùng xa camera lại tương ứng với khoảng cách thực tế rất lớn (ví dụ: $1\text{ px} \approx 20\text{ cm}$). Nếu ta chỉ đếm số pixel xe dịch chuyển để tính tốc độ:
    * Xe ở gần sẽ bị tính tốc độ **quá nhanh**.
    * Xe ở xa sẽ bị tính tốc độ **quá chậm**.
  * **Bản chất Homography:** Homography là một phép biến đổi hình học chiếu (projective transformation) biểu diễn bằng ma trận $3 \times 3$, ánh xạ tọa độ 2D từ mặt phẳng này sang mặt phẳng khác. Trong dự án, nó giúp ánh xạ tọa độ ảnh (pixel 2D nghiêng) lên mặt phẳng đường thực tế (tọa độ mét phẳng nhìn từ trên xuống - Bird's Eye View).
  
```
  [ Mặt phẳng ảnh (Pixel) ]        Ma trận H        [ Mặt phẳng đường (Mét) ]
       (Hình thang ROI)        ---------------->     (Hình chữ nhật thực tế)
          (u, v)                                            (x, y)
```

### Câu 5: Cấu trúc của ma trận Homography $H$ là gì? Hãy giải thích ý nghĩa vật lý của các phần tử trong ma trận $3 \times 3$ này.
* **Trả lời:**
  * Ma trận Homography $H$ có dạng:
    $$\begin{bmatrix} h_{11} & h_{12} & h_{13} \\ h_{21} & h_{22} & h_{23} \\ h_{31} & h_{32} & h_{33} \end{bmatrix}$$
  * Ý nghĩa vật lý cụ thể của các phân vùng phần tử:
    1. **Phân rã tuyến tính $\begin{bmatrix} h_{11} & h_{12} \\ h_{21} & h_{22} \end{bmatrix}$:** Điều khiển các phép xoay (rotation), co giãn (scaling) và cắt hình (shear) của hệ tọa độ phẳng.
    2. **Vector dịch chuyển $\begin{bmatrix} h_{13} \\ h_{23} \end{bmatrix}$:** Định nghĩa độ tịnh tiến (translation) theo trục X và Y trong thế giới thực, quyết định vị trí của gốc tọa độ $(0,0)$.
    3. **Vector phối cảnh $\begin{bmatrix} h_{31} & h_{32} \end{bmatrix}$:** Đây là bộ phận cốt lõi để xử lý camera nghiêng. Chúng tạo ra hiệu ứng hội tụ của các đường thẳng song song về một điểm vô cực (vanishing point), giúp bóp méo hình thang ảnh thành hình chữ nhật phẳng thực tế.
    4. **Hệ số chuẩn hóa $h_{33}$:** Được gán bằng $1$. Phép chiếu Homography mang tính đồng nhất (homogeneous coordinate system), nghĩa là nếu nhân cả ma trận với một hằng số $k \neq 0$ thì phép chiếu không thay đổi. Việc chia tất cả cho $h_{33}$ giúp triệt tiêu bậc tự do thừa, đưa số ẩn số cần tìm về **8**.

### Câu 6: Tại sao lại cần tối thiểu 4 cặp điểm tương ứng để tính toán ma trận $H$? Tại sao không dùng 3 điểm hay 5 điểm?
* **Trả lời:**
  * **Về mặt toán học:** Ma trận $H$ sau khi chuẩn hóa $h_{33} = 1$ sẽ còn lại đúng **8 ẩn số** cần giải ($h_{11}$ đến $h_{32}$).
  * Với mỗi cặp điểm tương ứng giữa ảnh $(u, v)$ và thực tế $(x, y)$, ta lập được hệ phương trình chiếu:
    $$x = \frac{h_{11}u + h_{12}v + h_{13}}{h_{31}u + h_{32}v + 1}$$
    $$y = \frac{h_{21}u + h_{22}v + h_{23}}{h_{31}u + h_{32}v + 1}$$
  * Nhân chéo mẫu số lên, mỗi cặp điểm tương ứng cho chúng ta **2 phương trình đại số tuyến tính độc lập**.
  * Để giải hệ phương trình có 8 ẩn số, ta bắt buộc phải có ít nhất 8 phương trình độc lập. Do đó, số cặp điểm tối thiểu cần thiết là:
    $$\text{Số điểm} = \frac{8 \text{ phương trình}}{2 \text{ phương trình/điểm}} = 4 \text{ điểm}$$
  * **Nếu dùng 3 điểm:** Chỉ có 6 phương trình, hệ thiếu nghiệm (không giải được ma trận $H$ duy nhất).
  * **Nếu dùng nhiều hơn 4 điểm (ví dụ 5 điểm):** Hệ phương trình sẽ bị thừa (over-determined). Khi đó ta sử dụng thuật toán bình phương tối thiểu (Least Squares) hoặc RANSAC (có sẵn trong `cv2.findHomography`) để tìm ra ma trận $H$ tối ưu nhất giúp giảm thiểu sai số trung bình.
  * **Điều kiện bắt buộc:** 4 điểm này **không được có 3 điểm nào thẳng hàng**, nếu không hệ phương trình sẽ bị suy biến hình học.

### Câu 7: Trình bày quy trình hoạt động cụ thể của Homography trong dự án này. Chỉ ra các dòng code tương ứng trong file `speed_estimator.py`.
* **Trả lời:** Quy trình gồm 3 bước rõ rệt:
  * **Bước 1: Khởi tạo và lập ma trận $H$:**
    * Tại hàm `__init__` ([speed_estimator.py:20-23](file:///d:/AI/Deeplearning/CVPROJECT/src/core/speed_estimator.py#L20-L23)): Định nghĩa 4 điểm thực tế `dst_pts` dưới dạng một hình chữ nhật giả định trên mặt đất có kích thước `real_width` $\times$ `real_length` (mét). Sau đó tính $H$ bằng OpenCV:
      ```python
      dst_pts = np.array([
          [0, 0], [real_width, 0], [real_width, real_length], [0, real_length]
      ], dtype=np.float32)
      self.H, _ = cv2.findHomography(self.src_pts, dst_pts)
      ```
  * **Bước 2: Chọn điểm đại diện cho xe trên ảnh:**
    * Tại file [main.py:125](file:///d:/AI/Deeplearning/CVPROJECT/src/main.py#L125), điểm đại diện được chọn là **trọng tâm cạnh dưới của bounding box** `(xcenter, bottom_y)`. 
    * *Giải thích:* Đây là điểm tiếp xúc giữa bánh xe và mặt đường (nằm trực tiếp trên mặt phẳng đường), phù hợp với giả định của phép biến đổi Homography phẳng. Nếu lấy tâm bounding box, chiều cao của xe sẽ tạo ra sai số dịch chuyển lớn.
  * **Bước 3: Chiếu điểm từ ảnh sang mét:**
    * Tại hàm `transform_point` ([speed_estimator.py:31-35](file:///d:/AI/Deeplearning/CVPROJECT/src/core/speed_estimator.py#L31-L35)): Sử dụng phép nhân ma trận chiếu thông qua hàm `cv2.perspectiveTransform`:
      ```python
      def transform_point(self, pt):
          pt_arr = np.array([[pt]], dtype=np.float32) # Định dạng 3D Array (1, 1, 2)
          transformed = cv2.perspectiveTransform(pt_arr, self.H)[0][0] # Thu về (2,)
          return transformed[0], transformed[1] # Trả về x, y thực tế (mét)
      ```

### Câu 8: Thuật toán tự động sắp xếp 4 điểm vùng đo (ROI) trong code hoạt động thế nào? Tại sao lại cần bước này?
* **Trả lời:**
  * **Lý do cần:** Phép tính `cv2.findHomography` yêu cầu thứ tự các điểm trong `src_pts` và `dst_pts` phải tương ứng khớp 1-1 (Ví dụ: Trên-Trái $\leftrightarrow$ `[0,0]`). Tuy nhiên, người dùng có thể nhấp chuột chọn tọa độ theo thứ tự bất kỳ. Do đó, cần tự động chuẩn hóa về thứ tự xoay theo chiều kim đồng hồ: **Trên-Trái $\rightarrow$ Trên-Phải $\rightarrow$ Dưới-Phải $\rightarrow$ Dưới-Trái**.
  * **Logic thuật toán** tại [speed_estimator.py:9-14](file:///d:/AI/Deeplearning/CVPROJECT/src/core/speed_estimator.py#L9-L14):
    1. `pts.sort(key=lambda p: p[1])`: Sắp xếp 4 điểm tăng dần theo trục Y (trên ảnh, trục Y hướng xuống dưới, tức Y nhỏ nhất nằm ở phía trên). Lúc này, 2 điểm đầu danh sách `pts[:2]` chắc chắn ở nửa trên ảnh, 2 điểm sau `pts[2:]` ở nửa dưới ảnh.
    2. `top_two = sorted(pts[:2], key=lambda p: p[0])`: Sắp xếp 2 điểm nửa trên theo trục X (từ trái qua phải). Điểm bên trái là **Trên-Trái** (`top_two[0]`), bên phải là **Trên-Phải** (`top_two[1]`).
    3. `bottom_two = sorted(pts[2:], key=lambda p: p[0])`: Sắp xếp 2 điểm nửa dưới theo trục X. Điểm bên trái là **Dưới-Trái** (`bottom_two[0]`), bên phải là **Dưới-Phải** (`bottom_two[1]`).
    4. Gộp lại theo thứ tự kim đồng hồ:
       `self.src_pts = np.array([top_two[0], top_two[1], bottom_two[1], bottom_two[0]], dtype=np.float32)`

---

## PHẦN 3: CÁC CÂU HỎI VỀ TÍNH TOÁN TỐC ĐỘ & BỘ LỌC LÀM MƯỢT EMA

### Câu 9: Thuật toán tính tốc độ thực tế hoạt động như thế nào? Tại sao em không tính tốc độ từ khung hình ngay lập tức (instantaneous) mà lại dùng hàng đợi `deque` lưu lịch sử?
* **Trả lời:**
  * **Công thức toán học:** Vận tốc = Quãng đường / Thời gian ($v = d/t$).
  * **Tại sao không dùng 2 khung hình liên tiếp:** Khoảng thời gian giữa 2 khung hình liên tiếp cực kỳ nhỏ (Ví dụ: camera 30 FPS $\rightarrow \Delta t \approx 0.033\text{ giây}$). Do sai số nhận diện của mô hình YOLOv8, khung bao bounding box có thể bị rung động nhẹ 1-2 pixel. Sai số 2 pixel này tương đương khoảng $0.15\text{ mét}$ thực tế. Khi chia cho $\Delta t$ quá nhỏ, sai số tốc độ tức thời sẽ bị phóng đại lên rất lớn:
    $$\Delta v = \frac{0.15\text{ m}}{0.033\text{ s}} \times 3.6 = 16.3\text{ km/h}$$
    Điều này làm tốc độ hiển thị bị nhảy số giật cục (noise).
  * **Giải pháp hàng đợi (`deque`):** Trong [speed_estimator.py:44-55](file:///d:/AI/Deeplearning/CVPROJECT/src/core/speed_estimator.py#L44-L55), hệ thống lưu lịch sử tối đa 10 tọa độ gần nhất của xe. Phép tính tốc độ chỉ được thực hiện khi thời gian trôi qua giữa tọa độ cũ nhất trong hàng đợi và tọa độ hiện tại lớn hơn một ngưỡng `min_time_diff` (ví dụ: $0.3\text{ giây}$):
    * Khoảng thời gian $\Delta t \ge 0.3\text{ giây}$ lớn gấp 10 lần thời gian của 1 khung hình, giúp **triệt tiêu sai số chia cho số cực nhỏ**.
    * Khoảng cách di chuyển lúc này cũng lớn hơn nhiều so với độ rung động của pixel, giúp phép chia ổn định và chính xác hơn.
    * Sau đó tốc độ được đổi từ $\text{m/s}$ sang $\text{km/h}$ bằng cách nhân với **`3.6`**.

### Câu 10: Rung động khung bao (Bounding Box Jitter) là gì và em giải quyết nó như thế nào? Giải thích toán học của bộ lọc EMA?
* **Trả lời:**
  * **Bounding Box Jitter:** Là hiện tượng các cạnh của hình hộp chữ nhật bao quanh vật thể bị rung rinh nhẹ giữa các khung hình do nhiễu ánh sáng, bóng đổ hoặc do thuật toán nhận diện của mô hình AI không ổn định tuyệt đối.
  * **Giải pháp bộ lọc EMA (Exponential Moving Average - Trung bình trượt lũy thừa):** Đây là một bộ lọc thông thấp (low-pass filter) giúp làm mịn tín hiệu.
  * **Công thức toán học áp dụng:**
    $$S_t = (1 - \alpha) \cdot S_{t-1} + \alpha \cdot Y_t$$
  * Trong mã nguồn ([speed_estimator.py:57-59](file:///d:/AI/Deeplearning/CVPROJECT/src/core/speed_estimator.py#L57-L59)):
    ```python
    current_speed = self.speed_display.get(vehicle_id, speed_kmph)
    smoothed_speed = 0.7 * current_speed + 0.3 * speed_kmph
    ```
    * Ở đây hệ số $\alpha = 0.3$ (Smoothing Factor).
    * Ý nghĩa: Tốc độ hiển thị hiện tại (`smoothed_speed`) sẽ giữ lại **70% giá trị tốc độ đã làm mượt của bước trước** và chỉ cập nhật thêm **30% biến động của tốc độ tức thời mới đo được** ở khung hình này. Điều này giúp đồ thị tốc độ thay đổi một cách mượt mà tự nhiên, loại bỏ các đỉnh đột biến (outliers) do rung động pixel gây ra.

---

## PHẦN 4: CÁC CÂU HỎI VỀ LOGIC CODE & THIẾT KẾ HỆ THỐNG

### Câu 11: Biến `distance_threshold` và `min_time_diff` trong code có vai trò gì?
* **Trả lời:**
  * **`min_time_diff`** (mặc định $0.3\text{ giây}$): Là khoảng thời gian tối thiểu để thực hiện một lần tính toán tốc độ mới. Tránh chia cho khoảng thời gian quá nhỏ gây khuếch đại nhiễu (như đã giải thích ở Câu 9).
  * **`distance_threshold`** (mặc định $0.5\text{ mét}$): Ngưỡng dịch chuyển tối thiểu trong thế giới thực. Nếu xe di chuyển quãng đường nhỏ hơn ngưỡng này (ví dụ xe đang dừng chờ đèn đỏ nhưng bounding box vẫn rung nhẹ), hệ thống sẽ gán tốc độ bằng $0.0\text{ km/h}$ thay vì tính ra tốc độ nhiễu nhỏ.

### Câu 12: Làm thế nào để xác định được tọa độ 4 điểm ảnh `src_pts` và kích thước thực tế `real_width`, `real_length`?
* **Trả lời:**
  * **`src_pts` (Tọa độ ảnh):** Được xác định thông qua công cụ hỗ trợ chọn tọa độ (ví dụ file `get_roi_coordinates.py` có sẵn trong dự án). Người dùng click chuột vào 4 góc của đoạn đường muốn đo tốc độ trên luồng video và ghi lại tọa độ pixel $(u, v)$ hiển thị.
  * **`real_width` (Chiều rộng thực tế) & `real_length` (Chiều dài thực tế):** Được xác định bằng các thông số thực tế ngoài đời thực:
    * Chiều rộng làn đường tiêu chuẩn tại Việt Nam thường từ $3.5\text{m}$ đến $4.5\text{m}$.
    * Chiều dài vạch kẻ đường đứt quãng hoặc khoảng cách giữa các cột mốc giao thông được đo đạc thực tế (ví dụ: một đoạn đường kẻ vạch dài $18\text{m}$).
  * Các thông số này sau đó được lưu trữ trong file cấu hình [cameras_config.yaml](file:///d:/AI/Deeplearning/CVPROJECT/cameras_config.yaml) để hệ thống tự động tải tùy theo camera đang chạy.

### Câu 13: Cơ chế `cleanup` trong lớp `SpeedEstimator` hoạt động thế nào và tại sao cần nó?
* **Trả lời:**
  * **Lý do cần:** Khi các phương tiện di chuyển ra khỏi khung hình camera, thông tin định danh và lịch sử vị trí của chúng vẫn nằm lại trong bộ nhớ RAM (các biến `self.history`, `self.speed_display`,...). Nếu không dọn dẹp, sau một thời gian dài chạy hệ thống, bộ nhớ RAM sẽ bị tràn (memory leak).
  * **Cơ chế hoạt động** ([speed_estimator.py:67-80](file:///d:/AI/Deeplearning/CVPROJECT/src/core/speed_estimator.py#L67-L80)):
    * Mỗi khi nhận diện xe, thời gian cập nhật mới nhất được lưu vào `self.last_seen[vehicle_id]`.
    * Hàm `cleanup` liên tục được gọi trong vòng lặp chính. Nó duyệt qua tất cả các ID xe đang quản lý, nếu khoảng thời gian kể từ lần cuối nhìn thấy xe lớn hơn `cleanup_time` (mặc định là $2.0\text{ giây}$), hệ thống sẽ:
      1. Kiểm tra xem tốc độ lớn nhất của xe đó (`self.max_speed`) có vượt quá giới hạn tốc độ cho phép (`speed_limit`) hay không. Nếu có, tiến hành in ra cảnh báo vi phạm tốc độ lên console (Ví dụ: `⚠️ Xe car ID:5 | Vượt tốc độ giới hạn! Max Speed: 42.5 km/h...`).
      2. Tiến hành xóa tất cả dữ liệu lịch sử liên quan đến xe đó ra khỏi bộ nhớ bằng hàm `.pop()`.

### Câu 14: Những hạn chế lớn nhất của phương pháp đo tốc độ bằng camera đơn (Monocular Camera) kết hợp Homography là gì? Cách khắc phục?
* **Trả lời:**
  * **Hạn chế:**
    1. **Giả định mặt phẳng phẳng (Flat Plane Assumption):** Homography giả định mặt đường là một mặt phẳng tuyệt đối. Nếu đường có dốc, gồ ghề, hoặc xe đi qua các gờ giảm tốc làm xe bị nảy lên hạ xuống $\rightarrow$ điểm đáy bánh xe không còn nằm trên mặt phẳng chiếu thực tế nữa, gây sai số đo tốc độ.
    2. **Độ cao của xe và góc nhìn camera:** Bounding box của xe tải lớn hoặc xe container rất cao. Nếu camera đặt quá nghiêng ở góc thấp (low angle), phần bánh xe có thể bị che khuất bởi thân xe khác hoặc chính phần đầu xe $\rightarrow$ điểm đáy `bottom_y` bị lệch, gây đo sai khoảng cách.
    3. **Che khuất (Occlusion):** Một chiếc xe bị che khuất một phần bởi xe khác sẽ làm bounding box nhận diện bị thu hẹp hoặc thay đổi hình dạng đột ngột, dẫn đến việc ước lượng sai vị trí bánh xe tiếp đất.
  * **Hướng khắc phục:**
    * Sử dụng camera đặt ở góc cao thẳng đứng nhìn xuống (gần góc 90 độ - top-down view) để giảm biến dạng phối cảnh và tránh che khuất.
    * Sử dụng mô hình nhận diện điểm then chốt (Keypoint Detection) để xác định chính xác tâm bánh xe hoặc điểm tiếp đất thay vì chỉ dựa vào bounding box của YOLO.
    * Tích hợp thêm cảm biến 3D (như LiDAR, Camera lập thể - Stereo Camera) để lấy trực tiếp chiều sâu (depth) thay vì dùng ma trận chiếu toán học 2D.
