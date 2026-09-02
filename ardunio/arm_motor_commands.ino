/*
 * BigTreeTech Octopus Pro v1.1 six-axis arm controller.
 *
 * Host protocol (kept compatible with the PCA9685 version):
 *   POSE <base> <shoulder> <elbow> <wrist_pitch> <wrist_rotate> <gripper>
 *   HOME | OPEN | CLOSE
 *
 * Motor sockets 0 through 5 are assigned in that order. POSE values are joint
 * angles in degrees, not raw steps.
 *
 * IMPORTANT: There is no endstop homing in this first version. Put the arm at
 * HOME_ANGLE before powering it. setup() declares that position as current.
 */

#include <Arduino.h>
#include <AccelStepper.h>
#include <math.h>

constexpr uint8_t AXIS_COUNT = 6;
constexpr uint32_t SERIAL_BAUD = 115200;

enum Axis : uint8_t { BASE, SHOULDER, ELBOW, WRIST_PITCH, WRIST_ROTATE, GRIPPER };

// Octopus Pro v1.1 motor sockets 0-5.
constexpr pin_size_t STEP_PIN[AXIS_COUNT] = {PF13, PG0, PF11, PG4, PF9, PC13};
constexpr pin_size_t DIR_PIN[AXIS_COUNT] = {PF12, PG1, PG3, PC1, PF10, PF0};
constexpr pin_size_t ENABLE_PIN[AXIS_COUNT] = {PF14, PF15, PG5, PA2, PG2, PF1};

// Calibrate for each motor, microstep setting, and gearbox:
// (motor full steps/rev * microsteps * gear ratio) / 360 degrees.
constexpr float STEPS_PER_DEGREE[AXIS_COUNT] = {
  8.8889f, 8.8889f, 8.8889f, 8.8889f, 8.8889f, 8.8889f
};
constexpr bool INVERT_DIRECTION[AXIS_COUNT] = {
  false, false, false, false, false, false
};
constexpr float MAX_SPEED[AXIS_COUNT] = {
  1200.0f, 1000.0f, 1000.0f, 1200.0f, 1200.0f, 800.0f
};
constexpr float ACCELERATION[AXIS_COUNT] = {
  600.0f, 500.0f, 500.0f, 600.0f, 600.0f, 400.0f
};

constexpr int MIN_ANGLE[AXIS_COUNT] = {0, 0, 0, 0, 0, 0};
constexpr int MAX_ANGLE[AXIS_COUNT] = {180, 180, 180, 180, 180, 180};
constexpr int HOME_ANGLE[AXIS_COUNT] = {90, 90, 90, 90, 90, 120};
constexpr int GRIPPER_OPEN_ANGLE = 120;
constexpr int GRIPPER_CLOSED_ANGLE = 55;

AccelStepper baseMotor(AccelStepper::DRIVER, STEP_PIN[BASE], DIR_PIN[BASE]);
AccelStepper shoulderMotor(AccelStepper::DRIVER, STEP_PIN[SHOULDER], DIR_PIN[SHOULDER]);
AccelStepper elbowMotor(AccelStepper::DRIVER, STEP_PIN[ELBOW], DIR_PIN[ELBOW]);
AccelStepper wristPitchMotor(AccelStepper::DRIVER, STEP_PIN[WRIST_PITCH], DIR_PIN[WRIST_PITCH]);
AccelStepper wristRotateMotor(AccelStepper::DRIVER, STEP_PIN[WRIST_ROTATE], DIR_PIN[WRIST_ROTATE]);
AccelStepper gripperMotor(AccelStepper::DRIVER, STEP_PIN[GRIPPER], DIR_PIN[GRIPPER]);

AccelStepper *motors[AXIS_COUNT] = {
  &baseMotor, &shoulderMotor, &elbowMotor,
  &wristPitchMotor, &wristRotateMotor, &gripperMotor
};
int currentAngle[AXIS_COUNT];

long angleToSteps(uint8_t axis, int angle) {
  return lroundf(angle * STEPS_PER_DEGREE[axis]);
}

bool anglesAreSafe(const int angles[AXIS_COUNT]) {
  for (uint8_t axis = 0; axis < AXIS_COUNT; ++axis) {
    if (angles[axis] < MIN_ANGLE[axis] || angles[axis] > MAX_ANGLE[axis]) {
      return false;
    }
  }
  return true;
}

void moveToAngles(const int angles[AXIS_COUNT]) {
  for (uint8_t axis = 0; axis < AXIS_COUNT; ++axis) {
    motors[axis]->moveTo(angleToSteps(axis, angles[axis]));
  }

  bool moving;
  do {
    moving = false;
    for (uint8_t axis = 0; axis < AXIS_COUNT; ++axis) {
      if (motors[axis]->distanceToGo() != 0) {
        motors[axis]->run();
        moving = true;
      }
    }
  } while (moving);

  for (uint8_t axis = 0; axis < AXIS_COUNT; ++axis) {
    currentAngle[axis] = angles[axis];
  }
}

void homeArm() {
  moveToAngles(HOME_ANGLE);
}

void moveGripperTo(int angle) {
  int pose[AXIS_COUNT];
  for (uint8_t axis = 0; axis < AXIS_COUNT; ++axis) {
    pose[axis] = currentAngle[axis];
  }
  pose[GRIPPER] = angle;
  moveToAngles(pose);
}

void handlePoseCommand(const String &command) {
  int angles[AXIS_COUNT];
  const int parsed = sscanf(
    command.c_str(), "POSE %d %d %d %d %d %d",
    &angles[BASE], &angles[SHOULDER], &angles[ELBOW],
    &angles[WRIST_PITCH], &angles[WRIST_ROTATE], &angles[GRIPPER]
  );

  if (parsed != AXIS_COUNT) {
    Serial.println("ERROR Invalid POSE command");
    return;
  }
  if (!anglesAreSafe(angles)) {
    Serial.println("ERROR Joint angle outside configured limits");
    return;
  }

  moveToAngles(angles);
  Serial.println("OK");
}

void setup() {
  Serial.begin(SERIAL_BAUD);
  Serial.setTimeout(100);

  for (uint8_t axis = 0; axis < AXIS_COUNT; ++axis) {
    motors[axis]->setEnablePin(ENABLE_PIN[axis]);
    motors[axis]->setPinsInverted(INVERT_DIRECTION[axis], false, true);
    motors[axis]->setMinPulseWidth(2);
    motors[axis]->setMaxSpeed(MAX_SPEED[axis]);
    motors[axis]->setAcceleration(ACCELERATION[axis]);
    motors[axis]->setCurrentPosition(angleToSteps(axis, HOME_ANGLE[axis]));
    motors[axis]->enableOutputs();
    currentAngle[axis] = HOME_ANGLE[axis];
  }

  Serial.println("READY Octopus Pro v1.1 stepper arm");
}

void loop() {
  if (!Serial.available()) {
    return;
  }

  String command = Serial.readStringUntil('\n');
  command.trim();

  if (command == "HOME") {
    homeArm();
    Serial.println("OK HOME");
  } else if (command == "OPEN") {
    moveGripperTo(GRIPPER_OPEN_ANGLE);
    Serial.println("OK OPEN");
  } else if (command == "CLOSE") {
    moveGripperTo(GRIPPER_CLOSED_ANGLE);
    Serial.println("OK CLOSE");
  } else if (command.startsWith("POSE ")) {
    handlePoseCommand(command);
  } else {
    Serial.println("ERROR Unknown command");
  }
}
