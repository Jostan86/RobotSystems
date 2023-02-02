import numpy as np
import math
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

def angle_between_two_points(points):
    angle = np.atan2(points[1][1] - points[0][1], points[1][0] - points[0][0])
    return angle

def angles_between_points(points):
    angles = []
    for i in range(1, len(points)):
        x1, y1 = points[i-1]
        x2, y2 = points[i]
        angle = math.atan2(y2 - y1, x2 - x1)
        angles.append(angle-np.pi/2)
    return angles

if __name__=='__main__':
    # midpoints_rel_to_car = [(-9.52, 26.3), (-6.8, 18.3), (-5.6, 13.8), (-4.8, 10.8), (-4.1, 8.6), (-3.4, 6.97)]
    midpoints_rel_to_car = [(-9.52, 26.3), (-6.8, 18.3), (-5.6, 13.8), (4.8, 10.8), (-4.1, 8.6), (-3.4, 6.97)]
    midpoints_rel_to_car.reverse()
    angles = angles_between_points(midpoints_rel_to_car)
    print(angles)
    for i in range(len(angles) - 1):

        angle_change = angles[i + 1] - angles[i]
        if abs(angle_change) > np.pi / 6:
            midpoints_rel_to_car = midpoints_rel_to_car[:i+2]
            break
    print(midpoints_rel_to_car)
    print(np.average(angles_between_points(midpoints_rel_to_car)))
    # midpoint = (len(list_of_values) + 1) // 2
    # first_half = list_of_values[:midpoint]
    # second_half = list_of_values[midpoint:]
    # print(first_half)
    # print(second_half)