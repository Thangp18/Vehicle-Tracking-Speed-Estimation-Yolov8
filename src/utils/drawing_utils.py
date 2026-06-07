import cv2

def draw_text_safe(img, text, pos, color, thickness=1):
    """Vẽ text an toàn, tránh bị khuất mép trên màn hình"""
    x, y = pos
    y = y + 30 if y < 20 else y
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
