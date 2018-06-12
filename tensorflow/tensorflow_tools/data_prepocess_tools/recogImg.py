

from PIL import Image
import os, sys
import shutil
import subprocess
import time

file_size=0

def getallfilefullpath(path):
    allfile=[]
    for dirpath,dirnames,filenames in os.walk(path):
        for dir in dirnames:
            allfile.append(os.path.join(dirpath,dir))
        for name in filenames:
            allfile.append(os.path.join(dirpath, name))
    print (" path %s has %s files"% (path ,len(allfile)))
    return allfile


def getallfilename(path):
    allfile=[]
    for dirpath,dirnames,filenames in os.walk(path):
        for name in filenames:
            allfile.append(name)
    print (" path %s has %s files" % (path, len(allfile)))
    return allfile


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print ("usage: ./sizeDirImage -i inputDirImg -o outDirImg")
        exit(-1)
    else:
        print ("loading ", sys.argv[2])

    inputDir = sys.argv[2]
    outputDir = sys.argv[4]+"/output/"
    if os.path.exists(outputDir) is False:
        os.makedirs(outputDir)

    allfiles = getallfilefullpath(inputDir)
    # allfiles = getallfilename(inputDir)
    for file in allfiles:
        portion = os.path.splitext(file)
        if portion[1] == ".jpg":
            # print (file)
            cmd_str = "python ./openImg.py "+file
            child = subprocess.Popen(cmd_str, shell=True)
            child.wait()
            if child.returncode != 0 :
                print (" img invalid:",file)
                fileBase = os.path.splitext(os.path.basename(file))[0]
                shutil.move(file,outputDir+"/"+fileBase+"_"+str(time.time())+".jpg")
            file_size=file_size+1
            if file_size % 100 == 0 :
                print("remained file :",str(file_size))





