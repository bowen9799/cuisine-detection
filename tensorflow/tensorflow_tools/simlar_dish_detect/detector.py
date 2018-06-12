##
## python detector.py --srcdir /home/xufeng02/develop/ai/origin/tensorflow-for-poets-2/tf_files/foods/train --out result --num 10  --threshold 0.99##
## negtive data from 70000 none dishes
##

import argparse
import os
import trainer
from utils import Utils
from const import const
from justor import label_image
import numpy as numpy
import time

if __name__ == '__main__':
    srcdir = "./"
    outdir = "result"
    num = 10
    threshold = "0.99"
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

    Utils.removeSubFilesInDir(outdir)  # clean out files last time
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    train = trainer.Trainer()
    # train.clean()                       #clean training files last time

    listfile = os.listdir(srcdir)
    print(listfile)

    dirnum = len(listfile)
    if dirnum == 0:
        exit(0)

    start = time.time()
    result_path = os.path.join(outdir, const.RESULTFILE)
    resultfile = open(result_path, "w")

    for i in range(dirnum - 1):  # training every dir
        traindir = os.path.join(srcdir, listfile[i])
        if not os.path.isdir(traindir):
            print(listfile[i] + ' is not a dir')
            continue
        train.train(traindir)
        resultfile.write("%s,%s\n" % (listfile[i], ",".join("")))

        output_path = os.path.join(outdir, listfile[i] + ".csv")
        output = open(output_path, "w")
        result_array = []

        for j in range(i + 1, dirnum):  # test other dir
            testdir = os.path.join(srcdir, listfile[j])
            if not os.path.isdir(testdir):
                print(listfile[j] + ' is not a dir')
                continue
            print ("calculate... ", listfile[j])
            output.write("%s,%s\n" % (listfile[j], ",".join("")))

            Utils.randomCopyFile(testdir, const.DEV_DIR, int(num))
            sum = 0
            testfile = os.listdir(const.DEV_DIR)
            labels = []

            for file in testfile:  # test every pic
                filepath = os.path.join(const.DEV_DIR, file)

                ret = label_image(filepath)
                if ret > threshold:
                    sum = sum + 1
                labels.append((file, ret))
            labels.sort(key=lambda x: x[1], reverse=True)
            for k in labels:
                output.write("%s,,%f\n" % (k[0], k[1]))
            output.write("%d,,%s\n" % (sum, ""))
            print('%s : %d' % (testdir, sum))

            Utils.removeFilesInDir(const.DEV_DIR)
            result_array.append((listfile[j], sum))

        result_array.sort(key=lambda x: x[1], reverse=True)
        for k in result_array:
            resultfile.write("%s,,%d\n" % (k[0], k[1]))
        train.clean()

    end = time.time()
    print('\n finish time : {:.3f}s\n'.format(end - start))
