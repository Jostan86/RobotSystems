from picarx_improved import Picarx
import time


if __name__ == "__main__":
    # try:

    px = Picarx()
    px.set_dir_servo_angle(0)
    time.sleep(0.5)
    px.forward(40)
    time.sleep(1)
    px.stop()
    px.set_dir_servo_angle(40)
    time.sleep(0.5)
    px.backward(40)
    time.sleep(1.2)
    px.stop()
    px.set_dir_servo_angle(-40)
    time.sleep(0.5)
    px.backward(40)
    time.sleep(1)
    px.stop()
    px.set_dir_servo_angle(0)
    time.sleep(0.5)
    px.stop()
#



