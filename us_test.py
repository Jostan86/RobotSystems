from picarx_improved import Picarx
import time


if __name__ == "__main__":
    px = Picarx()
    x = 0
    while x < 10000:
        x+=1
        distance = px.get_distance()
        print(distance)

        time.sleep(.2)