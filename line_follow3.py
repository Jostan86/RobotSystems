'''
    Line Following program for Picar-X:

    Pay attention to modify the reference value of the grayscale module
    according to the practical usage scenarios.Use the following:
        px.grayscale.reference = 1400
    or
        px.set_grayscale_reference(1400)

'''
from picarx_improved import Picarx
from time import sleep
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time

class GS_Line_Follow_Interpereter:
    def __init__(self, px, sensor_reading_bus, sensitivity=300, line_darker=True):
        self.sensor_readings_bus = sensor_reading_bus
        self.stop_threshold = 70
        self.px = px
        self.sensitivity = sensitivity
        if line_darker:
            self.polarity = 1
        else:
            self.polarity = -1
    def stop_check (self, sensor_reading):
        if abs(sensor_reading[0] - sensor_reading[1]) < self.stop_threshold and abs(sensor_reading[2] - sensor_reading[1]) < self.stop_threshold:

            return True
        else:
            return False

    def get_direction(self, sensor_readings):

        range_max = max(sensor_readings)
        range_min = range_max - self.sensitivity
        if range_min < 0:
            range_min = 0

        for sensor_num, sensor_reading in enumerate(sensor_readings):
            if sensor_reading > range_max:
                sensor_readings[sensor_num] = range_max
            if sensor_reading < range_min:
                sensor_readings[sensor_num] = range_min

        diff_left = self.polarity * ((sensor_readings[0] - sensor_readings[1])/self.sensitivity)
        diff_right = self.polarity * (-(sensor_readings[2] - sensor_readings[1])/self.sensitivity)

        steering_scale = diff_right + diff_left
        return steering_scale

class CV_Line_Follow_Interpreter:
    def __init__(self):
        ...

class Line_Follow_Controller:
    def __init__(self, px, interpreter):
        self.px = px
        self.interpreter = interpreter
    def follow_line(self):
        try:
            while True:
                sensor_readings = px.get_grayscale_data()
                if self.interpreter.stop_check(sensor_readings):
                    self.px.stop()
                else:
                    px.set_dir_servo_angle(25 * self.interpreter.get_direction(sensor_readings))
                    px.forward(40)

                sleep(.01)
        finally:
            px.stop()

class Bus_Structure:
    def __init__(self):
        self.message = None

    def write(self, message):
        self.message = message

    def read(self):
        return self.message


if __name__=='__main__':
    px = Picarx()
    GS_sensor_bus = Bus_Structure()
    # px.set_camera_servo2_angle(-35)
    # camera = CV_Line_Follow_Interpreter()
    # interpreter = GS_Line_Follow_Interpereter(px, GS_sensor_bus)
    # controller = Line_Follow_Controller(px, interpreter)
    # controller.follow_line()



