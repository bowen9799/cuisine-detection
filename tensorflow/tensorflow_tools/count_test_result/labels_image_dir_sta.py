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

import os
import argparse
import shutil

import numpy as np
import tensorflow as tf
from pdb import set_trace

from enum import Enum


class PredictType(Enum):
    TOP1 = 1
    TOP5 = 2
    NONE_TOP5 = 3


class ClassStatistics:
  def __init__(self):
    self.class_name = ""
    self.class_count = 0
    self.class_count_top1 = 0
    self.class_count_top1_pass_thresh = 0
    self.class_top1_under_thresh_files = []

    self.class_count_top5 = 0
    self.class_not_top1_but_top5_files = []

    self.class_count_none_top5 = 0
    self.class_none_top5_files = []

  def get_top1_acc(self):
    return self.class_count_top1 / self.class_count

  def get_top1_high_confidence(self):
    return self.class_count_top1_pass_thresh / self.class_count_top1

  def get_top5_acc(self):
    return self.class_count_top5 / self.class_count

  def overview(self):
    print("class:%s,count:%d,top1:%d,top1_high_acc:%d,top5:%d,none_top5:%d " % (self.class_name,
            self.class_count,
            self.class_count_top1,
            self.class_count_top1_pass_thresh,
            self.class_count_top5,
            self.class_count_none_top5))

  def posibility(self):
    print("class:%s TOP1: %.2f TOP5:%.2f TOP1-HIGH-CONF:%.2f",
          self.class_name,
          self.get_top1_acc(),
          self.get_top5_acc(),
          self.get_top1_high_confidence()
          )

class StatisticsContainer:
  def __init__(self):
    self.cls_sta_ = {}
    self.top1_thresh_hold=0.7

  def refresh_class(self,class_name,file_path,deal_type,score=None):
    if self.cls_sta_.get(class_name) == None:
      self.cls_sta_[class_name] = ClassStatistics()

    self.cls_sta_[class_name].class_name = class_name
    self.cls_sta_[class_name].class_count += 1
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    ################################################ dealing top1 ################################################
    if deal_type == PredictType.TOP1:
      self.cls_sta_[class_name].class_count_top1 += 1
      self.cls_sta_[class_name].class_count_top5 += 1
      if score >= self.top1_thresh_hold:
        self.cls_sta_[class_name].class_count_top1_pass_thresh +=1
      else:
        low_acc_file_dir = dir_name+"/ret_top1_but_low_acc/"
        if os.path.exists(low_acc_file_dir) is False:
          os.makedirs(low_acc_file_dir)
        shutil.copy(file_path,low_acc_file_dir+"/"+base_name)
        self.cls_sta_[class_name].class_top1_under_thresh_files.append(file_path)
    ################################################ dealing top5 ################################################
    if deal_type == PredictType.TOP5:
      self.cls_sta_[class_name].class_count_top5 += 1
      not_top1_but_top5_dir = dir_name + "/ret_not_top1_but_top5"
      if os.path.exists(not_top1_but_top5_dir) is False:
        os.makedirs(not_top1_but_top5_dir)
      shutil.copy(file_path, not_top1_but_top5_dir + "/" + base_name)
      self.cls_sta_[class_name].class_not_top1_but_top5_files.append(file_path)
    ################################################ dealing none top5 ################################################
    if deal_type == PredictType.NONE_TOP5:
      self.cls_sta_[class_name].class_count_none_top5 += 1
      none_top5_dir = dir_name + "/ret_none_top5"
      if os.path.exists(none_top5_dir) is False:
        os.makedirs(none_top5_dir)
      shutil.copy(file_path, none_top5_dir + "/" + base_name)
      self.cls_sta_[class_name].class_none_top5_files.append(file_path)
    self.cls_sta_[class_name].overview()

  def echo_statistics_report(self):
    print("ECHO STATISTICS OF MAP")
    for item in self.cls_sta_.items():
        item[1].overview()




def test_statis():
  sta_map.refresh_class("mm","../1.jpg",True)
  sta_map.refresh_class("mm","../2.jpg",True)
  sta_map.refresh_class("mm","../3.jpg",True)
  sta_map.refresh_class("mm","../4.jpg",False)
  sta_map.refresh_class("kk","../1.jpg",True)
  sta_map.refresh_class("kk","../2.jpg",True)
  sta_map.refresh_class("kk","../23.jpg",False)
  sta_map.refresh_class("kk","../77.jpg",True)
  sta_map.refresh_class("kk","../55.jpg",False)


def load_graph(model_file):
  graph = tf.Graph()
  graph_def = tf.GraphDef()

  with open(model_file, "rb") as f:
    graph_def.ParseFromString(f.read())
  with graph.as_default():
    tf.import_graph_def(graph_def)

  return graph


