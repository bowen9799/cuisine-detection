#==========================================
#从src 中随机挑选num个文件, copy 到num中
#xufeng02.zhou
#2018-04-28
#===========================================

from numpy  import *
import os
import sys
import shutil
import argparse
from utils import Utils

if __name__ == '__main__':
    src = "./"
    dist = "copy"
    num = 10
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", help="src dir to copy")
    parser.add_argument("--dist", help="dist dir to copy")
    parser.add_argument("--num", help="number to copy")
    args = parser.parse_args()

    src = args.src
    dist = args.dist
    num = args.num
    Utils.randomCopyFile(src, dist, int(num))