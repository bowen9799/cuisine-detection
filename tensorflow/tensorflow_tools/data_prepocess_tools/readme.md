
note:  please first apt install jpeginfo,
       then use python2.7 and tensorflow to preproces dataset
       recommend pyenv + anaconda2.7 + tensorflow


1.please make a new directory"dataset_preprocess", and put image folders in the "dataset_preprocess".
  directory should like this:
     +food_classify
            +classification_1
                -1.jpg
                -2.jpg
            +classification_2
                -1.jpg
                -2.jpg



2.#use following command to pint log in the terminal.
    sh ./data_prepocess.sh ./dataset_preprocess/food_classify
  #use following command to get stderr to txt.
    sh ./data_prepocess.sh ./dataset_preprocess/food_classify 2>0.txt
  #use following command to get stderr and stdout to txt.
    sh ./data_prepocess.sh ./dataset_preprocess/food_classify &>0.txt


