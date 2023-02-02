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
import math

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

class CV_Line_Follow_Interpreter:
    def __init__(self):
        ...
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
    if mask_sum / (segment.shape[0] * segment.shape[1] * 255) < threshold:
        return False
    return True
def is_single_blob(segment, threshold=200):
    """Determine if there are multiple blobs in the segment"""
    # Morphology to get rid of small dots in image
    kernel_open = np.ones((3, 3), np.uint8)
    kernel_close = np.ones((10, 10), np.uint8)
    segment = cv2.morphologyEx(segment, cv2.MORPH_OPEN, kernel_open)
    segment = cv2.morphologyEx(segment, cv2.MORPH_CLOSE, kernel_close)

    # Find blobs
    num_components, labels, stats, centroids = cv2.connectedComponentsWithStats(segment, 8, cv2.CV_32S)

    # Determine how many large blobs there are
    num_components_using = 0
    # Range starts at 1 because first component is the background
    for i in range(1, num_components):
        x, y, w, h, size = stats[i]
        if size > threshold:
            num_components_using += 1
        # cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        # cv2.circle(img, (int(centroids[i][0]), int(centroids[i][1])), 4, (0, 0, 255), -1)

    # If there are more than 1 large blob, return false, otherwise return true
    if num_components_using > 1:
        return False
    return True

def convert_to_relative_pos(point_pixel, image_height, image_width):
    """This function finds the position of a point in the image relative to the robot in the real world. It assumes a
    specific camera angle (-25), and that the camera is facing forwards. I doubt it would be very difficult to make it
    adaptable to different camera angles but that doesn't seem worth the effort at the moment."""
    # Horizontal and vertical FOV of the camera
    vertical_fov = 49 * 0.75
    horizontal_fov = 62.2

    angle_base = 41
    y_angle = angle_base + ((image_height-point_pixel[1]) / image_height) * vertical_fov
    y = 7.2 * np.tan(np.radians(y_angle))
    if point_pixel[0] > image_width/2:
        x_pos = point_pixel[0] - image_width/2
        sign = 1
    else:
        sign = -1
        x_pos = image_width/2 - point_pixel[0]

    x = sign * ((y + 11.6) * np.tan(np.radians(26.41 * (x_pos / (image_width/2)))))
    return (x, y)

def check_for_2_consecutive_nones(list_of_nones):
    non_none_count = 0
    last_non_none_index = None
    for i, val in enumerate(list_of_nones):
        if val is not None:
            non_none_count += 1
            if non_none_count > 2:
                return False
            if last_non_none_index is not None and i - last_non_none_index != 1:
                return False
            last_non_none_index = i
    else:
        return non_none_count == 2

def angles_between_points(points):
    angles = []
    for i in range(1, len(points)):
        x1, y1 = points[i-1]
        x2, y2 = points[i]
        angle = math.atan2(y2 - y1, x2 - x1)
        angles.append(angle - np.pi / 2 )
    return angles

def get_car_directions(midpoints, height, width):
    if all(val is None for val in midpoints):
        print("no line found")
        return None
    elif sum(val is not None for val in midpoints) <= 2:
        print("Can't see enough line")
        return None
    else:
        midpoints_rel_to_car = []
        for midpoint in midpoints:
            if midpoint is not None:
                midpoints_rel_to_car.append(convert_to_relative_pos(midpoint, height, width))

        midpoints_rel_to_car.reverse()

        midpoints_rel_to_car = [(0, -4)] + midpoints_rel_to_car[0:3]
        angles = angles_between_points(midpoints_rel_to_car)
        return np.average(angles)

    # if all(val is None for val in midpoints):
    #     print("no line found")
    #     return [None, None]
    # elif sum(val is not None for val in midpoints) == 1:
    #     print("line appears to be horizontal")
    #     return [np.pi/2, None]
    # elif check_for_2_consecutive_nones(midpoints):
    #     print("2 points found")
    #     midpoints_rel_to_car = [(0, 0)] + midpoints_rel_to_car
    #     return [np.average(angles_between_points(midpoints_rel_to_car)), None]
    # elif sum(val is not None for val in midpoints) == 2:
    #     print("2 non-consecutive points found")
    #     return [np.pi / 2, None]
    # else:
    #     angles = angles_between_points(midpoints_rel_to_car)
    #     for i in range(len(angles) - 1):
    #
    #         angle_change = angles[i + 1] - angles[i]
    #         if abs(angle_change) > np.pi / 6:
    #             midpoints_rel_to_car = midpoints_rel_to_car[:i + 2]
    #             break
    #
    #     if len(midpoints_rel_to_car) == 2:
    #         return [angles_between_points(midpoints_rel_to_car), None]
    #     elif len(midpoints_rel_to_car) <= 4:
    #         return [np.average(angles_between_points(midpoints_rel_to_car)), None]
    #     elif len(midpoints_rel_to_car) > 4:
    #         midpoint = (len(midpoints_rel_to_car) + 1) // 2
    #         points_close = midpoints_rel_to_car[:midpoint]
    #         points_far = midpoints_rel_to_car[midpoint:]
    #         return [np.average(angles_between_points(points_close)), np.average(angles_between_points(points_far))]



