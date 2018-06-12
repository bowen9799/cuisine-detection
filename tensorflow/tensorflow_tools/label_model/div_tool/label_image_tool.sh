#!/bin/sh

if [ -z "$1" ]; then
    if [ -z "$2" ]; then
        echo "Usage: labe_image_tool.sh [label] [imageDir]"
        exit
    fi
    if [ -z "$3" -o -z "$4" ]; then
        echo "Usage: labe_image_tool.sh [label] [imageDir] [pb] [label.txt]"
        exit
    fi
fi


LABEL_TEST="${1}"
echo $LABEL_TEST
CURRENT_DIR=$(pwd)
echo $CURRENT_DIR
DATA_DIR="$2"
#GRAPH_DIR="${CURRENT_DIR}/tf_files/models/mobilenet_v1_1.0_224"
GRAPH_PB="$3"
LABEL_TXT="$4"
#echo $GRAPH_DIR

LABEL_FAIL_DIR="${DATA_DIR}/label_test_fail_img"
LABEL_CHECK_DIR="${DATA_DIR}/label_test_check_img"
LABEL_PASS_DIR="${DATA_DIR}/label_test_pass_img"
mkdir -p "${LABEL_FAIL_DIR}"
mkdir -p "${LABEL_CHECK_DIR}"
mkdir -p "${LABEL_PASS_DIR}"


#python ./div_tool/label_image_with_ground_truth.py \
python ./scripts/label_image.py \
            --graph=${GRAPH_PB}\
            --image_path=${DATA_DIR} \
            --pattern="*.[jJPp][PpNn]*" \
            --labels=${LABEL_TXT} \
            --label_test=${LABEL_TEST}   \
            --label_test_ref=0.9 \
            --label_test_ref_bottom=0.05 \
            --lable_test_fail_dir=${LABEL_FAIL_DIR} \
            --lable_test_check_dir=${LABEL_CHECK_DIR}\
            --lable_test_pass_dir=${LABEL_PASS_DIR}





