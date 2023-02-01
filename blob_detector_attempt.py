# Standard imports
import cv2
import numpy as np
import time
# Read image
im = cv2.imread("img_1.png", cv2.IMREAD_GRAYSCALE)

# Setup SimpleBlobDetector parameters.
params = cv2.SimpleBlobDetector_Params()

# Change thresholds
params.minThreshold = 0
params.maxThreshold = 255

# Filter by Area.
params.filterByArea = True
params.minArea = 1500

# # Filter by Circularity
# params.filterByCircularity = True
# params.minCircularity = 0.1

# Filter by Convexity
params.filterByConvexity = True
params.minConvexity = 0.87

# Filter by Inertia
params.filterByInertia = True
params.minInertiaRatio = 0.01

# Create a detector with the parameters
ver = (cv2.__version__).split('.')
if int(ver[0]) < 3:
    detector = cv2.SimpleBlobDetector(params)
else:
    detector = cv2.SimpleBlobDetector_create(params)
# Show keypoints
keypoints = detector.detect(im)

im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

while True:
    cv2.imshow("Keypoints", im_with_keypoints)
    # cv2.waitKey(0)

    k = cv2.waitKey(1) & 0xFF
    # 27 is the ESC key, which means that if you press the ESC key to exit
    if k == 27:
        break
    time.sleep(.01)

print('quit ...')
cv2.destroyAllWindows()

