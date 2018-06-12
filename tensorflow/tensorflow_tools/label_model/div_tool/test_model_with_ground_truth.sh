
#!/bin/sh

if [ -z "$1" ]; then
    if [ -z "$2" ]; then
        echo "Usage: test_model_with_ground_truth.sh [architecture] [dataset_dir]"
        exit
    fi
fi
ARCHITECT="${1}"
TOTAL_DIR="${2}"
#cut the possible last"/"
if [ -z "${2##*/}" ]; then
    TOTAL_DIR="${2%/*}"
fi

DISH_CLEAN_PB_FIRST="tf_files/dish_first_pb"
#mkdir -p $DISH_CLEAN_PB_FIRST

#TRAIN_DIR=$1
TRAIN_DIR="./train/train_first"

for DATASET_DIR in $TOTAL_DIR/*
  do
    FOOD_NAME="${DATASET_DIR##*/}"


    #dataset must have only one dir
    if [ -d $DATASET_DIR ]; then
        sh ./div_tool/label_image_tool_with_ground_truth.sh truefood $TOTAL_DIR $FOOD_NAME ${DISH_CLEAN_PB_FIRST}_${ARCHITECT} ${ARCHITECT}
        break
    fi
  done

#RESULT_DIR="./result/${DATASET_DIR##*/}"
#echo $RESULT_DIR
#rm -rf $RESULT_DIR
#if [ -d $RESULT_DIR ]; then
#  exit
#fi
#mkdir -p "$RESULT_DIR/true"
#mkdir -p "$RESULT_DIR/false"
#cp -R $DATASET_DIR/label_test_pass_img/true/* "$RESULT_DIR/true"
#cp -R $DATASET_DIR/label_test_pass_img/false/* "$RESULT_DIR/false"





