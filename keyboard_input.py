from picarx_improved import Picarx
import time


if __name__ == "__main__":
    px = Picarx()
    input_string = None
    while input_string != "exit":
        input_string = input("What shall speedy boy do?\nYour options are:\npark-right - Perform a parallel park to the "
                             "right\npark-left - Perform a parallel park to the left\nk-right - Perform a k turn to "
                             "the right\nk-left - Perform a k turn to the left\nforward - Go forward ~30cm\nbackward - "
                             "Go backward ~30cm\n")
        print("You Chose:" + input_string + "\n")
        if input_string == "park-right":
            px.motor_commands.parallel_park(side="right")
        elif input_string == "park-left":
            px.motor_commands.parallel_park(side="left")
        elif input_string == "k-right":
            px.motor_commands.k_turn(dir="right")
        elif input_string == "k-left":
            px.motor_commands.k_turn(dir="left")
        elif input_string == "forward" or input_string == "backward":
            px.motor_commands.set_dir_servo_angle(0)
            time.sleep(0.3)
            if input_string == "forward":
                px.motor_commands.forward(40)
            else:
                px.motor_commands.backward(40)
            time.sleep(1.3)
            px.motor_commands.stop()
        elif input_string == "exit":
            print("Farewell\n")
            time.sleep(1)
        else:
            print("That is not an option!\n")
            time.sleep(1)





