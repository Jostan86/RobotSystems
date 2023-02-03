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

class CV_Interpreter:
    def __init__(self):
        # Threshold for converting the gray scale image into binary when looking for the line
        self.gray_scale_threshold = 60
        # number of segments to segment image into when looking for line
        self.num_segments = 6
        # Threshold of the number of pixels (as a fraction of the total) in a segment that must belong to the line
        # in order for the segment to be considered.
        self.contains_line_threshold = 0.05
        # Does not consider blobs smaller than this when determining if there are more than 1 blob in a segment
        self.remove_blob_size = 200

    def find_2d_midpoint(self, segment):

        nonzero_rows, nonzero_cols = np.nonzero(segment)
        if len(nonzero_cols) == 0 or len(nonzero_rows) == 0:
            return None
        x_coords = np.arange(segment.shape[1])[nonzero_cols]
        y_coords = np.arange(segment.shape[0])[nonzero_rows]
        weights = segment[nonzero_rows, nonzero_cols]
        return [int(np.average(x_coords, weights=weights)), int(np.average(y_coords, weights=weights))]

    def is_line_present(self, segment, threshold):
        """Check if there is at least some minimum amount of line seen in the segment."""
        mask_sum = np.sum(segment)
        if mask_sum / (segment.shape[0] * segment.shape[1] * 255) < threshold:
            return False
        return True
    def is_single_blob(self, segment, threshold=200):
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

    def convert_to_relative_pos(self, point_pixel, image_height, image_width):
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

    def check_for_2_consecutive_non_nones(self, list_of_nones):
        """Checks to see if there are 2 consecutive non None values in a list, and only 2 values total, returns true if
        these conditions are met. This function is actually being used at the moment."""
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

    def angles_between_points(self, points):
        """Find the angles between a list of points"""
        angles = []
        for i in range(1, len(points)):
            x1, y1 = points[i-1]
            x2, y2 = points[i]
            angle = math.atan2(y2 - y1, x2 - x1)
            angles.append(angle - np.pi / 2 )
        return angles

    def get_car_directions(self, midpoints, height, width):
        """Get the angle based on the midpoints found in the image"""

        # If no points are found or only 1 or 2, consider robot lost
        if all(val is None for val in midpoints):
            print("no line found")
            return None
        elif sum(val is not None for val in midpoints) <= 2:
            print("Can't see enough line")
            return None

        # If three or more are seen, convert the midpoints to geometry relative to the car, add a point at the base of the
        # front steering, and then find the average of all the angles between the segments.
        else:
            midpoints_rel_to_car = []
            for midpoint in midpoints:
                if midpoint is not None:
                    midpoints_rel_to_car.append(self.convert_to_relative_pos(midpoint, height, width))
            midpoints_rel_to_car.reverse()
            midpoints_rel_to_car = [(0, -6)] + midpoints_rel_to_car[0:3]
            angles = self.angles_between_points(midpoints_rel_to_car)
            return np.average(angles)

    def get_angle_from_frame(self, camera_frame):
        # cut off top quarter of image (to avoid seeing too much background)
        img = camera_frame
        height = img.shape[0]
        img = img[int(height / 4):, :]

        # Convert the frame to grayscale, using black tape so this works, otherwise it would have to be different
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to make the line white and the background black
        _, binary = cv2.threshold(gray, self.gray_scale_threshold, 255, cv2.THRESH_BINARY_INV)

        # Get the height and width of the image
        height, width = img.shape[:2]
        # Calculate the height of each segment
        segment_height = height // self.num_segments

        # Loop through each segment and determine the centroid of the line in that segment, or in reality, see if there
        # is one and only one large enough blob in the segment, then find the centroid of that blob.
        midpoints_rel_to_car = []
        midpoints = []
        for i in range(self.num_segments):
            # Make the segment
            segment = binary[i * segment_height: (i + 1) * segment_height, :]
            # Check if there is one largish blob in the segment
            if not self.is_line_present(segment, self.contains_line_threshold) or not \
                    self.is_single_blob(segment, threshold=self.remove_blob_size):
                midpoint = None
                midpoints.append(midpoint)
                continue

            # Find the midpoint of the large blob (line) in the segment
            midpoint = self.find_2d_midpoint(segment)

            # Add to the y value of the midpoint so that it can be compared relative to the whole image
            midpoint[1] += int(i * (1 / self.num_segments) * height)
            midpoints.append(midpoint)

            # Add a dot where the midpoint was connected on the original image
            cv2.circle(img, midpoint, 5, (255, 0, 0), -1)

        steering_dir = self.get_car_directions(midpoints, height, width)
        return steering_dir, img

class CV_controller:
    def __init__(self, px, interpreter):
        self.delay_time = 0.3

        self.move_speed = 40

        # Angle camera faces downward, there are some hard coded aspects in converting a seen point to relative geometry
        # that will break if this is changed
        self.camera_angle = -25

        self.px = px
        self.interpreter = interpreter

        self.px.set_camera_servo2_angle(self.camera_angle)
        self.camera = PiCamera()
        self.camera.resolution = (640, 480)
        self.camera.framerate = 24
        self.rawCapture = PiRGBArray(self.camera, size=self.camera.resolution)
        time.sleep(2)
        self.steering_dir_save = []

        for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):

            img = frame.array
            steering_dir, img = interpreter.get_angle_from_frame(self, img)

            # Use the steering direction obtained from the image
            if steering_dir is not None:
                # Convert to degrees
                steering_dir = -np.degrees(steering_dir)
                print("collected:" + str(steering_dir))

                # Append it to the list of saved steering angles, along with the collection time
                now = time.time()
                self.steering_dir_save.append((steering_dir, now))

                # remove all entries that are older than the set delay time
                self.steering_dir_save = [(v, t) for v, t in self.steering_dir_save if now - t < self.delay_time]

                # use the steering direction collected delay_time ago
                steering_dir = self.steering_dir_save[0][0]

                print("using:" + str(steering_dir))
                print('\n')

                self.px.set_dir_servo_angle(steering_dir)
                self.px.forward(self.move_speed)

            else:
                self.px.stop()

            # cv2.imshow("OG", img)

            # Clear the stream in preparation for the next frame
            self.rawCapture.truncate(0)

            k = cv2.waitKey(1) & 0xFF
            # 27 is the ESC key, which means that if you press the ESC key to exit
            if k == 27:
                break

        print('quit ...')
        self.px.stop()
        cv2.destroyAllWindows()
        self.camera.close()



if __name__=='__main__':

    px = Picarx()
    interpreter = CV_Interpreter()
    controller = CV_controller(px, interpreter)






