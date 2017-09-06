import scipy.misc
from neural_network.NeuralNetwork import NeuralNetwork

COORDINATES_FILE = 'coordinates.txt'

def estimate_cloudiness(image, coordinates):
    nn = NeuralNetwork()
    cloud_images = nn.run(images)
    nn.close()

    polygon = []
    for coordinates in polygon_coordinates:
        polygon.append(cv2.Point(coordinates[0], coordinates[1]))

    percentages = []
    for cloud_image in cloud_images:
        points_inside = 0
        cloudiness = 0
        for y in cloud_image.shape[0]:
            for x in cloud_image.shape[1]:
                if cv2.pointPolygonTest(cv2.Point(x, y), polygon, False)
                    cloudiness += cloud_image[x, y, 1]
                    points_inside += 1

        percentages.append(cloudiness / points_inside)

    return percentages

def get_image_coordinates(horizontal_coordinates):
    coordinates_file = open(COORDINATES_FILE)

    coordinates = []

    lines = coordinates_file.readlines()
    for line in lines:
        x, y, a, h = int(line[0]), int(line[1]), int(line[2]), int(line[3])
        coordinates.append((x, y, a, h))

    coordinates.sort()
    images_coordinates = []
    for coordinates in horizontal_coordinates:
        

def get_horizontal_coordinates(center_of_view, field_of_view):


def get_images(images_dir, start_date, end_date):
    images = []
    for dirpath, dirnames, filenames in walk(images_dir):
        for filename in filenames:
            if is_within_dates(filename, start_date, end_date):
               images.append(scipy.misc.imread(filename))

    return images

def get_cloudiness_percentages(start_date, end_date, center_of_view, field_of_view, images_dir):
    images = get_images(images_dir, start_date, end_date)
    horizontal_coordinates = get_horizontal_coordinates(center_of_view, field_of_view)
    image_coordinates = get_image_coordinates(horizontal_coordinates)

    percentages = []
    for image in images:
        percentages.append(estimate_cloudiness(image, image_coordinates))

    return percentages
