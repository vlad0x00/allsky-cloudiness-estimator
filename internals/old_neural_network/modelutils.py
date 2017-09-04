from scipy import misc
import numpy as np
import tensorflow as tf
import time
import re
import os
from tqdm import tqdm
import timeit
import dataset

IS_TRAINING = 'is_training'
PREDICTIONS = 'preds'
OUTPUTS = 'y'
INPUTS = 'inputs'


def create_model(session, model_fn, input_shape, output_shape):
    X = tf.placeholder(tf.float32, input_shape, name=INPUTS)
    y_true = tf.placeholder(tf.float32, output_shape, name=OUTPUTS)
    tf.placeholder(tf.bool, name=IS_TRAINING)
    y_hat = tf.identity(model_fn(X, input_shape, output_shape),
                          name=PREDICTIONS)  # Wrap model outputs with identity
    loss = per_pixel_classification_loss(y_true, y_hat, output_shape[3])
    tf.add_to_collection('train_ops', loss)
    tf.add_to_collection('train_ops', setup_optimizer(loss))
    tf.add_to_collection('train_summaries', tf.summary.scalar('loss', loss))

    tf.add_to_collection('val_ops', loss)
    tf.add_to_collection('val_summaries', tf.summary.scalar('val_loss', loss))
    tf.add_to_collection('val_summaries', tf.summary.image('X', X, 4))
    tf.add_to_collection('val_summaries', tf.summary.image('y_hat', y_hat, 4))
    tf.add_to_collection('val_summaries', tf.summary.image('y_true', y_true, 4))

    session.run(tf.global_variables_initializer())


def npcat(a, b):
    return np.vstack((a, b)) if a.size else b


def per_pixel_classification_loss(y_true, y_hat, num_classes):
    flat_logits = tf.reshape(tensor=y_hat, shape=(-1, num_classes))
    flat_labels = tf.reshape(tensor=y_true, shape=(-1, num_classes))

    cross_entropies = tf.nn.softmax_cross_entropy_with_logits(logits=flat_logits,
                                                              labels=flat_labels)

    return tf.reduce_sum(cross_entropies)


class ImageDataGenerator:
    def __init__(self, directory, batch_size):
        self.data_gen = dataset.get_cloud_data(directory)
        self.y = np.array([])
        self.x = np.array([])
        self.data_avail = True
        self.pos = 0
        self.batch_size = batch_size

    def shape(self):
        if self.x.shape[0] == 0:
            self._preload(1)
        return self.x.shape, self.y.shape

    def _preload(self, n):
        n = 10000000
        if not self.data_avail:
            return
        xs = []
        ys = []
        try:
            for i in range(n):
                x, y = next(self.data_gen)
                xs.append(x)
                ys.append(y)
        except StopIteration:
            self.data_avail = False
        self.x = npcat(self.x, np.array(xs))
        self.y = npcat(self.y, np.array(ys))

    def __iter__(self):
        return self

    def __next__(self):
        self._preload(self.batch_size)
        if self.pos >= len(self.x):
            self.pos = 0
            raise StopIteration
        idx = list(range(self.pos, min(self.pos + self.batch_size, len(self.x))))
        x_batch = np.array(self.x[idx])
        y_batch = np.array(self.y[idx])
        self.pos += self.batch_size
        return x_batch, y_batch

    def __len__(self):
        return len(self.x) / self.batch_size  # FIXME: actual length should be unknown


def load_image(path, flatten=False):
    return misc.imread(path, flatten=flatten) / 255


def get_tensor(name):
    return tf.get_default_graph().get_tensor_by_name(name)


def get_op(name):
    return tf.get_default_graph().get_operation_by_name(name)


def setup_optimizer(loss):
    with tf.variable_scope("adam_vars"):
        optimizer = tf.train.AdamOptimizer()
        gradients = optimizer.compute_gradients(loss=loss)

        for grad_var_pair in gradients:
            current_variable = grad_var_pair[1]
            current_gradient = grad_var_pair[0]

            # Relace some characters from the original variable name
            # tensorboard doesn't accept ':' symbol
            gradient_name_to_save = current_variable.name.replace(":", "_")

            # Let's get histogram of gradients for each layer and
            # visualize them later in tensorboard
            tf.add_to_collection('train_summaries', tf.summary.histogram(gradient_name_to_save, current_gradient))

        extra_update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        with tf.control_dependencies(extra_update_ops):
            return optimizer.apply_gradients(grads_and_vars=gradients)


def run_iteration(session, X_data, y_data, variables, training=False):
    # Map inputs to data.
    feed_dict = {
        get_tensor(INPUTS + ':0'): X_data,
        get_tensor(OUTPUTS + ':0'): y_data,
        get_tensor(IS_TRAINING + ':0'): training
    }

    # Compute variable values, and perform training step if required.
    values = session.run(variables, feed_dict=feed_dict)

    # Return loss value and number of correct predictions.
    return values


