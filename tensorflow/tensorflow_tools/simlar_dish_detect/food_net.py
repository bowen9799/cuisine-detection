# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os
import time

import numpy as np
import tensorflow as tf
from const import const
from utils import Utils
import psutil
import objgraph

class FoodNet(object):

    def load_labels(label_file):
        label = []
        proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
        for l in proto_as_ascii_lines:
            label.append(l.rstrip())
        return label

    def read_tensor_from_image_file(self, file_name, input_height=299, input_width=299,
                                    input_mean=0, input_std=255):
        with tf.Graph().as_default():
            input_name = "file_reader"
            output_name = "normalized"
            file_reader = tf.read_file(file_name, input_name)
            if file_name.endswith(".png"):
                image_reader = tf.image.decode_png(file_reader, channels=3,
                                                   name='png_reader')
            elif file_name.endswith(".gif"):
                image_reader = tf.squeeze(tf.image.decode_gif(file_reader,
                                                              name='gif_reader'))
            elif file_name.endswith(".bmp"):
                image_reader = tf.image.decode_bmp(file_reader, name='bmp_reader')
            else:
                image_reader = tf.image.decode_jpeg(file_reader, channels=3,
                                                    name='jpeg_reader')
            float_caster = tf.cast(image_reader, tf.float32)
            dims_expander = tf.expand_dims(float_caster, 0);
            resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
            normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
            normalized_sess = tf.Session()
            result = normalized_sess.run(normalized)

        return result

    def load_graph(model_file):
        graph = tf.Graph()
        graph_def = tf.GraphDef()

        with open(model_file, "rb") as f:
            graph_def.ParseFromString(f.read())
        with graph.as_default():
            tf.import_graph_def(graph_def)

        return graph

    def __init__(self, graphpath=const.GRAPH, labels=const.LABELS):
        print(graphpath, labels)

        self.input_height = 224
        self.input_width = 224
        self.input_mean = 128
        self.input_std = 128
        input_layer = "input"
        output_layer = "final_result"

        model_file = graphpath
        label_file = labels

        graph = FoodNet.load_graph(model_file)
        self.labels = FoodNet.load_labels(label_file)

        input_name = "import/" + input_layer
        output_name = "import/" + output_layer
        self.input_operation = graph.get_operation_by_name(input_name);
        self.output_operation = graph.get_operation_by_name(output_name);

        self.sess = tf.Session(graph=graph)
        self.normalized_sess = tf.Session()

    def label_files(self, files):
        label_ret = []
        start = time.time()

        objgraph.show_growth(limit=4)

        for file in files:
            print(file)
            if file.split('.')[-1] in const.EXTS:
                t = self.read_tensor_from_image_file(file,
                                                input_height=self.input_height,
                                                input_width=self.input_width,
                                                input_mean=self.input_mean,
                                                input_std=self.input_std)
                results = self.sess.run(self.output_operation.outputs[0],
                                   {self.input_operation.outputs[0]: t})
                results = np.squeeze(results)

                top_k = results.argsort()[-5:][::-1]


                for i in top_k:
                    if self.labels[i] == "1":
                        print(self.labels[i], results[i])
                        break

                label_ret.append((file, results[i]))

        end = time.time()
        print('\nEvaluation time (1-image): {:.3f}s\n'.format(end - start))
        # test every pic
        return label_ret

    def close(self):
        self.sess.close()
        self.normalized_sess.close()


