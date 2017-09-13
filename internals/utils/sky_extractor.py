import cv2

CROP_SIZE = 2300
BORDER_RADIUS = 1400
BORDER_SIZE = 520

def crop(img, crop_size, border_radius, border_size):
    cv2.circle(img, (round(img.shape[1] / 2), round(img.shape[0] / 2)), border_radius, (0, 0, 0), border_size, cv2.LINE_AA)

    crop_x = round((img.shape[1] - crop_size) / 2)
    crop_y = round((img.shape[0] - crop_size) / 2)
    return img[crop_y : (crop_y + crop_size), crop_x : (crop_x + crop_size)]

def resize(img, new_size, is_label):
    if is_label:
        method = cv2.INTER_NEAREST
    else:
        method = cv2.INTER_AREA
    return cv2.resize(img, dsize=(new_size, new_size), interpolation=method)

def extract_sky(img, final_size, is_label=False):
    img = crop(img, CROP_SIZE, BORDER_RADIUS, BORDER_SIZE)
    img = resize(img, final_size, is_label)
    return img
