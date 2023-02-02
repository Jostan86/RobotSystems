
from picarx_improved import Picarx
from time import sleep

class GS_Line_Follow_Interpereter:
    def __init__(self, px, sensitivity=300, line_darker=True):
        # Car will stop if difference between both sensors sets is less than this
        self.stop_threshold = 70
        self.px = px
        self.sensitivity = sensitivity
        if line_darker:
            self.polarity = 1
        else:
            self.polarity = -1
    def stop_check (self, sensor_reading):
        """Stop the car if it doesn't see any difference in the readings"""
        if abs(sensor_reading[0] - sensor_reading[1]) < self.stop_threshold and abs(sensor_reading[2] - sensor_reading[1]) < self.stop_threshold:
            return True
        else:
            return False

    def get_direction(self, sensor_readings):
        """Find the steering angle using the sensor"""

        # Set max range as the max reading
        range_max = max(sensor_readings)
        # Set min range as the max minus the sensitivity
        range_min = range_max - self.sensitivity
        # Don't allow a negative range
        if range_min < 0:
            range_min = 0


        for sensor_num, sensor_reading in enumerate(sensor_readings):
            # If a reading is below the minimum, change it
            if sensor_reading < range_min:
                sensor_readings[sensor_num] = range_min

        # Find the difference between each pair of sensors (left + middle, right + middle)
        diff_left = self.polarity * ((sensor_readings[0] - sensor_readings[1])/self.sensitivity)
        diff_right = self.polarity * (-(sensor_readings[2] - sensor_readings[1])/self.sensitivity)

        # Calculate the steering scale on range of -1 - 1
        steering_scale = diff_right + diff_left
        return steering_scale

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


if __name__=='__main__':
    px = Picarx()
    interpreter = GS_Line_Follow_Interpereter(px)
    controller = Line_Follow_Controller(px, interpreter)
    controller.follow_line()



