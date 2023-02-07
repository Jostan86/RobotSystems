from picarx_improved import Picarx
import time

px = Picarx()
while True:
    print(px.get_distance())
    time.sleep(.3)
