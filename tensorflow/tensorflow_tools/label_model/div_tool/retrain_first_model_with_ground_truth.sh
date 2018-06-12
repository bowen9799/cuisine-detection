
#!/bin/sh

if [ -z "$1" ]; then
    if [ -z "$2" ]; then
        echo "Usage: retrain_model_with_ground_truth.sh [architecture] [dataset_dir]"
        exit
    fi
fi
ARCHITECT="${1}"
TOTAL_DIR="${2}"

DISH_CLEAN_PB_FIRST="dish_first_pb"
DISH_CLEAN_PB_FIRST_ARCHITECT="tf_files/${DISH_CLEAN_PB_FIRST}_${ARCHITECT}"
echo DISH_CLEAN_PB_FIRST_ARCHITECT
mkdir -p $DISH_CLEAN_PB_FIRST_ARCHITECT



#TRAIN_DIR=$1
TRAIN_DIR="./train/train_first"
python -m scripts.retrain \
  --bottleneck_dir=tf_files/bottlenecks \
  --how_many_training_steps=500 \
  --model_dir=tf_files/models/ \
  --summaries_dir=tf_files/training_summaries/$ARCHITECT\
  --output_graph=$DISH_CLEAN_PB_FIRST_ARCHITECT/retrained_graph.pb \
  --output_labels=$DISH_CLEAN_PB_FIRST_ARCHITECT/retrained_labels.txt \
  --image_dir=$TRAIN_DIR \
  --architecture=$ARCHITECT

sh div_tool/test_model_with_ground_truth.sh $ARCHITECT $TOTAL_DIR





