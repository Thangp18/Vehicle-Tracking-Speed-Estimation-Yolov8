import cv2
import numpy as np
from ultralytics import YOLO
import yaml
import math
import time
from collections import deque
import os
import argparse

#highway
# line1= [(250, 79), (445, 82)]
# line2= [(94, 342), (597, 354)]
#vidtest
# line1= [(6, 242), (476, 280)]
# line2= [(516, 407), (2, 373)]
#test
# line1= [(307, 342), (622, 342)]
# line2= [(400, 226), (185, 226)]
#OQ
# [191, 122], [69, 161], [295, 531], [624, 317]
# KQ
# [281, 146], [179, 180], [295, 429], [556, 304]

# --- CẤU HÌNH ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
VIDEO_PATH = os.path.join(ROOT_DIR, "datasets", "KQAE7521.MP4")
MODEL_PATH = os.path.join(ROOT_DIR, "best_.pt")
YAML_PATH = os.path.join(ROOT_DIR, "data.yaml")

# Cấu hình vùng Homography
SRC_PTS = np.array([[281, 146], [179, 180], [295, 429], [556, 304]], dtype=np.float32)
REAL_WIDTH = 4.5
REAL_LENGTH = 18

# Tham số tính tốc độ
CLEANUP_TIME = 2.0
DISTANCE_THRESHOLD = 0.5
MIN_TIME_DIFF = 0.3
SPEED_LIMIT = 25
def args():
    parser = argparse.ArgumentParser(description='Speed Estimation and Vehicle Tracking')
    parser.add_argument('--video', '-v',type=str, default=VIDEO_PATH, help='Path to video file')
    parser.add_argument('--model', '-m', type=str, default=MODEL_PATH, help='Path to model file')
    parser.add_argument('--yaml', '-y', type=str, default=YAML_PATH, help='Path to yaml file')
    parser.add_argument('--src_pts', '-sp', type=np.array, default=SRC_PTS, help='Path to yaml file')
    parser.add_argument('--real_width', '-rw', type=float, default=REAL_WIDTH, help='Real width of the road')
    parser.add_argument('--real_length', '-rl', type=float, default=REAL_LENGTH, help='Real length of the road')
    parser.add_argument('--cleanup_time', '-ct', type=float, default=CLEANUP_TIME, help='Cleanup time')
    parser.add_argument('--distance_threshold', '-dt', type=float, default=DISTANCE_THRESHOLD, help='Distance threshold')
    parser.add_argument('--min_time_diff', '-mtd', type=float, default=MIN_TIME_DIFF, help='Min time diff')   
    parser.add_argument('--speed_limit', '-sl', type=float, default=SPEED_LIMIT, help='Speed limit')
    parser.add_argument('--output', '-o', type=str, default='output_speed.mp4', help='Path to output video file')
    parser.add_argument('--save', '-s', type=bool, default=True, help='Save output video')
    return parser.parse_args()

