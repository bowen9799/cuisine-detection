#!/bin/sh

if [ "$#" -ne "7" ]; then
    echo "Usage: model_convert_to_tflite.sh [model_name] [model_dir] [dataset_name] [checkpoint]  [model_output_node_name] [image_size] [inference_type]"
    exit
fi

#echo $#
MODEL_NAME="$1"
#echo $MODEL_NAME

MODEL_DIR="$2"
#echo $MODEL_DIR

DATASET_NAME="$3"
#echo $DATASET_NAME

MODEL_DATA_CHECKPOINT_NAME="$4"
#echo $MODEL_DATA_CHECKPOINT_NAME

MODEL_OUTPUT_NODE_NAME="$5"
#echo $MODEL_OUTPUT_NODE_NAME

IMAGE_SIZE="$6"
#echo $IMAGE_SIZE

INFERENCE_TYPE="$7"
#echo $INFERENCE_TYPE



CURRENT_DIR=$(pwd)
#echo $CURRENT_DIR
PREFIX_PATH="${CURRENT_DIR%/tensorflow*}"
#echo $PREFIX_PATH
TENSORFLOW_MASTER_PREFIX_PATH=$PREFIX_PATH/tensorflow_master/tensorflow
#echo $TENSORFLOW_MASTER_PREFIX_PATH
#echo $TENSORFLOW_MASTER_PREFIX_PATH/tensorflow/python/tools/freeze_graph
TENSORFLOW_MODELS_PREFIX_PATH=$PREFIX_PATH/tensorflow_models/models


python $TENSORFLOW_MODELS_PREFIX_PATH/research/PHICOMM/slim/export_inference_graph.py \
            --model_name=$MODEL_NAME \
            --output_file=$MODEL_DIR/inf_graph.pb \
            --dataset_name=$DATASET_NAME \
            --image_size=$IMAGE_SIZE

python $TENSORFLOW_MASTER_PREFIX_PATH/tensorflow/python/tools/freeze_graph.py \
            --input_graph=$MODEL_DIR/inf_graph.pb \
            --input_checkpoint=$MODEL_DIR/$MODEL_DATA_CHECKPOINT_NAME \
            --input_binary=true --output_graph=$MODEL_DIR/frozen.pb \
            --output_node_names=$MODEL_OUTPUT_NODE_NAME
toco \
  --input_file=$MODEL_DIR/frozen.pb \
  --output_file=$MODEL_DIR/optimized_graph.pb \
  --input_format=TENSORFLOW_GRAPHDEF \
  --output_format=TENSORFLOW_GRAPHDEF \
  --input_shape=1,$IMAGE_SIZE,$IMAGE_SIZE,3 \
  --input_array=input \
  --output_array=$MODEL_OUTPUT_NODE_NAME
toco \
    --input_file=$MODEL_DIR/optimized_graph.pb \
    --output_file=$MODEL_DIR/optimized_graph.tflite \
    --input_format=TENSORFLOW_GRAPHDEF \
    --output_format=TFLITE \
    --input_shape=1,$IMAGE_SIZE,$IMAGE_SIZE,3 \
    --input_array=input \
    --output_array=$MODEL_OUTPUT_NODE_NAME \
    --inference_type=$INFERENCE_TYPE \
    --input_type=$INFERENCE_TYPE


