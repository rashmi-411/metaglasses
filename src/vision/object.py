"""
yolo_assist.py
Simple real-time YOLOv8-based detector that speaks alerts for person/vehicle detection.
Dependencies:
    pip install ultralytics opencv-python pyttsx3 numpy

Run:
    python yolo_assist.py
"""

import time
from collections import defaultdict, deque

import cv2
import numpy as np
import pyttsx3
from ultralytics import YOLO

# ----------------- CONFIG -----------------
MODEL_NAME = "yolov8n.pt"     # small, fast; change to yolov8s.pt / yolov8m.pt for better accuracy
CAMERA_ID = 0                 # change if using external webcam / usb camera
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Classes we care about (COCO names): 'person', 'bicycle', 'motorcycle', 'car', 'bus', 'truck'
TARGET_CLASSES = {"person", "bicycle", "motorcycle", "car", "bus", "truck"}

# area thresholds (as fraction of frame area) to estimate distance zone. Tune for your camera.
VERY_CLOSE_THRESH = 0.12   # bounding box area > 12% -> VERY CLOSE (danger)
CLOSE_THRESH = 0.03        # area > 3% -> CLOSE
# else FAR

# voice config: minimal interval (seconds) between announcements per label+zone
ANNOUNCE_COOLDOWN = 2.5

# overall loudness rate limiting: don't speak more than once every N seconds
GLOBAL_COOLDOWN = 0.9

# How long to keep history of detections for smoothing (seconds)
HISTORY_SECONDS = 1.0
# ------------------------------------------

# COCO class names used by YOLOv8
COCO_NAMES = [
    "person","bicycle","car","motorcycle","airplane","bus","train","truck","boat","traffic light",
    "fire hydrant","stop sign","parking meter","bench","bird","cat","dog","horse","sheep","cow",
    "elephant","bear","zebra","giraffe","backpack","umbrella","handbag","tie","suitcase","frisbee",
    "skis","snowboard","sports ball","kite","baseball bat","baseball glove","skateboard","surfboard",
    "tennis racket","bottle","wine glass","cup","fork","knife","spoon","bowl","banana","apple","sandwich",
    "orange","broccoli","carrot","hot dog","pizza","donut","cake","chair","couch","potted plant","bed",
    "dining table","toilet","tv","laptop","mouse","remote","keyboard","cell phone","microwave","oven",
    "toaster","sink","refrigerator","book","clock","vase","scissors","teddy bear","hair drier","toothbrush"
]

# ----------------- Text-to-Speech -----------------
class Speaker:
    def __init__(self, rate=160, volume=1.0):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)
        # Try to pick a clear voice (optional)
        voices = self.engine.getProperty("voices")
        if voices:
            # pick a voice that sounds clear; fallback gracefully
            try:
                self.engine.setProperty("voice", voices[0].id)
            except Exception:
                pass
        self._last_spoken = 0.0

    def speak(self, text):
        # synchronous speak (blocking) - keeping messages short is important
        self.engine.say(text)
        self.engine.runAndWait()

    def try_speak(self, text, min_interval=0.2):
        """Non-strict global throttle: ensures a small gap between utterances."""
        now = time.time()
        if now - self._last_spoken < min_interval:
            return False
        self._last_spoken = now
        self.speak(text)
        return True

# ----------------- Helper functions -----------------
def bbox_area(box):
    # box: (x1,y1,x2,y2)
    x1, y1, x2, y2 = box
    w = max(0, x2 - x1)
    h = max(0, y2 - y1)
    return w * h

def zone_from_area_fraction(area_frac):
    if area_frac >= VERY_CLOSE_THRESH:
        return "very close"
    if area_frac >= CLOSE_THRESH:
        return "close"
    return "far"

def short_label_for_class(cls_name):
    # Normalize names for speech
    mapping = {
        "motorcycle": "motorbike",
        "truck": "truck",
        "bicycle": "bicycle",
        "car": "car",
        "bus": "bus",
        "person": "person",
    }
    return mapping.get(cls_name, cls_name)

