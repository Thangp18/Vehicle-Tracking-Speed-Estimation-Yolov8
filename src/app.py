import streamlit as st
import cv2
import tempfile
import yaml
import numpy as np
import time
from ultralytics import YOLO

# Import các biến và lớp từ file main.py
from implement.main import SpeedEstimator, draw_text_safe, MODEL_PATH, YAML_PATH, SRC_PTS, REAL_WIDTH, REAL_LENGTH

# Cấu hình giao diện Streamlit
st.set_page_config(page_title="Speed Estimation", layout="wide")

st.title("🚗 Nhận diện và Ước tính Tốc độ Phương tiện")
st.markdown("Tải lên một video để hệ thống nhận diện và tính toán tốc độ trực tiếp trên trình duyệt.")

# Cho phép người dùng tải file lên
uploaded_file = st.file_uploader("Chọn video (mp4, avi)", type=['mp4', 'avi', 'mov'])

if uploaded_file is not None:
    # Lưu video tải lên vào một file tạm
    tfile = tempfile.NamedTemporaryFile(delete=False) 
    tfile.write(uploaded_file.read())
    video_path = tfile.name

    # Hiển thị nút bắt đầu xử lý
    if st.button("Bắt đầu xử lý", use_container_width=True):
        st.info("Đang khởi tạo mô hình... Vui lòng đợi!")
        
        # 1. Tải cấu hình và mô hình YOLO
        with open(YAML_PATH) as f:
            classes = yaml.safe_load(f)['names']
        model = YOLO(MODEL_PATH)
        
        # 2. Khởi tạo VideoCapture và Estimator
        cap = cv2.VideoCapture(video_path)
        width, height = 640, 640
        estimator = SpeedEstimator(SRC_PTS, REAL_WIDTH, REAL_LENGTH)
        
        # Khung trống để hiển thị frame liên tục
        stframe = st.empty()
        prev_time = time.time()
        
        # 3. Vòng lặp xử lý video
        while cap.isOpened():
            flag, frame = cap.read()
            if not flag:
                break
                
            current_time_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            frame = cv2.resize(frame, (width, height))
            
            # Xóa các xe cũ và vẽ vùng Homography
            estimator.cleanup(current_time_sec)
            cv2.polylines(frame, [np.int32(SRC_PTS)], isClosed=True, color=(0, 255, 255), thickness=2)

            # Tracking với YOLOv8
            results = model.track(frame, persist=True, verbose=False)
            
            if results[0].boxes is not None and results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                ids = results[0].boxes.id.cpu().numpy().astype(int)
                cls_ids = results[0].boxes.cls.cpu().numpy().astype(int)

                for box, obj_id, cls_id in zip(boxes, ids, cls_ids):
                    x1, y1, x2, y2 = box
                    xcenter, bottom_y = int((x1 + x2) / 2), int(y2)
                    
                    # Kiểm tra xem xe có nằm trong vùng đo không
                    if cv2.pointPolygonTest(np.int32(SRC_PTS), (xcenter, bottom_y), False) >= 0:
                        label = classes[cls_id]
                        current_speed = estimator.update_and_get_speed(obj_id, label, (xcenter, bottom_y), current_time_sec)

                        # Vẽ bounding box và điểm đáy
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                        cv2.circle(frame, (xcenter, bottom_y), 4, (0, 0, 255), -1)
                        draw_text_safe(frame, f'{label} ID:{obj_id}', (int(x1), int(y1) - 10), (255, 255, 255), 1)
                        
                        # Vẽ tốc độ
                        speed_str = f'Speed: {current_speed:.1f} km/h' if current_speed is not None else '--- km/h'
                        draw_text_safe(frame, speed_str, (int(x2) - 40, int(y2) - 8), (0, 255, 255), 2)

            # Tính toán và vẽ FPS
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time
            cv2.putText(frame, f'FPS: {int(fps)}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Đẩy frame lên giao diện Streamlit thay vì dùng cv2.imshow
            stframe.image(frame, channels="BGR", use_column_width=True)

        cap.release()
        estimator.final_cleanup()
        st.success("Hoàn tất xử lý video!")
