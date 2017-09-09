import math
import os

COORDINATES_FILE = os.path.dirname(os.path.abspath(__file__)) + '/horizontal_coordinates.txt'
ORIGINAL_WIDTH = 5184
ORIGINAL_HEIGHT = 3456
IMAGE_CENTER_X = ORIGINAL_WIDTH / 2
IMAGE_CENTER_Y = ORIGINAL_HEIGHT / 2

def get_image_coordinates(horizontal_coordinates):
    coordinates_file = open(COORDINATES_FILE)

    file_coordinates = []
    lines = coordinates_file.readlines()
    for line in lines:
        line = line.strip().split(',')
        x, y, a, h = int(line[0]), int(line[1]), int(line[2]), int(line[3])
        file_coordinates.append((x, y, a, h))
    file_coordinates = sorted(file_coordinates, key = lambda x : x[3])

    azimuth_offset = 0
    for coordinates in file_coordinates:
        x, y, azimuth = coordinates[0], coordinates[1], coordinates[2]
        x -= IMAGE_CENTER_X
        y -= IMAGE_CENTER_Y

        angle = math.degrees(math.atan2(-y, x)) - azimuth
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
                distance_low = math.sqrt((IMAGE_CENTER_X - x_low) ** 2 + (IMAGE_CENTER_Y - y_low) ** 2)
                distance_high = math.sqrt((IMAGE_CENTER_X - x_high) ** 2 + (IMAGE_CENTER_Y - y_low) ** 2)

                if height_low != height_high:
                    distance_factor = (height - height_low) / (height_high - height_low)
                    distance = distance_low + distance_factor * (distance_high - distance_low)
                else:
                    distance = distance_low

                x = IMAGE_CENTER_X + distance * math.cos(math.radians(azimuth_offset + azimuth))
                y = ORIGINAL_HEIGHT - (IMAGE_CENTER_Y + distance * math.sin(math.radians(azimuth_offset + azimuth)))

                image_coordinates.append((round(x), round(y)))
                break

    return image_coordinates

def get_horizontal_coordinates(center_of_view, field_of_view, rotation):
    # TODO: Add Savan magic
    return [ (10, 20), (80, 20), (80, 70), (10, 70) ]
