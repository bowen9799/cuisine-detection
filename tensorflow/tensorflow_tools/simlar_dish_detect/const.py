# ==========================================
# 常量类
# xufeng02.zhou
# 2018-04-28
# ===========================================

class _const:
    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("can't change const %s" % name)
        if not name.isupper():
            raise self.ConstCaseError('const name "%s" is not all uppercase' % name)
        self.__dict__[name] = value


const = _const()
const.TRAIN_DIR = "./tf_files/pictures"
const.TRAIN_SRC = "./tf_files/pictures/1"
const.TRAIN_NEG = "./tf_files/pictures/0"
const.TRAIN_OTHER = "./tf_files/pictures/2"
const.DEV_DIR = "./tf_files/dev_set"
const.TRAIN_NUM = 100
const.BOTTLENECKS = "./tf_files/bottlenecks"
const.SUMMARIES = "./tf_files/training_summaries/"
const.GRAPH = "./tf_files/retrained_graph.pb"
const.LABELS = "./tf_files/retrained_labels.txt"
const.ARCHITECTURE = "mobilenet_0.50_224"
const.RESULTFILE = "result.csv"
const.NEG_PICTURES = "./none_dish"
const.EXTS= ['jpg','jpeg','JPG','JPEG','png','PNG']