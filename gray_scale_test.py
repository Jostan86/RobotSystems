from picarx_improved import Picarx
import time


if __name__ == "__main__":
    px = Picarx()
    x = 0
    while x < 10000:
        x+=1
        gl_list = px.grayscale.get_grayscale_data()
        print(gl_list)
        print(px.grayscale.get_line_status(gl_list))
        time.sleep(.2)





