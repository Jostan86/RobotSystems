
from picarx_improved import Picarx
from time import sleep
import rossros
import math
class GS_Line_Follow_Interpereter:
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

        sensor_msg = sensor_bus
        interpreter_msg = self.get_direction(sensor_msg)
        return interpreter_msg

class Line_Follow_Controller:
    def __init__(self, px):
        self.px = px

    def consumer(self, interpreter_bus):

        interpreter_msg = interpreter_bus
        if math.isclose(10, interpreter_msg):
            self.px.stop()
        else:
            px.set_dir_servo_angle(25 * interpreter_msg)
            px.forward(40)


class GS_sensor:
    def __init__(self, px):
        self.px = px

    def read_sensor(self):
        return px.get_grayscale_data()

class US_sensor:
    def __init__(self, px):
        self.px = px

    def read_US_sensor(self):
        return px.get_distance()

class US_controller:
    def __init__(self, stop_treshold=8):
        self.stop_threshold = stop_treshold

    def US_controller(self, distance):
        if distance > self.stop_threshold:
            px.stop()





if __name__=='__main__':
    px = Picarx()
    interpreter = GS_Line_Follow_Interpereter()
    gs_sensor = GS_sensor(px)
    gs_controller = Line_Follow_Controller(px)
    gs_sensor_bus = rossros.Bus([0,0,0], 'GS_sensor_bus')
    gs_interpreter_bus = rossros.Bus(0, 'GS_interpreter_bus')
    us_sensor = US_sensor(px)
    us_controller = US_controller(px)
    us_sensor_bus = rossros.Bus(0.0, 'US_sensor_bus')

    # Delay
    sensor_delay = 0.02
    interpreter_delay = 0.02
    controller_delay = .02

    GS_sensor = rossros.Producer(gs_sensor.read_sensor, gs_sensor_bus, delay=sensor_delay)
    GS_interpreter = rossros.ConsumerProducer(interpreter.producer_consumer, gs_sensor_bus, gs_interpreter_bus, delay=interpreter_delay)
    GS_controller = rossros.Consumer(gs_controller.consumer, gs_interpreter_bus, delay=controller_delay)
    rossros.runConcurrently([GS_sensor, GS_interpreter, GS_controller])

    # with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    #     eSensor = executor.submit(sensor.producer_sensor, sensor_bus, sensor_delay)
    #     eInterpreter = executor.submit(interpreter.producer_consumer, sensor_bus, interpreter_bus, interpreter_delay)
    #     eController = executor.submit(controller.consumer, interpreter_bus, controller_delay)
