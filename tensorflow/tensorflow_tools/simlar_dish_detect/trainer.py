from const import const
from utils import Utils
import os
import multiprocessing


class Trainer:

    @staticmethod
    def train(datadir):
        print ('copy traindata : %s -> %s' % (datadir, const.TRAIN_SRC))
        Utils.randomCopyFile(datadir, const.TRAIN_SRC, const.TRAIN_NUM)
        p = multiprocessing.Process(target=Trainer.run_tensorflow)
        p.start()
        p.join()

        pass

    @staticmethod
    def run_tensorflow():
        print ("training...")
        cmd = "".join([ \
            "python -m retrain " \
            , "--bottleneck_dir=", const.BOTTLENECKS \
            , "  --how_many_training_steps=100" \
            , "  --model_dir=tf_files/models/" \
            , "  --summaries_dir=", const.SUMMARIES, const.ARCHITECTURE \
            , "  --output_graph=", const.GRAPH \
            , "  --output_labels=", const.LABELS \
            , "  --architecture=", const.ARCHITECTURE \
            , "  --image_dir=", const.TRAIN_DIR \
            ])
        print(cmd)
        os.system(cmd)

    @staticmethod
    def clean():
        print ("clean training data..")
        if os.path.exists(const.TRAIN_SRC):
            Utils.removeFilesInDir(const.TRAIN_SRC);
        if os.path.exists(const.SUMMARIES):
            Utils.removeFilesInDir(const.SUMMARIES);
        if os.path.exists(const.BOTTLENECKS):
            Utils.removeFilesInDir(const.BOTTLENECKS);
        if os.path.exists(const.GRAPH):
            os.remove(const.GRAPH)
        if os.path.exists(const.LABELS):
            os.remove(const.LABELS)
        pass
