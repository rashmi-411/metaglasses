import cv2
import threading
from ultralytics import YOLO

# Load YOLO model with correct weights
model = YOLO("yolov8n.pt")  # Using YOLOv8 nano model for better detection

# Video capture (DroidCam)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("Camera not accessible.")
    exit()

try:
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame")
            break

        # Run YOLO detection
        results = model(frame, conf=0.25)  # Lower confidence threshold for more detections
        
        # Draw detection results
        for r in results:
            annotated_frame = r.plot()
            
        # Display the annotated frame
        cv2.imshow('YOLO Detection', annotated_frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Release the capture and cleanup
    cap.release()
    cv2.destroyAllWindows()

# Print detection information
def display_info(results):
    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Get class name and confidence
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            name = model.names[cls_id]
            print(f"Detected: {name} with confidence: {conf:.2f}")

try:
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame")
            break

        # Run YOLO detection
        results = model(frame, conf=0.25)  # Lower confidence threshold
        
        # Display detection information
        display_info(results)
        
        # Draw detection results
        for r in results:
            annotated_frame = r.plot()
            cv2.imshow('YOLO Detection', annotated_frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"Error during video processing: {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()