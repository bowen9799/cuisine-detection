#!/bin/sh

if [ -z "$1" ]; then
    if [ -z "$2" ]; then
        echo "Usage: labe_image_tool.sh [label] [imageDir] [pb] [ARCHITECT]"
        exit
    fi
    if [ -z "$3" ]; then
        echo "Usage: labe_image_tool.sh [label] [imageDir] [pb] [ARCHITECT]"
        exit
    fi
    if [ -z "$4" -o -z "$5" ]; then
        echo "labe_image_tool.sh [label] [imageDir] [pb] [ARCHITECT]"
        exit
    fi

fi
echo "$*"



LABEL_TEST="${1}"
echo $LABEL_TEST
CURRENT_DIR=$(pwd)
echo $CURRENT_DIR

TOTAL_DIR="$2"
TOTAL_DIR_NAME="${TOTAL_DIR##*/}"
PRE_TOTAL_DIR="${TOTAL_DIR%/*}"
FOOD_NAME="$3"
DATA_DIR="$TOTAL_DIR/$FOOD_NAME"

#DATA_DIR="$2"
#GRAPH_DIR="${CURRENT_DIR}/tf_files/models/mobilenet_v1_1.0_224"
GRAPH_DIR="$4"
ARCHITECT="$5"
echo $ARCHITECT
#echo $GRAPH_DIR

LABEL_FAIL_DIR="${PRE_TOTAL_DIR}/${TOTAL_DIR_NAME}_result_failed/$FOOD_NAME"
LABEL_CHECK_DIR="${PRE_TOTAL_DIR}/${TOTAL_DIR_NAME}_result_checked/$FOOD_NAME"
LABEL_PASS_DIR="${PRE_TOTAL_DIR}/${TOTAL_DIR_NAME}_result_pass/$FOOD_NAME"

if [ -d $LABEL_FAIL_DIR ]; then
  rm -rf $LABEL_FAIL_DIR
fi

if [ -d $LABEL_CHECK_DIR ]; then
  rm -rf $LABEL_CHECK_DIR
fi

if [ -d $LABEL_PASS_DIR ]; then
  rm -rf $LABEL_PASS_DIR
fi

mkdir -p "${LABEL_FAIL_DIR}"
mkdir -p "${LABEL_CHECK_DIR}"
mkdir -p "${LABEL_PASS_DIR}"


if [ $ARCHITECT = "mobilenet_1.0_224" ]; then
    #python ./scripts/label_image.py \
    python ./scripts/label_image_with_ground_truth.py \
                --graph=${GRAPH_DIR}/retrained_graph.pb\
                --image_path=${DATA_DIR} \
                --pattern="*.[jJPp][PpNn]*" \
                --labels=${GRAPH_DIR}/retrained_labels.txt \
                --label_test=${LABEL_TEST} \
                --label_test_ref=0.9 \
                --label_test_ref_bottom=0.05 \
                --lable_test_fail_dir=${LABEL_FAIL_DIR} \
                --lable_test_check_dir=${LABEL_CHECK_DIR}\
                --lable_test_pass_dir=${LABEL_PASS_DIR}\
                --process_mode="copy"
else
    #python ./scripts/label_image.py \
    python ./scripts/label_image_with_ground_truth.py \
                --graph=${GRAPH_DIR}/retrained_graph.pb\
                --image_path=${DATA_DIR} \
                --pattern="*.[jJPp][PpNn]*" \
                --labels=${GRAPH_DIR}/retrained_labels.txt \
                --input_height=299 \
                --input_width=299 \
                --input_layer="Mul"\
                --label_test=${LABEL_TEST} \
                --label_test_ref=0.6 \
                --label_test_ref_bottom=0.3 \
                --lable_test_fail_dir=${LABEL_FAIL_DIR} \
                --lable_test_check_dir=${LABEL_CHECK_DIR}\
                --lable_test_pass_dir=${LABEL_PASS_DIR}\
                --process_mode="copy"
fi






