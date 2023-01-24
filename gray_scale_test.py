from picarx_improved import Picarx
import time


if __name__ == "__main__":
    px = Picarx()
    x = 0
    while x < 15:
        x+=1
        print(px.grayscale.get_grayscale_data())
        time.sleep(1)





