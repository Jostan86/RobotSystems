
import logging
# from logdecorator import log_on_start , log_on_end , log_on_error
import os
import time
import atexit
import math

try :
    from robot_hat import *
    from robot_hat import reset_mcu
    reset_mcu()
    time.sleep (0.2)
except ImportError :
    print (" This computer does not appear to be a PiCar - X system ( robot_hat is not present ) . Shadowing hardware "
           "calls with substitute functions ")
    from sim_robot_hat import *

# from picarx_motor_commands import MotorCommands

logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO, datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)

# user and User home directory
User = os.popen('echo ${SUDO_USER:-$LOGNAME}').readline().strip()
UserHome = os.popen('getent passwd %s | cut -d: -f 6'%User).readline().strip()
config_file = '%s/.config/picar-x/picar-x.conf'%UserHome

class Picarx(object):

    # servo_pins: camera_servo_1, camera_servo_2
    # grayscale_pins: 3 adc channels
    # ultrasonic_pins: tring, echo
    # config: path of config file
    def __init__(self, 
                servo_pins:list=['P0', 'P1'],
                grayscale_pins:list=['A0', 'A1', 'A2'],
                ultrasonic_pins:list=['D2','D3'],
                config:str=config_file,
                ):

        # config_flie
        self.config_flie = fileDB(config, 774, User)
        # servos init 
        self.camera_servo_pin1 = Servo(PWM(servo_pins[0]))
        self.camera_servo_pin2 = Servo(PWM(servo_pins[1]))   
        self.cam_cal_value_1 = int(self.config_flie.get("picarx_cam_servo1", default_value=0))
        self.cam_cal_value_2 = int(self.config_flie.get("picarx_cam_servo2", default_value=0))
        self.camera_servo_pin1.angle(self.cam_cal_value_1)
        self.camera_servo_pin2.angle(self.cam_cal_value_2)

        # grayscale module init
        # usage: self.grayscale.get_grayscale_data()
        adc0, adc1, adc2 = grayscale_pins
        self.grayscale = Grayscale_Module(adc0, adc1, adc2, reference=1000)
        # ultrasonic init
        # usage: distance = self.ultrasonic.read()
        tring, echo= ultrasonic_pins
        self.ultrasonic = Ultrasonic(Pin(tring), Pin(echo))

        self.motor_commands = MotorCommands()
        
    def camera_servo1_angle_calibration(self,value):
        self.cam_cal_value_1 = value
        self.config_flie.set("picarx_cam_servo1", "%s"%value)
        self.camera_servo_pin1.angle(value)

    def camera_servo2_angle_calibration(self,value):
        self.cam_cal_value_2 = value
        self.config_flie.set("picarx_cam_servo2", "%s"%value)
        self.camera_servo_pin2.angle(value)

    def set_camera_servo1_angle(self,value):
        self.camera_servo_pin1.angle(-1*(value + -1*self.cam_cal_value_1))

    def set_camera_servo2_angle(self,value):
        self.camera_servo_pin2.angle(-1*(value + -1*self.cam_cal_value_2))

    def get_distance(self):
        return self.ultrasonic.read()

    def set_grayscale_reference(self, value):
        self.get_grayscale_reference = value
        
    def get_grayscale_data(self):
        return list.copy(self.grayscale.get_grayscale_data())

    def get_line_status(self,gm_val_list):
        return str(self.grayscale.get_line_status(gm_val_list))

    def forward_distance(self, distance):
        ...

    def backward_distance(self, distance):
        ...



if __name__ == "__main__":
    px = Picarx()
    px.motor_commands.forward(50)
    time.sleep(1)
    px.motor_commands.stop()
