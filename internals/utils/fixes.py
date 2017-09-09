import cv2
from os.path import dirname, abspath, join

DEAD_PIXEL_MASK = 'dead_pixel_mask.JPG'
DEAD_PIXEL_SIZE = 10

def fix_dead_pixels(img):
    mask = cv2.imread(join(dirname(abspath(__file__)), DEAD_PIXEL_MASK))
    gray_mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    _, contours, _ = cv2.findContours(gray_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for i, contour in enumerate(contours):
        if cv2.contourArea(contour) < 1.0:
            continue

        moments = cv2.moments(contour)
        cx = int(moments['m10']/moments['m00'])
        cy = int(moments['m01']/moments['m00'])

        x = round(cx - DEAD_PIXEL_SIZE / 2)
        y = round(cy - DEAD_PIXEL_SIZE / 2)
        w = DEAD_PIXEL_SIZE
        h = DEAD_PIXEL_SIZE

        roi = img[y : (y + h), x : (x + w)]
        cv2.blur(roi, (DEAD_PIXEL_SIZE, DEAD_PIXEL_SIZE), roi)

    return img

def fix(img):
    return fix_dead_pixels(img)
