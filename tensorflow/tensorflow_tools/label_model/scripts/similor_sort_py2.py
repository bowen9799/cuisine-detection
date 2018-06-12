# -*- coding:utf-8 -*-


"""
根据典型图片, 对目标文件夹中的文件进行相似度排序

python similor_sort_py2.py --dir src_dir


src_dir 结构
|--- src_dir
├    └──source (用户图片)
├    └──classic(典型图片)
├    └──sorted (排序后的图片)
├    └──data (restore data, 训练生成)
├    └──model (restore model, 训练生成)
"""

import turicreate as tc
import argparse
import os
import shutil
import time
from pdb import set_trace
import Queue
import numpy as np

DEBUG = False

def  main_min(dir, num):
    """ get the min distance to every classic pic

    :param dir:
    :param num:
    :return:
    """
    start_time = time.time()

    data_path = os.path.join(dir, "data")
    if os.path.exists(data_path):
        ref_data = tc.load_sframe(data_path)
    else:
        source_path = os.path.join(dir, "source")
        ref_data = tc.image_analysis.load_images(source_path)
        ref_data = ref_data.add_row_number()
        ref_data.save(data_path)

    mode_path = os.path.join(dir, "model")

    if os.path.exists(mode_path):
        model = tc.load_model(mode_path)
    else:
        model = tc.image_similarity.create(ref_data, label=None, feature=None, model='resnet-50', verbose=True)
        model.save(mode_path)

    num = ref_data.num_rows()

    bm_path = os.path.join(dir, "classic")
    bm_data = tc.image_analysis.load_images(bm_path)
    similar_images = model.query(bm_data, k=num)

    ret_array=np.zeros((bm_data.num_rows(), num))
    for image in similar_images:
        ref_label = image['reference_label']
        distance = image['distance']
        query_label=image['query_label']
        ret_array[query_label][ref_label]=distance;

    mina = np.amin(ret_array,axis=0)
    sort = np.argsort(mina)

    result_dir = os.path.join(dir,"sorted_dir")

    if not os.path.exists(result_dir):
        os.mkdir(result_dir)

    for k in sort:
        ref_label = k
        distance = mina[k]
        #if distance < 20:
        ref_row = ref_data[ref_label]
        path = ref_row['path']
        print(k, distance, os.path.basename(path))
        cp_path = os.path.join(result_dir, ('%05f_%s' % (distance, os.path.basename(path))))
        #cp_path = os.path.join(result_dir, ('%s' % (os.path.basename(path))))
        shutil.copyfile(path, cp_path)
        print(path, cp_path)


    print mina

def  main_average(dir, num):
    """ get the everage distance to every classic pic

    :param dir:
    :param num:
    :return:
    """
    start_time = time.time()

    data_path = os.path.join(dir, "data")
    if os.path.exists(data_path):
        ref_data = tc.load_sframe(data_path)
    else:
        source_path = os.path.join(dir, "source")
        ref_data = tc.image_analysis.load_images(source_path)
        ref_data = ref_data.add_row_number()
        ref_data.save(data_path)

    mode_path = os.path.join(dir, "model")

    if os.path.exists(mode_path):
        model = tc.load_model(mode_path)
    else:
        model = tc.image_similarity.create(ref_data, label=None, feature=None, model='resnet-50', verbose=True)
        model.save(mode_path)

    num = ref_data.num_rows()

    bm_path = os.path.join(dir, "classic")
    bm_data = tc.image_analysis.load_images(bm_path)
    similar_images = model.query(bm_data, k=num)

    ret_array=np.zeros((bm_data.num_rows(), num))
    for image in similar_images:
        ref_label = image['reference_label']
        distance = image['distance']
        query_label=image['query_label']
        ret_array[query_label][ref_label]=distance;

    mina = np.mean(ret_array,axis=0)
    sort = np.argsort(mina)

    result_dir = os.path.join(dir,"sorted_dir")

    if os.path.exists(result_dir):
        shutil.rmtree(result_dir)
    os.mkdir(result_dir)

    if DEBUG:
        result_file =os.path.join(result_dir,"_.csv")
        res_out =open(result_file, "w")
        res_out.write("name")
        for i in range(bm_data.num_rows()):
            res_out.write(",%s"%(os.path.basename(bm_data[0]["path"])))

        res_out.write(",average,state\n" )

    for k in sort:
        ref_label = k
        distance = mina[k]
        #if distance < 20:
        ref_row = ref_data[ref_label]
        path = ref_row['path']
        print(k, distance, os.path.basename(path))
        cp_path = os.path.join(result_dir, ('%05f_%s' % (distance, os.path.basename(path))))
        #cp_path = os.path.join(result_dir, ('%s' % (os.path.basename(path))))
        shutil.copyfile(path, cp_path)
        print(path, cp_path)

    l_threshled = 100
    h_threshled=len(sort)-100

    if DEBUG:
        j = 0;
        for k in sort:
            ref_row = ref_data[k]
            path = ref_row['path']
            res_out.write("%s"% (os.path.basename(path)))
            for i in range(bm_data.num_rows()):
                res_out.write(",%f" % (ret_array[i][k]))
            res_out.write(",%f" % (mina[k]))
            if j < l_threshled:
                res_out.write(",true\n")
            elif j > h_threshled:
                res_out.write(",false\n")
            else:
                res_out.write(",\n")
            j=j+1
            j=j+1

        res_out.flush()
    print mina

if __name__ == '__main__':
    dir = "./"
    out_dir = "./out_dir"
    selet_num = 0
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir",    help="source to test")
    parser.add_argument("--selet_num",    help="src dir to copy")
    args = parser.parse_args()

    if args.dir:
        dir = args.dir
    if args.selet_num:
        selet_num = int(args.selet_num)
    main_average(dir, selet_num)
