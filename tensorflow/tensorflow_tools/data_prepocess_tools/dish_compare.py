# -*- coding: utf-8 -*-
import os
import re
import cv2
import shutil
import sys,md5
import numpy as np
from matplotlib import pyplot as plt
from pdb import set_trace
import click

def classify_gray_hist(hist1,hist2):
    degree = 0
    hist_len = len(hist1)
    for i in range(hist_len):
        if hist1[i] != hist2[i]:
            degree = degree + abs(hist1[i]-hist2[i])/max(hist1[i],hist2[i])
    degree = 1 - degree/hist_len
    return degree

def scan_folder(path,s,com_mode):
    files= os.listdir(path) #得到文件夹下的所有文件名称
    for file in files: #遍历文件夹
         file_path = os.path.join(path,file)
         if not os.path.isdir(file_path): #判断是否是文件夹，不是文件夹才打开
            f1 = open(file_path,'r')
            if com_mode == 'hist':
                img = cv2.imread(path+"/"+file)
                hist = cv2.calcHist([img],[0],None,[256],[0.0,255.0])
                hist = hist/hist.sum()
                s.append([path+"/"+file, hist])
            else:
                md5_value = md5.new(f1.read()).digest()
                s.append([path+"/"+file,md5_value])
         else:
             scan_folder(file_path,s,com_mode)
    return s

def mymovefile(srcfile,dstfile):
    if not os.path.isfile(srcfile):
        print "%s not exist!"%(srcfile)
    else:
        fpath,fname=os.path.split(dstfile)    #分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)                #创建路径
        shutil.move(srcfile,dstfile)          #移动文件
        print "move %s -> %s"%( srcfile,dstfile)

def compare_and_move(path, compared_path, mode, hist_degree):
    file_list = []
    print(mode)
    scan_folder(path,file_list,mode)
    s_images = []
    print(path)

    for i in range(len(file_list)-1):
        #print(i)
        for j in range(i+1,len(file_list)):
            if mode == 'hist':
                degree = classify_gray_hist(file_list[i][1],file_list[j][1])
                if degree > float(hist_degree):
                    s_images.append(file_list[j][0].split("/")[-1])
                    print(file_list[i][0],file_list[j][0],degree)
            else:
                if file_list[i][1]==file_list[j][1]:
                    s_images.append(file_list[j][0].split("/")[-1])
                    print(file_list[i][0],file_list[j][0])
    set_trace()
    s_images = list(set(s_images))
    for s_image in s_images:
        mymovefile(path+"/"+s_image,compared_path+"/"+s_image)

@click.command()
@click.option('--input_dir', default='./food_classify', help='root path of image folder')
@click.option('--same_data_dir', default='./food_same', help='file search pattern for glob')
@click.option('--compare_mode', default='hist', help='choose compare mode:md5 or hist')
@click.option('--hist_degree', default='0.9', help='set hist compare degree:0.5~1.0')
def main(input_dir, same_data_dir, compare_mode, hist_degree):
    F_PATH = input_dir
    F_CPATH = same_data_dir+'_'+compare_mode
    if compare_mode == 'hist':
        F_CPATH = F_CPATH+'_'+hist_degree
    folders= os.listdir(F_PATH)
    for folder in folders:
        print(folder)
        """
        print(len(re.findall(r"\d{5}1",folder)) != 0)
        if len(re.findall(r"\d{5}1",folder)) == 0:
            continue
        """
        if os.path.isdir(F_PATH+"/"+folder):
            #if folder in ["1_000001","2_000002", "18_000018"]:
            #    continue
            PATH = F_PATH+"/"+folder
            CPATH = F_CPATH+"/"+folder
            compare_and_move(PATH,CPATH,compare_mode,hist_degree)

if __name__ == '__main__':
    main()


