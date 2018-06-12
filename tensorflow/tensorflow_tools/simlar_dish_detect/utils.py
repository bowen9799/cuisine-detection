import os
from numpy import *
import os
import sys
import shutil


class Utils:
    @staticmethod
    def removeFilesInDir(targetDir):
        for file in os.listdir(targetDir):
            targetFile = os.path.join(targetDir, file)
            if os.path.isfile(targetFile):
                os.remove(targetFile)
            else:
                Utils.removeFilesInDir(targetFile);
        os.rmdir(targetDir)
        pass

    @staticmethod
    def removeSubFilesInDir(targetDir):
        if not os.path.exists(targetDir):
            return

        for file in os.listdir(targetDir):
            targetFile = os.path.join(targetDir, file)
            if os.path.isfile(targetFile):
                os.remove(targetFile)
            else:
                Utils.removeFilesInDir(targetFile);
        pass

    @staticmethod
    def randomCopyFile(src_dir, dist_dir, num):
        listfile = os.listdir(src_dir)

        if not os.path.exists(dist_dir):
            os.makedirs(dist_dir)
        for i in range(num):
            num = random.randint(1, len(listfile))
            # print ('[%d] %s'%(i,listfile[num] ))
            srcfile = os.path.join(src_dir, listfile[num])
            distfile = os.path.join(dist_dir, listfile[num])
            if os.path.isfile(srcfile):
                shutil.copyfile(srcfile, distfile)
        pass

    @staticmethod
    def copyDir(src_dir, dist_dir):
        if os.path.exists(dist_dir):
            os.rmdir(dist_dir)
        shutil.copytree(src_dir, dist_dir)
        pass
