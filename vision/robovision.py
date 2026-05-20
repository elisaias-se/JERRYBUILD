from ultralytics import YOLO

MODEL_PATH = "best.engine"
VALID_CLASSES = ["trash"]
CONFIDENCE_THRESHOLD = 0.5


class TrashDetector:
    def __init__(self):
        print("Loading custom YOLO model...")
        self.model = YOLO(MODEL_PATH, task="detect")
        print("Model loaded!")
        print("Model classes:", self.model.names)

    def detect(self, frame):
        results = self.model(
            frame,
            conf=CONFIDENCE_THRESHOLD,
            verbose=False,
            device=0
        )

        detections = []

        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            label = self.model.names[cls_id]
            confidence = float(box.conf[0])

            if label not in VALID_CLASSES:
                continue

            x1, y1, x2, y2 = box.xyxy[0]

            detection = {
                "label": label,
                "confidence": confidence,
                "x1": float(x1),
                "y1": float(y1),
                "x2": float(x2),
                "y2": float(y2),
                "cx": int((x1 + x2) / 2),
                "cy": int((y1 + y2) / 2),
                "pixel_width": float(x2 - x1),
                "pixel_height": float(y2 - y1),
            }

            detections.append(detection)

        return detections