if __name__=='__main__':
    px = Picarx()
    px.set_camera_servo2_angle(-25)
    # controller = co
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 24
    rawCapture = PiRGBArray(camera, size=camera.resolution)
    time.sleep(2)
    steering_dir_save = []
    # Capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # cut off top quarter of image (to avoid seeing too much background)
        img = frame.array
        height = img.shape[0]
        img = img[int(height/4):,:]

        # Convert the frame to grayscale, using black tape so this works, otherwise it would have to be different
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to make the line white and the background black
        _, binary = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)

        # Split the image into several segments and evalulate the location of the line for each
        num_segments = 6
        # Threshold of the number of pixels (as a fraction of the total) in a segment that must belong to the line
        # in order for the segment to be considered.
        contains_line_threshold = 0.05
        # Does not consider blobs smaller than this when determining if there are more than 1 blob in a segment
        remove_blob_size = 200

        # Get the height and width of the image
        height, width = img.shape[:2]
        # Calculate the height of each segment
        segment_height = height // num_segments

        # Loop through each segment and determine the centroid of the line in that segment, or in reality, see if there
        # is one and only one large enough blob in the segment, then find the centroid of that blob.
        midpoints_rel_to_car = []
        midpoints = []

        for i in range(num_segments):
            # Make the segment
            segment = binary[i * segment_height: (i + 1) * segment_height, :]
            # Check if there is one largish blob in the segment
            if not is_line_present(segment, contains_line_threshold) or not is_single_blob(segment, threshold=remove_blob_size):
                midpoint = None
                midpoints.append(midpoint)
                continue
            # Find the midpoint of the large blob (line) in the segment
            midpoint = find_2d_midpoint(segment)
            # Add to the y value of the midpoint so that it can be compared relative to the whole image

            midpoint[1] += int(i * (1/num_segments) * height)
            midpoints.append(midpoint)
            # Add a dot where the midpoint was connected on the original image
            cv2.circle(img, midpoint, 5, (255, 0, 0), -1)

        steering_dir = get_car_directions(midpoints, height, width)
        if steering_dir is not None:


            steering_dir = -np.degrees(steering_dir)
            print("collected:" + str(steering_dir))
            now = time.time()
            steering_dir_save.append((steering_dir, now))

            # remove all entries that are older than a second
            steering_dir_save = [(v, t) for v, t in steering_dir_save if now - t < .3]

            # use the steering direction collected about a second ago
            steering_dir = steering_dir_save[0][0] #if data and now - data[-1][1] >= 1 else None

            print("using:" + str(steering_dir))
            print('\n')
            px.set_dir_servo_angle(steering_dir)
            px.forward(40)
        else:
            px.stop()
        # print(get_car_directions(midpoints, height, width))


        cv2.imshow("OG", img)
        # cv2.imshow("binary", binary)
        # cv2.imshow("binary2", binary2)

        # Clear the stream in preparation for the next frame
        rawCapture.truncate(0)

        k = cv2.waitKey(1) & 0xFF
        # 27 is the ESC key, which means that if you press the ESC key to exit
        if k == 27:
            break

    print('quit ...')
    px.stop()
    cv2.destroyAllWindows()
    camera.close()




    # camera = CV_Line_Follow_Interpreter()
    # interpreter = GS_Line_Follow_Interpereter(px)
    # controller = Line_Follow_Controller(px, interpreter)
    # controller.follow_line()



