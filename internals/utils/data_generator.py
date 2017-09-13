import scipy.misc

ROTATIONS = 3

def make_rotations(img):
    rows, cols = img.shape[0], img.shape[1]
    for i in range(ROTATIONS):
        yield scipy.misc.imrotate(img, 360 / ROTATIONS * i, interp='bicubic')

def generate_data(img):
    return make_rotations(img)