def read_tensor_from_image_file(file_name,
                                input_height=299,
                                input_width=299,
                                input_mean=0,
                                input_std=255):
  input_name = "file_reader"
  output_name = "normalized"
  file_reader = tf.read_file(file_name, input_name)
  if file_name.endswith(".png"):
    image_reader = tf.image.decode_png(
        file_reader, channels=3, name="png_reader")
  elif file_name.endswith(".gif"):
    image_reader = tf.squeeze(
        tf.image.decode_gif(file_reader, name="gif_reader"))
  elif file_name.endswith(".bmp"):
    image_reader = tf.image.decode_bmp(file_reader, name="bmp_reader")
  else:
    image_reader = tf.image.decode_jpeg(
        file_reader, channels=3, name="jpeg_reader")
  float_caster = tf.cast(image_reader, tf.float32)
  dims_expander = tf.expand_dims(float_caster, 0)
  resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
  normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
  sess = tf.Session()
  result = sess.run(normalized)

  return result


def load_labels(label_file):
  label = []
  proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
  for l in proto_as_ascii_lines:
    label.append(l.rstrip())
  return label

def inference(file_name,class_name):
  t = read_tensor_from_image_file(
      file_name,
      input_height=input_height,
      input_width=input_width,
      input_mean=input_mean,
      input_std=input_std)

  input_name = "import/" + input_layer
  output_name = "import/" + output_layer
  input_operation = graph.get_operation_by_name(input_name)
  output_operation = graph.get_operation_by_name(output_name)

  with tf.Session(graph=graph) as sess:
    results = sess.run(output_operation.outputs[0], {
        input_operation.outputs[0]: t
    })
  results = np.squeeze(results)

  top_k = results.argsort()[-5:][::-1]
  labels = load_labels(label_file)

  is_top1_checked = False
  is_contain_in_top5 = False
  for i in top_k:
    print(labels[i], results[i])
    if is_top1_checked is False \
            and labels[i] in class_name:
      print("   $ file: %s is at TOP1" % file_name)
      sta_map.refresh_class(class_name,file_name,PredictType.TOP1,results[i])
      is_contain_in_top5 = True
      continue
    is_top1_checked = True
    if labels[i] in class_name:
      is_contain_in_top5 = True
      print("   $ file: %s is at TOP5"%  file_name)
      sta_map.refresh_class(class_name,file_name,PredictType.TOP5)
      break
  if is_contain_in_top5 is False:
    print("   $ file: %s is at NONE-TOP5"%  file_name)
    sta_map.refresh_class(class_name, file_name, PredictType.NONE_TOP5)

sta_map = StatisticsContainer()


if __name__ == "__main__":
  # test_statis()
  # sta_map.echo_statistics_report()

  model_file = "inception_test.pb"
  label_file = "labels_final.txt"
  #input_height = 224
  #input_width = 224
  input_mean = 0
  input_std = 255
  input_layer = "input"
  #output_layer = "MobilenetV1/Predictions/Reshape_1"
  output_layer = "InceptionResnetV2/Logits/Predictions"
  input_height = 299
  input_width = 299

  parser = argparse.ArgumentParser()
  parser.add_argument("--image", help="image to be processed")
  parser.add_argument("--graph", help="graph/model to be executed")
  parser.add_argument("--labels", help="name of file containing labels")
  parser.add_argument("--input_height", type=int, help="input height")
  parser.add_argument("--input_width", type=int, help="input width")
  parser.add_argument("--input_mean", type=int, help="input mean")
  parser.add_argument("--input_std", type=int, help="input std")
  parser.add_argument("--input_layer", help="name of input layer")
  parser.add_argument("--output_layer", help="name of output layer")
  args = parser.parse_args()

  if args.graph:
    model_file = args.graph
  if args.image:
    file_name = args.image
  if args.labels:
    label_file = args.labels
  if args.input_height:
    input_height = args.input_height
  if args.input_width:
    input_width = args.input_width
  if args.input_mean:
    input_mean = args.input_mean
  if args.input_std:
    input_std = args.input_std
  if args.input_layer:
    input_layer = args.input_layer
  if args.output_layer:
    output_layer = args.output_layer

  graph = load_graph(model_file)

  file_list = os.listdir(file_name)
  for i in range(0,len(file_list)):
      path = os.path.join(file_name,file_list[i])
      if os.path.isfile(path):
          print(path)
          #set_trace()
          inference(path)
      else:
          sub_file_list = os.listdir(os.path.join(file_name,file_list[i]))
          for j in range(0,len(sub_file_list)):
              sub_path = os.path.join(os.path.join(file_name,file_list[i]),sub_file_list[j])
              if os.path.isfile(sub_path):
                print(" ")
                print("   $beging of one inference:",sub_path)
                list_dir = str(sub_path).split("/")
                if len(list_dir) < 2:
                  print( "path error" )
                  os._exit(-1)
                else:
                  class_name = (list_dir[len(list_dir)-2])
                  print ("from dir detected class name:",class_name)
                  inference(sub_path,class_name)
  sta_map.echo_statistics_report()