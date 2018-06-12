
#!/bin/sh

if [ -z "$1" ]; then
    if [ -z "$2" ]; then
        echo "Usage: label_deamon.sh [label] [imageRoot]"
        exit
    fi
fi

LABEL_TEST="$1"
echo "using label: $LABEL_TEST "
DATA_DIR="$2"


while true
do
        echo "---------- crawler labeling --------------"
        sleep 1
        for dirs in ${DATA_DIR}/*
            do
                #echo "have dirs : $dirs"
                for file in ${dirs}/*
                    do
                        #echo ${file}
                        if [ "${file##*.}" = "jpg" ] || [ "${file##*.}" = "jpeg" ] || [ "${file##*.}" = "png" ] || [ "${file##*.}" = "JPG" ] || [ "${file##*.}" = "JPEG" ] || [ "${file##*.}" = "PNG" ] || [ "${file##*.}" = "gif" ] ; then
                            echo "================================$dirs has file to dispose================================"
                            sh `dirname $0`/label_image_tool.sh $LABEL_TEST $dirs &
                            break;
                        fi
                        sleep 2 &
                    done
            done
            wait
done


