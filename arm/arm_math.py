import math


UPPER_ARM_CM = 13.5
FOREARM_CM = 13.5

MAX_SERVO_ANGLE = 180
MIN_SERVO_ANGLE = 0


def clamp(value, min_value=MIN_SERVO_ANGLE, max_value=MAX_SERVO_ANGLE):
    return max(min_value, min(max_value, value))


def calculate_base_angle(angle_deg):
    """
    Converts object angle from vision into base servo angle.
    0 degrees from vision means straight ahead.
    """
    return clamp(round(90 + angle_deg))


def calculate_2_link_ik(distance_cm, target_height_cm=3):
    """
    Calculates shoulder and elbow angles for a simple 2-link robotic arm.
    """

    max_reach = UPPER_ARM_CM + FOREARM_CM
    distance_cm = min(distance_cm, max_reach - 0.5)

    x = distance_cm
    z = target_height_cm

    r = math.sqrt(x**2 + z**2)

    cos_elbow = (r**2 - UPPER_ARM_CM**2 - FOREARM_CM**2) / (
        2 * UPPER_ARM_CM * FOREARM_CM
    )
    cos_elbow = clamp(cos_elbow, -1, 1)
    elbow_rad = math.acos(cos_elbow)

    target_angle_rad = math.atan2(z, x)

    cos_shoulder = (r**2 + UPPER_ARM_CM**2 - FOREARM_CM**2) / (
        2 * UPPER_ARM_CM * r
    )
    cos_shoulder = clamp(cos_shoulder, -1, 1)
    shoulder_offset_rad = math.acos(cos_shoulder)

    shoulder_rad = target_angle_rad + shoulder_offset_rad

    shoulder_angle = math.degrees(shoulder_rad)
    elbow_angle = math.degrees(elbow_rad)

    return round(clamp(shoulder_angle)), round(clamp(elbow_angle))


def calculate_5dof_pose(
    distance_cm,
    angle_deg,
    target_height_cm=3,
    wrist_angle=90,
    gripper_angle=120,
):
    """
    Full 5-motor pose.

    Motor 1: base
    Motor 2: shoulder
    Motor 3: elbow
    Motor 4: wrist rotation
    Motor 5: gripper open/close
    """

    base = calculate_base_angle(angle_deg)
    shoulder, elbow = calculate_2_link_ik(distance_cm, target_height_cm)

    return {
        "base": base,
        "shoulder": shoulder,
        "elbow": elbow,
        "wrist": round(clamp(wrist_angle)),
        "gripper": round(clamp(gripper_angle)),
    }