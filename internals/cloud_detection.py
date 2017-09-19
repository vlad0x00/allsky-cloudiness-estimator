from .utils.coordinates_helper import view2pixel
from .neural_network.NeuralNetwork import NeuralNetwork
from datetime import datetime, timedelta
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
import matplotlib.widgets as widgets

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

g_display_images = False
end = False

def turn_off_images(_):
    global g_display_images
    g_display_images = False
    plt.close()

def stop_processing(_):
    global end
    end = True
    plt.close()

def next_image(_):
    plt.close()

def estimate_cloudiness(image_paths, coordinates, display_images):
    global g_display_images
    global end

    g_display_images = display_images

    percentages = []

    input_coordinates = []
    output_coordinates = []
    for x, y in coordinates:
        input_coordinates.append((
                            round((x - (ORIGINAL_WIDTH - CROP_SIZE) / 2)
                            / (CROP_SIZE / NETWORK_INPUT_SIZE)),
                            round((y - (ORIGINAL_HEIGHT - CROP_SIZE) / 2)
                            / (CROP_SIZE / NETWORK_INPUT_SIZE))
        ))

        output_coordinates.append((
                            round((x - (ORIGINAL_WIDTH - CROP_SIZE) / 2)
                            / (CROP_SIZE / NETWORK_OUTPUT_SIZE)),
                            round((y - (ORIGINAL_HEIGHT - CROP_SIZE) / 2)
                            / (CROP_SIZE / NETWORK_OUTPUT_SIZE))
        ))
    output_polygon = path.Path(output_coordinates)

    neural_network = NeuralNetwork()
    for i in range(0, len(image_paths), BATCH_SIZE):
        print('Processing {}/{}'.format(i + 1, len(image_paths)))

        images = []
        for j in range(BATCH_SIZE):
            if i + j >= len(image_paths):
                break
            image = scipy.misc.imread(image_paths[i + j])
            image = np.array(image[:, :, ::-1]) # BGR -> RGB
            images.append(image)

        preprocessed_images = preprocess_images(images)
        cloud_outputs = neural_network.run(preprocessed_images)

        for i, cloud_output in enumerate(cloud_outputs[0]):
            points_inside = 0
            cloudiness = 0
            for y in range(cloud_output.shape[0]):
                for x in range(cloud_output.shape[1]):
                    if output_polygon.contains_point((x, y)):
                        cloudiness += cloud_output[y, x, 0]
                        points_inside += 1

            if points_inside > 0:
                percentages.append(int(round(100 * cloudiness / points_inside)))
            else:
                print('ERROR: Invalid coordinates or image')
                percentages.append(-1)

            if g_display_images:
                plt.figure(figsize=(10, 5))
                plt.figtext(0.43, 0.94, 'Cloudiness: ' + str(percentages[-1]) + '%', size='x-large')

                subplot = plt.subplot(121)
                plt.imshow(preprocessed_images[i][:, :, ::-1])
                plt.axis('off')
                plt.title('Night Sky', size='medium')
                input_polygon_patch = patches.Polygon(np.array(input_coordinates))
                input_polygon_patch.set_fill(False)
                input_polygon_patch.set_linewidth(0.3)
                input_polygon_patch.set_color('#eeefff')
                subplot.add_patch(input_polygon_patch)

                output = np.multiply(cloud_output, 255)
                output = np.stack([output, output.copy(), output.copy()], axis = -1)
                output = np.reshape(output, (output.shape[1], output.shape[0], 3))
                output = scipy.misc.imresize(output, (NETWORK_INPUT_SIZE, NETWORK_INPUT_SIZE), interp='bicubic')
                output = np.divide(output, 255)

                subplot = plt.subplot(122)
                plt.imshow(output)
                plt.axis('off')
                plt.title('Cloud Map', size='medium')
                input_polygon_patch = patches.Polygon(np.array(input_coordinates))
                input_polygon_patch.set_fill(False)
                input_polygon_patch.set_linewidth(0.3)
                input_polygon_patch.set_color('#eeefff')
                subplot.add_patch(input_polygon_patch)

                axes1 = plt.axes([0.265, 0.034, 0.15, 0.075])
                button1 = widgets.Button(axes1, 'Turn off images')
                button1.on_clicked(turn_off_images)

                axes2 = plt.axes([0.440, 0.034, 0.15, 0.075])
                button2 = widgets.Button(axes2, 'Stop processing')
                button2.on_clicked(stop_processing)

                axes3 = plt.axes([0.615, 0.034, 0.15, 0.075])
                button3 = widgets.Button(axes3, 'Next')
                button3.on_clicked(next_image)

                plt.show()

            if end:
                break
        if end:
            break
    neural_network.close()

    return percentages

def get_image_paths(images_dir, start_datetime, end_datetime, interval):
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
    last_datetime = None
    for path_and_datetime in paths_and_datetimes:
        if (last_datetime == None) or (path_and_datetime[1] - last_datetime >= interval):
            paths.append(path_and_datetime[0])
            datetimes.append(path_and_datetime[1])
            last_datetime = path_and_datetime[1]

    return paths, datetimes

def get_cloudiness_percentages(start_date, end_date, center_of_view, width_of_view, rotation, images_dir, interval=timedelta(minutes=30), display_images=False):
    image_paths, datetimes = get_image_paths(images_dir, start_date, end_date, interval)
    coordinates = view2pixel(center_of_view, width_of_view, rotation)
    percentages = estimate_cloudiness(image_paths, coordinates, display_images)

    datetimes_str = []
    for datetime in datetimes:
        datetimes_str.append(str(datetime))

    percentages_str = []
    for percentage in percentages:
        percentages_str.append(str(percentage) + '%')

    return datetimes_str, percentages_str
