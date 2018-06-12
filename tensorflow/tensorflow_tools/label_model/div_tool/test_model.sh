



TOTAL_DIR="./dataset"
PB_DIR="tf_files/pbs"
DISH_PB_FIRST="dish_first.pb"

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
for DATASET_DIR in $TOTAL_DIR/*
  do
    FOOD_NAME="${DATASET_DIR##*/}"
    if [ ! -f "$PB_DIR/$FOOD_NAME/$DISH_PB_FIRST" ]; then
      #echo "$FOOD_NAME $DISH_PB_FIRST is not exist, please check train/train_first"
      #open dir
      nautilus  train/train_first
      if promptyn "Sorry! $FOOD_NAME $DISH_PB_FIRST is not exist, please check train/train_first!. Then choose(y/n) to continue"; then
        #echo "yes"
        sh ./div_tool/retrain_first_model.sh
        exit
      fi
    fi
  done

#if all food has pb already, then directly test dataset
for DATASET_DIR in $TOTAL_DIR/*
  do
    FOOD_NAME="${DATASET_DIR##*/}"

    #test data with pb1
    sh ./div_tool/label_image_tool.sh truefood $DATASET_DIR \
        $PB_DIR/$FOOD_NAME/$DISH_PB_FIRST $PB_DIR/$FOOD_NAME/retrained_labels.txt

    RESULT_DIR="./result_pass/$FOOD_NAME"
    FAILED_DIR="./result_failed/$FOOD_NAME"
    echo $RESULT_DIR

    if [ -d $FAILED_DIR ]; then
      rm -rf $FAILED_DIR
    fi
    mkdir -p $FAILED_DIR

    if [ -d $RESULT_DIR ]; then
      rm -rf $RESULT_DIR
    fi

    mkdir -p $RESULT_DIR
    mkdir -p $FAILED_DIR
    cp -R $DATASET_DIR/label_test_pass_img/* $RESULT_DIR

    cp -R $DATASET_DIR/label_test_fail_img/* $FAILED_DIR

    #rm -rf $DATASET_DIR
  done

  endtime=`date +'%Y-%m-%d %H:%M:%S'`
  start_seconds=$(date --date="$starttime" +%s);
  end_seconds=$(date --date="$endtime" +%s);
  echo "testmodel.sh run time： "$((end_seconds-start_seconds))"s"
