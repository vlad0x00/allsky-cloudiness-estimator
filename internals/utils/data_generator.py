import cv2

ROTATIONS = 3

def make_rotations(img):
    rows, cols = img.shape[0], img.shape[1]
    for i in range(ROTATIONS):
        rotation_matrix = cv2.getRotationMatrix2D((cols / 2, rows / 2), 360 / ROTATIONS * i, 1)
        yield cv2.warpAffine(img, rotation_matrix, (cols, rows))

def generate_data(img):
    return make_rotations(img)
