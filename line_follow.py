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


# px = Picarx(grayscale_pins=['A0', 'A1', 'A2'])
# px.set_grayscale_reference(200)
# px.grayscale.reference = 1400
# px.set_grayscale_reference(200)
# last_state = None
# current_state = None
# px_power = 10
# offset = 20


# def outHandle():
#     global last_state, current_state
#     if last_state == 'left':
#         px.set_dir_servo_angle(-30)
#         px.backward(10)
#     elif last_state == 'right':
#         px.set_dir_servo_angle(30)
#         px.backward(10)
#     while True:
#         gm_val_list = px.get_grayscale_data()
#         gm_state = px.get_line_status(gm_val_list)
#         print("outHandle gm_val_list: %s, %s"%(gm_val_list, gm_state))
#         currentSta = gm_state
#         if currentSta != last_state:
#             break
#     sleep(0.001)
def mapping_func(sensor_reading):
    range_max = 300
    range_min = 100
    range = range_max - range_min
    diff_left = (sensor_reading[0] - sensor_reading[1])/range
    diff_right = -(sensor_reading[2] - sensor_reading[1])/range

    steering_scale = (diff_right + diff_left) / 2
    angle = 80 * steering_scale
    print(angle)
    return angle





if __name__=='__main__':
    px = Picarx()
    try:

        while True:
            gm_val_list = px.get_grayscale_data()
            gm_state = px.get_line_status(gm_val_list)
            print("gm_val_list: %s, %s"%(gm_val_list, gm_state))
            if gm_state == "stop":
                px.stop()
            elif gm_state == "right":
                px.set_dir_servo_angle(mapping_func(gm_val_list))
                px.forward(30)
            elif gm_state == "left":
                px.set_dir_servo_angle(mapping_func(gm_val_list))
                px.forward(30)
            elif gm_state == "forward":
                px.set_dir_servo_angle(mapping_func(gm_val_list))
                px.forward(30)
            else:
                px.stop()
            sleep(.01)
    finally:
        px.stop()

    # try:
    #     while True:
    #         gm_val_list = px.get_grayscale_data()
    #         gm_state = px.get_line_status(gm_val_list)
    #         print("gm_val_list: %s, %s"%(gm_val_list, gm_state))
    #
    #         if gm_state != "stop":
    #             last_state = gm_state
    #
    #         if gm_state == 'forward':
    #             px.set_dir_servo_angle(0)
    #             px.forward(px_power)
    #         elif gm_state == 'left':
    #             px.set_dir_servo_angle(offset)
    #             px.forward(px_power)
    #         elif gm_state == 'right':
    #             px.set_dir_servo_angle(-offset)
    #             px.forward(px_power)
    #         else:
    #             outHandle()
    # finally:
    #     px.stop()
