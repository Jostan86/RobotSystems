from picarx_improved import Picarx
import time


if __name__ == "__main__":
    # try:
    px = Picarx()
    px.set_dir_servo_angle(0)
    time.sleep(1)
    px.forward(40)
    time.sleep(8)




