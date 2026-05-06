print("🚀 Starting program...")

from ultralytics import YOLO
import cv2

print("Loading YOLO model...")
model = YOLO("yolov8n.pt")

import torch

if torch.cuda.is_available():
    model.to("cuda")
    print("Using GPU acceleration")
else:
    print("CUDA not available, using CPU")

print("Model loaded!")
REAL_HEIGHT = 12.0   # cm
FOCAL_LENGTH = 700
VALID_CLASSES = ["bottle", "cup"]

print("📷 Opening camera...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Camera failed to open")
    exit()
else:
    print("Camera opened successfully")

# (Remove this line - it's incorrect usage)
# cap.set(3, REAL_HEIGHT)

# REMOVE duplicate camera initialization
# cap = cv2.VideoCapture(0)

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame_count += 1

    # Only print every 30 frames to avoid spam
    if frame_count % 30 == 0:
        print(f"Processing frame {frame_count}")

    frame = cv2.resize(frame, (640, 480))

    print(" Running YOLO inference...")
    results = model(frame, classes=[39, 41], conf=0.5)
    print(" Inference complete")

    detected_any = False

    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        conf = float(box.conf[0])

        print(f"Detected: {label} ({conf:.2f})")

        if label not in VALID_CLASSES or conf < 0.5:
            continue

        detected_any = True

        x1, y1, x2, y2 = box.xyxy[0]

        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        pixel_height = y2 - y1

        if pixel_height == 0:
            print("Skipping invalid bounding box")
            continue

        distance = (REAL_HEIGHT * FOCAL_LENGTH) / pixel_height

        print(f"Object at ({cx}, {cy}) | Distance: {distance:.2f} cm")

        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
        cv2.putText(frame, f"{distance:.1f} cm",
                    (int(x1), int(y1)-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0,255,0), 2)

    if not detected_any:
        print("⚠️ No valid objects detected")

    cv2.imshow("Detection + Depth", frame)

    if cv2.waitKey(1) == 27:
        print("Exiting...")
        break

cap.release()
cv2.destroyAllWindows()
print("Program ended cleanly")