#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include <Adafruit_PWMServoDriver.h>
#include <SoftwareSerial.h>
#include "diffSteer.h"

SoftwareSerial picoSerial(2, 3);

Adafruit_MotorShield AFMS0 = Adafruit_MotorShield(0x61);
Adafruit_MotorShield AFMS1 = Adafruit_MotorShield(0x60);

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);

Adafruit_DCMotor *rear_right = AFMS0.getMotor(2);
Adafruit_DCMotor *middle_right = AFMS0.getMotor(3);
Adafruit_DCMotor *front_right = AFMS0.getMotor(4);
Adafruit_DCMotor *rear_left = AFMS1.getMotor(2);
Adafruit_DCMotor *front_left = AFMS1.getMotor(3);
Adafruit_DCMotor *middle_left = AFMS1.getMotor(4);

#define SERVOMIN 100
#define SERVOMAX 520

#define servo_front_left 13
#define servo_front_right 12
#define servo_rear_left 14
#define servo_rear_right 15

#define servo_front_left_center 355  
#define servo_front_right_center 355  
#define servo_rear_left_center 325    
#define servo_rear_right_center 345       

#define START 0xAA
#define END   0x55
#define PACKET_SIZE 11

enum State { WAIT_START, READ_DATA };
State state = WAIT_START;
byte buf[PACKET_SIZE];
int idx = 0;

byte j1a0, j1a1, j1a2;
byte j2a0, j2a1, j2a2;
long buttons;
bool left_trigger;
bool right_trigger;

bool connected = false;
bool zeroTurn = false;
bool lastButtonState_zeroTurn = false;

unsigned long lastPacketTime = 0;
#define TIMEOUT_MS 500

int lastAngle = 90;

diffSteer steer(427.5, 335.0, 338.0, 335.0);
int sp_fl, sp_fr, sp_ml, sp_mr, sp_rl, sp_rr;


void setup() {
  Serial.begin(9600);
  picoSerial.begin(9600);
 

  if(!pwm.begin()) {
   Serial.println("Could not find Servo Shield. Check wiring.");
    while (1); 
  }
  Serial.println("Servo Shield found.");
  pwm.setPWMFreq(60);

  if (!AFMS0.begin()) {         
    Serial.println("Could not find Motor Shield 1. Check wiring.");
    while (1);
  }
  Serial.println("Motor Shield 1 found.");

  if (!AFMS1.begin()) {         
    Serial.println("Could not find Motor Shield 2. Check wiring.");
    while (1);
  }
  Serial.println("Motor Shield 2 found.");

  servoCenter();
}

