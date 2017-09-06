from os.path import splitext
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
    label[label < 255 * UNSURE_LOWER_LIMIT] = 0
    label[np.logical_and(label >= 255 * UNSURE_LOWER_LIMIT, label < 255 * UNSURE_UPPER_LIMIT)] = 127
    label[label >= 255 * UNSURE_UPPER_LIMIT] = 255

    return label
