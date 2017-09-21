from math import sin, cos, tan, asin, acos, atan, atan2, radians, degrees, sqrt, fabs, pi
import os

COORDINATES_FILE = os.path.dirname(os.path.abspath(__file__)) + '/horizontal_coordinates.txt'
ORIGINAL_WIDTH = 5184
ORIGINAL_HEIGHT = 3456
IMAGE_CENTER_X = ORIGINAL_WIDTH / 2
IMAGE_CENTER_Y = ORIGINAL_HEIGHT / 2

def horizontal2pixel(horizontal_coordinates):
    coordinates_file = open(COORDINATES_FILE)

    file_coordinates = []
    lines = coordinates_file.readlines()
    for line in lines:
        line = line.strip().split(',')
        x, y, a, h = int(line[0]), int(line[1]), int(line[2]), int(line[3])
        file_coordinates.append((x, y, a, h))
    file_coordinates = sorted(file_coordinates, key=lambda x : x[3])

    azimuth_offset = 0
    for coordinates in file_coordinates:
        x, y, azimuth = coordinates[0], coordinates[1], coordinates[2]
        x -= IMAGE_CENTER_X
        y -= IMAGE_CENTER_Y

        if x < 10 and y < 10:
            continue

        angle = degrees(atan2(-y, x)) - azimuth
        while angle < -180:
            angle += 360

        azimuth_offset += angle
    azimuth_offset /= len(file_coordinates)

    image_coordinates = []
    for horizontal in horizontal_coordinates:
        azimuth = horizontal[0]
        height = horizontal[1]

        for i in range(len(file_coordinates) - 1):
            x_low, y_low, azimuth_low, height_low = file_coordinates[i]
            x_high, y_high, azimuth_high, height_high = file_coordinates[i + 1]
            if height_low <= height and height <= height_high:
                distance_low = sqrt((IMAGE_CENTER_X - x_low) ** 2 + (IMAGE_CENTER_Y - y_low) ** 2)
                distance_high = sqrt((IMAGE_CENTER_X - x_high) ** 2 + (IMAGE_CENTER_Y - y_high) ** 2)

                if height_low != height_high:
                    distance_factor = (height - height_low) / (height_high - height_low)
                    distance = distance_low + distance_factor * (distance_high - distance_low)
                else:
                    distance = distance_low

                x = IMAGE_CENTER_X + distance * cos(radians(azimuth_offset + azimuth))
                y = ORIGINAL_HEIGHT - (IMAGE_CENTER_Y + distance * sin(radians(azimuth_offset + azimuth)))

                image_coordinates.append((round(x), round(y)))
                break

    return image_coordinates

def angle_between_xy(p1, p2):
    return degrees(atan2(p2[1] - p1[1], p2[0] - p1[0]))

def view2pixel(center_of_view, width_of_view, rotation):
    # This is some real Savan magic

    azimuth = center_of_view[0]
    height = center_of_view[1]
    if height > 89:
        height = 89

    if fabs(rotation) < 1:
        rotation = 1 if rotation >= 0 else -1

    delta_azimuth = degrees(atan(tan(radians(width_of_view / 2)) * cos(radians(rotation))))
    #delta_zenithal = degrees(asin(sin(radians(width_of_view / 2)) * sin(radians(rotation))))
    delta_zenithal = degrees(atan(sin(radians(width_of_view / 2)) * sin(radians(rotation)) * cos(radians(rotation))))

    # p and q are projections of center_of_view to field of view sides
    p = (azimuth - delta_azimuth, height)
    q = (azimuth + delta_azimuth, height)

    # ps and qs are corresponding s points, where s is intersection of horizon-aligned and rotated field of view
    ps = (azimuth - delta_azimuth, height - delta_zenithal)
    qs = (azimuth + delta_azimuth, height + delta_zenithal)

    coordinates = [ p, ps, q, qs]
    for i in range(len(coordinates)):
        if coordinates[i][1] > 90:
            azimuth = coordinates[i][0] + 180
            if azimuth > 360:
                azimuth -= 360
            height = 180 - coordinates[i][1]
            coordinates[i] = (azimuth, height)

    helper_coordinates = horizontal2pixel(coordinates)

    p_xy = helper_coordinates[0]
    ps_xy = helper_coordinates[1]
    q_xy = helper_coordinates[2]
    qs_xy = helper_coordinates[3]

    pqs_angle = angle_between_xy(p_xy, qs_xy)

    c_xy = horizontal2pixel([ center_of_view ])[0]

    dx = p_xy[0] - q_xy[0]
    dy = p_xy[1] - q_xy[1]
    width = sqrt(dx ** 2 + dy ** 2)
    width /= cos(radians(height))
    height = width * 3 / 4

    diagonal = sqrt(width ** 2 + height ** 2)
    diagonal_angle = degrees(acos(width / diagonal))

    coordinates = []

    x = round(c_xy[0] + diagonal / 2 * cos(radians(pqs_angle + diagonal_angle)))
    y = round(c_xy[1] + diagonal / 2 * sin(radians(pqs_angle + diagonal_angle)))
    coordinates.append((x, y))

    x = round(c_xy[0] + diagonal / 2 * cos(radians(pqs_angle - diagonal_angle)))
    y = round(c_xy[1] + diagonal / 2 * sin(radians(pqs_angle - diagonal_angle)))
    coordinates.append((x, y))

    x = round(c_xy[0] + diagonal / 2 * cos(radians(pqs_angle + 180 + diagonal_angle)))
    y = round(c_xy[1] + diagonal / 2 * sin(radians(pqs_angle + 180 + diagonal_angle)))
    coordinates.append((x, y))

    x = round(c_xy[0] + diagonal / 2 * cos(radians(pqs_angle + 180 - diagonal_angle)))
    y = round(c_xy[1] + diagonal / 2 * sin(radians(pqs_angle + 180 - diagonal_angle)))
    coordinates.append((x, y))

    center = (0, 0)
    for x, y in coordinates:
        center = (center[0] + x, center[1] + y)
    center = (center[0] / len(coordinates), center[1] / len(coordinates))

    coordinates_and_angles = []
    for x, y in coordinates:
        angle = degrees(atan2(y - center[1], x - center[0]))
        coordinates_and_angles.append((x, y, angle))
    coordinates_and_angles = sorted(coordinates_and_angles, key=lambda x : x[2])

    coordinates = []
    for x, y, _ in coordinates_and_angles:
        coordinates.append((x, y))

    return coordinates
