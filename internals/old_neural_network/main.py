#!/usr/bin/env python3

import numpy as np
from sklearn.model_selection import train_test_split

import models
import dataset
import modelutils
import argparse

import tensorflow as tf

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--batchsize', help='Number of images per batch', default=1)
parser.add_argument('-e', '--epochs', help='Number of epochs to train', default=0)
parser.add_argument('-m', '--model', help='Restore a model file')
parser.add_argument('-t', '--test', help='Test the model when finished training', action='store_true')
args = parser.parse_args()

epochs = int(args.epochs)
batch_size = int(args.batchsize)
train = epochs > 0
if train:
    train_gen = modelutils.ImageDataGenerator('trainingset', batch_size)
    validation_gen = modelutils.ImageDataGenerator('validationset', batch_size)
    # X_train = X_train.reshape(X_train.shape[0], img_rows, img_cols, 3)
    # input_shape = (img_rows, img_cols, 3)
    # X_train = X_train.astype('float32')

    # print('X_train shape:', X_train.shape)
    # print('Image size: {}x{} (rows x cols)'.format(img_rows, img_cols))
    # print('input_shape:', input_shape)
    # print('y_train shape:', y_train.shape)
    # print('min(X_train)', np.min(X_train))
    # print('max(X_train)', np.max(X_train))
    # print('min(y_train)', np.min(y_train))
    # print('max(y_train)', np.max(y_train))

tf.reset_default_graph()
with tf.Session() as sess:
    if args.model is not None:
        # restore model if filename provided
        model_file = args.model
        modelutils.load_model(model_file, sess)
        print('Using model loaded from', model_file)
    elif train:
        input_shape, output_shape = train_gen.shape()
        modelutils.create_model(sess, models.fully_convolutional_network,
                                [None, input_shape[1], input_shape[2], input_shape[3]],
                                [None, output_shape[1], output_shape[2], output_shape[3]],
                                )
    else:
        raise RuntimeError('No model provided (-m) and not training (-e)')

    if train:
        print('Training')
        modelutils.run_model(sess, train_gen, validation_gen, epochs)

    if args.test:
        modelutils.evaluate(sess)

print('Done')
