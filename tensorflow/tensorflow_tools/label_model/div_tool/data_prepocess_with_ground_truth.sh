if [ -z "$1" ]; then
  echo "Usage: dataset_preprocess_with_ground_truth.sh [dataset_dir]"
  echo "for example dataset_preprocess_with_ground_truth.sh ./dataset"
  exit
fi

TOTAL_DIR="${1}"

 #cut the possible last"/"
if [ -z "${1##*/}" ]; then
     TOTAL_DIR="${1%/*}"
fi

#delete caches
rm -rf "./tf_files/bottlenecks"

for DATASET_DIR in $TOTAL_DIR/*
  do
    #dataset must have only one dir
    if [ -d $DATASET_DIR ]; then
      break
    fi
  done

#RESULT_DIR="./result/${DATASET_DIR##*/}"
#if [ -d $RESULT_DIR ]; then
#  echo "$RESULT_DIR is not empty,please save your result first, and then delete this dir"
#  exit
#fi
echo $DATASET_DIR
DATASET_PREPROCESS_DIR="${DATASET_DIR%/*}"
echo $DATASET_PREPROCESS_DIR
TRAIN_200_DIR="$DATASET_PREPROCESS_DIR/TRAIN_200"
#if [ -d $VALIDATION_500_DIR ]; then
#  exit 1
#fi
#mkdir -p "${TRAIN_200_DIR}"

#md5 compare and delete
python ./scripts/md5_compare.py --input_dir=${DATASET_DIR}
#similar image delete
python ./scripts/ImageDiff.py --input_dir=${DATASET_DIR}
#image uitl, provided by shenxue
python ./scripts/imgutils.py --input_dir=${DATASET_DIR}\
      --pattern "*/*.[jJPp][PpNn]*" --task "1-2-3" --nproc 2


FALSE_DIR="${DATASET_DIR}/false"
TRUE_DIR="${DATASET_DIR}/true"

#echo $FALSE_DIR
#echo $TRUE_DIR
#echo ${TRAIN_200_DIR}
python ./scripts/dataset_shuf.py \
        --true_dir=${TRUE_DIR} \
        --false_dir=${FALSE_DIR} \
        --shuf_dir=${TRAIN_200_DIR} \
        --shuf_num=100

TRAIN_FIRST_DIR="./train/train_first"
rm -rf "$TRAIN_FIRST_DIR/truefood"
rm -rf "$TRAIN_FIRST_DIR/falsefood"
mkdir -p "$TRAIN_FIRST_DIR/truefood"
mkdir -p "$TRAIN_FIRST_DIR/falsefood"
cp -R $TRAIN_200_DIR/false/* $TRAIN_FIRST_DIR/falsefood
cp -R $TRAIN_200_DIR/true/* $TRAIN_FIRST_DIR/truefood

MIXED_FOOD_DIR="./mixedthing"
MIXED_FOOD_TAR="mixedthing.tar.gz"
#get mixedthing
rm -rf "$TRAIN_FIRST_DIR/mixedthing"
tar -xzf $MIXED_FOOD_TAR
mv $MIXED_FOOD_DIR $TRAIN_FIRST_DIR/mixedthing

rm -rf ${TRAIN_200_DIR}


#sh div_tool/retrain_first_model_with_ground_truth.sh mobilenet_1.0_224 $TOTAL_DIR
sh div_tool/retrain_first_model_with_ground_truth.sh inception_v3 $TOTAL_DIR

