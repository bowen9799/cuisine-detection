##
## python auto_detect.py --srcdir srcfilePath --out result --num 10  --threshold 0.80
##      --srcdir    pictures for testing
##      --out       assign result dir
##      --num       numbers to simple for every dir
##      --threshold
##
##
## 3 classes, class0 from  none dish, class1 current dish, class2 from others dishes
##

import argparse
import os
from trainer import Trainer
from utils import Utils
from const import const
from food_net import FoodNet
import time
import multiprocessing
from pdb import set_trace
from numpy import *
#import psutil
#import objgraph

fileList = []


def test_sub_process(output_path, test_num, threshold, test_list, result_list):
    print ("test process start...")
    output = open(output_path, "w")
    foodnet = FoodNet(const.GRAPH, const.LABELS);

    for testdir in test_list:  # test other dir
        output.write("%s,\n" % (os.path.basename(testdir)))
        test_files = []
        listfile = os.listdir(testdir)

        for i in range(test_num):
            randint = random.randint(1, len(listfile))
            # print ('[%d] %s'%(i,listfile[num] ))
            test_files.append(os.path.join(testdir, listfile[randint]))

        result = foodnet.label_files(test_files)

        result.sort(key=lambda x: x[1], reverse=True)
        sum = 0;
        for k in result:
            output.write(",%s,,%f\n" % (os.path.basename(k[0]), k[1]))
            if k[1] > threshold:
                sum = sum + 1
        output.write("%d,\n" % (sum))
        print('%s : %d' % (os.path.basename(testdir), sum))
        #print(psutil.Process(os.getpid()).memory_info())
        #objgraph.show_growth(limit=4)

        #objgraph.show_refs(foodnet, filename='sample-backref-graph.png')

        result_list.append((os.path.basename(testdir), sum))
    foodnet.close()
    print ("test process finish...")
    output.close()
    pass


def test_others(cur_dir, dir_list):
    output_path = os.path.join(outdir, cur_dir + ".csv")
    result_array = []

    with multiprocessing.Manager() as manager:
        test_list = manager.list()
        test_list.extend(dir_list)
        result_list = manager.list()
        p_label = multiprocessing.Process(target=test_sub_process, args=(output_path, int(num), float(threshold), test_list,result_list))
        p_label.start()
        p_label.join()
        result_array.extend(result_list)

    result_array.sort(key=lambda x: x[1], reverse=True)
    for k in result_array:
        resultfile.write(",%s,,%d\n" % (k[0], k[1]))
    resultfile.flush()



if __name__ == '__main__':
    srcdir = "./"
    outdir = "result"
    num = 10
    threshold = "0.90"
    dict = []
    const.ROOTDIR = os.getcwd();

    parser = argparse.ArgumentParser()
    parser.add_argument("--srcdir", help="src dir")
    parser.add_argument("--outdir", help="output dir")
    parser.add_argument("--num", help="number to simpling")
    parser.add_argument("--threshold", help="just threshold")

    FLAGS, unparsed = parser.parse_known_args()
    print(FLAGS)
    print(type(FLAGS))

    args = parser.parse_args()

    if args.srcdir:
        srcdir = args.srcdir
    if args.outdir:
        outdir = args.outdir
    if args.num:
        num = args.num
    if args.threshold:
        threshold = float(args.threshold)

    #Utils.removeSubFilesInDir(outdir)  # clean out files last time
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    #Trainer.clean()  # clean training files last time
    #Utils.removeSubFilesInDir(const.TRAIN_OTHER)  # clean out files last time
    #Utils.removeSubFilesInDir(const.TRAIN_NEG)

    fileList = os.listdir(srcdir)
    print(fileList)

    dirnum = len(fileList)
    if dirnum == 0:
        exit(0)

    start = time.time()
    #Utils.copyDir(const.NEG_PICTURES, const.TRAIN_NEG)

    result_path = os.path.join(outdir, const.RESULTFILE)
    resultfile = open(result_path, "w")

    for i in range(dirnum - 1):  # training every dir
        traindir = os.path.join(srcdir, fileList[i])
        if not os.path.isdir(traindir):
            print(fileList[i] + ' is not a dir')
            continue

        for j in range(1, dirnum):
            if j == i:
                continue
            otherdir = os.path.join(srcdir, fileList[j])
            if not os.path.isdir(otherdir):
                continue
            Utils.randomCopyFile(otherdir, const.TRAIN_OTHER, int(num))
        resultfile.write("%s\n" % (fileList[i]))
        #Trainer.train(traindir)
        dir_list = [];
        for j in range(i + 1, dirnum):  # test other dir
            testdir = os.path.join(srcdir, fileList[j])
            if not os.path.isdir(testdir):
                print(fileList[j] + ' is not a dir')
                continue
            dir_list.append(testdir)

        test_others(fileList[i], dir_list)

        #Trainer.clean()
        Utils.removeSubFilesInDir(const.TRAIN_OTHER)
        #set_trace()

    resultfile.close()
    #Utils.removeSubFilesInDir(const.TRAIN_NEG)
    end = time.time()
    print('\n finish time : {:.3f}s\n'.format(end - start))
