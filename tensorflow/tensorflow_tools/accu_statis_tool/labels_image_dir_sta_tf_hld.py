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
from multiprocessing import cpu_count

import os, sys
import argparse
import shutil
import _thread
import time
import threadpool

import numpy as np
import tensorflow as tf
from pdb import set_trace

from enum import Enum

sys.path.append(".")
from xls_helper import *

TOP1_THRESH_HOLD = 0.7
REPORT_PATH = "/mnt/hgfs/E/tmp/221_dish_report.xls"
DISH_FINISHED=[]


def check_already_finished_dir(dir_list,class_name_dir):
    for dir in dir_list:
        if dir in class_name_dir or class_name_dir in dir or dir == class_name_dir:
            return True
    return False


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

    @staticmethod
    def get_sheet_head():
        return ("品类", "总数", "TOP1数目", "TOP5数目", "非TOP5数目", "TOP1比率", "TOP5比率", "非TOP5比率", "TOP1高置信度比率", "TOP1高置信度阈值")

    def get_sheet_items(self):
        return (
        self.class_name, self.class_count, self.class_count_top1, self.class_count_top5, self.class_count_none_top5,
        self.get_top1_acc(), self.get_top5_acc(), self.get_none_top5_acc(),
        self.get_top1_high_confidence(), TOP1_THRESH_HOLD)

    def get_top1_acc(self):
        if self.class_count == 0:
            return 0
        return self.class_count_top1 / self.class_count

    def get_top1_high_confidence(self):
        if self.class_count_top1 == 0:
            return 0
        return self.class_count_top1_pass_thresh / self.class_count_top1

    def get_top5_acc(self):
        if self.class_count == 0:
            return 0
        return self.class_count_top5 / self.class_count

    def get_none_top5_acc(self):
        if self.class_count == 0:
            return 0
        return self.class_count_none_top5 / self.class_count

    def overview(self):
        print("      $$$class:%s,count:%d,top1:%d,top1_high_acc:%d,top5:%d,none_top5:%d " % (self.class_name,
                                                                                             self.class_count,
                                                                                             self.class_count_top1,
                                                                                             self.class_count_top1_pass_thresh,
                                                                                             self.class_count_top5,
                                                                                             self.class_count_none_top5))

    def posibility(self):
        print("class:%s TOP1: %.2f TOP5:%.2f TOP1-HIGH-CONF:%.2f" % (
            self.class_name,
            self.get_top1_acc(),
            self.get_top5_acc(),
            self.get_top1_high_confidence()
        ))


class StatisticsContainer:
    def __init__(self):
        self.cls_sta_ = {}
        self.last_class_name=""

    def refresh_class(self, class_name, file_path, deal_type, score=None):
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
            if score >= TOP1_THRESH_HOLD:
                self.cls_sta_[class_name].class_count_top1_pass_thresh += 1
            else:
                low_acc_file_dir = dir_name + "/ret_top1_but_low_acc/"
                if os.path.exists(low_acc_file_dir) is False:
                    os.makedirs(low_acc_file_dir)
                shutil.copy(file_path, low_acc_file_dir + "/" + base_name)
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
        print(" ........  ALL classes :", len(self.cls_sta_))
        if self.last_class_name != class_name :
            if check_already_finished_dir(DISH_FINISHED,self.last_class_name) is False:
                print(" ")
                print(" .... Appending Saving last class: ", self.last_class_name)
                print(" ")
                append_excel_one_row(REPORT_PATH,self.cls_sta_[self.last_class_name].get_sheet_items())
        self.last_class_name = class_name

    def echo_statistics_report(self):
        print("ECHO STATISTICS OF MAP")
        for item in self.cls_sta_.items():
            item[1].overview()
            item[1].posibility()


def load_graph(model_file):
    graph = tf.Graph()
    graph_def = tf.GraphDef()

    with open(model_file, "rb") as f:
        graph_def.ParseFromString(f.read())
    with graph.as_default():
        tf.import_graph_def(graph_def)

    return graph


def read_tensor_from_image_file_use_tfplaceholder(input_height=299, input_width=299,
                                                  input_mean=0, input_std=255):
    input_name = "file_reader"
    output_name = "normalized"

    file_name_placeholder = tf.placeholder("string", name="fname")
    file_reader = tf.read_file(file_name_placeholder, input_name)
    image_reader = tf.image.decode_jpeg(file_reader, channels=3,
                                        name='jpeg_reader')
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0);
    resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    return normalized


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


def post_process(top_k,results,filepack):
    is_top1_checked = False
    is_contain_in_top5 = False
    for i in top_k:
        print(labels[i], results[i])
        if is_top1_checked is False \
                and labels[i] in filepack.class_name:
            print("   $ file: %s is at TOP1" % filepack.file_name)
            sta_map.refresh_class(filepack.class_name, filepack.file_name, PredictType.TOP1, results[i])
            is_contain_in_top5 = True
            continue
        is_top1_checked = True
        if labels[i] in filepack.class_name:
            is_contain_in_top5 = True
            print("   $ file: %s is at TOP5" % filepack.file_name)
            sta_map.refresh_class(filepack.class_name, filepack.file_name, PredictType.TOP5)
            break
    if is_contain_in_top5 is False:
        print("   $ file: %s is at NONE-TOP5" % file_name)
        sta_map.refresh_class(filepack.class_name, filepack.file_name, PredictType.NONE_TOP5)


