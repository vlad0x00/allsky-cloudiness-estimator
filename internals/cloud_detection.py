from .utils.coordinates_helper import get_image_coordinates, get_horizontal_coordinates
from .neural_network.NeuralNetwork import NeuralNetwork
from datetime import datetime
from matplotlib import path
import scipy.misc
import numpy as np
from PIL import Image
from .utils.sky_extractor import extract_sky
from .utils.fixes import fix_dead_pixels
from os import walk
from os.path import join, splitext
import matplotlib.patches as patches
import matplotlib.pyplot as plt

IMAGES_EXT = '.jpg'
ORIGINAL_WIDTH = 5184
ORIGINAL_HEIGHT = 3456
CROP_SIZE = 2300
NETWORK_INPUT_SIZE = 512
NETWORK_OUTPUT_SIZE = 128
BATCH_SIZE = 1

def preprocess_images(images):
    preprocessed_images = []

    for image in images:
        preprocessed = fix_dead_pixels(image)
        preprocessed = extract_sky(preprocessed, NETWORK_INPUT_SIZE)
        preprocessed = np.divide(preprocessed, 255)
        preprocessed_images.append(preprocessed)

    return preprocessed_images

def estimate_cloudiness(image_paths, coordinates, display_images):
    percentages = []

    input_coordinates = []
    output_coordinates = []
    for x, y in coordinates:
        input_coordinates.append((
                            (x - (ORIGINAL_WIDTH - CROP_SIZE) // 2)
                            // (CROP_SIZE // NETWORK_INPUT_SIZE),
                            (y - (ORIGINAL_HEIGHT - CROP_SIZE) // 2)
                            // (CROP_SIZE // NETWORK_INPUT_SIZE)
        ))

        output_coordinates.append((
                            (x - (ORIGINAL_WIDTH - CROP_SIZE) // 2)
                            // (CROP_SIZE // NETWORK_OUTPUT_SIZE),
                            (y - (ORIGINAL_HEIGHT - CROP_SIZE) // 2)
                            // (CROP_SIZE // NETWORK_OUTPUT_SIZE)
        ))
    output_polygon = path.Path(output_coordinates)

    #neural_network = NeuralNetwork()
    for i in range(0, len(image_paths), BATCH_SIZE):
        images = []
        for j in range(BATCH_SIZE):
            if i + j >= len(image_paths):
                break
            image = scipy.misc.imread(image_paths[i + j])
            image = np.array(image[:, :, ::-1]) # BGR -> RGB
            images.append(image)

        preprocessed_images = preprocess_images(images)
        #cloud_outputs = neural_network.run(preprocessed_images)

        #for i, cloud_output in enumerate(cloud_outputs[0]):
        for i, cloud_output in enumerate(preprocessed_images):
            '''
            points_inside = 0
            cloudiness = 0
            for y in range(cloud_output.shape[0]):
                for x in range(cloud_output.shape[1]):
                    if output_polygon.contains_point((x, y)):
                        cloudiness += cloud_output[x, y, 0]
                        points_inside += 1

            if points_inside > 0:
                percentages.append(cloudiness / points_inside)
            else:
                print('ERROR: Invalid coordinates or image')
                percentages.append(-1)
            '''

            if display_images:
                plt.figure(figsize=(10, 5))

                subplot = plt.subplot(121)
                plt.imshow(preprocessed_images[i])
                input_polygon_patch = patches.Polygon(np.array(input_coordinates))
                input_polygon_patch.set_fill(False)
                input_polygon_patch.set_linewidth(0.3)
                input_polygon_patch.set_color('#eeefff')
                subplot.add_patch(input_polygon_patch)
                plt.title('Cloudiness: ' + '20%')

                subplot = plt.subplot(122)
                plt.imshow(preprocessed_images[i])
                input_polygon_patch = patches.Polygon(np.array(input_coordinates))
                input_polygon_patch.set_fill(False)
                input_polygon_patch.set_linewidth(0.3)
                input_polygon_patch.set_color('#eeefff')
                subplot.add_patch(input_polygon_patch)

                plt.show()
    #neural_network.close()

    return percentages

def get_image_paths(images_dir, start_datetime, end_datetime):
    paths_and_datetimes = []
    for dirpath, dirnames, filenames in walk(images_dir):
        for filename in filenames:
            root, ext = splitext(filename)

            if ext.lower() == IMAGES_EXT:
                path = join(dirpath, filename)
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

def get_cloudiness_percentages(start_date, end_date, center_of_view, field_of_view, rotation, images_dir, display_images=False):
    image_paths, datetimes = get_image_paths(images_dir, start_date, end_date)
    horizontal_coordinates = get_horizontal_coordinates(center_of_view, field_of_view, rotation)
    image_coordinates = get_image_coordinates(horizontal_coordinates)
    percentages = estimate_cloudiness(image_paths, image_coordinates, display_images)

    return datetimes, percentages
