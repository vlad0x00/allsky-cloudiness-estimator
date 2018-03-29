#!/usr/bin/env python3

import argparse
from os import walk
from os.path import join
from neural_network.NeuralNetwork import NeuralNetwork
from utils.labeling import is_label, remove_label
import random

parser = argparse.ArgumentParser()
parser.add_argument('image_dir', help='Directory with train images and their labels')
parser.add_argument('-b', '--batchsize', help='Number of images per batch', default=1)
parser.add_argument('-e', '--epochs', help='Number of epochs to train', default=1)
args = parser.parse_args()

image_dir = args.image_dir
batch_size = int(args.batchsize)
epochs = int(args.epochs)

def get_image_paths(dir):
    paths = []
    for dirpath, dirnames, filenames in walk(dir):
        for filename in filenames:
            if is_label(filename):
                paths.append((join(dirpath, remove_label(filename)), join(dirpath, filename)))

    random.shuffle(paths)

    return paths

with NeuralNetwork() as nn:
    nn.train(get_image_paths(image_dir), batch_size, epochs)
