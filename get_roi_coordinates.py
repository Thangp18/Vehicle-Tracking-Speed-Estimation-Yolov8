import cv2
import numpy as np
import yaml
import os
import argparse

# Biến toàn cục lưu trữ các điểm được click
points = []
img_display = None
frame_original = None

def click_event(event, x, y, flags, params):
    global points, img_display, frame_original
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append([x, y])
            print(f"Điểm {len(points)}: ({x}, {y})")
            
            # Vẽ điểm vừa click (màu đỏ)
            cv2.circle(img_display, (x, y), 5, (0, 0, 255), -1)
            cv2.putText(img_display, f"P{len(points)}:({x},{y})", (x + 8, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Vẽ đường nối nếu có từ 2 điểm trở lên
            if len(points) > 1:
                cv2.line(img_display, tuple(points[-2]), tuple(points[-1]), (255, 0, 0), 2)
            
            # Khi đã chọn đủ 4 điểm, vẽ đường khép kín nối điểm cuối với điểm đầu
            if len(points) == 4:
                cv2.line(img_display, tuple(points[3]), tuple(points[0]), (255, 0, 0), 2)
                print("\n=== TOẠ ĐỘ VÙNG ROI ĐÃ CHỌN ===")
                print(f"src_pts: {points}")
                print("===============================\n")
                print("Nhấn 's' để lưu tọa độ vào cameras_config.yaml")
                print("Nhấn 'c' để xóa và chọn lại từ đầu")
                print("Nhấn 'q' để thoát")
            
            cv2.imshow("Lay toa do ROI - Click 4 diem", img_display)

def main():
    global points, img_display, frame_original
    parser = argparse.ArgumentParser(description="Công cụ lấy toạ độ 4 điểm ROI tương tác bằng chuột.")
    parser.add_argument("--source", default=None, help="Đường dẫn file video hoặc index Webcam (0, 1) hoặc đường dẫn RTSP")
    parser.add_argument("--size", type=int, default=640, help="Resize khung hình về kích thước vuông (mặc định 640)")
    args = parser.parse_args()

    # Xác định nguồn video
    source = args.source
    config_file = "cameras_config.yaml"
    
    # Nếu không truyền source, thử đọc từ file config
    if source is None:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
                cameras = config_data.get("cameras", {})
                if cameras:
                    print("Chọn camera từ config để cấu hình lại:")
                    cam_list = list(cameras.keys())
                    for idx, cam in enumerate(cam_list):
                        print(f"{idx+1}. {cam} (Nguồn: {cameras[cam].get('video_source')})")
                    choice = input("Nhập số thứ tự (hoặc nhấn Enter để tự nhập nguồn khác): ").strip()
                    if choice.isdigit() and 1 <= int(choice) <= len(cam_list):
                        selected_cam = cam_list[int(choice) - 1]
                        source = cameras[selected_cam].get('video_source')
                        print(f"--> Đang sử dụng nguồn từ camera '{selected_cam}': {source}")
            except Exception as e:
                print(f"Lỗi đọc file cấu hình: {e}")
                
    if source is None:
        source = input("Nhập đường dẫn file video hoặc RTSP URL hoặc Webcam ID (ví dụ: 0): ").strip()
        
    # Chuyển đổi Webcam ID sang số nguyên
    if isinstance(source, str) and source.isdigit():
        source = int(source)

    print(f"Đang mở nguồn video: {source} ...")
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print("❌ Lỗi: Không thể mở nguồn video. Vui lòng kiểm tra lại đường dẫn/thiết bị.")
        return

    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        print("❌ Lỗi: Không thể lấy khung hình từ video.")
        return

    # Resize khung hình giống kích thước xử lý chính
    frame_original = cv2.resize(frame, (args.size, args.size))
    img_display = frame_original.copy()

    cv2.namedWindow("Lay toa do ROI - Click 4 diem")
    cv2.setMouseCallback("Lay toa do ROI - Click 4 diem", click_event)

    print("\nHướng dẫn sử dụng:")
    print("1. Click chuột trái lần lượt để chọn 4 điểm theo thứ tự:")
    print("   P1 (Trên-Trái) -> P2 (Trên-Phải) -> P3 (Dưới-Phải) -> P4 (Dưới-Trái)")
    print("2. Nhấn 's' để lưu trực tiếp vào cameras_config.yaml")
    print("3. Nhấn 'c' để xóa các điểm và chọn lại")
    print("4. Nhấn 'q' để thoát")

    while True:
        cv2.imshow("Lay toa do ROI - Click 4 diem", img_display)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('c'):
            points = []
            img_display = frame_original.copy()
            print("Đã xóa các điểm. Hãy click chọn lại.")
        elif key == ord('s'):
            if len(points) == 4:
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config_data = yaml.safe_load(f) or {}
                        
                        cameras = config_data.get("cameras", {})
                        if not cameras:
                            cameras = {}
                        
                        print("\nDanh sách camera hiện tại trong config:")
                        for cam in cameras.keys():
                            print(f"- {cam}")
                        cam_name = input("Nhập tên camera để cập nhật tọa độ (ví dụ: cam_1, nhấn Enter để lưu thành 'cam_custom'): ").strip()
                        if not cam_name:
                            cam_name = "cam_custom"
                        
                        if cam_name not in cameras:
                            cameras[cam_name] = {}
                        
                        # Ghi đè src_pts
                        # Lưu dưới dạng danh sách python chuẩn để yaml ghi đẹp mắt
                        cameras[cam_name]["src_pts"] = [[int(pt[0]), int(pt[1])] for pt in points]
                        config_data["cameras"] = cameras
                        
                        with open(config_file, 'w', encoding='utf-8') as f:
                            yaml.dump(config_data, f, default_flow_style=False)
                            
                        print(f"✔ Đã lưu thành công tọa độ ROI của '{cam_name}' vào {config_file}!")
                        break
                    except Exception as e:
                        print(f"❌ Lỗi ghi file cấu hình: {e}")
                else:
                    print(f"❌ Lỗi: Không tìm thấy file {config_file} ở thư mục hiện tại để ghi.")
            else:
                print("⚠ Cảnh báo: Vui lòng click đủ 4 điểm trước khi lưu!")

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
