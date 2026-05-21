import cv2
import numpy as np
from ultralytics import YOLO
import yaml
import math
import time
from collections import deque
import os

# Xác định thư mục gốc của project (chứa data.yaml, best_.pt)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

#highway
# line1= [(250, 79), (445, 82)]
# line2= [(94, 342), (597, 354)]
#vidtest
# line1= [(6, 242), (476, 280)]
# line2= [(516, 407), (2, 373)]
#test
# line1= [(307, 342), (622, 342)]
# line2= [(400, 226), (185, 226)]

# 1. Cấu hình Homography
# (Cần thay đổi các điểm này sao cho khớp với mặt đường trong video của bạn)
# Lấy từ thông số highway ở trên: 
# Top-Left, Top-Right (từ line 1), Bottom-Right, Bottom-Left (từ line 2)
src_pts = np.array([
    [281, 146], [179, 180], [295, 429], [556, 304]
], dtype=np.float32)

# Giả sử bề rộng đoạn đường là 4 mét, chiều dài đoạn đường (từ Line 1 tới Line 2) là 20 mét
REAL_WIDTH = 3.5
REAL_LENGTH = 17.0

dst_pts = np.array([
    [0, 0], 
    [REAL_WIDTH, 0], 
    [REAL_WIDTH, REAL_LENGTH], 
    [0, REAL_LENGTH]
], dtype=np.float32)

# Tính ma trận Homography
H, _ = cv2.findHomography(src_pts, dst_pts)

# Cấu hình tính tốc độ và lưu trữ
history_positions = {}
speed_display = {}
last_seen = {}

CLEANUP_TIME = 2.0  # Xoá ID không xuất hiện sau 2 giây
DISTANCE_THRESHOLD = 0.5  # Ngưỡng mét (nếu di chuyển ít hơn thì xem như đứng im)
MIN_TIME_DIFF = 0.3  # Khoảng thời gian tối thiểu để tính tốc độ

def calculate_speed_homography(vehicle_id, cur_point, video_time):
    # Biến đổi toạ độ pixel (x, y) sang toạ độ thực tế (X, Y) tính bằng mét
    pt = np.array([[cur_point]], dtype=np.float32)
    transformed_pt = cv2.perspectiveTransform(pt, H)[0][0]
    
    real_x, real_y = transformed_pt[0], transformed_pt[1]
    
    # Cập nhật thời gian xuất hiện cuối cùng để dọn dẹp
    last_seen[vehicle_id] = video_time
    
    if vehicle_id not in history_positions:
        history_positions[vehicle_id] = deque(maxlen=10)
        history_positions[vehicle_id].append((real_x, real_y, video_time))
        return

    history = history_positions[vehicle_id]
    
    # Lấy vị trí cũ nhất trong history để tính vận tốc trên quãng đường dài hơn
    old_x, old_y, old_time = history[0]
    time_diff = video_time - old_time
    
    if time_diff > MIN_TIME_DIFF:
        distance = math.hypot(real_x - old_x, real_y - old_y)
        
        if distance < DISTANCE_THRESHOLD:
            # Nếu xe di chuyển quá ít (đang đỗ/tắc đường)
            speed_kmph = 0.0
        else:
            speed_mps = distance / time_diff
            speed_kmph = speed_mps * 3.6
            
        # Làm mượt tốc độ
        if vehicle_id in speed_display:
            speed_display[vehicle_id] = 0.7 * speed_display[vehicle_id] + 0.3 * speed_kmph
        else:
            speed_display[vehicle_id] = speed_kmph
                
    # Lưu vị trí hiện tại vào history
    history.append((real_x, real_y, video_time))

def cleanup_old_tracks(current_time):
    # Dọn dẹp các xe không còn xuất hiện
    keys_to_remove = [k for k, v in last_seen.items() if current_time - v > CLEANUP_TIME]
    for k in keys_to_remove:
        history_positions.pop(k, None)
        speed_display.pop(k, None)
        last_seen.pop(k, None)

def draw_text_safe(img, text, pos, color, thickness=1):
    x, y = pos
    # Điều chỉnh y để không bị khuất nếu ở sát mép trên
    if y < 20:
        y += 30
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)


def main():
    yaml_path = os.path.join(ROOT_DIR, "data.yaml")
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    classes = data['names']
    clas = [i for i in classes]
    print(clas)

    model_path = os.path.join(ROOT_DIR, "best_.pt")
    model = YOLO(model_path)
    
    video_path = os.path.join(ROOT_DIR, "datasets", "KQAE7521.mp4")
    cap = cv2.VideoCapture(video_path)

    # Cấu hình VideoWriter
    width, height = 640, 640
    fps_video = int(cap.get(cv2.CAP_PROP_FPS))
    if fps_video == 0: fps_video = 30
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output_speed.mp4', fourcc, fps_video, (width, height))

    prev_time = time.time()

    while cap.isOpened():
        flag, frame = cap.read()
        if not flag:
            break
            
        current_time_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        frame = cv2.resize(frame, (width, height))

        # Dọn dẹp dữ liệu cũ mỗi frame
        cleanup_old_tracks(current_time_sec)

        # Vẽ vùng chọn Homography lên ảnh
        cv2.polylines(frame, [np.int32(src_pts)], isClosed=True, color=(0, 255, 255), thickness=2)

        # Tracking
        result = model.track(frame, persist=True, verbose=False, conf=0.7)

        if result[0].boxes is not None and result[0].boxes.id is not None:
            boxes = result[0].boxes.xyxy.cpu().numpy()
            ids = result[0].boxes.id.cpu().numpy().astype(int)
            cls_ids = result[0].boxes.cls.cpu().numpy().astype(int)

            for box, id, cls_id in zip(boxes, ids, cls_ids):
                x1, y1, x2, y2 = box
                xcenter = int((x1 + x2) / 2)
                
                # CHÚ Ý QUAN TRỌNG: Lấy toạ độ phần ĐÁY của xe (bánh xe chạm đường) thay vì ycenter
                bottom_y = int(y2)
                
                # Kiểm tra xe có nằm trong vùng Homography không
                inside = cv2.pointPolygonTest(np.int32(src_pts), (xcenter, bottom_y), False)
                
                if inside >= 0:
                    label = classes[cls_id]

                    # Tính toán tốc độ dựa trên toạ độ đã Transform
                    calculate_speed_homography(id, (xcenter, bottom_y), current_time_sec)

                    # Vẽ bounding box
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.circle(frame, (xcenter, bottom_y), 4, (0, 0, 255), -1)
                    
                    draw_text_safe(frame, f'{label} ID:{id}', (int(x1), int(y1) - 10), (255, 255, 255), 1)

                    if id in speed_display:
                        speed = f'Speed: {speed_display[id]:.1f} km/h'
                        # In ra tốc độ của xe đang tracking trong vùng
                        print(f'Xe {label} ID:{id} | Speed: {speed_display[id]:.1f} km/h')
                    else:
                        speed = '--- km/h'
                    draw_text_safe(frame, speed, (int(x2) - 40, int(y2) - 8), (0, 255, 255), 2)

        # Tính toán và hiển thị FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time
        cv2.putText(frame, f'FPS: {int(fps)}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Ghi frame
        out.write(frame)

        cv2.imshow("Speed Estimate", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()