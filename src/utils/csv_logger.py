import csv
import os
import time

class CSVLogger:
    """Lớp hỗ trợ ghi nhận nhật ký vi phạm tốc độ của phương tiện ra file CSV."""
    def __init__(self, filepath="violations.csv"):
        self.filepath = filepath
        
        # Tạo thư mục chứa nếu chưa tồn tại
        dir_name = os.path.dirname(filepath)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
            
        # Nếu file chưa tồn tại hoặc rỗng, khởi tạo hàng tiêu đề (Header)
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            with open(filepath, mode='w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["id xe", "nhãn xe", "thời gian"])

    def log_violation(self, vehicle_id, label, current_time_sec, source_type):
        """
        Ghi nhận một phương tiện vi phạm mới.
        - Tránh trùng lặp được quản lý ở luồng ngoài (qua set tracking).
        - Định dạng thời gian dựa vào kiểu nguồn đầu vào.
        """
        if "Camera" in source_type or "RTSP" in source_type or source_type == "webcam":
            # Ghi thời gian thực tế của hệ thống
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        else:
            # Ghi thời gian tương đối tính bằng giây của video
            time_str = f"{current_time_sec:.1f}s"
            
        with open(self.filepath, mode='a', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([vehicle_id, label, time_str])
