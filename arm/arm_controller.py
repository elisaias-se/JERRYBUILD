class ArmController:
    def __init__(self):
        print("Arm controller ready")

    def pick_up(self, grasp):
        print("Arm command:")
        print(f"Move to X: {grasp['x_cm']:.2f} cm")
        print(f"Move to Y: {grasp['y_cm']:.2f} cm")
        print(f"Gripper angle: {grasp['gripper_angle']} degrees")

        # Later:
        # send serial command to Arduino here