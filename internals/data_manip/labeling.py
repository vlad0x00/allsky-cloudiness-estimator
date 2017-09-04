from os.path import splitext
import cv2
import numpy as np

def is_label(path):
    root, _ = splitext(path)
    return root[-1:] == 'l'

def remove_label(path):
    root, ext = splitext(path)
    return root[:-1] + ext

def add_label(path):
    root, ext = splitext(path)
    return root + 'l' + ext

UNSURE_LOWER_LIMIT = 0.1
UNSURE_UPPER_LIMIT = 0.9

def normalize(label):
    ret, clouded = cv2.threshold(label, 255 * UNSURE_UPPER_LIMIT, 255, cv2.THRESH_BINARY)

    ret, semiclouded = cv2.threshold(label, 255 * UNSURE_LOWER_LIMIT, 255, cv2.THRESH_BINARY)
    semiclouded -= clouded
    semiclouded = np.divide(semiclouded, 2)

    label = semiclouded + clouded

    return label
