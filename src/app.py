import os
import streamlit as st
import cv2
import yaml
import numpy as np
import time
import tempfile
import pandas as pd
from ultralytics import YOLO

from main import MODEL_PATH, YAML_PATH, SRC_PTS, REAL_WIDTH, REAL_LENGTH
from core.speed_estimator import SpeedEstimator
from utils.drawing_utils import draw_text_safe
from utils.video_stream import VideoStream

from ui.styles import apply_custom_css, get_class_color
from ui.sidebar import render_sidebar
from ui.dashboard import (
    render_header, render_status, render_metrics_row,
    render_violations_realtime, render_violations_history,
    render_idle_screen, render_results_tabs
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
apply_custom_css()

# ---------------------------------------------------------------------------
# Tìm file config camera
# ---------------------------------------------------------------------------
CONFIG_PATH = None
possible_paths = [
    os.path.join(os.path.dirname(__file__), "..", "..", "cameras_config.yaml"),
    os.path.join(os.path.dirname(__file__), "..", "cameras_config.yaml"),
    os.path.join(os.path.dirname(__file__), "cameras_config.yaml"),
    "cameras_config.yaml"
]
for p in possible_paths:
    if os.path.exists(p):
        CONFIG_PATH = os.path.abspath(p)
        break

# ---------------------------------------------------------------------------
# Session State khởi tạo
# ---------------------------------------------------------------------------
if "running" not in st.session_state:
    st.session_state["running"] = False
if "speed_log" not in st.session_state:
    st.session_state["speed_log"] = []
if "violation_log" not in st.session_state:
    st.session_state["violation_log"] = []
if "stats" not in st.session_state:
    st.session_state["stats"] = {
        "total_vehicles": 0, "avg_speed": 0.0,
        "max_speed": 0.0, "fps": 0.0, "violations": 0,
    }
if "output_video_path" not in st.session_state:
    st.session_state["output_video_path"] = None

# ---------------------------------------------------------------------------
# Rendering Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    sidebar_params = render_sidebar(CONFIG_PATH)

# Extract params
video_path = sidebar_params["video_path"]
source_type = sidebar_params["source_type"]
frame_size = sidebar_params["frame_size"]
roi_pts = sidebar_params["roi_pts"]
conf_threshold = sidebar_params["conf_threshold"]
speed_limit = sidebar_params["speed_limit"]
real_width = sidebar_params["real_width"]
real_length = sidebar_params["real_length"]
cleanup_time = sidebar_params["cleanup_time"]
distance_threshold = sidebar_params["distance_threshold"]
min_time_diff = sidebar_params["min_time_diff"]
save_output_video = sidebar_params["save_output_video"]
csv_output_path = sidebar_params["csv_output_path"]

# ---------------------------------------------------------------------------
# Main Area
# ---------------------------------------------------------------------------
render_header()

status_placeholder = st.empty()
progress_placeholder = st.empty()

# Metric row — 5 cards ngang (phía trên video)
metrics_row_placeholder = st.empty()
render_metrics_row(metrics_row_placeholder, st.session_state["stats"])

# Video + Violations layout
col_video_main, col_violations_main = st.columns([7, 3])

with col_video_main:
    st.markdown('<div class="video-container">', unsafe_allow_html=True)
    stframe = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

with col_violations_main:
    violation_title_placeholder = st.empty()
    violation_placeholder = st.empty()

st.markdown("---")

# Results section — Tabbed
results_container = st.container()

# ---------------------------------------------------------------------------
# Xử lý Logic
# ---------------------------------------------------------------------------
if st.session_state["running"]:
    if video_path is None or (isinstance(video_path, str) and video_path == "rtsp://"):
        st.warning("⚠️ Vui lòng cấu hình nguồn video/camera trước khi bắt đầu!")
        st.session_state["running"] = False
        st.stop()
    else:
        render_status(status_placeholder, "running")

        with st.spinner("Đang khởi tạo mô hình…"):
            try:
                with open(YAML_PATH) as f:
                    classes = yaml.safe_load(f)["names"]
                model = YOLO(MODEL_PATH)
            except Exception as e:
                st.error(f"❌ Lỗi khi tải mô hình: {e}")
                st.session_state["running"] = False
                st.stop()

            if isinstance(video_path, str) and video_path.isdigit():
                cap_source = int(video_path)
            else:
                cap_source = video_path

            if source_type == "Camera (Webcam)":
                cap = VideoStream(cap_source).start()
            else:
                cap = cv2.VideoCapture(cap_source)

            if not cap.isOpened():
                st.error("❌ Không thể mở nguồn video/camera.")
                st.session_state["running"] = False
                st.stop()

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
        frame_w = frame_size
        frame_h = frame_size

        out = None
        if save_output_video:
            try:
                temp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                temp_out_path = temp_out.name
                temp_out.close()
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                fps_video = int(cap.get(cv2.CAP_PROP_FPS)) or 30
                out = cv2.VideoWriter(temp_out_path, fourcc, fps_video, (frame_w, frame_h))
                st.session_state["output_video_path"] = temp_out_path
            except Exception as e:
                st.warning(f"Không thể khởi tạo bộ ghi video: {e}")
                out = None

        estimator = SpeedEstimator(
            src_pts=roi_pts, real_width=real_width, real_length=real_length,
            speed_limit=speed_limit, width=frame_w, height=frame_h,
            cleanup_time=cleanup_time, distance_threshold=distance_threshold,
            min_time_diff=min_time_diff
        )

        all_speeds = []
        seen_ids = set()
        frame_idx = 0
        fps_timer = time.time()
        violation_tracker = {}
        
        from utils.csv_logger import CSVLogger
        csv_logger = CSVLogger(csv_output_path)
        logged_violations = set()

        while cap.isOpened() and st.session_state["running"]:
            flag, frame = cap.read()
            if not flag or frame is None:
                if source_type == "Camera (Webcam)":
                    time.sleep(0.01)
                    continue
                else:
                    break

            frame_idx += 1

            if source_type == "Camera (Webcam)":
                current_time_sec = time.time()
            else:
                current_time_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

            frame = cv2.resize(frame, (frame_w, frame_h))
            estimator.cleanup(current_time_sec)
            cv2.polylines(
                frame, [np.int32(roi_pts)],
                isClosed=True, color=(0, 255, 255), thickness=2
            )

            results = model.track(frame, persist=True, verbose=False, conf=conf_threshold)

            if results[0].boxes is not None and results[0].boxes.id is not None:
                boxes   = results[0].boxes.xyxy.cpu().numpy()
                ids     = results[0].boxes.id.cpu().numpy().astype(int)
                cls_ids = results[0].boxes.cls.cpu().numpy().astype(int)

                for box, obj_id, cls_id in zip(boxes, ids, cls_ids):
                    x1, y1, x2, y2 = box
                    xcenter  = int((x1 + x2) / 2)
                    bottom_y = int(y2)

                    if cv2.pointPolygonTest(np.int32(roi_pts), (xcenter, bottom_y), False) >= 0:
                        label = classes[cls_id]
                        current_speed = estimator.update_and_get_speed(obj_id, label, (xcenter, bottom_y), current_time_sec)

                        seen_ids.add(obj_id)
                        if current_speed is not None and current_speed > 0:
                            all_speeds.append(current_speed)
                            
                            if current_speed > speed_limit:
                                color = (100, 100, 255)
                                speed_color = (100, 100, 255)
                                if obj_id not in violation_tracker:
                                    if source_type == "Camera (Webcam)":
                                        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time_sec))
                                    else:
                                        time_str = f"{current_time_sec:.1f}s"
                                    violation_tracker[obj_id] = {
                                        "ID xe": obj_id,
                                        "Loại xe": label.capitalize(),
                                        "Tốc độ vi phạm (km/h)": current_speed,
                                        "Thời điểm": time_str
                                    }
                                    if obj_id not in logged_violations:
                                        csv_logger.log_violation(obj_id, label, current_time_sec, source_type)
                                        logged_violations.add(obj_id)
                                else:
                                    if current_speed > violation_tracker[obj_id]["Tốc độ vi phạm (km/h)"]:
                                        violation_tracker[obj_id]["Tốc độ vi phạm (km/h)"] = current_speed
                            else:
                                color = (100, 255, 100)
                                speed_color = (100, 255, 100)
                        else:
                            color = (100, 255, 100)
                            speed_color = (100, 255, 100)

                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                        
                        label_text = f"{label} ID:{obj_id}"
                        (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                        ty = max(int(y1) - 10, 20)
                        cv2.rectangle(frame, (int(x1), ty - th - 4), (int(x1) + tw + 4, ty + 2), color, -1)
                        cv2.putText(frame, label_text, (int(x1) + 2, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                        cv2.circle(frame, (xcenter, bottom_y), 4, color, -1)
                        speed_str = f"{current_speed:.1f} km/h" if current_speed is not None else "--- km/h"
                        draw_text_safe(frame, speed_str, (int(x2) - 60, int(y2) - 8), speed_color, 2)

            if out is not None:
                out.write(frame)

            elapsed = time.time() - fps_timer
            fps_val  = 1.0 / elapsed if elapsed > 0 else 0.0
            fps_timer = time.time()

            # --- OPTIMIZE STREAMLIT RENDERING ---
            # Update UI elements only every 3 frames to drastically reduce WebSocket/DOM overhead,
            # while keeping full frame processing speed.
            UI_UPDATE_INTERVAL = 3
            if frame_idx % UI_UPDATE_INTERVAL == 0:
                avg_spd = float(np.mean(all_speeds)) if all_speeds else 0.0
                max_spd = float(max(all_speeds))     if all_speeds else 0.0

                st.session_state["stats"] = {
                    "total_vehicles": len(seen_ids),
                    "avg_speed":      avg_spd,
                    "max_speed":      max_spd,
                    "fps":            fps_val,
                    "violations":     len(violation_tracker),
                }

                render_metrics_row(metrics_row_placeholder, st.session_state["stats"])
                render_violations_realtime(violation_title_placeholder, violation_placeholder, violation_tracker, speed_limit)

                if total_frames > 0 and source_type == "Video":
                    pct = min(frame_idx / total_frames, 1.0)
                    progress_placeholder.progress(pct, text=f"Frame {frame_idx}/{total_frames} — {pct*100:.1f}%")

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                stframe.image(frame_rgb, channels="RGB", width='stretch')

            # Release GIL for 2ms to let Tornado web server transfer websocket packets smoothly
            time.sleep(0.002)

        if source_type == "Camera (Webcam)":
            cap.stop()
        else:
            cap.release()
        if out is not None:
            out.release()

        speed_log = []
        for vid, spd in estimator.max_speed.items():
            lbl = estimator.labels.get(vid, "Unknown")
            speed_log.append({"id": vid, "label": lbl, "max_speed": spd})
        estimator.final_cleanup()

        st.session_state["speed_log"] = speed_log
        st.session_state["violation_log"] = list(violation_tracker.values())
        st.session_state["running"]   = False

        progress_placeholder.empty()
        render_status(status_placeholder, "stopped")
        
        try:
            st.rerun()
        except AttributeError:
            st.experimental_rerun()

else:
    render_status(status_placeholder, "idle")
    render_idle_screen(stframe)
    render_metrics_row(metrics_row_placeholder, st.session_state["stats"])
    render_violations_history(
        violation_title_placeholder, violation_placeholder,
        st.session_state.get("violation_log", []), speed_limit
    )
    
    with results_container:
        render_results_tabs(
            st.session_state.get("speed_log", []),
            st.session_state.get("violation_log", []),
            st.session_state.get("output_video_path"),
            speed_limit
        )