def inference(filepack_list):
    with tf.Session(graph=graph) as sess:
        read_tensor_from_image_file_op = read_tensor_from_image_file_use_tfplaceholder(
            input_height=input_height,
            input_width=input_width,
            input_mean=input_mean,
            input_std=input_std)
        for filepack in file_pack_list:
            print(" ")
            print("   $ reading file:", filepack.file_name)
            if os.path.isfile(filepack.file_name):
                print(" ")
                print("   $beging of one inference:", filepack.file_name)
                t = sess.run(read_tensor_from_image_file_op, feed_dict={"fname:0": filepack.file_name})
                results = sess.run(output_operation.outputs[0], {
                    input_operation.outputs[0]: t
                })
                results = np.squeeze(results)
                top_k = results.argsort()[-5:][::-1]
                _thread.start_new_thread(post_process,(top_k,results,filepack))
                # post_process(top_k,results,filepack)


def iterator_main(filepack):
    jpgcheck = 'jpeginfo' + ' -c ' + filepack.file_name + ' -d' + '\n'
    os.system(jpgcheck)
    if os.path.splitext(filepack.file_name)[1] != ".jpg" and os.path.isfile(filepack.file_name):
        newname = os.path.splitext(filepack.file_name)[0] + ".jpg"
        os.rename(filepack.file_name, newname)
        filepack.file_name = newname
    if os.path.isfile(filepack.file_name):
        list_dir = str(filepack.file_name).split("/")
        if len(list_dir) < 2:
            print("path error")
            os._exit(-1)
        else:
            filepack.class_name = (list_dir[len(list_dir) - 2])
            print("from dir detected class name:", filepack.class_name)
    else:
        print(" check img error, skiping", filepack.file_name)
        filepack.file_name = ""


class FilePack:
    def __init__(self, file_name, class_name):
        self.file_name = file_name
        self.class_name = class_name
    def __lt__(self, other):
        return self.class_name.lower() < other.class_name.lower()

def thread_pool(enter_func,param_list):
  pool = threadpool.ThreadPool(cpu_count()*2)
  requests = threadpool.makeRequests(enter_func, param_list)
  [pool.putRequest(req) for req in requests]
  pool.wait()


def preprocess(sub_path):
    filepack = FilePack(sub_path, "")
    iterator_main(filepack)
    if os.path.isfile(filepack.file_name):
        if check_already_finished_dir(DISH_FINISHED, filepack.class_name) is False:
            print("   ** ADD %s %s" % (filepack.class_name, filepack.file_name))
            file_pack_list.append(filepack)


sta_map = StatisticsContainer()

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("usage: python ./labels_image_dir_sta.py --image=xxxpath --report=xxxpath")
        exit(-1)

    os.environ["CUDA_VISIBLE_DEVICES"] = ""

    start_time = time.time()
    model_file = "mobilenet_v2_model/mobilenet_v2_frozen.pb"
    label_file = "mobilenet_v2_model/labels_221.txt"
    output_layer = "MobilenetV2/Predictions/Reshape_1"
    input_height = 224
    input_width = 224
    #
    input_mean = 0
    input_std = 255
    input_layer = "input"

    #model_file = "inception_resnet_v2/inception_resnet_v2_frozen.pb"
    #label_file = "inception_resnet_v2/labels_final.txt"
    #input_mean = 0
    #input_std = 255
    #input_layer = "input"
    #output_layer = "InceptionResnetV2/Logits/Predictions"
    #input_height = 299
    #input_width = 299

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
    parser.add_argument("--report", help="report")
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
    if args.report:
        REPORT_PATH = args.report
        if os.path.exists(REPORT_PATH) is False:
            xls_writer = XlsHelper()
            xls_writer.add_sheet("DishReport")
            xls_writer.add_sheet_data("DishReport", ClassStatistics.get_sheet_head())
            xls_writer.save(REPORT_PATH)
            print(" Saving new ",REPORT_PATH)

    DISH_FINISHED = read_excel(REPORT_PATH)
    print("DISH_FINISHED:",DISH_FINISHED)

    graph = load_graph(model_file)
    input_name = "import/" + input_layer
    output_name = "import/" + output_layer
    input_operation = graph.get_operation_by_name(input_name)
    output_operation = graph.get_operation_by_name(output_name)
    labels = load_labels(label_file)

    sub_path_list = []
    file_pack_list = []
    file_list = os.listdir(file_name)
    for i in range(0, len(file_list)):
        path = os.path.join(file_name, file_list[i])
        if os.path.isfile(path):
            print(path)
            # set_trace()
            # inference(path)
        else:
            sub_file_list = os.listdir(os.path.join(file_name, file_list[i]))
            for j in range(0, len(sub_file_list)):
                sub_path = os.path.join(os.path.join(file_name, file_list[i]), sub_file_list[j])
                sub_path_list.append(sub_path)
                # iterator_main(sub_path)
    thread_pool(preprocess,sub_path_list)
    file_pack_list.sort()
    inference(file_pack_list)
    sta_map.echo_statistics_report()

    if check_already_finished_dir(DISH_FINISHED, sta_map.last_class_name) is False:
        print(" ")
        print(" .... Appending Saving FINAL class: ", sta_map.last_class_name)
        print(" ")
        append_excel_one_row(REPORT_PATH, sta_map.cls_sta_[sta_map.last_class_name].get_sheet_items())

    print(' ALL COST: %d second' % (time.time() - start_time))
