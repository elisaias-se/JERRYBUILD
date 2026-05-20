print("🚀 Starting program...")

from ultralytics import YOLO
import cv2
import torch
import time

print("Loading custom YOLO model...")

model = YOLO("best.engine", task="detect")

print("Model loaded!")
print("Model classes:", model.names)

REAL_HEIGHT = 12.0
FOCAL_LENGTH = 700

# Tune this based on your camera's real horizontal field of view
CAMERA_HORIZONTAL_FOV = 70  # degrees

VALID_CLASSES = ["trash"]


def calculate_horizontal_angle(cx, frame_width, horizontal_fov=CAMERA_HORIZONTAL_FOV):
    """
    Calculates the horizontal angle of the detected object from camera center.

    Negative angle = object is left of center
    Positive angle = object is right of center
    """
    image_center_x = frame_width / 2
    pixel_offset = cx - image_center_x

    angle_per_pixel = horizontal_fov / frame_width
    angle = pixel_offset * angle_per_pixel

    return angle


print("📷 Opening camera...")

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
    frame_height, frame_width = frame.shape[:2]

    start_time = time.time()

    results = model(frame, conf=0.5, verbose=False, device=0)

    end_time = time.time()

    inference_ms = (end_time - start_time) * 1000
    fps = 1000 / inference_ms

    print(f"Inference: {inference_ms:.2f} ms | FPS: {fps:.2f}")

    detected_any = False

    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        conf = float(box.conf[0])

        print(f"Detected: {label} ({conf:.2f})")

        if label not in VALID_CLASSES:
            continue

        detected_any = True

        x1, y1, x2, y2 = box.xyxy[0]

        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        angle = calculate_horizontal_angle(cx, frame_width)

        pixel_height = y2 - y1

        if pixel_height == 0:
            print("Skipping invalid bounding box")
            continue

        distance = (REAL_HEIGHT * FOCAL_LENGTH) / pixel_height

        print(
            f"{label} at ({cx}, {cy}) | "
            f"Distance: {distance:.2f} cm | "
            f"Angle: {angle:.2f}°"
        )

        cv2.rectangle(
            frame,
            (int(x1), int(y1)),
            (int(x2), int(y2)),
            (0, 255, 0),
            2
        )

        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        cv2.putText(
            frame,
            f"{label} {conf:.2f} | {distance:.1f} cm | {angle:.1f} deg",
            (int(x1), int(y1) - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )

    if not detected_any and frame_count % 30 == 0:
        print("⚠️ No valid objects detected")

    cv2.imshow("Custom Trash Detection", frame)

    if cv2.waitKey(1) == 27:
        print("Exiting...")
        break

cap.release()
cv2.destroyAllWindows()

print("Program ended cleanly")