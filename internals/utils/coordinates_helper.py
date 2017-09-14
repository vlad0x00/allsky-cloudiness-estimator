from math import sin, cos, tan, asin, acos, atan, atan2, radians, degrees, sqrt
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

def view2pixel(center_of_view, field_of_view, rotation):
    # This is some real Savan magic

    delta_azimuth = degrees(atan(tan(radians(field_of_view / 2)) * cos(radians(rotation))))
    delta_zenithal = degrees(asin(sin(radians(field_of_view / 2)) * sin(radians(rotation))))

    # p and q are projections of center_of_view to field of view sides
    p = (center_of_view[0] - delta_azimuth, center_of_view[1] - delta_zenithal)
    q = (center_of_view[0] + delta_azimuth, center_of_view[1] + delta_zenithal)

    # ps and qs are corresponding s points, where s is intersection of horizon-aligned and rotated field of view
    ps = (center_of_view[0] - delta_azimuth, center_of_view[1])
    qs = (center_of_view[0] + delta_azimuth, center_of_view[1])

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

    # angle between p and ps, and q and qs respectively
    p_angle = degrees(atan2(ps_xy[1] - p_xy[1], ps_xy[0] - p_xy[0]))
    q_angle = degrees(atan2(qs_xy[1] - q_xy[1], qs_xy[0] - q_xy[0]))

    dx = p_xy[0] - q_xy[0]
    dy = p_xy[1] - q_xy[1]
    width = round(sqrt(dx ** 2 + dy ** 2))
    height = round(width * 3 / 4)

    coordinates = []

    x = round(p_xy[0] + height / 2 * cos(radians(p_angle)))
    y = round(p_xy[1] + height / 2 * sin(radians(p_angle)))
    coordinates.append((x, y))

    x = round(p_xy[0] + height / 2 * cos(radians(p_angle + 180)))
    y = round(p_xy[1] + height / 2 * sin(radians(p_angle + 180)))
    coordinates.append((x, y))

    x = round(q_xy[0] + height / 2 * cos(radians(q_angle)))
    y = round(q_xy[1] + height / 2 * sin(radians(q_angle)))
    coordinates.append((x, y))

    x = round(q_xy[0] + height / 2 * cos(radians(q_angle + 180)))
    y = round(q_xy[1] + height / 2 * sin(radians(q_angle + 180)))
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
