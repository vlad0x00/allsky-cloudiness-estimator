#!/usr/bin/env python3

import argparse
import multiprocessing
import errno
import sys
import scipy.misc
from multiprocessing.pool import ThreadPool
from os.path import join, splitext, basename
from os import makedirs, walk
from utils.labeling import is_label, remove_label, add_label, normalize
from utils.fixes import fix_dead_pixels
from utils.sky_extractor import extract_sky
from utils.data_generator import generate_data
from utils.name_generator import generate_name
from utils.patching import extract_patches

IMG_RESIZE = 512
IMG_PATCH_SIZE = 256
IMG_STRIDE = 128
LABEL_RESIZE = 128
LABEL_PATCH_SIZE = 60
LABEL_STRIDE = 32
LABEL_PATCH_PADDING = 2

IMG_STRIDES = round((IMG_RESIZE - IMG_PATCH_SIZE + IMG_STRIDE) / IMG_STRIDE)
LABEL_STRIDES = round((LABEL_RESIZE - (LABEL_PATCH_SIZE + 2 * LABEL_PATCH_PADDING) + LABEL_STRIDE) / LABEL_STRIDE)
assert IMG_STRIDES == LABEL_STRIDES

OUTPUT_EXTENSION = '.png'

parser = argparse.ArgumentParser()
parser.add_argument('input_dir', help = 'Directory from which the raw images and their labels are loaded')
parser.add_argument('output_dir', help = 'Directory to which the output images are stored')
parser.add_argument('-p', '--patching', help = 'Enable the patching method', action = 'store_true')
parser.add_argument('-l', '--limit', help = 'Limit the number of inputs to process', default = -1)
parser.add_argument('-u', '--unlabeled', help = 'Prepare inputs without labels to test the network (less processing)', action = 'store_true')
args = parser.parse_args()

input_dir = args.input_dir
output_dir = args.output_dir
patching = args.patching
limit = int(args.limit)
unlabeled = args.unlabeled

def get_image_paths(input_dir, get_labeled = True):
    labeled = set()
    unlabeled = set()

    for dirpath, dirnames, filenames in walk(input_dir):
        for filename in filenames:
            if is_label(filename):
                labeled.add(join(dirpath, remove_label(filename)))
            else:
                unlabeled.add(join(dirpath, filename))

    for path in labeled:
        unlabeled.remove(path)

    if get_labeled:
        paths = labeled
    else:
        paths = unlabeled

    for path in paths:
        yield path,

def process_labeled(input_img_path):
    print('Processing', input_img_path)

    img = scipy.misc.imread(input_img_path)
    label = scipy.misc.imread(add_label(input_img_path))
    if img is None or label is None:
        return

    img = fix_dead_pixels(img)
    imgs = generate_data(img)
    img_skies = []
    for img in imgs:
        img_skies.append(extract_sky(img, IMG_RESIZE))

    label = normalize(label)
    labels = generate_data(label)
    label_skies = []
    for label in labels:
        label_skies.append(extract_sky(label, LABEL_RESIZE, True))

    root, ext = splitext(basename(input_img_path))

    if args.patching:
        img_patches = []
        img_patch_names = []
        for sky in img_skies:
            patches = extract_patches(sky,
                IMG_PATCH_SIZE,
                IMG_STRIDE
                )

            for patch in patches:
                img_patches.append(patch)
                img_patch_names.append(root + '_' + generate_name() + OUTPUT_EXTENSION)

        label_patches = []
        label_patch_names = []
        i = 0
        for sky in label_skies:
            patches = extract_patches(sky,
                LABEL_PATCH_SIZE,
                LABEL_STRIDE,
                LABEL_PATCH_PADDING
            )

            for patch in patches:
                label_patches.append(patch)
                label_patch_names.append(add_label(img_patch_names[i]))
                i += 1

        for patch, name in zip(img_patches, img_patch_names):
            scipy.misc.imsave(join(args.output_dir, name), patch)

        for patch, name in zip(label_patches, label_patch_names):
            scipy.misc.imsave(join(args.output_dir, name), patch)
    else:
        for img, label in zip(img_skies, label_skies):
            name = generate_name()
            scipy.misc.imsave(join(args.output_dir, root + '_' + name + OUTPUT_EXTENSION), img)
            scipy.misc.imsave(join(args.output_dir, root + '_' + name + 'l' + OUTPUT_EXTENSION), label)

def process_unlabeled(input_img_path):
    print('Processing', input_img_path)

    img = scipy.misc.imread(input_img_path)
    if img is None:
        return

    img = fix_dead_pixels(img)
    sky = extract_sky(img, IMG_RESIZE)

    root, ext = splitext(basename(input_img_path))

    if (args.patching):
        patches = extract_patches(sky,
            IMG_PATCH_SIZE,
            IMG_STRIDE
        )

        for patch in patches:
            scipy.misc.imsave(join(args.output_dir, root + '_' + generate_name() + OUTPUT_EXTENSION), patch)
    else:
        scipy.misc.imsave(join(args.output_dir, root + OUTPUT_EXTENSION), sky)

def take(l, n):
    for i in range(n):
        yield next(l)

def prepare_data():
    try:
        makedirs(output_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    image_paths = get_image_paths(input_dir, not unlabeled)

    if limit > 0:
        image_paths = take(image_paths, limit)

    pool = ThreadPool()
    if unlabeled:
        pool.starmap(process_unlabeled, image_paths)
    else:
        pool.starmap(process_labeled, image_paths)

prepare_data()
