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
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time
from sklearn.cluster import KMeans

class GS_Line_Follow_Interpereter:
    def __init__(self, px, sensitivity=300, line_darker=True):
        self.stop_threshold = 70
        self.px = px
        self.sensitivity = sensitivity
        if line_darker:
            self.polarity = 1
        else:
            self.polarity = -1
    def stop_check (self, sensor_reading):
        if abs(sensor_reading[0] - sensor_reading[1]) < self.stop_threshold and abs(sensor_reading[2] - sensor_reading[1]) < self.stop_threshold:

            return True
        else:
            return False

    def get_direction(self, sensor_readings):

        range_max = max(sensor_readings)
        range_min = range_max - self.sensitivity
        if range_min < 0:
            range_min = 0

        for sensor_num, sensor_reading in enumerate(sensor_readings):
            if sensor_reading > range_max:
                sensor_readings[sensor_num] = range_max
            if sensor_reading < range_min:
                sensor_readings[sensor_num] = range_min

        diff_left = self.polarity * ((sensor_readings[0] - sensor_readings[1])/self.sensitivity)
        diff_right = self.polarity * (-(sensor_readings[2] - sensor_readings[1])/self.sensitivity)

        steering_scale = diff_right + diff_left
        return steering_scale

class CV_Line_Follow_Interpreter:
    def __init__(self):
        with PiCamera() as camera:
            print("start color detect")
            camera.resolution = (640, 480)
            camera.framerate = 24
            rawCapture = PiRGBArray(camera, size=camera.resolution)
            time.sleep(2)

            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                img = frame.array
                height = img.shape[0]
                img = img[int(height/4):,:]
                # img, img_2, img_3 = self.color_detect(img, 'red')  # Color detection function
                # cv2.imshow("video", img)  # OpenCV image show
                # cv2.imshow("mask", img_2)  # OpenCV image show
                # cv2.imshow("morphologyEx_img", img_3)  # OpenCV image show
                # rawCapture.truncate(0)  # Release cache
                #
                # k = cv2.waitKey(1) & 0xFF
                # # 27 is the ESC key, which means that if you press the ESC key to exit
                # if k == 27:
                #     break


                # # Convert the image to grayscale
                # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                #
                # # Threshold the grayscale image to get only black pixels
                # _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                #
                # # Find edges using Canny
                # edges = cv2.Canny(thresh, 100, 200)
                #
                # # Perform Hough Transform on the edges
                # lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, maxLineGap=50)
                #
                # # Draw lines on the image
                # for line in lines:
                #     x1, y1, x2, y2 = line[0]
                #     cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                # Convert the image to HSV color space
                # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                #
                # # Define a range of black color in HSV
                # lower_black = np.array([0, 0, 0])
                # upper_black = np.array([180, 255, 40])
                #
                # # Threshold the HSV image to get only black pixels
                # mask = cv2.inRange(hsv, lower_black, upper_black)
                #
                # # Find edges using Canny
                # edges = cv2.Canny(mask, 200, 400)
                #
                # # Perform Hough Transform on the edges
                # lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 25, maxLineGap=10, minLineLength=50)
                # #lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, maxLineGap=20, minLineLength=200)
                #
                #
                # save_fit = []
                # # Draw lines on the image
                # if lines is not None:
                #     for line in lines:
                #         x1, y1, x2, y2 = line[0]
                #         if x1 == x2:
                #             pass
                #         fit = np.polyfit((x1, x2), (y1, y2), 1)
                #         slope = fit[0]
                #         intercept = fit[1]
                #         save_fit.append((slope, intercept))
                #         cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                #
                #     fit_average = np.average(save_fit, axis=0)
                #     if len(save_fit) > 0:
                #         #lane_lines.append(make_points(img, fit_average)
                #
                #         height, width, _ = img.shape
                #         slope, intercept = fit_average
                #         y1 = height
                #         y2 = 0
                #         x1 = max(-width, min(2 * width, int((y1-intercept)/slope)))
                #         x2 = max(-width, min(2 * width, int((y2-intercept)/slope)))
                #
                #         cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                #
                #
                #

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray, (5, 5), 0)
                ret, thresh = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)
                contours, hierarchy = cv2.findContours(thresh.copy(), 1, cv2.CHAIN_APPROX_NONE)
                if len(contours) > 0:

                    c = max(contours, key=cv2.contourArea)

                    M = cv2.moments(c)

                    cx = int(M['m10'] / M['m00'])

                    cy = int(M['m01'] / M['m00'])

                    cv2.line(img, (cx, 0), (cx, 720), (255, 0, 0), 1)

                    cv2.line(img, (0, cy), (1280, cy), (255, 0, 0), 1)

                    cv2.drawContours(img, contours, -1, (0, 255, 0), 1)

                    if cx >= 120:
                        print("Turn Left!")

                    if cx < 120 and cx > 50:
                        print("On Track!")

                    if cx <= 50:
                        print("Turn Right")



                else:

                    print("I don't see the line")


                # Show the result
                cv2.imshow('lines', img)
                # cv2.imshow('mask', mask)
                rawCapture.truncate(0)  # Release cache

                k = cv2.waitKey(1) & 0xFF
                # 27 is the ESC key, which means that if you press the ESC key to exit
                if k == 27:
                    break

            print('quit ...')
            cv2.destroyAllWindows()
            camera.close()

        self.color_dict = {'red': [0, 4], 'orange': [5, 18], 'yellow': [22, 37], 'green': [42, 85], 'blue': [92, 110],
                      'purple': [115, 165],
                      'red_2': [165, 180]}  # Here is the range of H in the HSV color space represented by the color

        self.kernel_5 = np.ones((5, 5), np.uint8)  # Define a 5×5 convolution kernel with element values of all 1.

    def color_detect(self,img, color_name):

        # The blue range will be different under different lighting conditions and can be adjusted flexibly.  H: chroma, S: saturation v: lightness
        resize_img = cv2.resize(img, (160, 120),
                                interpolation=cv2.INTER_LINEAR)  # In order to reduce the amount of calculation, the size of the picture is reduced to (160,120)
        hsv = cv2.cvtColor(resize_img, cv2.COLOR_BGR2HSV)  # Convert from BGR to HSV
        color_type = color_name

        mask = cv2.inRange(hsv, np.array([min( self.color_dict[color_type]), 60, 60]), np.array(
            [max( self.color_dict[color_type]), 255,
             255]))  # inRange()：Make the ones between lower/upper white, and the rest black
        if color_type == 'red':
            mask_2 = cv2.inRange(hsv, ( self.color_dict['red_2'][0], 0, 0), ( self.color_dict['red_2'][1], 255, 255))
            mask = cv2.bitwise_or(mask, mask_2)

        morphologyEx_img = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel_5,
                                            iterations=1)  # Perform an open operation on the image

        # Find the contour in morphologyEx_img, and the contours are arranged according to the area from small to large.
        _tuple = cv2.findContours(morphologyEx_img, cv2.REdeTR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # compatible with opencv3.x and openc4.x
        if len(_tuple) == 3:
            _, contours, hierarchy = _tuple
        else:
            contours, hierarchy = _tuple

        color_area_num = len(contours)  # Count the number of contours

        if color_area_num > 0:
            for i in contours:  # Traverse all contours
                x, y, w, h = cv2.boundingRect(
                    i)  # Decompose the contour into the coordinates of the upper left corner and the width and height of the recognition object

                # Draw a rectangle on the image (picture, upper left corner coordinate, lower right corner coordinate, color, line width)
                if w >= 8 and h >= 8:  # Because the picture is reduced to a quarter of the original size, if you want to draw a rectangle on the original picture to circle the target, you have to multiply x, y, w, h by 4.
                    x = x * 4
                    y = y * 4
                    w = w * 4
                    h = h * 4
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw a rectangular frame
                    cv2.putText(img, color_type, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                                2)  # Add character description

        return img, mask, morphologyEx_img

class Line_Follow_Controller:
    def __init__(self, px, interpreter):
        self.px = px
        self.interpreter = interpreter
    def follow_line(self):
        try:
            while True:
                sensor_readings = px.get_grayscale_data()
                if self.interpreter.stop_check(sensor_readings):
                    self.px.stop()
                else:
                    px.set_dir_servo_angle(25 * self.interpreter.get_direction(sensor_readings))
                    px.forward(40)

                sleep(.01)
        finally:
            px.stop()


def find_2d_midpoint(segment):

    nonzero_rows, nonzero_cols = np.nonzero(segment)
    if len(nonzero_cols) == 0 or len(nonzero_rows) == 0:
        return None
    x_coords = np.arange(segment.shape[1])[nonzero_cols]
    y_coords = np.arange(segment.shape[0])[nonzero_rows]
    weights = segment[nonzero_rows, nonzero_cols]
    return [int(np.average(x_coords, weights=weights)), int(np.average(y_coords, weights=weights))]

def is_line_present(segment, threshold):
    """Check if there is at least some minimum amount of line seen in the segment."""
    mask_sum = np.sum(segment)
    if mask_sum / (segment.shape[0] * segment.shape[1]) < threshold:
        return False
    return True

def is_one_blob(segment, k):
    """Check if there is only one blob of mask."""
    nonzero_pixels = np.transpose(np.nonzero(segment))
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(nonzero_pixels)
    labels = kmeans.labels_
    return len(set(labels)) == 1

if __name__=='__main__':
    px = Picarx()
    px.set_camera_servo2_angle(-25)
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 24
    rawCapture = PiRGBArray(camera, size=camera.resolution)
    time.sleep(2)
    # Capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # Convert the frame to grayscale
        img = frame.array
        height = img.shape[0]
        img = img[int(height/4):,:]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #
        # # Apply thresholding to make the line black and the background white
        _, binary = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)


        num_segments = 6
        contains_line_threshold = 0.05
        contains_line_threshold_k = 1

        # Get the height and width of the image
        height, width = img.shape[:2]

        segment_height = height // num_segments

        for i in range(num_segments):
            segment = binary[i * segment_height: (i + 1) * segment_height, :]
            if not is_line_present(segment, contains_line_threshold) or not is_one_blob(segment, contains_line_threshold_k):
                midpoint = None
                continue
            midpoint = find_2d_midpoint(segment)
            if midpoint is not None:
                midpoint[1] += int(i * (1/num_segments) * height)

            cv2.circle(img, midpoint, 5, (255, 0, 0), -1)
            # cv2.imshow(f"Segment {i + 1}", segment)


        # Show the image
        # cv2.imshow("Line Detection", frame.array)
        cv2.imshow("og", img)
        cv2.imshow("Line Detection", binary)

        # Clear the stream in preparation for the next frame
        rawCapture.truncate(0)

        k = cv2.waitKey(1) & 0xFF
        # 27 is the ESC key, which means that if you press the ESC key to exit
        if k == 27:
            break

    print('quit ...')
    cv2.destroyAllWindows()
    camera.close()




    # camera = CV_Line_Follow_Interpreter()
    # interpreter = GS_Line_Follow_Interpereter(px)
    # controller = Line_Follow_Controller(px, interpreter)
    # controller.follow_line()



