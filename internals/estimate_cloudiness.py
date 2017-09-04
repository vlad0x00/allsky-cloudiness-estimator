import cv2
from neural_network.NeuralNetwork import NeuralNetwork

def estimate_cloudiness(images, polygon_coordinates):
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
