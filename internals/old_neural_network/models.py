import tensorflow as tf
import numpy as np


# def classifier_style_network(inputs):
#    conv1 = Conv2D(64, (5, 5), activation='relu', strides=(1, 1), padding='VALID')(inputs)
#    conv2 = Conv2D(64, (5, 5), activation='relu', strides=(1, 1), padding='VALID')(conv1)
#    max_pool1 = MaxPooling2D((2, 2), None, padding = 'VALID')(conv2)
#
#    conv3 = Conv2D(128, (3, 3), activation='relu', strides=(2, 2), padding='VALID')(max_pool1)
#    conv4 = Conv2D(128, (3, 3), activation='relu', strides=(2, 2), padding='VALID')(conv3)
#    max_pool2 = MaxPooling2D((2, 2), None, padding = 'VALID')(conv4)
#
#    conv5 = Conv2D(256, (3, 3), activation='relu', strides=(2, 2), padding='VALID')(max_pool2)
#    conv6 = Conv2D(256, (3, 3), activation='relu', strides=(2, 2), padding='VALID')(conv5)
#    max_pool3 = MaxPooling2D((2, 2), None, padding = 'VALID')(conv6)
#
#    flat1 = Flatten()(max_pool3)
#
#    dense1 = Dense(4096, activation = 'relu')(flat1)
#    dense2 = Dense(2025, activation = 'relu')(dense1)
#    conv7 = Conv2D(1, (3,3), activation='relu', padding='SAME')(Reshape(45,45)(dense2))
#    preds = UpSampling2D(size=(inputs.shape[0]/45, inputs.shape[1]/45))(conv7)
#    #dense3 = Dense(128 * 128, activation = 'relu')(dense2)
#    return preds




def fully_convolutional_network(inputs, input_shape, output_shape):
    normd = tf.layers.batch_normalization(inputs, axis=1)
    conv0 = tf.layers.conv2d(normd, 64, (3, 3), padding='SAME', activation=tf.nn.relu, name='conv0')
    conv1 = tf.layers.conv2d(conv0, 64, (3, 3), padding='SAME', activation=tf.nn.relu, name='conv1')
    max_pool1 = tf.layers.max_pooling2d(conv1, (3, 3), 2, padding='SAME', name='maxpool1')
    conv2 = tf.layers.conv2d(max_pool1, 128, (3, 3), padding='SAME', activation=tf.nn.relu, name='conv2')
    conv3 = tf.layers.conv2d(conv2, 128, (3, 3), padding='SAME', activation=tf.nn.relu, name='conv3')
    max_pool2 = tf.layers.max_pooling2d(conv3, (3, 3), 2, padding='SAME', name='maxpool2')
    conv4 = tf.layers.conv2d(max_pool2, 256, (3, 3), padding='SAME', activation=tf.nn.relu, name='conv4')
    conv5 = tf.layers.conv2d(conv4, 256, (3, 3), padding='SAME', activation=tf.nn.relu, name='conv5')
    upsample1 = tf.image.resize_nearest_neighbor(conv5, size=np.array(input_shape[1:3]) / 2, name='upsample1')
    concat1 = tf.concat([conv3, upsample1], 3, 'shortcut1')
    conv6 = tf.layers.conv2d(concat1, 128, (3, 3), activation=tf.nn.relu, padding='SAME', name='conv6')
    conv7 = tf.layers.conv2d(conv6, 128, (3, 3), activation=tf.nn.relu, padding='SAME', name='conv7')
    upsample2 = tf.image.resize_nearest_neighbor(conv1, size=output_shape[1:3], name='upsample2')
    upsample3 = tf.image.resize_nearest_neighbor(conv7, size=output_shape[1:3], name='upsample3')
    concat2 = tf.concat([upsample2, upsample3], 3, 'shortcut2')
    conv8 = tf.layers.conv2d(concat2, 64, (3, 3), activation=tf.nn.relu, padding='SAME', name='conv8')
    conv9 = tf.layers.conv2d(conv8, 64, (3, 3), activation=tf.nn.relu, padding='SAME', name='conv9')
    conv10 = tf.layers.conv2d(conv9, output_shape[3], (3, 3), padding='SAME', activation=tf.nn.relu, name='conv10')
    return conv10
