#!/bin/bash
set -e

# tensorflow models dir
TENSORFLOW_MODELS_DIR=../../tensorflow_models/models

# Where the pre-trained MobileNet V2 checkpoint is saved to.
PRETRAINED_CHECKPOINT_DIR=${TENSORFLOW_MODELS_DIR}/research/slim/mobilenetv2/mobilenetv2_food469_model

# Where the pre-trained MobileNet V2 checkpoint is saved to.
MODEL_NAME=mobilenet_v2

# Where the training (fine-tuned) checkpoint and logs will be saved to.
TRAIN_DIR=finetune221_form_dish469_with_mobilenetv2_log

# Where the dataset is saved to.
DATASET_DIR=food221_tfrecord

# Fine-tune only the new layers for 1000 steps.
######需要修改${TENSORFLOW_MODELS_DIR}/research/slim/datasets/imagenet.py中num_classes为真正的值，如221
######在preprocessing_factory.py的57行添加:  'mobilenet_v2': inception_preprocessing,

python ${TENSORFLOW_MODELS_DIR}/research/slim/train_image_classifier.py \
  --train_dir=${TRAIN_DIR} \
  --dataset_name=imagenet \
  --dataset_split_name=train \
  --dataset_dir=${DATASET_DIR} \
  --model_name=${MODEL_NAME} \
  --checkpoint_path=${PRETRAINED_CHECKPOINT_DIR}/model.ckpt-471058 \
  --checkpoint_exclude_scopes=MobilenetV2/Logits \
  --trainable_scopes=MobilenetV2/Logits \
  --max_number_of_steps=1000 \
  --batch_size=32 \
  --train_image_size=224 \
  --learning_rate=0.01 \
  --learning_rate_decay_type=fixed \
  --save_interval_secs=60 \
  --save_summaries_secs=60 \
  --log_every_n_steps=10 \
  --optimizer=rmsprop \
  --weight_decay=0.00004

# Run evaluation.
python ${TENSORFLOW_MODELS_DIR}/research/slim/eval_image_classifier.py \
  --checkpoint_path=${TRAIN_DIR} \
  --eval_dir=${TRAIN_DIR} \
  --dataset_name=imagenet \
  --dataset_split_name=validation \
  --dataset_dir=${DATASET_DIR} \
  --model_name=${MODEL_NAME} \
  --eval_image_size=224


MODEL_NAME=mobilenet_v2
MODEL_DIR=/media/xing/新加卷1/finetune221_form_dish469_with_mobilenetv2_log
DATASET_NAME=imagenet
IMAGE_SIZE=224
python ${TENSORFLOW_MODELS_DIR}/research/slim/export_inference_graph.py \
            --model_name=$MODEL_NAME \
            --output_file=$MODEL_DIR/inf_graph.pb \
            --dataset_name=$DATASET_NAME \
            --image_size=$IMAGE_SIZE \
            --batch_size=1

##修改${TENSORFLOW_MODELS_DIR}/research/slim/nets/mobilenet/mobilenet_v2.py中depth_multiplier两处默认值（1.0改为1.4）
##tensorflow根目录下：
MODEL_DATA_CHECKPOINT_NAME=model.ckpt-1000
MODEL_OUTPUT_NODE_NAME=MobilenetV2/Predictions/Reshape_1


../../tensorflow-master/tensorflow/bazel-bin/tensorflow/python/tools/freeze_graph \
            --input_graph=$MODEL_DIR/inf_graph.pb \
            --input_checkpoint=$MODEL_DIR/$MODEL_DATA_CHECKPOINT_NAME \
            --input_binary=true --output_graph=$MODEL_DIR/frozen.pb \
            --output_node_names=$MODEL_OUTPUT_NODE_NAME


##冻结图转优化图
toco   --input_file=$MODEL_DIR/frozen.pb   --output_file=$MODEL_DIR/optimized_graph.pb   --input_format=TENSORFLOW_GRAPHDEF   --output_format=TENSORFLOW_GRAPHDEF   --input_shape=1,${IMAGE_SIZE},${IMAGE_SIZE},3   --input_array=input   --output_array=MobilenetV2/Predictions/Reshape_1
##优化图生成tflite
toco   --input_file=${MODEL_DIR}/optimized_graph.pb   --output_file=${MODEL_DIR}/optimized_graph.lite   --input_format=TENSORFLOW_GRAPHDEF   --output_format=TFLITE   --input_shape=1,${IMAGE_SIZE},${IMAGE_SIZE},3   --input_array=input   --output_array=MobilenetV2/Predictions/Reshape_1    --inference_type=FLOAT   --input_type=FLOAT






