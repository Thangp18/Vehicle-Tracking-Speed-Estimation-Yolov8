# Giải Thích Phương Pháp Phối Cảnh Homography và Bộ Lọc EMA

Tài liệu này giải thích chi tiết hai phương pháp kỹ thuật quan trọng nhất được áp dụng trong lớp `SpeedEstimator` của dự án để tính toán tốc độ phương tiện chính xác từ góc nhìn camera nghiêng.

---

## 1. Phương Pháp Phối Cảnh Homography (Homography Perspective Transformation)

### 1.1. Vấn đề của Camera Góc Nghiêng
Khi camera được lắp đặt ở góc nghiêng, khoảng cách hiển thị trên màn hình (đơn vị: pixel) không đồng tỷ lệ với khoảng cách thực tế (đơn vị: mét):
* **Biến dạng phối cảnh**: Hai phương tiện di chuyển cùng một vận tốc thực tế, nhưng xe ở gần camera sẽ di chuyển được nhiều pixel hơn trên khung hình so với xe ở xa.
* Nếu chỉ đếm số pixel dịch chuyển đơn thuần để tính tốc độ, kết quả sẽ bị sai số nghiêm trọng (xe ở gần bị đo quá nhanh, xe ở xa bị đo quá chậm).

**Homography** là phép biến đổi ma trận $3 \times 3$ giúp ánh xạ (project) các điểm tọa độ từ mặt phẳng ảnh nghiêng 2D (hệ tọa độ pixel) sang một mặt phẳng phẳng 2D khác trong không gian thực tế (hệ tọa độ mét trên mặt đường phẳng).

---

### 1.2. Giải thích cặn kẽ về Ma trận H (Homography Matrix)

Ma trận Homography $H$ là một ma trận kích thước $3 \times 3$:

```
    [ h11  h12  h13 ]
H = [ h21  h22  h23 ]
    [ h31  h32  h33 ]
```

Mỗi phần tử trong ma trận này đóng một vai trò vật lý cụ thể trong phép biến đổi hình học giữa hai mặt phẳng:

#### A. Phân rã cấu trúc vật lý của ma trận H:

1. **Khối con Biến đổi Tuyến tính (Xoay, Co giãn, Cắt):**
   ```
   [ h11  h12 ]
   [ h21  h22 ]
   ```
   * $h11, h22$: Thực hiện phép co giãn (scaling) theo trục X và Y.
   * $h12, h21$: Thực hiện phép xoay (rotation) và phép cắt hình (shear) đối với hệ trục tọa độ phẳng.

2. **Vector Dịch chuyển (Translation):**
   ```
   [ h13 ]
   [ h23 ]
   ```
   * $h13$: Dịch chuyển gốc tọa độ theo trục X thực tế (trái/phải).
   * $h23$: Dịch chuyển gốc tọa độ theo trục Y thực tế (lên/xuống).

3. **Vector Phối cảnh (Perspective Projection Vector):**
   ```
   [ h31  h32 ]
   ```
   * **Đây là hai tham số quan trọng nhất đối với camera nghiêng**. Chúng chịu trách nhiệm bẻ cong phối cảnh (tạo hiệu ứng xa - gần).
   * Khi $h31$ hoặc $h32$ khác 0, các đường thẳng song song trên ảnh sẽ có xu hướng hội tụ về một điểm vô cực (vanishing point). Nhờ hai tham số này, ma trận $H$ có thể biến đổi một **hình thang** (vùng phối cảnh camera nghiêng) thành một **hình chữ nhật** (vùng mặt đường thực tế nhìn từ trên xuống).

4. **Hệ số chuẩn hóa quy mô:**
   * $h33$: Thường được gán cố định bằng $1$.
   * Trong hình học chiếu, ma trận Homography mang tính đồng nhất (homogeneous), nghĩa là nếu nhân toàn bộ ma trận $H$ với một hằng số $k \neq 0$, phép biến đổi tọa độ vẫn không hề thay đổi. Do đó ta chia tất cả các phần tử cho $h33$ để triệt tiêu biến số này, giảm số lượng ẩn số cần tìm từ 9 xuống còn **8 ẩn số**.

---

#### B. Tại sao lại cần đúng 4 cặp điểm để tính toán ma trận H?

Như đã phân tích ở trên, sau khi chuẩn hóa $h33 = 1$, ma trận $H$ có đúng **8 ẩn số** cần giải quyết: $h11, h12, h13, h21, h22, h23, h31, h32$.

