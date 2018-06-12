
#!/bin/sh

if [ -z "$1" ]; then
    echo "Usage: retrain_model.sh [train_images_dir] "
    exit
fi

TRAIN_DIR=$1

python -m scripts.retrain \
  --bottleneck_dir=tf_files/bottlenecks \
  --how_many_training_steps=500 \
  --model_dir=tf_files/models/ \
  --summaries_dir=tf_files/training_summaries/"mobilenet_1.0_224"\
  --output_graph=tf_files/retrained_graph.pb \
  --output_labels=tf_files/retrained_labels.txt \
  --architecture="mobilenet_1.0_224" \
  --image_dir=$TRAIN_DIR


