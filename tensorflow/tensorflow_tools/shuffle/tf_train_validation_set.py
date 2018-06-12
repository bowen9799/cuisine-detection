# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
r"""Downloads and converts Flowers data to TFRecords of TF-Example protos.

This module downloads the Flowers data, uncompresses it, reads the files
that make up the Flowers data and creates two TFRecord datasets: one for train
and one for test. Each TFRecord dataset is comprised of a set of TF-Example
protocol buffers, each of which contain a single image and label.

The script should take about a minute to run.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from multiprocessing import cpu_count

import math
import os
import random
import sys
import time
import pickle
import shutil
import threadpool
import tensorflow as tf

sys.path.append("./")
import dataset_utils

OUTPUT_PATH = ""
_RANDOM_SEED = 0


class GlobalProcess:
    def __init__(self):
        self.all_step = 0
        self.finished_file = []

    def reset(self):
        self.all_step = 0
        self.finished_file = []

    def set_all_step(self, step):
        self.all_step = step

    def add_finish(self, file):
        self.finished_file.append(file)


class ImageReader(object):
    """Helper class that provides TensorFlow image coding utilities."""

    def __init__(self):
        # Initializes function that decodes RGB JPEG data.
        self._decode_jpeg_data = tf.placeholder(dtype=tf.string)
        self._decode_jpeg = tf.image.decode_jpeg(self._decode_jpeg_data, channels=3)

    def read_image_dims(self, sess, image_data):
        image = self.decode_jpeg(sess, image_data)
        return image.shape[0], image.shape[1]

    def decode_jpeg(self, sess, image_data):
        image = sess.run(self._decode_jpeg,
                         feed_dict={self._decode_jpeg_data: image_data})
        assert len(image.shape) == 3
        assert image.shape[2] == 3
        return image


def _get_filenames_and_classes(dataset_dir):
    """Returns a list of filenames and inferred class names.

    Args:
      dataset_dir: A directory containing a set of subdirectories representing
        class names. Each subdirectory should contain PNG or JPG encoded images.

    Returns:
      A list of image file paths, relative to `dataset_dir` and the list of
      subdirectories, representing class names.
    """
    file_root = os.path.join(dataset_dir, './')
    directories = []
    class_names = []
    for filename in os.listdir(file_root):
        path = os.path.join(file_root, filename)
        if os.path.isdir(path):
            directories.append(path)
            class_names.append(filename)

    photo_filenames = []
    for directory in directories:
        for filename in os.listdir(directory):
            path = os.path.join(directory, filename)
            photo_filenames.append(path)

    return photo_filenames, sorted(class_names)


def _get_dataset_filename(dir, split_name, shard_id, num_shards):
    output_filename = '%s_%05d_of_%05d_%d.tfrecord' % (
        split_name, shard_id, num_shards, VERSION)
    return os.path.join(dir, output_filename)


def create_tf(split_name, filenames, class_names_to_ids, dataset_dir,
              num_shards, shard_id, num_per_shard, image_reader, sess):
    output_filename = _get_dataset_filename(
        OUTPUT_PATH, split_name, shard_id, num_shards)

    with tf.python_io.TFRecordWriter(output_filename) as tfrecord_writer:
        start_ndx = shard_id * num_per_shard
        end_ndx = min((shard_id + 1) * num_per_shard, len(filenames))
        for i in range(start_ndx, end_ndx):
            # sys.stdout.write('\r>> Converting image %d/%d shard %d' % (
            #     i + 1, len(filenames), shard_id))
            # sys.stdout.flush()

            # Read the filename:
            image_data = tf.gfile.FastGFile(filenames[i], 'rb').read()
            height, width = image_reader.read_image_dims(sess, image_data)

            class_name = os.path.basename(os.path.dirname(filenames[i]))
            class_id = class_names_to_ids[class_name]

            example = dataset_utils.image_to_tfexample(
                image_data, b'jpg', height, width, class_id)
            tfrecord_writer.write(example.SerializeToString())
    g_process.add_finish(output_filename)
    sys.stdout.write('\r>> Converting image %d/%d of files: %d' % (
        len(g_process.finished_file), g_process.all_step, len(filenames)))
    sys.stdout.flush()


def thread_pool(enter_func, param_list):
    pool = threadpool.ThreadPool(cpu_count())
    requests = threadpool.makeRequests(enter_func, param_list)
    [pool.putRequest(req) for req in requests]
    pool.wait()


def _convert_dataset(split_name, filenames, class_names_to_ids, dataset_dir, num_shards):
    """Converts the given filenames to a TFRecord dataset.

    Args:
      split_name: The name of the dataset, either 'train' or 'validation'.
      filenames: A list of absolute paths to png or jpg images.
      class_names_to_ids: A dictionary from class names (strings) to ids
        (integers).
      dataset_dir: The directory where the converted datasets are stored.
    """
    assert split_name in ['train', 'validation']

    num_per_shard = int(math.ceil(len(filenames) / float(num_shards)))

    with tf.Graph().as_default():
        image_reader = ImageReader()

        with tf.Session('') as sess:
            param_list = []
            for shard_id in range(num_shards):
                # create_tf(split_name, filenames, class_names_to_ids, dataset_dir,
                #           num_shards, shard_id, num_per_shard, image_reader, sess)
                param_list.append(
                    ((split_name, filenames, class_names_to_ids, dataset_dir,
                      num_shards, shard_id, num_per_shard, image_reader, sess), None))
            thread_pool(create_tf, param_list)

    sys.stdout.write('\n')
    sys.stdout.flush()


def run(dataset_dir):
    """Runs the download and conversion operation.

    Args:
      dataset_dir: The dataset directory where the dataset is stored.
    """
    if not tf.gfile.Exists(dataset_dir):
        tf.gfile.MakeDirs(dataset_dir)

    photo_filenames, class_names = _get_filenames_and_classes(dataset_dir)
    if len(photo_filenames) == 0:
        print(" no files detected")
        exit(-1)
    zz = zip(class_names, range(len(class_names)))
    class_names_to_ids = dict(zip(class_names, range(len(class_names))))

    random.seed(_RANDOM_SEED)
    random.shuffle(photo_filenames)

    labels_to_class_names = dict(zip(range(len(class_names)), class_names))
    if os.path.exists(OUTPUT_PATH) is True:
        shutil.rmtree(OUTPUT_PATH)
    if os.path.exists(OUTPUT_PATH) is False:
        os.makedirs(OUTPUT_PATH)
    dataset_utils.write_label_file(labels_to_class_names, OUTPUT_PATH)

    print("all files:%d classes: %d " % (len(photo_filenames), len(class_names)))

    _NUM_VALIDATION = math.ceil(len(photo_filenames)/10)
    training_filenames = photo_filenames[_NUM_VALIDATION:]
    validation_filenames = photo_filenames[:_NUM_VALIDATION]

    num_shards = math.ceil(len(training_filenames) / 1000)
    g_process.set_all_step(num_shards)
    _convert_dataset("train", training_filenames, class_names_to_ids,
                     dataset_dir, num_shards)

    num_shards = math.ceil(len(validation_filenames) / 1000)
    g_process.reset()
    g_process.set_all_step(num_shards)
    _convert_dataset("validation", validation_filenames, class_names_to_ids,
                     dataset_dir, num_shards)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("usage: ./tf_train_validation_set.py -i data_set_dir -o out_put_dir")
        exit(-1)
    OUTPUT_PATH = str(sys.argv[4]+"/output_tfrecord")
    start_time = time.time()
    VERSION = int(start_time)
    g_process = GlobalProcess()
    run(sys.argv[2])
    print(' ALL COST: %.5f second' % (time.time() - start_time))