Với mỗi cặp điểm tương ứng giữa ảnh $(u, v)$ và thực tế $(x, y)$, ta thiết lập phương trình chiếu:
* $x = \frac{h11 \cdot u + h12 \cdot v + h13}{h31 \cdot u + h32 \cdot v + 1}$
* $y = \frac{h21 \cdot u + h22 \cdot v + h23}{h31 \cdot u + h32 \cdot v + 1}$

Biến đổi tuyến tính bằng cách nhân chéo mẫu số lên, ta có hệ 2 phương trình độc lập với các ẩn số $h_{ij}$:
1. $h11 \cdot u + h12 \cdot v + h13 - h31 \cdot u \cdot x - h32 \cdot v \cdot x = x$
2. $h21 \cdot u + h22 \cdot v + h23 - h31 \cdot u \cdot y - h32 \cdot v \cdot y = y$

* Mỗi cặp điểm tương ứng cung cấp cho chúng ta **2 phương trình**.
* Để giải được hệ phương trình có **8 ẩn số**, toán học yêu cầu chúng ta phải có ít nhất **8 phương trình độc lập**.
* Do đó, số cặp điểm tối thiểu cần thiết là:
  $$\text{Số điểm cần chọn} = \frac{8 \text{ phương trình}}{2 \text{ phương trình/điểm}} = 4 \text{ điểm}$$

* **Lưu ý quan trọng**: 4 điểm này tuyệt đối không được thẳng hàng. Nếu có 3 điểm thẳng hàng, hệ phương trình sẽ bị suy biến và không thể giải ra ma trận $H$ duy nhất.

---

