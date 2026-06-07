import cv2
import threading

class VideoStream:
    def __init__(self, src=0):
        if isinstance(src, str) and src.startswith("rtsp"):
            self.stream = cv2.VideoCapture(src, cv2.CAP_FFMPEG)
        else:
            self.stream = cv2.VideoCapture(src)
        self.grabbed, self.frame = self.stream.read()
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            if not self.stream.isOpened():
                self.stopped = True
                return
            try:
                self.grabbed, self.frame = self.stream.read()
            except Exception:
                self.stopped = True
                return

    def read(self):
        return self.grabbed, self.frame

    def stop(self):
        self.stopped = True
        self.stream.release()

    def isOpened(self):
        return self.stream.isOpened()

    def get(self, prop_id):
        return self.stream.get(prop_id)
