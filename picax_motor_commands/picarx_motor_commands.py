import logging
# from logdecorator import log_on_start , log_on_end , log_on_error
import os
import math
import time
import atexit
try :
    from robot_hat import *
except ImportError :
    print (" This computer does not appear to be a PiCar - X system ( robot_hat is not present ) . Shadowing hardware "
           "calls with substitute functions ")
    from sim_robot_hat import *

logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO, datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)

# user and User home directory
User = os.popen('echo ${SUDO_USER:-$LOGNAME}').readline().strip()
UserHome = os.popen('getent passwd %s | cut -d: -f 6'%User).readline().strip()
config_file = '%s/.config/picar-x/picar-x.conf'%UserHome


class MotorCommands(object):
    PERIOD = 4095
    PRESCALER = 10
    TIMEOUT = 0.02

    # servo_pins: direction_servo, camera_servo_1, camera_servo_2 
    # motor_pins: left_swicth, right_swicth, left_pwm, right_pwm
    # grayscale_pins: 3 adc channels
    # ultrasonic_pins: tring, echo
    # config: path of config file
    def __init__(self, 
                servo_pins:list=['P2'],
                motor_pins:list=['D4', 'D5', 'P12', 'P13'],
                config:str=config_file,
                ):

        # config_flie
        self.config_flie = fileDB(config, 774, User)
        # servos init
        self.dir_servo_pin = Servo(PWM(servo_pins[0]))
        self.dir_cal_value = int(self.config_flie.get("picarx_dir_servo", default_value=0))

        self.dir_servo_pin.angle(self.dir_cal_value)

        # motors init
        self.left_rear_dir_pin = Pin(motor_pins[0])
        self.right_rear_dir_pin = Pin(motor_pins[1])
        self.left_rear_pwm_pin = PWM(motor_pins[2])
        self.right_rear_pwm_pin = PWM(motor_pins[3])
        self.motor_direction_pins = [self.left_rear_dir_pin, self.right_rear_dir_pin]
        self.motor_speed_pins = [self.left_rear_pwm_pin, self.right_rear_pwm_pin]
        self.cali_dir_value = self.config_flie.get("picarx_dir_motor", default_value="[1,1]")
        self.cali_dir_value = [int(i.strip()) for i in self.cali_dir_value.strip("[]").split(",")]
        self.cali_speed_value = [0, 0]
        self.dir_current_angle = 0
        for pin in self.motor_speed_pins:
            pin.period(self.PERIOD)
            pin.prescaler(self.PRESCALER)


    def set_motor_speed(self,motor,speed):
        # global cali_speed_value,cali_dir_value
        motor -= 1
        if speed >= 0:
            direction = 1 * self.cali_dir_value[motor]
        elif speed < 0:
            direction = -1 * self.cali_dir_value[motor]
        speed = abs(speed)
        # if speed != 0:
            # speed = int(speed /2 ) + 50
        speed = speed - self.cali_speed_value[motor]
        if direction < 0:
            self.motor_direction_pins[motor].high()
            self.motor_speed_pins[motor].pulse_width_percent(speed)
        else:
            self.motor_direction_pins[motor].low()
            self.motor_speed_pins[motor].pulse_width_percent(speed)

    def motor_speed_calibration(self,value):
        # global cali_speed_value,cali_dir_value
        self.cali_speed_value = value
        if value < 0:
            self.cali_speed_value[0] = 0
            self.cali_speed_value[1] = abs(self.cali_speed_value)
        else:
            self.cali_speed_value[0] = abs(self.cali_speed_value)
            self.cali_speed_value[1] = 0

    def motor_direction_calibration(self,motor, value):
        # 1: positive direction
        # -1:negative direction
        motor -= 1
        # if value == 1:
        #     self.cali_dir_value[motor] = -1 * self.cali_dir_value[motor]
        # self.config_flie.set("picarx_dir_motor", self.cali_dir_value)
        if value == 1:
            self.cali_dir_value[motor] = 1
        elif value == -1:
            self.cali_dir_value[motor] = -1
        self.config_flie.set("picarx_dir_motor", self.cali_dir_value)

    def dir_servo_angle_calibration(self,value):
        self.dir_cal_value = value
        self.config_flie.set("picarx_dir_servo", "%s"%value)
        self.dir_servo_pin.angle(value)

    def set_dir_servo_angle(self,value):
        self.dir_current_angle = value
        angle_value  = value + self.dir_cal_value
        self.dir_servo_pin.angle(angle_value)

    def set_power(self,speed):
        self.set_motor_speed(1, speed)
        self.set_motor_speed(2, speed) 

    def backward(self,speed):
        axel_length = 117
        axel_seperation = 95
        atexit.register(self.stop)
        current_angle = self.dir_current_angle
        if current_angle != 0:
            abs_current_angle = abs(current_angle)
            # if abs_current_angle >= 0:
            if abs_current_angle > 40:
                abs_current_angle = 40
            # power_scale = (100 - abs_current_angle) / 100.0
            power_scale = (axel_length / math.tan(math.radians(current_angle)) - axel_seperation / 2) / (
                        axel_length / math.tan(math.radians(current_angle)) + axel_seperation / 2)
            if (current_angle / abs_current_angle) > 0:
                self.set_motor_speed(1, -1*speed*power_scale)
                self.set_motor_speed(2, speed)
            else:
                self.set_motor_speed(1, -1*speed)
                self.set_motor_speed(2, speed / power_scale)
        else:
            self.set_motor_speed(1, -1*speed)
            self.set_motor_speed(2, speed)  

    def forward(self,speed):
        atexit.register(self.stop)
        current_angle = self.dir_current_angle
        axel_length = 117
        axel_seperation = 95
        if current_angle != 0:
            abs_current_angle = abs(current_angle)
            # if abs_current_angle >= 0:
            if abs_current_angle > 40:
                abs_current_angle = 40

            power_scale = (axel_length/math.tan(math.radians(current_angle)) - axel_seperation/2) / (axel_length/math.tan(math.radians(current_angle)) + axel_seperation/2)

            if (current_angle / abs_current_angle) > 0:

                self.set_motor_speed(1, speed * power_scale)
                self.set_motor_speed(2, -speed)
            else:
                self.set_motor_speed(1, speed)
                self.set_motor_speed(2, -speed / power_scale)
        else:
            self.set_motor_speed(1, speed)
            self.set_motor_speed(2, -1*speed)                  

    def stop(self):
        self.set_motor_speed(1, 0)
        self.set_motor_speed(2, 0)

    def forward_distance(self, distance):
        ...

    def backward_distance(self, distance):
        ...

    def parallel_park(self, side="right"):
        self.set_dir_servo_angle(0)
        time.sleep(0.5)
        self.forward(40)
        time.sleep(1.3)
        self.stop()
        if side == "right":
            self.set_dir_servo_angle(40)
        else:
            self.set_dir_servo_angle(-40)
        time.sleep(0.5)
        self.backward(40)
        time.sleep(1.5)
        self.stop()
        if side == "right":
            self.set_dir_servo_angle(-40)
        else:
            self.set_dir_servo_angle(40)
        time.sleep(0.5)
        self.backward(40)
        time.sleep(1.3)
        self.stop()
        self.set_dir_servo_angle(0)
        time.sleep(0.5)
        self.stop()

    def k_turn(self, dir="left"):

        if dir=="left":
            self.set_dir_servo_angle(-30)
        else:
            self.set_dir_servo_angle(30)
        time.sleep(0.5)
        self.forward(50)
        time.sleep(1.6)
        self.stop()
        if dir=="left":
            self.set_dir_servo_angle(30)
        else:
            self.set_dir_servo_angle(-30)
        time.sleep(0.5)
        self.backward(50)
        time.sleep(1.6)
        self.stop()
        self.set_dir_servo_angle(0)
        time.sleep(0.5)
        self.forward(40)
        time.sleep(.8)
        self.stop()


