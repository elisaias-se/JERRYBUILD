print("🚀 Starting program...")

import cv2
import time
import platform

from vision.robovision import TrashDetector
from tracking.camera_math import (
    FRAME_WIDTH,
    FRAME_HEIGHT,
    calculate_distance_cm,
    calculate_horizontal_angle,
    calculate_xy,
)
from grasping.grasp_planner import plan_grip
from arm.arm_controller import ArmController


def open_camera(camera_index=0):
    current_os = platform.system()
    print(f"Detected OS: {current_os}")

    if current_os == "Windows":
        return cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    elif current_os == "Linux":
        return cv2.VideoCapture(camera_index, cv2.CAP_V4L2)
    else:
        return cv2.VideoCapture(camera_index)


detector = TrashDetector()
arm = ArmController()

print("📷 Opening camera...")
cap = open_camera(0)

if not cap.isOpened():
    print("ERROR: Camera failed to open")
    exit()

print("Camera opened successfully")

frame_count = 0

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    frame_count += 1
    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
    frame_height, frame_width = frame.shape[:2]

    start_time = time.time()

    detections = detector.detect(frame)

    end_time = time.time()

    inference_ms = (end_time - start_time) * 1000
    fps = 1000 / inference_ms if inference_ms > 0 else 0

    if frame_count % 30 == 0:
        print(f"Processing frame {frame_count}")
        print(f"Inference: {inference_ms:.2f} ms | FPS: {fps:.2f}")

    if len(detections) == 0 and frame_count % 30 == 0:
        print("No valid trash detected")

    for detection in detections:
        distance_cm = calculate_distance_cm(detection["pixel_height"])

        if distance_cm is None:
            continue

        angle_deg = calculate_horizontal_angle(
            detection["cx"],
            frame_width
        )

        x_cm, y_cm = calculate_xy(distance_cm, angle_deg)

        grasp = plan_grip(detection, x_cm, y_cm)

        print(
            f"{detection['label']} | "
            f"Distance: {distance_cm:.2f} cm | "
            f"Angle: {angle_deg:.2f}° | "
            f"X: {x_cm:.2f} cm | "
            f"Y: {y_cm:.2f} cm | "
            f"Grip: {grasp['gripper_angle']}°"
        )

        x1 = int(detection["x1"])
        y1 = int(detection["y1"])
        x2 = int(detection["x2"])
        y2 = int(detection["y2"])
        cx = detection["cx"]
        cy = detection["cy"]

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        cv2.putText(
            frame,
            f"{detection['label']} {distance_cm:.1f}cm {angle_deg:.1f}deg",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )

        # Keep this commented until you trust the coordinates.
        # arm.pick_up(grasp)

    cv2.imshow("Custom Trash Detection", frame)

    if cv2.waitKey(1) == 27:
        print("Exiting...")
        break

cap.release()
cv2.destroyAllWindows()

print("Program ended cleanly")