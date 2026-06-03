def plan_grip(detection, x_cm, y_cm):
    width = detection["pixel_width"]
    height = detection["pixel_height"]

    if width > height:
        orientation = "horizontal"
        gripper_angle = 90
        wrist_angle = 90
    else:
        orientation = "vertical"
        gripper_angle = 0
        wrist_angle = 0

    return {
        "x_cm": x_cm,
        "y_cm": y_cm,
        "orientation": orientation,
        "gripper_angle": gripper_angle,
        "wrist_angle": wrist_angle,
    }