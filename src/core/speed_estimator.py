import cv2
import numpy as np
import math
from collections import deque

class SpeedEstimator:
    """Lớp quản lý trạng thái theo dõi và tính toán tốc độ của các xe."""
    def __init__(self, src_pts, real_width, real_length, speed_limit=25.0, width=640, height=640, cleanup_time=2.0, distance_threshold=0.5, min_time_diff=0.3):
        pts = list(src_pts)
        pts.sort(key=lambda p: p[1])
        top_two = sorted(pts[:2], key=lambda p: p[0])
        bottom_two = sorted(pts[2:], key=lambda p: p[0])
        
        self.src_pts = np.array([top_two[0], top_two[1], bottom_two[1], bottom_two[0]], dtype=np.float32)# xếp theo chiều kim đồng hồ 
        self.speed_limit = speed_limit
        self.cleanup_time = cleanup_time
        self.distance_threshold = distance_threshold
        self.min_time_diff = min_time_diff

        dst_pts = np.array([
            [0, 0], [real_width, 0], [real_width, real_length], [0, real_length]
        ], dtype=np.float32)
        self.H, _ = cv2.findHomography(self.src_pts, dst_pts)

        self.history = {}
        self.speed_display = {}
        self.max_speed = {}
        self.last_seen = {}
        self.labels = {}

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

        if vehicle_id not in self.history:
            self.history[vehicle_id] = deque(maxlen=100)
            self.history[vehicle_id].append((real_x, real_y, current_time))
            return None

        history = self.history[vehicle_id]
        
        # Tìm điểm cũ nhất trong lịch sử đạt tối thiểu min_time_diff
        old_x, old_y, old_time = None, None, None
        for i in range(len(history) - 1, -1, -1):
            x, y, t = history[i]
            if current_time - t >= self.min_time_diff:
                old_x, old_y, old_time = x, y, t
                break

        if old_time is not None:
            time_diff = current_time - old_time
            distance = math.hypot(real_x - old_x, real_y - old_y)
            speed_kmph = 0.0 if distance < self.distance_threshold else (distance / time_diff) * 3.6
            
            current_speed = self.speed_display.get(vehicle_id, speed_kmph)
            smoothed_speed = 0.7 * current_speed + 0.3 * speed_kmph
            self.speed_display[vehicle_id] = smoothed_speed
            
            if smoothed_speed > self.max_speed.get(vehicle_id, 0):
                self.max_speed[vehicle_id] = smoothed_speed
                
        history.append((real_x, real_y, current_time))
        return self.speed_display.get(vehicle_id)

    def cleanup(self, current_time):
        """Xoá các xe đã ra khỏi khung hình và chỉ in tốc độ nếu vượt speed limit"""
        expired_ids = [k for k, v in self.last_seen.items() if current_time - v > self.cleanup_time]
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

    def final_cleanup(self):
        """Called when video/stream is finished to flush remaining items"""
        pass