### 1.3. Triển khai trong Mã nguồn
Bạn có thể tham khảo trực tiếp các đoạn code trong file [speed_estimator.py](file:///d:/AI/Deeplearning/CVPROJECT/src/core/speed_estimator.py):

* **Bước 1: Khởi tạo và Tính toán ma trận $H$**
  Trong hàm `__init__` (dòng 8-23), ta nhận vào 4 điểm pixel `src_pts` tạo thành hình thang bao quanh vùng đo (ROI) trên ảnh và ánh xạ chúng với 4 góc của hình chữ nhật thực tế `dst_pts` trên mặt đường (kích thước `real_width` x `real_length` tính bằng mét):
  ```python
  # Tọa độ thực tế (dst_pts) tương ứng với 4 góc vùng đo:
  # P1 (Trên-Trái) -> (0, 0)
  # P2 (Trên-Phải) -> (real_width, 0)
  # P3 (Dưới-Phải) -> (real_width, real_length)
  # P4 (Dưới-Trái) -> (0, real_length)
  dst_pts = np.array([
      [0, 0], [real_width, 0], [real_width, real_length], [0, real_length]
  ], dtype=np.float32)
  
  # Sử dụng hàm OpenCV để tính ma trận H
  self.H, _ = cv2.findHomography(self.src_pts, dst_pts)
  ```

* **Bước 2: Chuyển đổi tọa độ pixel sang tọa độ mét**
  Hàm `transform_point` (dòng 31-35) nhận tọa độ pixel đáy của xe `(xcenter, bottom_y)` và trả về vị trí mét thực tế `(real_x, real_y)` trên mặt đường phẳng:
  ```python
  def transform_point(self, pt):
      pt_arr = np.array([[pt]], dtype=np.float32)
      # Thực hiện nhân ma trận phối cảnh
      transformed = cv2.perspectiveTransform(pt_arr, self.H)[0][0]
      return transformed[0], transformed[1]
  ```

* **Bước 3: Tính khoảng cách thực tế dịch chuyển**
  Trong hàm `update_and_get_speed` (dòng 54-55), khoảng cách di chuyển thực tế (mét) được tính bằng công thức Euclid giữa điểm hiện tại và điểm cũ nhất trong lịch sử:
  ```python
  distance = math.hypot(real_x - old_x, real_y - old_y)
  speed_kmph = 0.0 if distance < self.distance_threshold else (distance / time_diff) * 3.6
  ```

---

## 2. Bộ Lọc Làm Mượt EMA (Exponential Moving Average Filter)

### 2.1. Tại sao cần bộ lọc EMA?
* **Rung động khung bao (Bounding Box Jitter)**: Các mô hình nhận diện vật thể như YOLOv8 không thể cho ra tọa độ khung bao hoàn toàn tĩnh ở mọi khung hình. Bounding box thường bị rung động 1-2 pixel giữa các khung hình liên tiếp do chất lượng ánh sáng, bóng đổ hoặc chuyển động của vật thể.
* **Khuếch đại sai số**: Vì khoảng thời gian giữa các khung hình cực kỳ nhỏ (ví dụ camera chạy ở $30\text{ FPS} \approx 0.033\text{ giây}$), chỉ cần bánh xe bị lệch ảo đi $2\text{ pixel}$ (khoảng $0.15\text{m}$ thực tế), vận tốc tức thời tính được sẽ bị sai số khổng lồ:
  $$\Delta v = (0.15\text{m} / 0.033\text{ giây}) * 3.6 = 16.3\text{ km/h}$$
* Điều này dẫn đến chỉ số tốc độ hiển thị bị giật cục và nhảy số liên tục. Bộ lọc EMA (bộ lọc thông thấp) giúp giải quyết triệt để hiện tượng này.

---

### 2.2. Thuật toán EMA
Công thức tính toán tốc độ sau khi làm mượt tại khung hình hiện tại:

$$S_t = (1 - \alpha) \cdot S_{t-1} + \alpha \cdot Y_t$$

Hoặc viết theo dạng trong code dự án sử dụng hệ số $\alpha = 0.3$:

$$S_t = 0.7 \cdot S_{t-1} + 0.3 \cdot Y_t$$

Trong đó:
* **S_t**: Tốc độ đã làm mượt tại thời điểm hiện tại (`smoothed_speed`).
* **S_{t-1}**: Tốc độ đã làm mượt tại khung hình trước đó (`current_speed`).
* **Y_t**: Tốc độ tức thời vừa đo được bằng khoảng cách thực/thời gian thực (`speed_kmph`).
* **\alpha = 0.3**: Hệ số làm mượt (Smoothing Factor). Với hệ số $0.3$, hệ thống sẽ lấy $70\%$ quán tính của giá trị tốc độ cũ đã làm mượt và chỉ cập nhật thêm $30\%$ biến động của tốc độ tức thời mới đo được.

---

### 2.3. Triển khai trong Mã nguồn
Đoạn code triển khai bộ lọc EMA nằm tại hàm `update_and_get_speed` (dòng 57-59):

```python
# Lấy tốc độ mượt ở bước trước đó. Nếu xe mới xuất hiện, khởi tạo bằng speed_kmph
current_speed = self.speed_display.get(vehicle_id, speed_kmph)

# Áp dụng bộ lọc EMA
smoothed_speed = 0.7 * current_speed + 0.3 * speed_kmph

# Cập nhật và lưu lại tốc độ đã làm mượt
self.speed_display[vehicle_id] = smoothed_speed
```

---

## 3. Tóm tắt sự kết hợp của hai phương pháp
1. **YOLOv8** phát hiện xe và cung cấp tọa độ khung ảnh (pixel) $\rightarrow$
2. **Homography** chuyển tọa độ pixel bị nghiêng thành tọa độ mét phẳng thực tế $\rightarrow$
3. **Tính toán Euclid** cho ra tốc độ tức thời $\rightarrow$
4. **Bộ lọc EMA** làm mịn tốc độ, loại bỏ sai số rung giật của khung bao định dạng pixel $\rightarrow$
5. Kết quả tốc độ hiển thị chính xác, ổn định và mượt mà trên Dashboard.

---

## 4. Giải thích chi tiết về Chỉ số Mảng và Index trong hàm `transform_point`

Trong hàm [transform_point](file:///d:/AI/Deeplearning/CVPROJECT/src/core/speed_estimator.py#L31-L35):
```python
def transform_point(self, pt):
    pt_arr = np.array([[pt]], dtype=np.float32)
    transformed = cv2.perspectiveTransform(pt_arr, self.H)[0][0]
    return transformed[0], transformed[1]
```

Lý do xuất hiện các chỉ số `[0][0]` và `transformed[0]`, `transformed[1]` liên quan đến quy định nghiêm ngặt về **định dạng chiều dữ liệu (Shape)** của thư viện OpenCV:

### 4.1. Khái niệm tọa độ (u, v) là gì?
Trong lĩnh vực thị giác máy tính (Computer Vision), để tránh nhầm lẫn ký hiệu:
* **(x, y)**: Thường được dùng để ký hiệu tọa độ trong **thế giới thực** (đơn vị: mét, centimét).
* **(u, v)**: Được dùng để ký hiệu tọa độ **điểm ảnh (pixel)** trên khung hình 2D của camera.
  * **u**: Tọa độ theo trục ngang (cột), tính từ mép trái ảnh sang phải.
  * **v**: Tọa độ theo trục dọc (hàng), tính từ mép trên ảnh xuống dưới.
  * *Ví dụ:* Một điểm ảnh ở chính giữa khung hình $640 \times 640$ có tọa độ ảnh là $(u, v) = (320, 320)$.

---

### 4.2. Khái niệm 3 chiều (Shape) trong mảng của OpenCV
Hàm `cv2.perspectiveTransform` yêu cầu mảng đầu vào phải là mảng **3 chiều** (3D Array) với cấu trúc kích thước (Shape) là `(Chiều 1, Chiều 2, Chiều 3)`:

1. **Chiều thứ nhất (Chiều 1 - Nhóm điểm / Batch):**
   * Ý nghĩa: Số lượng tập hợp (nhóm) các điểm cần xử lý cùng lúc.
   * Trong thực tế, bạn có thể truyền nhiều nhóm điểm khác nhau. Ở dự án này, chúng ta chỉ truyền **1 nhóm duy nhất**, do đó chiều này có kích thước là **`1`**.
   * Trên giao diện code, nó tương ứng với cặp ngoặc vuông ngoài cùng: `[ ... ]`.

2. **Chiều thứ hai (Chiều 2 - Số lượng điểm / List of Points):**
   * Ý nghĩa: Số lượng điểm ảnh cụ thể nằm trong nhóm đó. 
   * Bạn có thể truyền danh sách chứa $N$ điểm (ví dụ $100$ điểm của $100$ xe chạy để chuyển đổi đồng loạt). Tuy nhiên, hàm `transform_point` của chúng ta chỉ xử lý cho **1 điểm duy nhất** của 1 chiếc xe tại một thời điểm $\rightarrow$ Chiều này có kích thước là **`1`**.
   * Trên giao diện code, nó tương ứng với cặp ngoặc vuông thứ hai: `[[ ... ]]`.

3. **Chiều thứ ba (Chiều 3 - Tọa độ của điểm / Coordinates):**
   * Ý nghĩa: Chứa các thành phần tọa độ của điểm đó.
   * Vì đây là điểm 2D trên ảnh nên luôn luôn có **`2`** thành phần tọa độ là `[u, v]` (hoặc `[real_x, real_y]`).
   * Trên giao diện code, nó tương ứng với cặp ngoặc vuông trong cùng chứa số cụ thể: `[[[u, v]]]`.

---

### 4.3. Phân tích từng dòng lệnh trong Code

1. **Khởi tạo mảng đầu vào `pt_arr`:**
   ```python
   pt_arr = np.array([[pt]], dtype=np.float32)
   ```
   Nếu điểm đầu vào là `pt = (u, v)`, câu lệnh này tạo ra mảng `[[[u, v]]]` có **Shape = `(1, 1, 2)`**.
   * Chiều 1 (Nhóm điểm) = 1.
   * Chiều 2 (Số điểm) = 1.
   * Chiều 3 (Tọa độ) = 2 (chứa $u$ và $v$).

2. **Xử lý qua `cv2.perspectiveTransform`:**
   Hàm trả về kết quả là mảng 3D có cùng kích thước **Shape = `(1, 1, 2)`**:
   ```python
   # Kết quả trả về dạng: [[[real_x, real_y]]]
   ```

3. **Giải thích chỉ số `[0][0]`:**
   Để lấy được giá trị tọa độ thực tế ra ngoài, ta bóc tách từng lớp ngoặc vuông:
   * `transformed_array[0]` $\rightarrow$ Bóc lớp ngoặc thứ nhất (chiều 1). Thu được mảng 2D: `[[real_x, real_y]]` (Shape: `(1, 2)`).
   * `transformed_array[0][0]` $\rightarrow$ Bóc lớp ngoặc thứ hai (chiều 2). Thu được mảng 1D: `[real_x, real_y]` (Shape: `(2,)`).
   
   Biến `transformed` nhận giá trị là mảng 1D `[real_x, real_y]`.

4. **Giải thích chỉ số `[0]` và `[1]` khi trả về:**
   Vì `transformed = [real_x, real_y]`, ta lấy:
   * `transformed[0]` $\rightarrow$ Giá trị thực tế trục X (`real_x`).
   * `transformed[1]` $\rightarrow$ Giá trị thực tế trục Y (`real_y`).

   Hàm trả về 2 giá trị riêng biệt `real_x, real_y` giúp lập trình viên dễ dàng gán trực tiếp: `real_x, real_y = self.transform_point(point)`.

---

## 5. Giải thích Thuật toán Tự động Sắp xếp 4 Điểm Vùng đo (ROI)

Trong hàm khởi tạo `__init__` của [SpeedEstimator](file:///d:/AI/Deeplearning/CVPROJECT/src/core/speed_estimator.py#L9-L14), ta có đoạn xử lý:
```python
pts = list(src_pts)
pts.sort(key=lambda p: p[1])
top_two = sorted(pts[:2], key=lambda p: p[0])
bottom_two = sorted(pts[2:], key=lambda p: p[0])

self.src_pts = np.array([top_two[0], top_two[1], bottom_two[1], bottom_two[0]], dtype=np.float32)
```

### 5.1. Tại sao cần sắp xếp lại thứ tự điểm?
Khi tính toán Homography bằng OpenCV, thứ tự của 4 điểm nguồn (`src_pts`) trên ảnh và 4 điểm đích (`dst_pts`) ngoài đời thực **phải khớp hoàn toàn 1-1 với nhau**.

Trong code, 4 điểm đích `dst_pts` được định nghĩa cố định theo thứ tự vòng tròn kim đồng hồ:
1. Điểm 1: `[0, 0]` (Góc Trên - Trái)
2. Điểm 2: `[real_width, 0]` (Góc Trên - Phải)
3. Điểm 3: `[real_width, real_length]` (Góc Dưới - Phải)
4. Điểm 4: `[0, real_length]` (Góc Dưới - Trái)

Do đó, 4 điểm pixel lấy từ ảnh (`src_pts`) bắt buộc cũng phải được sắp xếp theo đúng thứ tự: **Trên-Trái $\rightarrow$ Trên-Phải $\rightarrow$ Dưới-Phải $\rightarrow$ Dưới-Trái**. Tuy nhiên, người dùng có thể nhập tọa độ hoặc click chuột chọn điểm với thứ tự ngẫu nhiên. Đoạn mã trên dùng để **tự động sắp xếp lại 4 điểm bất kỳ về đúng chuẩn này**.

---

### 5.2. Giải thích chi tiết từng bước logic

1. **`pts.sort(key=lambda p: p[1])` (Sắp xếp theo trục Y):**
   * Trong tọa độ ảnh kỹ thuật số, trục $Y$ hướng từ trên xuống dưới (phía trên đỉnh là $Y=0$, dưới đáy là $Y$ lớn nhất).
   * Lệnh này sắp xếp 4 điểm tăng dần theo giá trị Y (`p[1]`).
   * Kết quả: 2 điểm nằm phía **nửa trên** màn hình (có Y nhỏ nhất) sẽ đứng đầu danh sách (`pts[:2]`). 2 điểm nằm ở **nửa dưới** màn hình (có Y lớn nhất) sẽ đứng cuối danh sách (`pts[2:]`).

2. **`top_two = sorted(pts[:2], key=lambda p: p[0])` (Xử lý nửa trên):**
   * Lấy 2 điểm ở nửa trên (`pts[:2]`), sắp xếp chúng tăng dần theo trục X (`p[0]`, từ trái sang phải).
   * Điểm có X nhỏ hơn nằm bên trái $\rightarrow$ Điểm **Trên - Trái** (`top_two[0]`).
   * Điểm có X lớn hơn nằm bên phải $\rightarrow$ Điểm **Trên - Phải** (`top_two[1]`).

3. **`bottom_two = sorted(pts[2:], key=lambda p: p[0])` (Xử lý nửa dưới):**
   * Lấy 2 điểm ở nửa dưới (`pts[2:]`), sắp xếp tăng dần theo trục X.
   * Điểm có X nhỏ hơn nằm bên trái $\rightarrow$ Điểm **Dưới - Trái** (`bottom_two[0]`).
   * Điểm có X lớn hơn nằm bên phải $\rightarrow$ Điểm **Dưới - Phải** (`bottom_two[1]`).

4. **Gộp mảng kết quả `self.src_pts`:**
   ```python
   self.src_pts = np.array([top_two[0], top_two[1], bottom_two[1], bottom_two[0]], dtype=np.float32)
   ```
   Gộp lại thành mảng theo đúng thứ tự vòng tròn kim đồng hồ để khớp hoàn hảo với `dst_pts`:
   * Phần tử 0: `top_two[0]` (Trên-Trái) $\leftrightarrow$ `[0, 0]`
   * Phần tử 1: `top_two[1]` (Trên-Phải) $\leftrightarrow$ `[real_width, 0]`
   * Phần tử 2: `bottom_two[1]` (Dưới-Phải) $\leftrightarrow$ `[real_width, real_length]`
   * Phần tử 3: `bottom_two[0]` (Dưới-Trái) $\leftrightarrow$ `[0, real_length]`
