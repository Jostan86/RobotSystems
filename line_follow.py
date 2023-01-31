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

class GS_Line_Follow_Interpereter:
    def __init__(self, px, sensitivity=300, line_darker=True):
        self.px = px
        self.sensitivity = sensitivity
        if line_darker:
            self.polarity = 1
        else:
            self.polarity = -1
    def stop_check (self, sensor_reading):
        if abs(sensor_reading[0] - sensor_reading[1]) < 30 and abs(sensor_reading[2] - sensor_reading[1]) < 30:

            return True
        else:
            return False

    def set_wheel_angle(self, sensor_readings):

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
        angle = 25 * steering_scale
        print(angle)
        return angle

    def follow_line(self):
        try:

            while True:
                sensor_readings = px.get_grayscale_data()
                # gm_state = px.get_line_status(gm_val_list)
                # print("gm_val_list: %s, %s" % (gm_val_list, gm_state))
                if self.stop_check(sensor_readings):
                    self.px.stop()
                else:
                    self.set_wheel_angle(sensor_readings)
                    px.forward(40)
                # if gm_state == "stop":
                #     px.stop()
                # elif gm_state == "right":
                #     px.set_dir_servo_angle(GS_Line_Follow_Interpereter.mapping_func(gm_val_list))
                #     px.forward(50)
                # elif gm_state == "left":
                #     px.set_dir_servo_angle(GS_Line_Follow_Interpereter.mapping_func(gm_val_list))
                #     px.forward(50)
                # elif gm_state == "forward":
                #     px.set_dir_servo_angle(GS_Line_Follow_Interpereter.mapping_func(gm_val_list))
                #     px.forward(50)
                # else:
                #     px.stop()
                sleep(.01)
        finally:
            px.stop()







if __name__=='__main__':
    px = Picarx()
    interpreter = GS_Line_Follow_Interpereter(px)
    interpreter.follow_line()
    # px.set_grayscale_reference(200)
    # try:
    #
    #     while True:
    #         gm_val_list = px.get_grayscale_data()
    #         gm_state = px.get_line_status(gm_val_list)
    #         print("gm_val_list: %s, %s"%(gm_val_list, gm_state))
    #         if gm_state == "stop":
    #             px.stop()
    #         elif gm_state == "right":
    #             px.set_dir_servo_angle(GS_Line_Follow_Interpereter.mapping_func(gm_val_list))
    #             px.forward(50)
    #         elif gm_state == "left":
    #             px.set_dir_servo_angle(GS_Line_Follow_Interpereter.mapping_func(gm_val_list))
    #             px.forward(50)
    #         elif gm_state == "forward":
    #             px.set_dir_servo_angle(GS_Line_Follow_Interpereter.mapping_func(gm_val_list))
    #             px.forward(50)
    #         else:
    #             px.stop()
    #         sleep(.01)
    # finally:
    #     px.stop()

