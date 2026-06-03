/* Upload code to connected Arduino Mega 2560
   Controls servos through PCA9685 servo driver
*/

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Servo pulse calibration
#define SERVOMIN 150
#define SERVOMAX 600
#define SERVO_FREQ 50

// PCA9685 channel assignments
const int BASE_CH = 0;
const int SHOULDER_CH = 1;
const int ELBOW_CH = 2;
const int WRIST_CH = 3;
const int GRIPPER_CH = 4;

int basePos = 90;
int shoulderPos = 90;
int elbowPos = 90;
int wristPos = 90;
int gripperPos = 120;

const int GRIPPER_OPEN = 120;
const int GRIPPER_CLOSED = 55;

void setup() {
  Serial.begin(115200);

  pwm.begin();
  pwm.setPWMFreq(SERVO_FREQ);
  delay(10);

  homeArm();

  Serial.println("PCA9685 arm controller ready");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "HOME") {
      homeArm();
      Serial.println("OK HOME");
    }
    else if (command == "OPEN") {
      openGripper();
      Serial.println("OK OPEN");
    }
    else if (command == "CLOSE") {
      closeGripper();
      Serial.println("OK CLOSE");
    }
    else if (command.startsWith("POSE")) {
      handlePoseCommand(command);
    }
    else {
      Serial.println("ERROR: Unknown command");
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

int angleToPulse(int angle) {
  angle = constrain(angle, 0, 180);
  return map(angle, 0, 180, SERVOMIN, SERVOMAX);
}

void writeServo(int channel, int angle) {
  pwm.setPWM(channel, 0, angleToPulse(angle));
}

void homeArm() {
  moveArmToPose(90, 90, 90, 90, GRIPPER_OPEN);
}

void moveArmToPose(int base, int shoulder, int elbow, int wrist, int gripper) {
  base = constrain(base, 0, 180);
  shoulder = constrain(shoulder, 0, 180);
  elbow = constrain(elbow, 0, 180);
  wrist = constrain(wrist, 0, 180);
  gripper = constrain(gripper, 0, 180);

  smoothMove(BASE_CH, basePos, base);
  smoothMove(SHOULDER_CH, shoulderPos, shoulder);
  smoothMove(ELBOW_CH, elbowPos, elbow);
  smoothMove(WRIST_CH, wristPos, wrist);
  smoothMove(GRIPPER_CH, gripperPos, gripper);
}

void openGripper() {
  smoothMove(GRIPPER_CH, gripperPos, GRIPPER_OPEN);
}

void closeGripper() {
  smoothMove(GRIPPER_CH, gripperPos, GRIPPER_CLOSED);
}

void smoothMove(int channel, int &currentPos, int targetPos) {
  targetPos = constrain(targetPos, 0, 180);

  while (currentPos != targetPos) {
    if (currentPos < targetPos) {
      currentPos++;
    } else {
      currentPos--;
    }

    writeServo(channel, currentPos);
    delay(15);
  }
}