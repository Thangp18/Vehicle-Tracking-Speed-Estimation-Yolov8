import streamlit as st
import cv2
import tempfile
import yaml
import numpy as np
import time
import pandas as pd
from ultralytics import YOLO

# Import các biến và lớp từ file main.py
from implement.main import (
    SpeedEstimator, draw_text_safe,
    MODEL_PATH, YAML_PATH, SRC_PTS, REAL_WIDTH, REAL_LENGTH
)

# ---------------------------------------------------------------------------
# Cấu hình trang
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Vehicle Speed Estimation",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------------
# CSS – Dark theme + Glassmorphism
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ===== Global ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f1117 0%, #1a1d2e 50%, #0d1b2a 100%);
    color: #e2e8f0;
}

/* ===== Header gradient banner ===== */
.hero-banner {
    background: linear-gradient(135deg, #1e3a5f 0%, #0d2137 40%, #162032 100%);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(56,189,248,0.08) 0%, transparent 70%);
}
.hero-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #38bdf8, #818cf8, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 8px 0;
}
.hero-subtitle {
    color: #94a3b8;
    font-size: 0.95rem;
    margin: 0;
}

/* ===== Metric cards ===== */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 20px;
}
.metric-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 20px 18px;
    text-align: center;
    transition: border-color 0.3s;
}
.metric-card:hover { border-color: rgba(56,189,248,0.3); }
.metric-icon { font-size: 1.6rem; margin-bottom: 6px; }
.metric-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: #38bdf8;
    line-height: 1.1;
}
.metric-label {
    font-size: 0.72rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
}

/* ===== Video frame container ===== */
.video-container {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 12px;
}