class SpeedEstimator:
    """Lớp quản lý trạng thái theo dõi và tính toán tốc độ của các xe."""
    def __init__(self, src_pts, real_width, real_length, speed_limit=SPEED_LIMIT):
        dst_pts = np.array([
            [0, 0], [real_width, 0], [real_width, real_length], [0, real_length]
        ], dtype=np.float32)
        self.H, _ = cv2.findHomography(src_pts, dst_pts)
        
        self.history = {}
        self.speed_display = {}
        self.max_speed = {}
        self.last_seen = {}
        self.labels = {}
        self.src_pts = src_pts
        self.speed_limit = speed_limit

    def transform_point(self, pt):
        """Chuyển đổi tọa độ pixel sang mét"""
        pt_arr = np.array([[pt]], dtype=np.float32)
        transformed = cv2.perspectiveTransform(pt_arr, self.H)[0][0]
        return transformed[0], transformed[1]

    def update_and_get_speed(self, vehicle_id, label, point, current_time):
        """Cập nhật vị trí, tính tốc độ và trả về tốc độ đã làm mượt"""
        self.last_seen[vehicle_id] = current_time
        self.labels[vehicle_id] = label
        
        real_x, real_y = self.transform_point(point)

        # Nếu là lần đầu tiên xe xuất hiện
        if vehicle_id not in self.history:
            self.history[vehicle_id] = deque(maxlen=10)
            self.history[vehicle_id].append((real_x, real_y, current_time))
            return None

        history = self.history[vehicle_id]
        old_x, old_y, old_time = history[0]
        time_diff = current_time - old_time

        if time_diff > MIN_TIME_DIFF:
            distance = math.hypot(real_x - old_x, real_y - old_y)
            speed_kmph = 0.0 if distance < DISTANCE_THRESHOLD else (distance / time_diff) * 3.6
            
            # Làm mượt tốc độ
            current_speed = self.speed_display.get(vehicle_id, speed_kmph)
            smoothed_speed = 0.7 * current_speed + 0.3 * speed_kmph
            self.speed_display[vehicle_id] = smoothed_speed
            
            # Cập nhật Max speed
            if smoothed_speed > self.max_speed.get(vehicle_id, 0):
                self.max_speed[vehicle_id] = smoothed_speed
                
        history.append((real_x, real_y, current_time))
        return self.speed_display.get(vehicle_id)

    def cleanup(self, current_time):
        """Xoá các xe đã ra khỏi khung hình và chỉ in tốc độ nếu vượt speed limit"""
        expired_ids = [k for k, v in self.last_seen.items() if current_time - v > CLEANUP_TIME]
        for k in expired_ids:
            if k in self.max_speed:
                label = self.labels.get(k, "Unknown")
                max_spd = self.max_speed[k]
                if max_spd > self.speed_limit:
                    print(f'⚠️ Xe {label} ID:{k} | Vượt tốc độ giới hạn! Max Speed: {max_spd:.1f} km/h (Limit: {self.speed_limit:.1f} km/h)')
            self.history.pop(k, None)
            self.speed_display.pop(k, None)
            self.max_speed.pop(k, None)
            self.last_seen.pop(k, None)
            self.labels.pop(k, None)

def draw_text_safe(img, text, pos, color, thickness=1):
    """Vẽ text an toàn, tránh bị khuất mép trên màn hình"""
    x, y = pos
    y = y + 30 if y < 20 else y
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)


def main(args):
    with open(YAML_PATH) as f:
        classes = yaml.safe_load(f)['names']
    print(f"Loaded classes: {classes}")

    model = YOLO(args.model)
    cap = cv2.VideoCapture(args.video)
    
    width, height = 640, 640
    fps_video = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(args.output, fourcc, fps_video, (width, height))

    estimator = SpeedEstimator(args.src_pts, args.real_width, args.real_length, args.speed_limit)
    prev_time = time.time()

    while cap.isOpened():
        flag, frame = cap.read()
        if not flag: break
            
        current_time_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        frame = cv2.resize(frame, (width, height))
        
        estimator.cleanup(current_time_sec)
        cv2.polylines(frame, [np.int32(args.src_pts)], isClosed=True, color=(0, 255, 255), thickness=2)

        results = model.track(frame, persist=True, verbose=False)
        
        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            ids = results[0].boxes.id.cpu().numpy().astype(int)
            cls_ids = results[0].boxes.cls.cpu().numpy().astype(int)

            for box, obj_id, cls_id in zip(boxes, ids, cls_ids):
                x1, y1, x2, y2 = box
                xcenter, bottom_y = int((x1 + x2) / 2), int(y2)
                
                # check xe trong vùng
                if cv2.pointPolygonTest(np.int32(args.src_pts), (xcenter, bottom_y), False) >= 0:
                    label = classes[cls_id]
                    
                    # Tính toán tốc độ
                    current_speed = estimator.update_and_get_speed(obj_id, label, (xcenter, bottom_y), current_time_sec)

                    if current_speed is not None and current_speed > args.speed_limit:
                        color = (100, 100, 255) 
                        speed_text_color = (100, 100, 255)
                    else:
                        color = (100, 255, 100)  
                        speed_text_color = (100, 255, 100) 
                    #vẽ bbox                        
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    cv2.circle(frame, (xcenter, bottom_y), 4, color, -1)
                    
                    draw_text_safe(frame, f'{label} ID:{obj_id}', (int(x1), int(y1) - 10), (100, 255, 100), 2)
                    
                    speed_str = f'Speed: {current_speed:.1f} km/h' if current_speed is not None else '--- km/h'
                    draw_text_safe(frame, speed_str, (int(x2) - 40, int(y2) - 8), speed_text_color, 2)

        out.write(frame)
        cv2.imshow("Speed Estimate", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main(args())