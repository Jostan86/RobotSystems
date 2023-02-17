import time

from picarx_improved import Picarx
from time import sleep
import rossros
import math

class GS_Interpereter:
    def __init__(self, sensitivity=300, line_darker=True):
        # Car will stop if difference between both sensors sets is less than this
        self.stop_threshold = 70
        self.sensitivity = sensitivity
        if line_darker:
            self.polarity = 1
        else:
            self.polarity = -1

    def get_direction(self, sensor_readings):
        """Find the steering angle using the sensor"""

        # Check if all three sensor reading are similar, if so, return stop signal, which I'm using 10 for in this case
        if abs(sensor_readings[0] - sensor_readings[1]) < self.stop_threshold and abs(sensor_readings[2] - sensor_readings[1]) < self.stop_threshold:
            return 10

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

    def producer_consumer(self, sensor_bus):
        """Takes the sensor reading in and returns the interpreter message"""
        sensor_msg = sensor_bus
        interpreter_msg = self.get_direction(sensor_msg)
        return interpreter_msg

class GS_Controller:
    def __init__(self, px):
        self.px = px

    def consumer(self, interpreter_bus):
        """Based on the greyscale interpreter value, sends a command to the car"""
        interpreter_msg = interpreter_bus
        if math.isclose(10, interpreter_msg):
            self.px.stop()
        else:
            px.set_dir_servo_angle(25 * interpreter_msg)
            px.forward(40)


class GS_Sensor:
    def __init__(self, px):
        self.px = px

    def read_sensor(self):
        """Gets a greyscale sensor reading from the car and returns it"""
        return px.get_grayscale_data()

class US_Sensor:
    def __init__(self, px):
        self.px = px

    def read_sensor(self):
        """Gets the distance measurement from the car and returns it"""
        return px.get_distance()

class US_Controller:
    def __init__(self, px, stop_treshold=12):
        self.px = px
        self.stop_threshold = stop_treshold
        self.prev_readings = [False, False, False]

    def controller(self, distance):
        """Controller for the ultrasonic sensor, returns stop signal if three reading in a row are under the stop
        distance threshold"""
        self.prev_readings = self.prev_readings[1:]
        if distance < self.stop_threshold:
            self.prev_readings.append(True)
        else:
            self.prev_readings.append(False)

        if all(self.prev_readings):
            return True
        else:
            return False


if __name__=='__main__':
    # Delay
    sensor_delay = 0.02
    interpreter_delay = 0.02
    controller_delay = 0.02
    US_sensor_delay = 0.1
    US_controller_delay = 0.1
    
    px = Picarx()
    interpreter = GS_Interpereter()
    gs_sensor = GS_Sensor(px)
    gs_controller = GS_Controller(px)
    us_sensor = US_Sensor(px)
    
    gs_sensor_bus = rossros.Bus([0, 0, 0], 'GS_sensor_bus')
    gs_interpreter_bus = rossros.Bus(0, 'GS_interpreter_bus')
    us_sensor_bus = rossros.Bus(0.0, 'US_sensor_bus')


    while True:
        
        us_termination_bus = rossros.Bus(False, 'US_termination_bus')
        time_termination_bus = rossros.Bus(False, 'timer_bus')
        us_controller = US_Controller(px)
        term_busses = (us_termination_bus, time_termination_bus)


        GS_sensor_CP = rossros.Producer(gs_sensor.read_sensor, gs_sensor_bus, termination_buses=term_busses,
                                        delay=sensor_delay)
        GS_interpreter_CP = rossros.ConsumerProducer(interpreter.producer_consumer, gs_sensor_bus, gs_interpreter_bus,
                                                     termination_buses=term_busses, delay=interpreter_delay)
        GS_controller_CP = rossros.Consumer(gs_controller.consumer, gs_interpreter_bus,
                                            termination_buses=term_busses, delay=controller_delay)

        US_controller_CP = rossros.ConsumerProducer(us_controller.controller, us_sensor_bus, term_busses,
                                                    termination_buses=term_busses, delay=US_controller_delay)
        US_sensor_CP = rossros.Producer(us_sensor.read_sensor, us_sensor_bus, termination_buses=term_busses,
                                        delay=US_sensor_delay)

        timer = rossros.Timer(time_termination_bus, duration=3, termination_buses=term_busses)
        rossros.runConcurrently([GS_sensor_CP, GS_interpreter_CP, GS_controller_CP, US_controller_CP, US_sensor_CP, timer])
        px.stop()


        msg = input('Press enter to restart line following, or type stop to end program: ')
        if msg == 'stop':
            break

