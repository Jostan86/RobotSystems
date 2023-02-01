# Standard imports
import cv2
import numpy as np
import time
# Read image
im = cv2.imread("img2.png", cv2.IMREAD_GRAYSCALE)
_, im = cv2.threshold(im, 100, 255, cv2.THRESH_BINARY_INV)
im = 255-im
kernel = np.ones((10,10),np.uint8)
# Setup SimpleBlobDetector parameters.
im = cv2.morphologyEx(im, cv2.MORPH_OPEN, kernel)


# Get the connected components
num_components, labels, stats, centroids = cv2.connectedComponentsWithStats(im, 4, cv2.CV_32S)
for i in range(1, num_components):
    x, y, w, h, size = stats[i]
    cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2)
    cv2.circle(im, (int(centroids[i][0]), int(centroids[i][1])), 4, (0, 0, 255), -1)

while True:
    cv2.imshow("Keypoints", im)
    # cv2.waitKey(0)

    k = cv2.waitKey(1) & 0xFF
    # 27 is the ESC key, which means that if you press the ESC key to exit
    if k == 27:
        break
    time.sleep(.01)

print('quit ...')
cv2.destroyAllWindows()

