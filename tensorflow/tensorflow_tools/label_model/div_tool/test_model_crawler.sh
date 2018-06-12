if [ -z "$1" ]; then
  if [ -z "$2" ]; then
    echo "Usage: test_model_crawler.sh [dataset_dir] [ARCHITECT]"
    echo "for example test_model_crawler.sh ./dataset mobilenet_1.0_224"
    exit
  fi
fi

TOTAL_DIR="${1}"
#cut the possible last"/"
if [ -z "${1##*/}" ]; then
    TOTAL_DIR="${1%/*}"
fi

ARCHITECT="$2"

#TOTAL_DIR="./dataset"
PB_DIR="tf_files/pbs"
DISH_PB_FIRST="dish_first.pb"
CRAWLER_DIR="crawler"

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
starttime=`date +'%Y-%m-%d %H:%M:%S'`

if [ ! -f "$PB_DIR/$CRAWLER_DIR/$DISH_PB_FIRST" ]; then
  #echo "$CRAWLER_DIR $DISH_PB_FIRST is not exist, please check train/train_first"
  #open dir
  nautilus  train/train_first
  if promptyn "Sorry! $CRAWLER_DIR $DISH_PB_FIRST is not exist, please check train/train_first!. Then choose(y/n) to continue"; then
    #echo "yes"
    sh ./div_tool/retrain_first_model_crawler.sh $TOTAL_DIR $ARCHITECT
    exit
  fi
fi


#if all food has pb already, then directly test dataset
for DATASET_DIR in $TOTAL_DIR/*
  do
    FOOD_NAME="${DATASET_DIR##*/}"

    #test data with pb1
    sh ./div_tool/label_image_tool_crawler.sh truefood $TOTAL_DIR $FOOD_NAME \
        $PB_DIR/$CRAWLER_DIR/$DISH_PB_FIRST $PB_DIR/$CRAWLER_DIR/retrained_labels.txt $ARCHITECT

  done

  endtime=`date +'%Y-%m-%d %H:%M:%S'`
  start_seconds=$(date --date="$starttime" +%s);
  end_seconds=$(date --date="$endtime" +%s);
  echo "testmodel.sh run time： "$((end_seconds-start_seconds))"s"
