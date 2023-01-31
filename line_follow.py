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

def mapping_func(sensor_reading):

    range_max = 400
    range_min = 120
    range = range_max - range_min
    for sensor_num, sensor_reading in enumerate(sensor_reading):
        if sensor_reading > range_max:
            sensor_reading[sensor_num] = range_max
        if sensor_reading < range_min:
            sensor_reading[sensor_num] = range_min

    diff_left = (sensor_reading[0] - sensor_reading[1])/range
    diff_right = -(sensor_reading[2] - sensor_reading[1])/range

    steering_scale = (diff_right + diff_left) / 2
    angle = 80 * steering_scale
    print(angle)
    return angle





if __name__=='__main__':
    px = Picarx()
    px.set_grayscale_reference(200)
    try:

        while True:
            gm_val_list = px.get_grayscale_data()
            gm_state = px.get_line_status(gm_val_list)
            print("gm_val_list: %s, %s"%(gm_val_list, gm_state))
            if gm_state == "stop":
                px.stop()
            elif gm_state == "right":
                px.set_dir_servo_angle(mapping_func(gm_val_list))
                px.forward(50)
            elif gm_state == "left":
                px.set_dir_servo_angle(mapping_func(gm_val_list))
                px.forward(50)
            elif gm_state == "forward":
                px.set_dir_servo_angle(mapping_func(gm_val_list))
                px.forward(50)
            else:
                px.stop()
            sleep(.01)
    finally:
        px.stop()

