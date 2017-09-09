from .utils.coordinates_helper import get_image_coordinates, get_horizontal_coordinates
from .neural_network.NeuralNetwork import NeuralNetwork
from PIL import Image
from datetime import datetime
from matplotlib import path
import scipy.misc
import os
import cv2
import numpy as np
from .utils.sky_extractor import extract_sky
from .utils.fixes import fix_dead_pixels

ORIGINAL_WIDTH = 5184
ORIGINAL_HEIGHT = 3456
CROP_SIZE = 2300
NETWORK_INPUT_SIZE = 512
NETWORK_OUTPUT_SIZE = 128

def estimate_cloudiness(images, coordinates):
    processed_images = []

    for image in images:
        processed_images.append(extract_sky(fix_dead_pixels(image), NETWORK_INPUT_SIZE))
        
    nn = NeuralNetwork()
    cloud_outputs = nn.run(processed_images)
    nn.close()

    processed_outputs = []
    for i in range(cloud_outputs[0].shape[0]):
        cloud_output = cloud_outputs[0][i]

        cloud_output = np.reshape(cloud_output, (NETWORK_OUTPUT_SIZE, NETWORK_OUTPUT_SIZE, 1))
        cloud_output = np.multiply(cloud_output, 255)
        cloud_output = np.stack([ cloud_output, np.copy(cloud_output), np.copy(cloud_output) ], axis = -1)
        cloud_output = np.reshape(cloud_output, (NETWORK_OUTPUT_SIZE, NETWORK_OUTPUT_SIZE, 3))
        cloud_output = scipy.misc.imresize(cloud_output, (CROP_SIZE, CROP_SIZE), interp = 'bicubic')
        cloud_output = np.divide(cloud_output, 255)

        processed_outputs.append(cloud_output)

    for i in range(len(coordinates)):
        coordinates[i] = (
                            coordinates[i][0] - (ORIGINAL_WIDTH - CROP_SIZE) // 2,
                            coordinates[i][1] - (ORIGINAL_HEIGHT - CROP_SIZE) // 2
        )

    polygon = path.Path(coordinates)

    percentages = []
    for cloud_output in processed_outputs:
        points_inside = 0
        cloudiness = 0
        for y in range(cloud_output.shape[0]):
            for x in range(cloud_output.shape[1]):
                if polygon.contains_point((x, y)):
                    cloudiness += cloud_output[x, y, 0]
                    points_inside += 1

        if points_inside > 0:
            percentages.append(cloudiness / points_inside)
        else:
            # TODO: Handle this as error
            percentages.append(0)

    return percentages

def get_image_paths(images_dir, start_datetime, end_datetime):
    paths_and_datetimes = []
    for dirpath, dirnames, filenames in os.walk(images_dir):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            image_datetime = datetime.strptime(Image.open(path)._getexif()[36867], '%Y:%m:%d %H:%M:%S')
            if start_datetime <= image_datetime and image_datetime <= end_datetime:
                paths_and_datetimes.append((path, image_datetime))

    paths_and_datetimes = sorted(paths_and_datetimes, key = lambda x : x[1])

    paths = []
    datetimes = []
    for path_and_datetime in paths_and_datetimes:
        paths.append(path_and_datetime[0])
        datetimes.append(str(path_and_datetime[1]))

    return paths, datetimes

def get_cloudiness_percentages(start_date, end_date, center_of_view, field_of_view, rotation, images_dir):
    paths, datetimes = get_image_paths(images_dir, start_date, end_date)
    horizontal_coordinates = get_horizontal_coordinates(center_of_view, field_of_view, rotation)
    image_coordinates = get_image_coordinates(horizontal_coordinates)

    percentages = []
    for i in range(0, len(paths), 4):
        images = []
        for j in range(4):
            if i + j >= len(paths):
                break
            images.append(scipy.misc.imread(paths[i + j]))

        percentages += estimate_cloudiness(images, image_coordinates)

    return datetimes, percentages
