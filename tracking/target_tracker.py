from collections import deque
import statistics


class TargetTracker:
    def __init__(self, max_samples=12):
        self.samples = deque(maxlen=max_samples)

    def update(self, distance_cm, angle_deg, x_cm, y_cm):
        if distance_cm is None:
            return

        self.samples.append({
            "distance_cm": distance_cm,
            "angle_deg": angle_deg,
            "x_cm": x_cm,
            "y_cm": y_cm,
        })

    def is_ready(self):
        return len(self.samples) == self.samples.maxlen

    def is_stable(self, max_distance_std=1.5, max_angle_std=3.0):
        if not self.is_ready():
            return False

        distances = [s["distance_cm"] for s in self.samples]
        angles = [s["angle_deg"] for s in self.samples]

        distance_std = statistics.stdev(distances)
        angle_std = statistics.stdev(angles)

        return distance_std <= max_distance_std and angle_std <= max_angle_std

    def get_average_target(self):
        if not self.samples:
            return None

        return {
            "distance_cm": statistics.mean(s["distance_cm"] for s in self.samples),
            "angle_deg": statistics.mean(s["angle_deg"] for s in self.samples),
            "x_cm": statistics.mean(s["x_cm"] for s in self.samples),
            "y_cm": statistics.mean(s["y_cm"] for s in self.samples),
        }

    def reset(self):
        self.samples.clear()