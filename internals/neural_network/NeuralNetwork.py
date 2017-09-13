import random
import tensorflow as tf
import scipy.misc
import numpy as np
import os.path
import math
from tqdm import tqdm

VALIDATION_PERCENT = 0.1
LOG_DIR = os.path.dirname(os.path.abspath(__file__))  + '/logs/'
MODEL_FILENAME = os.path.dirname(os.path.abspath(__file__)) + '/model/network_model'
LEARNING_RATE = 0.001
DROPOUT_RATE = 0.25

class NeuralNetwork:

    def __init__(self):
        tf.reset_default_graph()
        self.session = tf.Session()
        self.writer = tf.summary.FileWriter(LOG_DIR)

        if os.path.isfile(MODEL_FILENAME + '.meta'):
            print('NeuralNetwork: Model file exists, loading...')
            self._load_model(MODEL_FILENAME)
            self.model_loaded = True
            print('NeuralNetwork: Model successfully loaded')
        else:
            self.model_loaded = False

    def _load_model(self, model_filename):
        saver = tf.train.import_meta_graph(model_filename + '.meta')
        saver.restore(self.session, model_filename)

        self.image = tf.get_default_graph().get_operation_by_name('image').outputs[0]
        self.label = tf.get_default_graph().get_operation_by_name('label').outputs[0]

        self.dropout_probability = tf.get_default_graph().get_operation_by_name('dropout_probability').outputs[0]

        self.output = tf.get_default_graph().get_operation_by_name('output').outputs[0]

        self.loss = tf.get_collection('loss')[0]
        self.train_step = tf.get_collection('train_step')[0]
        self._setup_summary()

        self.writer.add_graph(tf.get_default_graph())

    def _create_model(self, image_shape, label_shape):
        self.image = tf.placeholder(tf.float32, [None, image_shape[0], image_shape[1], image_shape[2]], name='image')
        self.label = tf.placeholder(tf.float32, [None, label_shape[0], label_shape[1], label_shape[2]], name='label')

        self.dropout_probability = tf.placeholder_with_default(0.0, shape=(), name='dropout_probability')

        layer = self.image
        layer = tf.layers.conv2d(layer, 32, (5, 5), padding='SAME', activation=tf.nn.relu, name='conv0')
        layer = tf.layers.conv2d(layer, 32, (5, 5), padding='SAME', activation=tf.nn.relu, name='conv1')
        layer = tf.layers.max_pooling2d(layer, (3, 3), 2, padding='SAME', name='maxpool0')
        layer = tf.layers.conv2d(layer, 64, (3, 3), padding='SAME', activation=tf.nn.relu, name='conv2')
        layer = tf.layers.max_pooling2d(layer, (3, 3), 2, padding='SAME', name='maxpool1')
        layer = tf.layers.conv2d(layer, 64, (3, 3), padding='SAME', activation=tf.nn.relu, name='conv3')
        start0 = layer
        layer = tf.layers.max_pooling2d(layer, (3, 3), 2, padding='SAME', name='maxpool2')
        layer = tf.layers.conv2d(layer, 128, (3, 3), padding='SAME', activation=tf.nn.relu, name='conv4')
        layer = tf.layers.dropout(layer, rate=self.dropout_probability, name='drop0')
        start1 = layer
        layer = tf.layers.max_pooling2d(layer, (3, 3), 2, padding='SAME', name='maxpool3')
        layer = tf.layers.conv2d(layer, 128, (3, 3), padding='SAME', activation=tf.nn.relu, name='conv5')
        layer = tf.layers.dropout(layer, rate=self.dropout_probability, name='drop1')
        layer = tf.image.resize_nearest_neighbor(layer, size=(label_shape[0] // 2, label_shape[1] // 2), name='upsample0')
        end1 = layer
        layer = tf.layers.conv2d(layer, 64, (3, 3), padding='SAME', activation=tf.nn.relu, name='conv6')
        layer = tf.layers.dropout(layer, rate=self.dropout_probability, name='drop2')
        layer = tf.image.resize_nearest_neighbor(layer, size=label_shape[0:2], name='upsample1')
        end0 = layer
        layer = tf.layers.conv2d(layer, 64, (3, 3), padding='SAME', activation=tf.nn.relu, name='conv7')
        layer = tf.layers.conv2d(layer, label_shape[2], (3, 3), padding='SAME', activation=tf.sigmoid, name='conv8')

        concat0 = tf.concat([start0, end0], 3, 'concat0')
        concat1 = tf.concat([start1, end1], 3, 'concat1')

        self.output = tf.identity(layer, name='output')

        self._setup_loss()
        self._setup_optimizer()
        self._setup_summary()

        # Initialize weights
        self.session.run(tf.global_variables_initializer())

        self.writer.add_graph(tf.get_default_graph())

    def _setup_loss(self):
        #flat_logits = tf.reshape(tensor = self.output, shape = (-1, int(self.output.shape[3])))
        #flat_labels = tf.reshape(tensor = self.label, shape = (-1, int(self.label.shape[3])))

        #cross_entropies = tf.nn.softmax_cross_entropy_with_logits(logits=flat_logits,
        #                                                          labels=flat_labels)

        self.loss = tf.losses.mean_squared_error(self.label, self.output)
        tf.add_to_collection('loss', self.loss)

    def _setup_optimizer(self):
        optimizer = tf.train.AdamOptimizer(LEARNING_RATE)
        # Batch normalization in TensorFlow requires this extra dependency
        extra_update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        with tf.control_dependencies(extra_update_ops):
            self.train_step = optimizer.minimize(self.loss)
            tf.add_to_collection('train_step', self.train_step)

    def _setup_summary(self):
        self.training_loss_summary = tf.summary.scalar('Training Loss', self.loss)

        self.validation_loss_summary = tf.summary.scalar('Validation Loss', self.loss)
        self.image_summary = tf.summary.image('Image', self.image)
        self.label_summary = tf.summary.image('Label', self.label)
        self.output_summary = tf.summary.image('Output', self.output)

    def train(self, image_and_label_paths, batch_size, epochs):
        if not self.model_loaded:
            print('NeuralNetwork: No model exists, creating one...')
            test_image = scipy.misc.imread(image_and_label_paths[0][0])
            test_label = scipy.misc.imread(image_and_label_paths[0][1], flatten=True)
            test_label = np.reshape(test_label, (test_label.shape[0], test_label.shape[1], 1))
            self._create_model(test_image.shape, test_label.shape)
            print('NeuralNetwork: Model successfully created')

        training_paths, validation_paths = self._split_training_and_validation(image_and_label_paths)

        training_size = len(training_paths)
        training_batches_per_epoch = int(math.ceil(training_size / batch_size))

        validation_size = len(validation_paths)
        validation_batches_per_epoch = int(math.ceil(validation_size / batch_size))

        saver = tf.train.Saver()

        for epoch in range(epochs):
            print('NeuralNetwork: Training... (Epoch {}/{})'.format(epoch + 1, epochs))
            training_losses = []
            for batch in tqdm(range(training_batches_per_epoch)):
                batch_images, batch_labels = self._load_batch(training_paths, batch, batch_size)

                variables = [ self.loss, self.train_step, self.training_loss_summary,  ]
                feed_dict = { self.image : batch_images, self.label : batch_labels, self.dropout_probability : DROPOUT_RATE }
                loss, _, loss_summary = self.session.run(variables, feed_dict=feed_dict)

                step = epoch * training_batches_per_epoch + batch
                self.writer.add_summary(loss_summary, step)

                training_losses.append(loss * len(batch_images))
            training_loss = np.sum(training_losses) / training_size

            print('NeuralNetwork: Validating... (Epoch {}/{})'.format(epoch + 1, epochs))
            validation_losses = []
            for batch in tqdm(range(validation_batches_per_epoch)):
                batch_images, batch_labels = self._load_batch(validation_paths, batch, batch_size)

                variables = [ self.loss, self.validation_loss_summary,
                                self.image_summary, self.label_summary, self.output_summary ]
                feed_dict = { self.image : batch_images, self.label : batch_labels }
                loss, loss_summary, image_summary, label_summary, output_summary = self.session.run(
                                                                    variables, feed_dict=feed_dict)

                step = epoch * validation_batches_per_epoch + batch
                self.writer.add_summary(loss_summary, step)
                self.writer.add_summary(image_summary, step)
                self.writer.add_summary(label_summary, step)
                self.writer.add_summary(output_summary, step)

                validation_losses.append(loss * len(batch_images))
            if validation_size > 0:
                validation_loss = np.sum(validation_losses) / validation_size
            else:
                validation_loss = 0

            print("NeuralNetwork: Epoch {}/{}, training loss = {:.10g} validation loss = {:.10g}"
                   .format(epoch + 1, epochs, training_loss, validation_loss))

            saver.save(self.session, MODEL_FILENAME)
        print('NeuralNetwork: Training done')

    def _load_batch(self, paths, batch, batch_size):
        start = batch * batch_size
        end = start + batch_size
        if end > len(paths):
            end = len(paths)

        images = []
        labels = []

        for idx in range(start, end):
            image = scipy.misc.imread(paths[idx][0])
            image = image[:, :, ::-1] # BGR -> RGB
            image = np.divide(image, 255)
            images.append(image)

            label = scipy.misc.imread(paths[idx][1], flatten=True)
            label = np.reshape(label, (label.shape[0], label.shape[1], 1))
            label = np.divide(label, 255)
            labels.append(label)

        return images, labels

    def _split_training_and_validation(self, image_and_label_paths):
        training = []
        validation = []

        for paths in image_and_label_paths:
            if random.uniform(0, 1) <= VALIDATION_PERCENT:
                validation.append(paths)
            else:
                training.append(paths)

        return training, validation

    def run(self, images):
        if not self.model_loaded:
            print('No model to run the network on')
            return []

        variables = [ self.output ]
        feed_dict = { self.image : images }
        outputs = self.session.run(variables, feed_dict=feed_dict)

        return outputs

    def close(self):
        self.writer.close()
        self.session.close()
