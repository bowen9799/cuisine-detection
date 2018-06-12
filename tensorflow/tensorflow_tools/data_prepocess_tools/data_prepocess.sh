if [ -z "$1" ]; then
  echo "Usage: dataset_preprocess.sh [dataset_dir]"
  echo "for example dataset_preprocess.sh ./dataset_preprocess/food_classify"
  exit
fi

DATASET_DIR="${1}"

 #cut the possible last"/"
if [ -z "${1##*/}" ]; then
    DATASET_DIR="${1%/*}"
fi

echo $DATASET_DIR
DATASET_PREPROCESS_DIR="${DATASET_DIR%/*}"
echo $DATASET_PREPROCESS_DIR



#md5 compare and delete
python ./md5_compare.py --input_dir=${DATASET_DIR}

#jpeginfo check
python ./jpegcheck.py --input_dir=${DATASET_DIR}

#image uitl, provided by shenxue
python imgutils.py --input_dir=${DATASET_DIR}\
                   --pattern "*/*.jpg" --task "1-2-3" --nproc 2

#create tfrecord, including jpeginfo check, delete error jpg
python create_tfrecord.py  --dataset_dir="${DATASET_PREPROCESS_DIR}" \
                           --validation_size=0.2 \
                           --tfrecord_filename="food"

