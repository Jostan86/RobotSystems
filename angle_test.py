from picarx_improved import Picarx
import time


if __name__ == "__main__":
    px = Picarx()
    input_string = None
    while input_string != "exit":
        input_string = input("What shall speedy boy do? Your options are:\npark-right - Perform a parallel park to the "
                             "right\npark-left - Perform a parallel park to the left\nk-right - Perform a k turn to "
                             "the right\nk-left - Perform a k turn to the left\nforward - Go forward ~30cm\nbackward - "
                             "Go backward ~30cm")
        if input == "park-right":
            px.motor_commands.parallel_park(side="right")
        elif input == "park-left":
            px.motor_commands.parallel_park(side="left")
        elif input == "k-right":
            px.motor_commands.k_turn(dir="right")
        elif input == "k-left":
            px.motor_commands.k_turn(dir="left")
        elif input == "forward" or input == "backward":
            px.motor_commands.set_dir_servo_angle(0)
            time.sleep(0.3)
            if input == "forward":
                px.motor_commands.forward(40)
            else:
                px.motor_commands.backward(40)
            time.sleep(1)
            px.motor_commands.stop()




