import time
import serial

from arm.arm_math import calculate_5dof_pose, clamp


GRIPPER_OPEN = 120
GRIPPER_CLOSED = 55


class ArmController:
    def __init__(self, port="/dev/ttyACM0", baud_rate=115200):
        self.arduino = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)

    def send_pose(self, pose):
        command = (
            f"POSE {pose['base']} {pose['shoulder']} "
            f"{pose['elbow']} {pose['wrist']} {pose['gripper']}\n"
        )

        print("Sending:", command.strip())
        self.arduino.write(command.encode())
        self.arduino.flush()

        response = self.arduino.readline().decode(errors="ignore").strip()
        print("Arduino response:", response)

    def home_arm(self):
        self.arduino.write(b"HOME\n")
        self.arduino.flush()
        print("Arduino response:", self.arduino.readline().decode(errors="ignore").strip())

    def open_gripper(self):
        self.arduino.write(b"OPEN\n")
        self.arduino.flush()
        print("Arduino response:", self.arduino.readline().decode(errors="ignore").strip())

    def close_gripper(self):
        self.arduino.write(b"CLOSE\n")
        self.arduino.flush()
        print("Arduino response:", self.arduino.readline().decode(errors="ignore").strip())
    def move_to_target(self, distance_cm, angle_deg, wrist_angle):
        pose = calculate_5dof_pose(
            distance_cm=distance_cm,
            angle_deg=angle_deg,
            target_height_cm=3,
            wrist_angle=wrist_angle,
            gripper_angle=GRIPPER_OPEN,
        )

        self.send_pose(pose)

    def pickup_object(self, distance_cm, angle_deg, wrist_angle):
        approach_pose = calculate_5dof_pose(
            distance_cm=distance_cm,
            angle_deg=angle_deg,
            target_height_cm=6,
            wrist_angle=wrist_angle,
            gripper_angle=GRIPPER_OPEN,
        )

        grab_pose = calculate_5dof_pose(
            distance_cm=distance_cm,
            angle_deg=angle_deg,
            target_height_cm=2,
            wrist_angle=wrist_angle,
            gripper_angle=GRIPPER_OPEN,
        )

        closed_pose = grab_pose.copy()
        closed_pose["gripper"] = GRIPPER_CLOSED

        lift_pose = closed_pose.copy()
        lift_pose["shoulder"] = clamp(lift_pose["shoulder"] + 20)

        self.send_pose(approach_pose)
        time.sleep(1)

        self.send_pose(grab_pose)
        time.sleep(1)

        self.send_pose(closed_pose)
        time.sleep(1)

        self.send_pose(lift_pose)
        time.sleep(1)

    def close_connection(self):
        self.arduino.close()