# ----------------- Main -----------------
def main():
    # Initialize speaker
    speaker = Speaker(rate=150, volume=0.9)

    # Load model
    print("Loading model... (this may take a moment)")
    model = YOLO(MODEL_NAME)  # ultralytics will load weights and handle device selection
    print("Model loaded.")

    # Start camera
    cap = cv2.VideoCapture(CAMERA_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("ERROR: Could not open camera. Exiting.")
        return

    frame_area = FRAME_WIDTH * FRAME_HEIGHT

    # Cooldown trackers
    last_announce = defaultdict(lambda: 0.0)  # key: (label, zone) -> last time spoken
    global_last = 0.0

    # small temporal smoothing: keep detections from last HISTORY_SECONDS seconds
    history = deque()  # entries: (timestamp, class_name, area_frac, center_x)

    print("Starting detection. Press 'q' to quit.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            now = time.time()
            # Run inference (ultralytics returns list of results)
            results = model(frame, stream=False, verbose=False)  # one inference per frame

            # results[0] contains .boxes
            detections = []
            r = results[0]
            if hasattr(r, "boxes") and r.boxes is not None:
                boxes = np.array(r.boxes.xyxy.cpu()) if r.boxes.xyxy is not None else []
                confs = np.array(r.boxes.conf.cpu()) if r.boxes.conf is not None else []
                cls_ids = np.array(r.boxes.cls.cpu()) if r.boxes.cls is not None else []
                for box, conf, cid in zip(boxes, confs, cls_ids):
                    idx = int(cid)
                    if idx < 0 or idx >= len(COCO_NAMES):
                        continue
                    name = COCO_NAMES[idx]
                    if name not in TARGET_CLASSES:
                        continue
                    x1, y1, x2, y2 = map(float, box)
                    area = bbox_area((x1, y1, x2, y2))
                    area_frac = area / float(frame_area)
                    cx = (x1 + x2) / 2.0
                    detections.append((name, area_frac, (x1, y1, x2, y2), float(conf), cx))

            # Add to history and prune
            history.append((now, detections))
            while history and now - history[0][0] > HISTORY_SECONDS:
                history.popleft()

            # Aggregate latest detections per class by choosing the largest box in recent history
            aggregated = {}
            for ts, dets in history:
                for name, area_frac, box, conf, cx in dets:
                    prev = aggregated.get(name)
                    if (prev is None) or (area_frac > prev[0]):
                        aggregated[name] = (area_frac, box, conf, cx)

            # For each aggregated detection, decide on speaking
            messages = []
            for name, (area_frac, box, conf, cx) in aggregated.items():
                zone = zone_from_area_fraction(area_frac)
                label = short_label_for_class(name)
                # Create a short message
                if zone == "very close":
                    msg = f"{label} very close! Stop."
                elif zone == "close":
                    msg = f"{label} close."
                else:
                    msg = f"{label} ahead."

                key = (label, zone)
                now = time.time()
                # enforce per-label cooldown and global cooldown
                if now - last_announce[key] >= ANNOUNCE_COOLDOWN and now - global_last >= GLOBAL_COOLDOWN:
                    messages.append((msg, key))
                    last_announce[key] = now
                    global_last = now

            # Speak messages (one by one)
            for msg, key in messages:
                print(f"[ALERT] {msg}")
                speaker.try_speak(msg, min_interval=0.05)  # try_speak will throttle tiny gaps

            # Optional: draw boxes and show frame for debugging (sighted helper)
            # draw aggregated boxes
            for name, (area_frac, box, conf, cx) in aggregated.items():
                x1, y1, x2, y2 = map(int, box)
                color = (0, 255, 0) if zone_from_area_fraction(area_frac) != "very close" else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                text = f"{name} {area_frac*100:.1f}%"
                cv2.putText(frame, text, (x1, max(0, y1-6)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            cv2.putText(frame, "Press 'q' to quit", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 1)
            cv2.imshow("YOLO Assist (debug)", frame)

            # keyboard handling
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

    except KeyboardInterrupt:
        print("Interrupted by user.")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Exiting.")

if __name__ == "__main__":
    main()