model_name = 'deep_cloud'


def load_model(filename, session):  # unused session for ensuring existing session
    # Later, launch the model, use the saver to restore variables from disk, and
    # do some work with the model.
    # Restore variables from disk.
    saver = tf.train.import_meta_graph(filename)
    saver.restore(session, tf.train.latest_checkpoint('./'))
    print("Model restored.")


def run_model(session,
              train_gen, validation_gen,
              epochs=1,
              variables=None):
    saver = tf.train.Saver(keep_checkpoint_every_n_hours=1)
    writer = tf.summary.FileWriter('./logs/' + time.strftime('%b %d %H:%M:%S'))
    train_ops = tf.get_collection('train_ops')
    train_summaries = tf.get_collection('train_summaries')
    val_ops = tf.get_collection('val_ops')
    val_summaries = tf.get_collection('val_summaries')
    writer.add_graph(tf.get_default_graph())
    total_loss = 0
    if variables is None:
        variables = []

    tf.get_default_graph().finalize()
    train_step_count = 0
    validation_step_count = 0
    # Count iterations since the beginning of training.
    for e in range(epochs):
        # Track time an epoch takes
        start_time = timeit.default_timer()
        # Keep track of performance stats (loss and accuracy) in current epoch.
        losses = []
        validation_losses = []

        # Iterate over the dataset once.
        dataset_size = 0
        train_gen_progress = tqdm(train_gen)
        for x_train, y_train in train_gen_progress:
            values = run_iteration(session, x_train, y_train, train_summaries + train_ops + variables, True)
            for summary in values[:len(train_summaries)]:
                writer.add_summary(summary, train_step_count)
            # Update performance stats.
            loss = values[len(train_summaries)]
            losses.append(loss * len(x_train))
            dataset_size += len(x_train)
            train_gen_progress.set_description('loss: %2.3f' % (loss,))
            train_step_count += 1

        validationset_size = 0
        for x_validate, y_validate in validation_gen:
            values = run_iteration(session, x_validate, y_validate, val_summaries + val_ops)
            for summary in values[:len(val_summaries)]:
                writer.add_summary(summary, validation_step_count)
            validation_loss = values[len(val_summaries)]
            validation_losses.append(validation_loss * len(x_validate))
            validationset_size += len(x_validate)
            validation_step_count += 1
        saver.save(session, model_name, global_step=e)
        total_loss = np.sum(losses) / dataset_size
        total_validation_loss = np.sum(validation_losses) / validationset_size
        elapsed = timeit.default_timer() - start_time
        print("Epoch {}, loss = {:.10g} validation_loss = {:.10g} in {:.10g}s"
              .format(e, total_loss, total_validation_loss, elapsed))
    writer.close()
    return total_loss


def predict(session, X_data):
    # Map inputs to data.
    feed_dict = {
        get_tensor(INPUTS + ':0'): X_data,
        get_tensor(IS_TRAINING + ':0'): False
    }

    # Compute variable values, and perform training step if required.
    return session.run(get_tensor(PREDICTIONS + ':0'), feed_dict=feed_dict)


def take(n, l):
    for i in range(n):
        yield next(l)


def image_generator():
    is_unlabeled = re.compile(r'.*[^l]\.png$')
    for dirname, dirnames, filenames in os.walk('validationset/'):
        for f in filenames:
            if is_unlabeled.match(f):
                path = os.path.join(dirname, f)
                print('Reading', path)
                yield (load_image(path), path)


def evaluate(sess):
    image_gen = image_generator()
    cont = True
    while cont:
        try:
            genres = list(take(10, image_gen))
        except StopIteration:
            cont = False
            pass
        if len(genres) == 0:
            break
        print('Predicting', len(genres), 'images')
        images = list(map(lambda x: x[0], genres))
        imagenames = list(map(lambda x: x[1], genres))
        preds = predict(sess, images)
        for i in range(len(preds)):
            pred = preds[i]
            # pred = pred.reshape(pred.shape[0], pred.shape[1])
            target = imagenames[i] + '-pred.png'
            # pred[pred[:, :] < 0] = 0
            # pred[pred[:, :] >= 1] = 1
            # threshold = 0.5
            # pred[pred[:,:] >= threshold] = 1
            # pred[pred[:,:] < threshold] = 0
            for i in range(3):
                print(str(i), '- min:', np.min(pred[:, :, i]), 'max:', np.max(pred[:, :, i]))
            print('Saved prediction', target, 'min:', np.min(pred), 'max:', np.max(pred))
            misc.imsave(target, pred)
