if [ -z "$1" ]; then
  echo "Usage: dataset_preprocess.sh [dataset_dir]"
  echo "for example dataset_preprocess.sh ./dataset"
  exit
fi

TOTAL_DIR="${1}"

#cut the possible last"/"
if [ -z "${1##*/}" ]; then
    TOTAL_DIR="${1%/*}"
fi

#TOTAL_DIR="./dataset"
PB_DIR="tf_files/pbs"
DISH_PB_FIRST="dish_first.pb"

CRAWLER_DIR="crawler"

TRAIN_FIRST_DIR="train/train_first"
TRAIN_SECOND_DIR="train/train_second"

MIXED_FOOD_DIR="./mixedthing"
MIXED_FOOD_TAR="mixedthing.tar.gz"
CRAWLER_PB_FIRST_TAR="crawler_pb_first_mobilenet_1.0_224.tar.gz"
#CRAWLER_PB_FIRST_TAR="crawler_pb_first_inception_v3.tar.gz"

DIRECT_TEST_LABEL="true"

starttime=`date +'%Y-%m-%d %H:%M:%S'`

mkdir -p "./tf_files"
#delete caches
rm -rf "./tf_files/bottlenecks"

for DATASET_DIR in $TOTAL_DIR/*
  do
    #dataset must have only one dir
    if [ -d $DATASET_DIR ]; then
        #echo $DATASET_DIR

        #merge subdir in DATASET_DIR.
        python ./scripts/merge_folder.py --input_dir=${DATASET_DIR}
        #jpeginfo check
        python ./scripts/jpegcheck.py --input_dir=${DATASET_DIR}

        #md5 compare and delete
        python ./scripts/md5_compare.py --input_dir=${DATASET_DIR}
    #similar image delete
        python ./scripts/ImageDiff.py --input_dir=${DATASET_DIR}
    #image uitl, provided by shenxue
        python ./scripts/imgutils.py --input_dir=${DATASET_DIR}\
                --pattern "*.[jJPp][PpNn]*" --task "1-2-3" --nproc 2

    fi
  done


if [ ! -f "$PB_DIR/$CRAWLER_DIR/$DISH_PB_FIRST" ] ; then
    tar -zxf $CRAWLER_PB_FIRST_TAR
    mv ./pbs ./tf_files
fi


#if pb1 is not prepared, then prepare training images
if [ ! -f "$PB_DIR/$CRAWLER_DIR/$DISH_PB_FIRST" ] ; then


    DIRECT_TEST_LABEL="false"

    rm -rf "$PB_DIR/$CRAWLER_DIR"

    mkdir -p "$TRAIN_FIRST_DIR/$CRAWLER_DIR/truefood"
    mkdir -p "$TRAIN_FIRST_DIR/$CRAWLER_DIR/mixedthing"
    #mkdir -p "$TRAIN_FIRST_DIR/$CRAWLER_DIR/falsefood"


    #get mixedthing
    tar -xzf $MIXED_FOOD_TAR
    cp -R $MIXED_FOOD_DIR/* $TRAIN_FIRST_DIR/$CRAWLER_DIR/mixedthing

fi

promptyn () {
    while true; do
        read -p "$1 " yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) echo "Please answer yes to continue, or ctrl+c to quit";;
            * ) echo "Please answer yes to continue, or ctrl+c to quit.";;
        esac
    done
}

endtime=`date +'%Y-%m-%d %H:%M:%S'`
start_seconds=$(date --date="$starttime" +%s);
end_seconds=$(date --date="$endtime" +%s);
echo "datapreprocess.sh run time： "$((end_seconds-start_seconds))"s"
#if all food has pb already, then directly test dataset
if [ $DIRECT_TEST_LABEL != "false" ]; then
    sh ./div_tool/test_model_crawler.sh $TOTAL_DIR mobilenet_1.0_224
    #sh ./div_tool/test_model_crawler.sh $TOTAL_DIR inception_v3
else
    #open imageviewer
    #gthumb -n train
    #open dir
    nautilus  train/train_first

    if promptyn "Congratulations! data prepocess has finished, it's time to clean food!
        plase go to train/train_first to clean truefood.
        then choose(y/n) to continue"; then
        #echo "yes"
        sh ./div_tool/retrain_first_model_crawler.sh $TOTAL_DIR mobilenet_1.0_224
        #sh ./div_tool/retrain_first_model_crawler.sh $TOTAL_DIR inception_v3
        exit
    fi
fi








