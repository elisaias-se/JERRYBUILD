/*Upload code to connected Arduino (Intended for Arduino 2560 MEGA)*/
#include <Servo.h>

Servo baseServo;
Servo shoulderServo;
Servo elbowServo;
Servo wristServo;
Servo gripperServo;

const int BASE_PIN = 2;
const int SHOULDER_PIN = 3;
const int ELBOW_PIN = 4;
const int WRIST_PIN = 5;
const int GRIPPER_PIN = 6;

int basePos = 90;
int shoulderPos = 90;
int elbowPos = 90;
int wristPos = 90;
int gripperPos = 120;

const int GRIPPER_OPEN = 120;
const int GRIPPER_CLOSED = 55;

void setup() {
  Serial.begin(115200);

  baseServo.attach(BASE_PIN);
  shoulderServo.attach(SHOULDER_PIN);
  elbowServo.attach(ELBOW_PIN);
  wristServo.attach(WRIST_PIN);
  gripperServo.attach(GRIPPER_PIN);

  homeArm();
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "HOME") {
      homeArm();
    }
    else if (command == "OPEN") {
      openGripper();
    }
    else if (command == "CLOSE") {
      closeGripper();
    }
    else if (command.startsWith("POSE")) {
      handlePoseCommand(command);
    }
  }
}

void handlePoseCommand(String command) {
  int base;
  int shoulder;
  int elbow;
  int wrist;
  int gripper;

  int parsed = sscanf(
    command.c_str(),
    "POSE %d %d %d %d %d",
    &base,
    &shoulder,
    &elbow,
    &wrist,
    &gripper
  );

  if (parsed == 5) {
    moveArmToPose(base, shoulder, elbow, wrist, gripper);
    Serial.println("OK");
  } else {
    Serial.println("ERROR: Invalid POSE command");
  }
}

void homeArm() {
  smoothMove(baseServo, basePos, 90);
  smoothMove(shoulderServo, shoulderPos, 90);
  smoothMove(elbowServo, elbowPos, 90);
  smoothMove(wristServo, wristPos, 90);
  smoothMove(gripperServo, gripperPos, GRIPPER_OPEN);
}

void moveArmToPose(int base, int shoulder, int elbow, int wrist, int gripper) {
  base = constrain(base, 0, 180);
  shoulder = constrain(shoulder, 0, 180);
  elbow = constrain(elbow, 0, 180);
  wrist = constrain(wrist, 0, 180);
  gripper = constrain(gripper, 0, 180);

  smoothMove(baseServo, basePos, base);
  smoothMove(shoulderServo, shoulderPos, shoulder);
  smoothMove(elbowServo, elbowPos, elbow);
  smoothMove(wristServo, wristPos, wrist);
  smoothMove(gripperServo, gripperPos, gripper);
}

void openGripper() {
  smoothMove(gripperServo, gripperPos, GRIPPER_OPEN);
}

void closeGripper() {
  smoothMove(gripperServo, gripperPos, GRIPPER_CLOSED);
}

void smoothMove(Servo &servo, int &currentPos, int targetPos) {
  targetPos = constrain(targetPos, 0, 180);

  while (currentPos != targetPos) {
    if (currentPos < targetPos) {
      currentPos++;
    } else {
      currentPos--;
    }

    servo.write(currentPos);
    delay(15);
  }
}