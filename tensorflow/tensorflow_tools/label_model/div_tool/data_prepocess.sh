#if [ -z "$1" ]; then
#  echo "Usage: dataset_preprocess.sh [dataset_dir]"
#  echo "for example dataset_preprocess.sh ./dataset_preprocess/food_classify"
#  exit
#fi

#DATASET_DIR="${1}"#

# #cut the possible last"/"
#if [ -z "${1##*/}" ]; then
#    DATASET_DIR="${1%/*}"
#fi

TOTAL_DIR="./dataset"
PB_DIR="tf_files/pbs"
DISH_PB_FIRST="dish_first.pb"

TRAIN_FIRST_DIR="train/train_first"
TRAIN_SECOND_DIR="train/train_second"

MIXED_FOOD_DIR="./mixedthing"
MIXED_FOOD_TAR="mixedthing.tar.gz"

DIRECT_TEST_LABEL="true"

starttime=`date +'%Y-%m-%d %H:%M:%S'`

#delete caches
rm -rf "./tf_files/bottlenecks"

for DATASET_DIR in $TOTAL_DIR/*
  do
    #dataset must have only one dir
    if [ -d $DATASET_DIR ]; then
        echo $DATASET_DIR

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

for DATASET_DIR in $TOTAL_DIR/*
  do
    #dataset must have only one dir
    if [ -d $DATASET_DIR ]; then
        #echo $DATASET_DIR

        FOOD_NAME="${DATASET_DIR##*/}"
        echo $FOOD_NAME

        #if pb1 is not prepared, then prepare training images
        if [ ! -f "$PB_DIR/$FOOD_NAME/$DISH_PB_FIRST" ] ; then

            DIRECT_TEST_LABEL="false"

            rm -rf "$PB_DIR/$FOOD_NAME"

            SELECTED_IMAGES=$(ls -1 "${DATASET_DIR}" | shuf | head -300)
            mkdir -p "$TRAIN_FIRST_DIR/$FOOD_NAME/truefood"
            mkdir -p "$TRAIN_FIRST_DIR/$FOOD_NAME/mixedthing"
            mkdir -p "$TRAIN_FIRST_DIR/$FOOD_NAME/falsefood"

            #get food set to be fileterd by human
            for SELECTED_IMAGE in ${SELECTED_IMAGES}; do
            #echo ${DATA_DIR}/${LABEL}/${IMAGE}
            #echo ${MIXED_FOOD_DIR}
                cp "${DATASET_DIR}/${SELECTED_IMAGE}" "$TRAIN_FIRST_DIR/$FOOD_NAME/${SELECTED_IMAGE}"
            done

            #get mixedthing
            tar -xzf $MIXED_FOOD_TAR
            mv $MIXED_FOOD_DIR $TRAIN_FIRST_DIR/$FOOD_NAME/mixedthing

        fi

    fi
  done

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
    sh ./div_tool/test_model.sh
else
    #open imageviewer
    #gthumb -n train
    #open dir
    nautilus  train/train_first

    if promptyn "Congratulations! data prepocess has finished, it's time to clean food!
        plase go to train/train_first to clean truefood.
        then choose(y/n) to continue"; then
        #echo "yes"
        sh ./div_tool/retrain_first_model.sh
        exit
    fi
fi








