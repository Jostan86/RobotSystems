from picarx_improved import Picarx
import time


if __name__ == "__main__":
    px = Picarx()
    x = 0
    while x < 10000:
        x+=1
        print(px.grayscale.get_grayscale_data())
        print(px.grayscale.get_line_status())
        time.sleep(.2)





