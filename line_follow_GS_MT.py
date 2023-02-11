
from picarx_improved import Picarx
from time import sleep
import concurrent.futures
from readerwriterlock import rwlock

class GS_Line_Follow_Interpereter:
    def __init__(self, sensitivity=300, line_darker=True):
        # Car will stop if difference between both sensors sets is less than this
        self.stop_threshold = 70
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
        if self.stop_check(sensor_readings):
            return None

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

    def producer_consumer(self, sensor_bus, interpreter_bus, delay_time):
        while True:
            sensor_msg = sensor_bus.read()
            interpreter_msg = self.get_direction(sensor_msg)
            interpreter_bus.write(interpreter_msg)
            sleep(delay_time)

class Line_Follow_Controller:
    def __init__(self, px, interpreter, sensor):
        self.px = px
        self.interpreter = interpreter
        self.sensor = sensor

    def consumer(self, interpreter_bus, delay_time):

        while True:
            interpreter_msg = interpreter_bus.read()
            if interpreter_msg is None:
                self.px.stop()
            else:
                px.set_dir_servo_angle(25 * interpreter_msg)
                px.forward(40)

            sleep(delay_time)

class GS_sensor:
    def __init__(self, px):
        self.px = px

    def read_sensor(self):
        return px.get_grayscale_data()

    def producer_sensor(self, sensor_bus, delay_time):
        while True:
            sensor_bus.write(self.read_sensor())
            sleep(delay_time)

class bus_struct:
    def __init__(self):
        self.message = None
        self.lock = rwlock.RWLockWriteD()

    def write(self, message):
        with self.lock.gen_wlock():
            self.message = message

    def read(self):
        with self.lock.gen_rlock():
            message = self.message
        return message


if __name__=='__main__':
    px = Picarx()
    interpreter = GS_Line_Follow_Interpereter()
    sensor = GS_sensor(px)
    controller = Line_Follow_Controller(px, interpreter, sensor)
    sensor_bus = bus_struct()
    interpreter_bus = bus_struct()

    # Delays
    sensor_delay = 0.05
    interpreter_delay = 0.05
    controller_delay = 0.05

    input("Press enter to begin")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        eSensor = executor.submit(sensor.producer_sensor, sensor_bus, sensor_delay)
        eInterpreter = executor.submit(interpreter.producer_consumer, sensor_bus, interpreter_bus, interpreter_delay)
        eController = executor.submit(controller.consumer, interpreter_bus, controller_delay)






