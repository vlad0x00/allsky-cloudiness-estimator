import cv2
import numpy as np
from math import sqrt

def extract_patches(img, patch_size, stride, padding = 0):
    size, _, _ = img.shape

    kernel_size = patch_size + 2 * padding
    axis_total_strides = round((size - kernel_size + stride) / stride)

    patches = []
    for x in range(axis_total_strides):
        for y in range(axis_total_strides):
            x_offset_min = x * stride + padding
            x_offset_max = x_offset_min + patch_size
            y_offset_min = y * stride + padding
            y_offset_max = y_offset_min + patch_size

            patches.append(img[y_offset_min : y_offset_max, x_offset_min : x_offset_max])

    return patches

def stitch_patches(patches, patch_size, stride, padding = 0):
    kernel_size = patch_size + 2 * padding
    axis_total_strides = round(sqrt(len(patches)))

    size = round(sqrt(len(patches)) * stride - stride + kernel_size)

    img = np.zeros((size, size, patches[0].shape[2]), dtype = np.uint32)
    patch_counters = np.zeros((size, size, patches[0].shape[2]), dtype = np.uint32)

    i = 0
    for x in range(axis_total_strides):
        for y in range(axis_total_strides):

            x_offset_min = x * stride + padding
            x_offset_max = x_offset_min + patch_size
            y_offset_min = y * stride + padding
            y_offset_max = y_offset_min + patch_size

            img[y_offset_min : y_offset_max, x_offset_min : x_offset_max] += patches[i]
            patch_counters[y_offset_min : y_offset_max, x_offset_min : x_offset_max] += 1

            i += 1

    patch_counters[patch_counters == 0] = 1
    img = np.divide(img, patch_counters)
    img = img.astype(np.uint8)

    return img