/* ===== Status badge ===== */
.status-running {
    display: inline-block;
    background: rgba(52,211,153,0.15);
    color: #34d399;
    border: 1px solid rgba(52,211,153,0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.82rem;
    font-weight: 600;
}
.status-stopped {
    display: inline-block;
    background: rgba(248,113,113,0.15);
    color: #f87171;
    border: 1px solid rgba(248,113,113,0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.82rem;
    font-weight: 600;
}
.status-idle {
    display: inline-block;
    background: rgba(148,163,184,0.1);
    color: #94a3b8;
    border: 1px solid rgba(148,163,184,0.2);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.82rem;
    font-weight: 600;
}

/* ===== Sidebar ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] .stSlider > div { color: #e2e8f0; }

/* ===== Buttons ===== */
.stButton > button {
    width: 100%;
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 12px 0;
    border: none;
    transition: all 0.25s ease;
}
div[data-testid="stButton"]:first-of-type > button {
    background: linear-gradient(135deg, #0ea5e9, #6366f1);
    color: white;
}
div[data-testid="stButton"]:first-of-type > button:hover {
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(14,165,233,0.35);
}

/* ===== Dataframe ===== */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* ===== Divider ===== */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* ===== Hide Streamlit branding ===== */
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Màu bounding box theo loại xe
# ---------------------------------------------------------------------------
CLASS_COLORS = {
    "xe buyt": (255, 165,   0),   # cam
    "xe hoi":  (  0, 200, 100),   # xanh lá
    "xe may":  ( 30, 144, 255),   # xanh dương
    "xe tai":  (220,  50,  50),   # đỏ
}
DEFAULT_COLOR = (128, 0, 255)  # tím cho class không xác định


def get_class_color(label: str):
    return CLASS_COLORS.get(label.lower(), DEFAULT_COLOR)


# ---------------------------------------------------------------------------
# Session State khởi tạo
# ---------------------------------------------------------------------------
if "running" not in st.session_state:
    st.session_state["running"] = False
if "speed_log" not in st.session_state:
    st.session_state["speed_log"] = []   # list of {id, label, max_speed}
if "stats" not in st.session_state:
    st.session_state["stats"] = {
        "total_vehicles": 0,
        "avg_speed": 0.0,
        "max_speed": 0.0,
        "fps": 0.0,
    }

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 12px 0 4px;'>
        <div style='font-size:2.5rem'>🚗</div>
        <div style='font-weight:700; font-size:1rem; color:#38bdf8'>Speed Estimator</div>
        <div style='font-size:0.75rem; color:#475569'>YOLOv8 + Homography</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**📂 Nguồn đầu vào**")
    source_type = st.radio(
        "Chọn nguồn:",
        ("Video", "Camera (Webcam)"),
        label_visibility="collapsed"
    )

    video_path = None
    if source_type == "Video":
        uploaded_file = st.file_uploader(
            "Tải lên video", type=["mp4", "avi", "mov"],
            help="Hỗ trợ mp4, avi, mov"
        )
        if uploaded_file is not None:
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(uploaded_file.read())
            video_path = tfile.name
    else:
        camera_id = st.number_input("Camera ID", min_value=0, max_value=5, value=0, step=1)
        video_path = int(camera_id)

    st.markdown("---")
    st.markdown("**⚙️ Tham số xử lý**")

    conf_threshold = st.slider(
        "Confidence Threshold", min_value=0.1, max_value=0.9,
        value=0.35, step=0.05,
        help="Ngưỡng tin cậy tối thiểu để chấp nhận detection"
    )
    frame_size = st.select_slider(
        "Kích thước khung (px)", options=[480, 640, 720], value=640,
        help="Kích thước resize frame trước khi xử lý"
    )
    cleanup_time = st.slider(
        "Cleanup Time (giây)", min_value=1.0, max_value=6.0,
        value=2.0, step=0.5,
        help="Thời gian chờ trước khi xóa xe khỏi bộ nhớ"
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
        st.session_state["stats"] = {
            "total_vehicles": 0, "avg_speed": 0.0,
            "max_speed": 0.0, "fps": 0.0,
        }

    if stop_btn:
        st.session_state["running"] = False

# ---------------------------------------------------------------------------
# Main Area – Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <p class="hero-title">🚗 Vehicle Speed Estimation System</p>
    <p class="hero-subtitle">
        Nhận diện & theo dõi phương tiện theo thời gian thực với <strong>YOLOv8</strong>
        và ước tính tốc độ qua thuật toán <strong>Homography</strong>.
        Thiết lập tham số tại sidebar rồi nhấn <em>Bắt đầu</em>.
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Metric Cards
# ---------------------------------------------------------------------------
stats = st.session_state["stats"]

metric_html = f"""
<div class="metric-grid">
    <div class="metric-card">
        <div class="metric-icon">🚘</div>
        <div class="metric-value">{stats['total_vehicles']}</div>
        <div class="metric-label">Tổng xe phát hiện</div>
    </div>
    <div class="metric-card">
        <div class="metric-icon">📊</div>
        <div class="metric-value">{stats['avg_speed']:.1f} <span style='font-size:1rem;color:#94a3b8'>km/h</span></div>
        <div class="metric-label">Tốc độ trung bình</div>
    </div>
    <div class="metric-card">
        <div class="metric-icon">🏎️</div>
        <div class="metric-value">{stats['max_speed']:.1f} <span style='font-size:1rem;color:#94a3b8'>km/h</span></div>
        <div class="metric-label">Tốc độ cao nhất</div>
    </div>
    <div class="metric-card">
        <div class="metric-icon">⚡</div>
        <div class="metric-value">{stats['fps']:.1f}</div>
        <div class="metric-label">FPS xử lý</div>
    </div>
</div>
"""
metric_placeholder = st.empty()
metric_placeholder.markdown(metric_html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Status + Progress
# ---------------------------------------------------------------------------
status_placeholder = st.empty()
progress_placeholder = st.empty()

# ---------------------------------------------------------------------------
# Video display
# ---------------------------------------------------------------------------
st.markdown('<div class="video-container">', unsafe_allow_html=True)
stframe = st.empty()
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Speed history table placeholder (hiển thị sau khi xong)
# ---------------------------------------------------------------------------
table_placeholder = st.empty()

# ---------------------------------------------------------------------------
# Hiển thị bảng lịch sử nếu đã có dữ liệu từ lần chạy trước
# ---------------------------------------------------------------------------
if st.session_state["speed_log"] and not st.session_state["running"]:
    df = pd.DataFrame(st.session_state["speed_log"])
    df = df.sort_values("max_speed", ascending=False).reset_index(drop=True)
    df.index += 1
    df.columns = ["ID xe", "Loại xe", "Tốc độ tối đa (km/h)"]
    table_placeholder.dataframe(
        df.style.format({"Tốc độ tối đa (km/h)": "{:.1f}"}),
        use_container_width=True
    )

# ---------------------------------------------------------------------------
# Vòng lặp xử lý chính
# ---------------------------------------------------------------------------
if st.session_state["running"]:
    if video_path is None and source_type == "Video":
        st.warning("⚠️ Vui lòng tải lên một video trước khi bắt đầu!")
        st.session_state["running"] = False
    else:
        status_placeholder.markdown(
            '<span class="status-running">● Đang xử lý…</span>',
            unsafe_allow_html=True
        )

        with st.spinner("Đang khởi tạo mô hình…"):
            try:
                with open(YAML_PATH) as f:
                    classes = yaml.safe_load(f)["names"]
                model = YOLO(MODEL_PATH)
            except Exception as e:
                st.error(f"❌ Lỗi khi tải mô hình: {e}")
                st.session_state["running"] = False
                st.stop()

            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                st.error("❌ Không thể mở nguồn video/camera.")
                st.session_state["running"] = False
                st.stop()

        # --- Thông tin video ---
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
        frame_w = frame_size
        frame_h = frame_size

        estimator = SpeedEstimator(SRC_PTS, REAL_WIDTH, REAL_LENGTH)

        # Override cleanup time từ sidebar
        import implement.main as _main_module
        _main_module.CLEANUP_TIME = cleanup_time

        # Theo dõi thống kê
        all_speeds: list[float] = []
        seen_ids: set = set()
        frame_idx = 0
        fps_timer = time.time()

        # ---------------------------------------------------------------------------
        # Vòng lặp frame
        # ---------------------------------------------------------------------------
        while cap.isOpened() and st.session_state["running"]:
            flag, frame = cap.read()
            if not flag:
                break

            frame_idx += 1

            # --- Thời gian ---
            if source_type == "Camera (Webcam)":
                current_time_sec = time.time()
            else:
                current_time_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

            # --- Resize ---
            frame = cv2.resize(frame, (frame_w, frame_h))

            # --- Cleanup + vẽ vùng đo ---
            estimator.cleanup(current_time_sec)
            cv2.polylines(
                frame, [np.int32(SRC_PTS)],
                isClosed=True, color=(0, 255, 255), thickness=2
            )

            # --- YOLO Tracking ---
            results = model.track(
                frame, persist=True, verbose=False, conf=conf_threshold
            )

            if results[0].boxes is not None and results[0].boxes.id is not None:
                boxes   = results[0].boxes.xyxy.cpu().numpy()
                ids     = results[0].boxes.id.cpu().numpy().astype(int)
                cls_ids = results[0].boxes.cls.cpu().numpy().astype(int)

                for box, obj_id, cls_id in zip(boxes, ids, cls_ids):
                    x1, y1, x2, y2 = box
                    xcenter  = int((x1 + x2) / 2)
                    bottom_y = int(y2)

                    if cv2.pointPolygonTest(
                        np.int32(SRC_PTS), (xcenter, bottom_y), False
                    ) >= 0:
                        label = classes[cls_id]
                        color = get_class_color(label)

                        current_speed = estimator.update_and_get_speed(
                            obj_id, label, (xcenter, bottom_y), current_time_sec
                        )

                        # Cập nhật thống kê
                        seen_ids.add(obj_id)
                        if current_speed is not None and current_speed > 0:
                            all_speeds.append(current_speed)

                        # --- Vẽ bounding box màu theo loại xe ---
                        cv2.rectangle(
                            frame,
                            (int(x1), int(y1)), (int(x2), int(y2)),
                            color, 2
                        )
                        # Nền nhãn
                        label_text = f"{label}  ID:{obj_id}"
                        (tw, th), _ = cv2.getTextSize(
                            label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                        )
                        ty = max(int(y1) - 10, 20)
                        cv2.rectangle(
                            frame,
                            (int(x1), ty - th - 4), (int(x1) + tw + 4, ty + 2),
                            color, -1
                        )
                        cv2.putText(
                            frame, label_text,
                            (int(x1) + 2, ty),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
                        )

                        # Tốc độ
                        cv2.circle(frame, (xcenter, bottom_y), 4, (0, 0, 255), -1)
                        speed_str = (
                            f"{current_speed:.1f} km/h"
                            if current_speed is not None else "--- km/h"
                        )
                        draw_text_safe(
                            frame, speed_str,
                            (int(x2) - 60, int(y2) - 8),
                            (0, 255, 255), 2
                        )

            # --- Tính FPS ---
            elapsed = time.time() - fps_timer
            fps_val  = 1.0 / elapsed if elapsed > 0 else 0.0
            fps_timer = time.time()

            avg_spd = float(np.mean(all_speeds)) if all_speeds else 0.0
            max_spd = float(max(all_speeds))     if all_speeds else 0.0

            # Cập nhật session state stats
            st.session_state["stats"] = {
                "total_vehicles": len(seen_ids),
                "avg_speed":      avg_spd,
                "max_speed":      max_spd,
                "fps":            fps_val,
            }

            # --- Cập nhật metric cards ---
            metric_placeholder.markdown(f"""
<div class="metric-grid">
    <div class="metric-card">
        <div class="metric-icon">🚘</div>
        <div class="metric-value">{len(seen_ids)}</div>
        <div class="metric-label">Tổng xe phát hiện</div>
    </div>
    <div class="metric-card">
        <div class="metric-icon">📊</div>
        <div class="metric-value">{avg_spd:.1f} <span style='font-size:1rem;color:#94a3b8'>km/h</span></div>
        <div class="metric-label">Tốc độ trung bình</div>
    </div>
    <div class="metric-card">
        <div class="metric-icon">🏎️</div>
        <div class="metric-value">{max_spd:.1f} <span style='font-size:1rem;color:#94a3b8'>km/h</span></div>
        <div class="metric-label">Tốc độ cao nhất</div>
    </div>
    <div class="metric-card">
        <div class="metric-icon">⚡</div>
        <div class="metric-value">{fps_val:.1f}</div>
        <div class="metric-label">FPS xử lý</div>
    </div>
</div>
""", unsafe_allow_html=True)

            # --- Progress bar (chỉ khi có tổng frames) ---
            if total_frames > 0 and source_type == "Video":
                pct = min(frame_idx / total_frames, 1.0)
                progress_placeholder.progress(
                    pct,
                    text=f"Frame {frame_idx}/{total_frames} — {pct*100:.1f}%"
                )

            # --- Hiển thị frame ---
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            stframe.image(frame_rgb, channels="RGB", use_container_width=True)

        # --- Kết thúc vòng lặp ---
        cap.release()

        # Thu thập speed log từ estimator
        speed_log = []
        for vid, spd in estimator.max_speed.items():
            lbl = estimator.labels.get(vid, "Unknown")
            speed_log.append({"id": vid, "label": lbl, "max_speed": spd})
        estimator.final_cleanup()

        # Lưu vào session state
        st.session_state["speed_log"] = speed_log
        st.session_state["running"]   = False

        progress_placeholder.empty()
        status_placeholder.markdown(
            '<span class="status-stopped">✔ Hoàn tất xử lý</span>',
            unsafe_allow_html=True
        )

        # --- Bảng kết quả ---
        if speed_log:
            st.markdown("---")
            st.markdown("### 📋 Bảng tốc độ tối đa từng xe")
            df = pd.DataFrame(speed_log)
            df = df.sort_values("max_speed", ascending=False).reset_index(drop=True)
            df.index += 1
            df.columns = ["ID xe", "Loại xe", "Tốc độ tối đa (km/h)"]
            table_placeholder.dataframe(
                df.style.format({"Tốc độ tối đa (km/h)": "{:.1f}"}),
                use_container_width=True
            )
        else:
            st.info("Không có dữ liệu tốc độ xe nào được ghi nhận trong vùng đo.")

else:
    # Trạng thái idle
    status_placeholder.markdown(
        '<span class="status-idle">○ Chờ bắt đầu</span>',
        unsafe_allow_html=True
    )
    stframe.markdown("""
    <div style="
        height: 360px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #334155;
        border: 2px dashed #1e293b;
        border-radius: 12px;
        gap: 12px;
    ">
        <div style="font-size: 3rem">📹</div>
        <div style="font-size: 1rem; font-weight: 600">Chọn nguồn video và nhấn Bắt đầu</div>
        <div style="font-size: 0.8rem; color: #475569">Video sẽ xuất hiện tại đây</div>
    </div>
    """, unsafe_allow_html=True)
