print("🚀 Starting program...")

from ultralytics import YOLO
import cv2
import torch

print("Loading custom YOLO model...")

# LOAD YOUR CUSTOM TRAINED MODEL

model = YOLO("best.pt")


if torch.cuda.is_available():
    model.to("cuda")
    print("Using GPU acceleration")
else:
    print("CUDA not available, using CPU")

print("Model loaded!")
print("Model classes:", model.names)

REAL_HEIGHT = 12.0
FOCAL_LENGTH = 700

# Your merged dataset should now only contain this class
VALID_CLASSES = ["trash"]

print("📷 Opening camera...")

# Windows camera backend (Ubuntu method)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Camera failed to open")
    exit()
else:
    print("Camera opened successfully")

frame_count = 0

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    frame_count += 1

    if frame_count % 30 == 0:
        print(f"Processing frame {frame_count}")

    frame = cv2.resize(frame, (640, 640))

    print("Running YOLO inference...")

    # REMOVE old COCO class filtering
    results = model(frame, conf=0.5)

    print("Inference complete")

    detected_any = False

    for box in results[0].boxes:

        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        conf = float(box.conf[0])

        print(f"Detected: {label} ({conf:.2f})")

        # Only allow trash detections
        if label not in VALID_CLASSES:
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

        print(f"{label} at ({cx}, {cy}) | Distance: {distance:.2f} cm")

        # Bounding box
        cv2.rectangle(
            frame,
            (int(x1), int(y1)),
            (int(x2), int(y2)),
            (0, 255, 0),
            2
        )

        # Center point
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        # Label text
        cv2.putText(
            frame,
            f"{label} {conf:.2f} | {distance:.1f} cm",
            (int(x1), int(y1)-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0,255,0),
            2
        )

    if not detected_any and frame_count % 30 == 0:
        print("⚠️ No valid objects detected")

    cv2.imshow("Custom Trash Detection", frame)

    # ESC key exits
    if cv2.waitKey(1) == 27:
        print("Exiting...")
        break

cap.release()
cv2.destroyAllWindows()

print("Program ended cleanly")