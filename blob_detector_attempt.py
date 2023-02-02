import cv2
import numpy as np


def perspective_transform(image, src, dst):
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(image, M, (382, 269))
    return warped


def find_position(image, src, dst, object_pt):
    # Perform the perspective transform
    M = cv2.getPerspectiveTransform(src, dst)
    warped = perspective_transform(image, src, dst)

    # Find the position of the object in the transformed image
    object_pt_transformed = np.dot(M, np.array([object_pt[0], object_pt[1], 1]))
    object_pt_transformed = object_pt_transformed / object_pt_transformed[2]

    return object_pt_transformed[0:2]


if __name__ == '__main__':
    # Load the image
    image = cv2.imread('img3.png')

    # Define the source and destination points for the perspective transform
    src = np.float32([[0, 0], [0, image.shape[0]], [image.shape[1], image.shape[0]], [image.shape[1], 0]])
    # dst = np.float32([[100, 0], [0, image.shape[0]], [image.shape[1] - 100, image.shape[0]], [image.shape[1], 0]])
    dst = np.float32([[0, 0], [134, 269], [248, 269], [382, 0]])

    # Define the position of the object in the original image
    object_pt = [320, 180]

    resmatrix = cv2.getPerspectiveTransform(src, dst)
    resultimage = cv2.warpPerspective(image, resmatrix, (382, 269))

    # object_pt_transformed = np.dot(resmatrix, np.array([object_pt[0], object_pt[1], 1]))
    # object_pt_transformed = object_pt_transformed / object_pt_transformed[2]

    # Find the position of the object relative to the base of the camera
    object_position = find_position(image, src, dst, object_pt)

    print("Object position relative to the base of the camera:", object_position)
    # importing the module cv2 and numpy

    while True:
    #     # reading the image which is to be transformed
    #     image = cv2.imread('img3.png')
    #     # specifying the points in the source image which is to be transformed to the corresponding points in the destination image
    #     srcpts = np.float32([[0, 0], [0, image.shape[0]], [image.shape[1], image.shape[0]], [image.shape[1], 0]])
    #     destpts = np.float32([[0, 0], [134, 268], [382-134, 268], [382, 0]])
    #     # applying PerspectiveTransform() function to transform the perspective of the given source image to the corresponding points in the destination image
    #     resmatrix = cv2.getPerspectiveTransform(srcpts, destpts)
    #     # applying warpPerspective() function to display the transformed image
    #     resultimage = cv2.warpPerspective(image, resmatrix, (382, 331))
    #     # displaying the original image and the transformed image as the output on the screen
        cv2.imshow('frame', image)
        cv2.imshow('frame1', resultimage)
        if cv2.waitKey(24) == 27:
            break


