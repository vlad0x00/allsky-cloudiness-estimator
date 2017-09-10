from .utils.coordinates_helper import get_image_coordinates, get_horizontal_coordinates
from .neural_network.NeuralNetwork import NeuralNetwork
from datetime import datetime
from matplotlib import path
import scipy.misc
import os
import numpy as np
from PIL import Image
from .utils.sky_extractor import extract_sky
from .utils.fixes import fix_dead_pixels

ORIGINAL_WIDTH = 5184
ORIGINAL_HEIGHT = 3456
CROP_SIZE = 2300
NETWORK_INPUT_SIZE = 512
NETWORK_OUTPUT_SIZE = 128
BATCH_SIZE = 1

def process_images(images):
    processed_images = []

    for image in images:
        processed = fix_dead_pixels(image)
        processed = extract_sky(processed, NETWORK_INPUT_SIZE)
        processed = np.divide(processed, 255)
        processed_images.append(processed)

    return processed_images

def estimate_cloudiness(image_paths, coordinates):
    percentages = []

    for i in range(len(coordinates)):
        coordinates[i] = (
                            (coordinates[i][0] - (ORIGINAL_WIDTH - CROP_SIZE) // 2)
                            // (CROP_SIZE // NETWORK_OUTPUT_SIZE),
                            (coordinates[i][1] - (ORIGINAL_HEIGHT - CROP_SIZE) // 2)
                            // (CROP_SIZE // NETWORK_OUTPUT_SIZE)
        )
    polygon = path.Path(coordinates)

    neural_network = NeuralNetwork()
    for i in range(0, len(image_paths), BATCH_SIZE):
        images = []
        for j in range(BATCH_SIZE):
            if i + j >= len(image_paths):
                break
            image = scipy.misc.imread(image_paths[i + j])
            image = np.array(image[:, :, ::-1]) # BGR -> RGB
            images.append(image)

        processed_images = process_images(images)
        cloud_outputs = neural_network.run(processed_images)

        for cloud_output in cloud_outputs[0]:
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

    neural_network.close()

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
    image_paths, datetimes = get_image_paths(images_dir, start_date, end_date)
    horizontal_coordinates = get_horizontal_coordinates(center_of_view, field_of_view, rotation)
    image_coordinates = get_image_coordinates(horizontal_coordinates)
    percentages = estimate_cloudiness(image_paths, image_coordinates)

    return datetimes, percentages
