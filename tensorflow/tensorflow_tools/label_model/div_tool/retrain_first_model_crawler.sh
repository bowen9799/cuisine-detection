
#!/bin/sh

if [ -z "$1" ]; then
  if [ -z "$2" ]; then
        echo "Usage: retrain_model.sh [dataset_dir] [ARCHITECT]"
        echo "for example retrain_model.sh ./dataset mobilenet_1.0_224"
        exit
  fi
fi


TRAIN_FIRST_DIR="train/train_first"
PB_DIR="tf_files/pbs"
DISH_PB_FIRST="dish_first.pb"
TOTAL_DIR="${1}"
#TOTAL_DIR="./dataset"
RESULT_DIR="./result_pass"
CRAWLER_DIR="crawler"
ARCHITECT="${2}"

FILE_NUM_THRESHOLD=31
VALIDATION_CHECK_FILE_NUM_THRESHOLD=200

starttime=`date +'%Y-%m-%d %H:%M:%S'`
for DATASET_DIR in $TRAIN_FIRST_DIR/*
  do
    #dataset must have only one dir
    if [ -d $DATASET_DIR ]; then
        echo $DATASET_DIR
        TRUEFOOD_NUM="$DATASET_DIR/truefood"
        FALSEFOOD_NUM="$DATASET_DIR/falsefood"

        #FOOD_NAME="${DATASET_DIR##*/}"
        #echo $FOOD_NAME

        #get file num in the dir
        true_content=$(ls -l $TRUEFOOD_NUM |grep "^-"|wc -l)
        echo "$true_content"
        #false_content=$(ls -l $FALSEFOOD_NUM |grep "^-"|wc -l)
        #echo "$false_content"

        if [ "$true_content" = "0" ]; then
            echo "$FOOD_NAME dir is empty"
            continue
        fi

        #compare if filenum > threshlod
        #if [ $true_content -gt $FILE_NUM_THRESHOLD -a $false_content -gt $FILE_NUM_THRESHOLD ]; then
        if [ $true_content -gt $FILE_NUM_THRESHOLD ]; then
            echo "filenume enough"

            #retrain pb1
            mkdir -p  $PB_DIR/$CRAWLER_DIR
            python -m scripts.retrain \
              --bottleneck_dir=tf_files/bottlenecks \
              --how_many_training_steps=500 \
              --model_dir=tf_files/models/ \
              --summaries_dir=tf_files/training_summaries/$ARCHITECT\
              --output_graph=$PB_DIR/$CRAWLER_DIR/$DISH_PB_FIRST \
              --output_labels=$PB_DIR/$CRAWLER_DIR/retrained_labels.txt \
              --architecture=$ARCHITECT \
              --image_dir=$DATASET_DIR

            #backup train_first data, validate validation500,copy check data to train_Second
            if [ -f $PB_DIR/$CRAWLER_DIR/$DISH_PB_FIRST ]; then
                #back up train_first train data
                mkdir -p $PB_DIR/$CRAWLER_DIR/train_first
                cp -R $DATASET_DIR/* $PB_DIR/$CRAWLER_DIR/train_first
                rm -rf $DATASET_DIR
            fi

        else
            echo "$CRAWLER_DIR cannot be checked, let people check"
            mkdir -p $PB_DIR/$CRAWLER_DIR/train_first
            cp -R $DATASET_DIR/* $PB_DIR/$CRAWLER_DIR/train_first
            rm -rf $DATASET_DIR

            mkdir -p $RESULT_DIR/$CRAWLER_DIR
            mv $TOTAL_DIR/$CRAWLER_DIR/* $RESULT_DIR/$CRAWLER_DIR
            rm -rf $TOTAL_DIR/$CRAWLER_DIR
        fi

    fi
  done

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

endtime=`date +'%Y-%m-%d %H:%M:%S'`
start_seconds=$(date --date="$starttime" +%s);
end_seconds=$(date --date="$endtime" +%s);
echo "retrain_first_model_crawler.sh run time： "$((end_seconds-start_seconds))"s"

train_first_remain_num=$(ls -l $TRAIN_FIRST_DIR |grep "^d"|wc -l)
if [ $train_first_remain_num -gt 0 ]; then
    #open dir
    nautilus  train/train_first
    if promptyn "Sorry! please contiune checking truefood in train/train_first! Then choose(y/n) to continue"; then
        #echo "yes"
        sh ./div_tool/retrain_first_model_crawler.sh $TOTAL_DIR $ARCHITECT
        exit
    fi
else
    echo "Congratulations! we will go on test dataset!"
    sh ./div_tool/test_model_crawler.sh $TOTAL_DIR $ARCHITECT
    exit
fi