void loop() {

  if (connected && (millis() - lastPacketTime > TIMEOUT_MS)) {
        connected = false;
    }

  while (picoSerial.available()) {
    byte b = picoSerial.read();
    //Serial.print("RX: 0x");
     //Serial.println(b, HEX);

      switch (state) {
        case WAIT_START:
          if (b == START) {
            //Serial.println("START found");
            buf[0] = b;
            idx = 1;
            state = READ_DATA;
          }
          break;

        case READ_DATA:
          buf[idx++] = b;
            if (idx == PACKET_SIZE) {
              //Serial.print("END byte: 0x");
              //Serial.println(buf[10], HEX);
              if (buf[10] == END) {
                //Serial.println("valid packet");
                process_packet();
                }
                state = WAIT_START;
                idx = 0;
              }
              break;
      }
  }

  //Serial.print("connected: ");
  //Serial.println(connected);

 if (!connected) {
    rear_right->run(RELEASE);
    middle_right->run(RELEASE);
    front_right->run(RELEASE);
    rear_left->run(RELEASE);
    front_left->run(RELEASE);
    middle_left->run(RELEASE);
    return;
}

bool currentButtonState_zeroTurn = (buttons & (1UL << 17)) != 0;
if (currentButtonState_zeroTurn && !lastButtonState_zeroTurn) {
  zeroTurn = !zeroTurn;
}
lastButtonState_zeroTurn = currentButtonState_zeroTurn;

int speed = 0;

if (zeroTurn) {
  zeroTurnServos();
  if (j1a2 > 140){
    speed = map(j1a2, 140, 255, 0, 255);
    front_left->run(BACKWARD);   front_left->setSpeed(speed);
    front_right->run(FORWARD);  front_right->setSpeed(speed);
    middle_left->run(BACKWARD);  middle_left->setSpeed(speed);
    middle_right->run(FORWARD); middle_right->setSpeed(speed);
    rear_left->run(BACKWARD);    rear_left->setSpeed(speed);
    rear_right->run(FORWARD);   rear_right->setSpeed(speed);

  } else if (j1a2 < 115){
    speed = map(j1a2, 115, 0, 0, 255);
    front_left->run(FORWARD);   front_left->setSpeed(speed);
    front_right->run(BACKWARD);  front_right->setSpeed(speed);
    middle_left->run(FORWARD);  middle_left->setSpeed(speed);
    middle_right->run(BACKWARD); middle_right->setSpeed(speed);
    rear_left->run(FORWARD);    rear_left->setSpeed(speed);
    rear_right->run(BACKWARD);   rear_right->setSpeed(speed);

  } else {
    rear_right->run(RELEASE);
    middle_right->run(RELEASE);
    front_right->run(RELEASE);
    rear_left->run(RELEASE);
    front_left->run(RELEASE);
    middle_left->run(RELEASE);    
  }
} else {
    
    float steerAngle = map(j2a1, 0, 255, 180, 0);  // 90 = straight

    if (j1a0 > 140) {
        speed = map(j1a0, 140, 255, 0, 255);
        steer.calcSpeed(speed, steerAngle, sp_fl, sp_fr, sp_ml, sp_mr, sp_rl, sp_rr);
        front_left->run(FORWARD);   front_left->setSpeed(sp_fl);
        front_right->run(FORWARD);  front_right->setSpeed(sp_fr);
        middle_left->run(FORWARD);  middle_left->setSpeed(sp_ml);
        middle_right->run(FORWARD); middle_right->setSpeed(sp_mr);
        rear_left->run(FORWARD);    rear_left->setSpeed(sp_rl);
        rear_right->run(FORWARD);   rear_right->setSpeed(sp_rr);

    } else if (j1a0 < 115) {
        speed = map(j1a0, 115, 0, 0, 255);
        steer.calcSpeed(speed, steerAngle, sp_fl, sp_fr, sp_ml, sp_mr, sp_rl, sp_rr);
        front_left->run(BACKWARD);   front_left->setSpeed(sp_fl);
        front_right->run(BACKWARD);  front_right->setSpeed(sp_fr);
        middle_left->run(BACKWARD);  middle_left->setSpeed(sp_ml);
        middle_right->run(BACKWARD); middle_right->setSpeed(sp_mr);
        rear_left->run(BACKWARD);    rear_left->setSpeed(sp_rl);
        rear_right->run(BACKWARD);   rear_right->setSpeed(sp_rr);

    } else {
        rear_right->run(RELEASE);
        middle_right->run(RELEASE);
        front_right->run(RELEASE);
        rear_left->run(RELEASE);
        front_left->run(RELEASE);
        middle_left->run(RELEASE);
    }

    if (j2a1 > 140 || j2a1 < 115) {
        int angle = map(j2a1, 255, 0, 0, 180);
        
        if (abs(angle - lastAngle) > 2) {
            lastAngle = angle;
            
            int ang_fl, ang_fr, ang_rl, ang_rr;
            steer.calcSteerAngle(steerAngle, ang_fl, ang_fr, ang_rl, ang_rr);

            pwm.setPWM(servo_front_left,  0, servoAngleToPulse(ang_fl, servo_front_left_center));
            pwm.setPWM(servo_front_right, 0, servoAngleToPulse(ang_fr, servo_front_right_center));
            pwm.setPWM(servo_rear_left,   0, servoAngleToPulse(ang_rl, servo_rear_left_center));
            pwm.setPWM(servo_rear_right,  0, servoAngleToPulse(ang_rr, servo_rear_right_center));
        }
    } else {
        servoCenter();
        lastAngle = 90;
    }
  }



}




/*
convert desired angle into pwn signal
input angle from 0 to 180, 90 is a middle of servo roation 
*/
int servoAngleToPulse(int angle, int center) {
    return constrain(center + angle, SERVOMIN, SERVOMAX);
}
void servoCenter()
{
  pwm.setPWM(servo_front_left, 0, servo_front_left_center);
  pwm.setPWM(servo_front_right, 0, servo_front_right_center);
  pwm.setPWM(servo_rear_left, 0, servo_rear_left_center);
  pwm.setPWM(servo_rear_right, 0, servo_rear_right_center);
}

void process_packet() {
  connected = true;
  lastPacketTime = millis();
  j1a0 = buf[1];
  j1a1 = buf[2];
  j1a2 = buf[3];

  j2a0 = buf[4];
  j2a1 = buf[5];
  j2a2 = buf[6];

  byte btn_low  = buf[7];
  byte btn_mid  = buf[8];
  byte btn_high = buf[9];

   buttons = ((long)btn_high << 16) | ((long)btn_mid << 8) | btn_low;

  left_trigger  = buttons & (1 << 16);
  right_trigger = buttons & (1 << 17);
}

void zeroTurnServos()
{
  pwm.setPWM(servo_front_left,  0, servoAngleToPulse( 100, servo_front_left_center));
  pwm.setPWM(servo_front_right, 0, servoAngleToPulse(-100, servo_front_right_center));
  pwm.setPWM(servo_rear_left,   0, servoAngleToPulse(-100, servo_rear_left_center));
  pwm.setPWM(servo_rear_right,  0, servoAngleToPulse( 100, servo_rear_right_center));
}

