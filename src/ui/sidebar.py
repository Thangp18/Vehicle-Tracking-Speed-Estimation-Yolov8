import streamlit as st
import cv2
import numpy as np
import tempfile
import yaml
import os

def preview_roi(video_source, points, frame_size):
    """Đọc frame đầu tiên và vẽ vùng đo để người dùng xem trước"""
    if video_source is None:
        return None
    try:
        if isinstance(video_source, str) and video_source.isdigit():
            cap_source = int(video_source)
        else:
            cap_source = video_source
        
        cap = cv2.VideoCapture(cap_source)
        if not cap.isOpened():
            return None
        flag, frame = cap.read()
        cap.release()
        
        if not flag or frame is None:
            return None
            
        frame = cv2.resize(frame, (frame_size, frame_size))
        # Vẽ đa giác vùng đo (màu vàng)
        cv2.polylines(
            frame, [np.int32(points)],
            isClosed=True, color=(0, 255, 255), thickness=2
        )
        # Vẽ các đỉnh đa giác và đánh số thứ tự
        for idx, pt in enumerate(points):
            cv2.circle(frame, (int(pt[0]), int(pt[1])), 6, (0, 0, 255), -1)
            cv2.putText(
                frame, f"P{idx+1}", (int(pt[0]) + 10, int(pt[1]) + 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
            )
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except Exception as e:
        print(f"Error in preview_roi: {e}")
        return None


def render_sidebar(CONFIG_PATH):
    st.markdown("""
    <div style='text-align:center; padding: 12px 0 4px;'>
        <div style='font-size:2.5rem'>🚗</div>
        <div style='font-weight:700; font-size:1rem; color:#38bdf8'>Speed Estimator</div>
        <div style='font-size:0.75rem; color:#475569'>YOLOv8 + Homography</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # Đọc cấu hình từ YAML nếu có
    cameras_dict = {}
    if CONFIG_PATH and os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                cameras_dict = config_data.get('cameras', {})
        except Exception as e:
            st.error(f"Lỗi đọc config YAML: {e}")

    st.markdown("**📂 Nguồn đầu vào & Cấu hình**")
    source_options = ["Tải lên Video", "Nhập RTSP URL", "Webcam ID"]
    if cameras_dict:
        source_options = [f"Camera: {cam}" for cam in cameras_dict.keys()] + source_options

    selected_source = st.selectbox(
        "Chọn cấu hình/nguồn:",
        options=source_options,
        help="Chọn camera cấu hình sẵn từ file yaml hoặc tự nhập nguồn mới"
    )

    # Các giá trị mặc định cho tham số
    default_source = None
    default_pts = [[281, 146], [179, 180], [295, 429], [556, 304]]
    default_real_width = 4.5
    default_real_length = 18.0
    default_speed_limit = 25.0

    video_path = None
    source_type = "Video"  # Dùng để quyết định cách xử lý thời gian thực

    if selected_source.startswith("Camera:"):
        cam_name = selected_source.replace("Camera: ", "")
        cam_cfg = cameras_dict.get(cam_name, {})
        default_source = cam_cfg.get("video_source", 0)
        
        cfg_pts = cam_cfg.get("src_pts", default_pts)
        if len(cfg_pts) >= 4:
            default_pts = cfg_pts[:4]
            
        default_real_width = cam_cfg.get("real_width", default_real_width)
        default_real_length = cam_cfg.get("real_length", default_real_length)
        default_speed_limit = cam_cfg.get("speed_limit", default_speed_limit)
        
        st.info(f"Đã tải cấu hình camera: {cam_name}")
        
        if isinstance(default_source, str) and not default_source.isdigit():
            video_path = default_source
            if video_path.startswith("rtsp"):
                source_type = "Camera (Webcam)"
            else:
                source_type = "Video"
        else:
            video_path = int(default_source)
            source_type = "Camera (Webcam)"
            
    elif selected_source == "Tải lên Video":
        uploaded_file = st.file_uploader(
            "Tải lên video", type=["mp4", "avi", "mov"],
            help="Hỗ trợ mp4, avi, mov"
        )
        if uploaded_file is not None:
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tfile.write(uploaded_file.read())
            video_path = tfile.name
        source_type = "Video"
        
    elif selected_source == "Nhập RTSP URL":
        rtsp_url = st.text_input("Nhập RTSP URL:", value="rtsp://")
        video_path = rtsp_url
        source_type = "Camera (Webcam)"
        
    elif selected_source == "Webcam ID":
        camera_id = st.number_input("Camera ID", min_value=0, max_value=5, value=0, step=1)
        video_path = int(camera_id)
        source_type = "Camera (Webcam)"

    st.markdown("---")

    # Kích thước khung ảnh xử lý (cần định nghĩa trước để preview_roi hoạt động chính xác)
    frame_size = st.select_slider(
        "Kích thước khung xử lý (px)", options=[480, 640, 720], value=640,
        help="Kích thước resize frame trước khi đưa vào YOLO"
    )

    # Expander Hiệu chỉnh ROI
    with st.expander("📐 Hiệu chỉnh Vùng đo (ROI)", expanded=False):
        st.write("Nhập tọa độ x, y của 4 điểm (px) ứng với khung hình kích thước trên:")
        col_roi1, col_roi2 = st.columns(2)
        with col_roi1:
            p1_x = st.number_input("P1 (TL) X", value=int(default_pts[0][0]), step=1)
            p1_y = st.number_input("P1 (TL) Y", value=int(default_pts[0][1]), step=1)
            p4_x = st.number_input("P4 (BL) X", value=int(default_pts[3][0]), step=1)
            p4_y = st.number_input("P4 (BL) Y", value=int(default_pts[3][1]), step=1)
        with col_roi2:
            p2_x = st.number_input("P2 (TR) X", value=int(default_pts[1][0]), step=1)
            p2_y = st.number_input("P2 (TR) Y", value=int(default_pts[1][1]), step=1)
            p3_x = st.number_input("P3 (BR) X", value=int(default_pts[2][0]), step=1)
            p3_y = st.number_input("P3 (BR) Y", value=int(default_pts[2][1]), step=1)

        roi_pts = np.array([[p1_x, p1_y], [p2_x, p2_y], [p3_x, p3_y], [p4_x, p4_y]], dtype=np.float32)
        
        if st.button("👁 Xem trước Vùng đo", use_container_width=True):
            if video_path is None or (isinstance(video_path, str) and video_path == "rtsp://"):
                st.warning("Vui lòng tải video hoặc cấu hình nguồn trước khi xem.")
            else:
                with st.spinner("Đang lấy frame xem trước..."):
                    img_preview = preview_roi(video_path, roi_pts, frame_size)
                    if img_preview is not None:
                        st.image(img_preview, caption="Ảnh xem trước vùng đo", use_container_width=True)
                    else:
                        st.error("Không thể lấy frame từ nguồn video này.")

    st.markdown("---")
    st.markdown("**⚙️ Tham số Ước lượng & YOLO**")

    conf_threshold = st.slider(
        "YOLO Confidence Threshold", min_value=0.1, max_value=0.9,
        value=0.35, step=0.05,
        help="Ngưỡng tin cậy tối thiểu để nhận diện vật thể"
    )
    speed_limit = st.number_input(
        "Giới hạn tốc độ (km/h)", min_value=1.0, max_value=200.0,
        value=float(default_speed_limit), step=5.0,
        help="Giới hạn tốc độ của làn đường này để phát hiện vi phạm"
    )
    real_width = st.number_input(
        "Chiều rộng đường thực tế (m)", min_value=1.0, max_value=50.0,
        value=float(default_real_width), step=0.5,
        help="Chiều rộng thực tế của đường (khoảng cách ngang thực tế trong vùng ROI)"
    )
    real_length = st.number_input(
        "Chiều dài đường thực tế (m)", min_value=1.0, max_value=200.0,
        value=float(default_real_length), step=1.0,
        help="Chiều dài thực tế của đường (khoảng cách dọc thực tế trong vùng ROI)"
    )
    cleanup_time = st.slider(
        "Cleanup Time (giây)", min_value=1.0, max_value=10.0,
        value=2.0, step=0.5,
        help="Thời gian xóa ID xe khỏi bộ nhớ sau khi xe đi khỏi khung hình"
    )
    distance_threshold = st.slider(
        "Distance Threshold (m)", min_value=0.1, max_value=5.0,
        value=0.5, step=0.1,
        help="Khoảng cách tối thiểu xe dịch chuyển để cập nhật tốc độ"
    )
    min_time_diff = st.slider(
        "Min Time Diff (giây)", min_value=0.1, max_value=2.0,
        value=0.3, step=0.1,
        help="Khoảng thời gian tối thiểu giữa 2 lần cập nhật để tính vận tốc"
    )
    
    save_output_video = st.checkbox(
        "Ghi và lưu video kết quả", value=False,
        help="Lưu lại video đã xử lý để tải xuống sau khi chạy xong"
    )

    st.markdown("---")

    col_start, col_stop = st.columns(2)
    with col_start:
        start_btn = st.button("▶ Bắt đầu", use_container_width=True)
    with col_stop:
        stop_btn = st.button("⏹ Dừng", use_container_width=True)

    if start_btn:
        st.session_state["running"] = True
        st.session_state["speed_log"] = []
        st.session_state["violation_log"] = []
        st.session_state["stats"] = {
            "total_vehicles": 0, "avg_speed": 0.0,
            "max_speed": 0.0, "fps": 0.0,
        }
        st.session_state["output_video_path"] = None

    if stop_btn:
        st.session_state["running"] = False
        
    return {
        "video_path": video_path,
        "source_type": source_type,
        "frame_size": frame_size,
        "roi_pts": roi_pts,
        "conf_threshold": conf_threshold,
        "speed_limit": speed_limit,
        "real_width": real_width,
        "real_length": real_length,
        "cleanup_time": cleanup_time,
        "distance_threshold": distance_threshold,
        "min_time_diff": min_time_diff,
        "save_output_video": save_output_video
    }
