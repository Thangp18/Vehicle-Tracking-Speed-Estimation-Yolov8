import os
import cv2
import numpy as np
from ultralytics import YOLO
import yaml
import time
import argparse

from utils.video_stream import VideoStream
from utils.drawing_utils import draw_text_safe
from core.speed_estimator import SpeedEstimator

# --- CẤU HÌNH ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CAMERA_SOURCE = 0
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

def args_parser():
    parser = argparse.ArgumentParser(description='Speed Estimation and Vehicle Tracking from Camera')
    parser.add_argument('--config', '-c', type=str, default=None, help='Path to camera config file (YAML)')
    parser.add_argument('--camera', '-cam', type=str, default=None, help='Name of the camera to run from config')
    parser.add_argument('--source', '-src', default=CAMERA_SOURCE, help='Camera index (e.g. 0, 1) or RTSP URL')
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
    parser.add_argument('--csv', '-csv', type=str, default='violations.csv', help='Path to output CSV file for speed violations')
    return parser.parse_args()

def main(args):
    with open(args.yaml) as f:
        classes = yaml.safe_load(f)['names']
    print(f"Loaded classes: {classes}")

    model = YOLO(args.model)
    
    camera_source = args.source
    src_pts = args.src_pts
    real_width = args.real_width
    real_length = args.real_length
    speed_limit = args.speed_limit
    save_output = args.save
    output_path = args.output
    csv_output = args.csv

    if args.config and args.camera:
        if not os.path.exists(args.config):
            print(f"Error: Config file '{args.config}' not found.")
            return
        with open(args.config, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        cameras = config_data.get('cameras', {})
        if args.camera not in cameras:
            print(f"Error: Camera '{args.camera}' not found in config. Available cameras: {list(cameras.keys())}")
            return
        
        cam_cfg = cameras[args.camera]
        print(f"--> Loading configuration for camera: '{args.camera}'")
        camera_source = cam_cfg.get('video_source', camera_source)
        src_pts = np.array(cam_cfg.get('src_pts', src_pts), dtype=np.float32)
        real_width = cam_cfg.get('real_width', real_width)
        real_length = cam_cfg.get('real_length', real_length)
        speed_limit = cam_cfg.get('speed_limit', speed_limit)
        save_output = cam_cfg.get('save_output', save_output)
        output_path = cam_cfg.get('output_path', output_path)
        csv_output = cam_cfg.get('csv_output_path', csv_output)

    if isinstance(camera_source, str) and camera_source.isdigit():
        camera_source = int(camera_source)

    cap = VideoStream(camera_source).start()
    
    width, height = 640, 640
    fps_video = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    out = None
    if save_output:
        out = cv2.VideoWriter(output_path, fourcc, fps_video, (width, height))

    estimator = SpeedEstimator(
        src_pts, real_width, real_length, speed_limit, width, height, 
        args.cleanup_time, args.distance_threshold, args.min_time_diff
    )
    start_time = time.time()
    
    is_live = isinstance(camera_source, int) or (isinstance(camera_source, str) and camera_source.startswith("rtsp"))
    source_type = "Camera (Webcam)" if is_live else "Video"
    
    from utils.csv_logger import CSVLogger
    csv_logger = CSVLogger(csv_output)
    logged_violations = set()

    while cap.isOpened():
        flag, frame = cap.read()
        if not flag or frame is None: 
            continue
            
        if source_type == "Camera (Webcam)":
            current_time_sec = time.time() - start_time
        else:
            current_time_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            
        frame = cv2.resize(frame, (width, height))
        
        estimator.cleanup(current_time_sec)
        cv2.polylines(frame, [np.int32(src_pts)], isClosed=True, color=(0, 255, 255), thickness=2)

        results = model.track(frame, persist=True, verbose=False)
        
        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            ids = results[0].boxes.id.cpu().numpy().astype(int)
            cls_ids = results[0].boxes.cls.cpu().numpy().astype(int)

            for box, obj_id, cls_id in zip(boxes, ids, cls_ids):
                x1, y1, x2, y2 = box
                xcenter, bottom_y = int((x1 + x2) / 2), int(y2)
                
                if cv2.pointPolygonTest(np.int32(src_pts), (xcenter, bottom_y), False) >= 0:
                    label = classes[cls_id]
                    
                    current_speed = estimator.update_and_get_speed(obj_id, label, (xcenter, bottom_y), current_time_sec)

                    if current_speed is not None and current_speed > speed_limit:
                        color = (100, 100, 255) 
                        speed_text_color = (100, 100, 255)
                        if obj_id not in logged_violations:
                            csv_logger.log_violation(obj_id, label, current_time_sec, source_type)
                            logged_violations.add(obj_id)
                    else:
                        color = (100, 255, 100)  
                        speed_text_color = (100, 255, 100) 
                        
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    cv2.circle(frame, (xcenter, bottom_y), 4, color, -1)
                    
                    draw_text_safe(frame, f'{label} ID:{obj_id}', (int(x1), int(y1) - 10), (100, 255, 100), 2)
                    
                    speed_str = f'Speed: {current_speed:.1f} km/h' if current_speed is not None else '--- km/h'
                    draw_text_safe(frame, speed_str, (int(x2) - 40, int(y2) - 8), speed_text_color, 2)

        if out is not None:
            out.write(frame)
        cv2.imshow("Speed Estimate", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.stop()
    if out is not None:
        out.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main(args_parser())
