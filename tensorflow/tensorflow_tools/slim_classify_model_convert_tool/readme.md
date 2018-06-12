

Note: please install toco first. go to FoodAi/tensorflow/tensorflow_master/tensorflow, run
      1.bazel build tensorflow/contrib/lite/toco:toco
      2.bazel-bin/tensorflow/contrib/lite/toco/toco

      go back to "FoodAi/tensorflow/tensorflow_tools/model_convert_to_tflite" try toco in the command , if ok, then go on to use shell.

用法: sh ./model_convert_to_tflite.sh [model_name] [model_dir] [dataset_name] [checkpoint]  [model_output_node_name] [image_size] [inference_type]"

示例: (in the model_convert_to_tflite dir,run the following command)
       1.sh ./model_convert_to_tflite.sh inception_resnet_v2 ./sample/inception_resnet_v2 imagenet model.ckpt-383425 InceptionResnetV2/Logits/Predictions 299 FLOAT
       2.sh ./model_convert_to_tflite.sh mobilenet_v2 [model_dir] foods [checkpoint] MobilenetV2/Predictions/Reshape_1 224 FLOAT

    注意: 如果指令执行失败 (log见下面详情),显示为shape不对应, 很有可能是训练的模型类别和自定义的类别对应比如 NUM_CLASSES=193! but foods.NUM_CLASSES = 1001!
    可以通过如下方式解决:
        1. chanage _NUM_CLASSES=193 in the FoodAi/tensorflow/tensorflow_models/models/research/PHICOMM/slim/datasets/foods.py (do not submit this change to gerrit!)
        #2. you can setup a new dataset like "FoodAi/tensorflow/tensorflow_models/models/research/PHICOMM/slim/datasets/imagenet.py" , change _NUM_CLASSES to 193 and add this dataset in datasets.factory.py.(actually this dataset should be bulid before train.)

    failed log:
    InvalidArgumentError (see above for traceback): Assign requires shapes of both tensors to match. lhs shape= [1001] rhs shape= [193]
        [[Node: save/Assign_52 = Assign[T=DT_FLOAT, _class=["loc:@InceptionResnetV2/Logits/Logits/biases"], use_locking=true, validate_shape=true, _device="/job:localhost/replica:0/task:0/device:CPU:0"](InceptionResnetV2/Logits/Logits/biases, save/RestoreV2:52)]]


命令行输入参数解释:
model_name: this argment shows the name of the architecture to save, must regiter in dict(networks_map, arg_scopes_map) of "tensorflow/tensorflow_models/models/research/PHICOMM/slim/nets/nets_factory.py".

model_dir: this argment shows the model save directory, directory must contain checkpoint

dataset_name: this argment shows the trained dataset. must regiter in "tensorflow/tensorflow_models/models/research/PHICOMM/slim/datasets/datasets.factory.py", this argment also be relevant with the num_classes. If use imagenet, then num_classes is 1001.

checkpoint:checkpoint to be used, must exist in model_dir.

model_output_node_name:this argment shows the output node name of model, if not know, use summarize_graph to get it.
Know more about summarize_graph, please see "tensorflow/tensorflow_master/tensorflow/tensorflow/tools/summarize_graph_main.cc"

image_size:The image size to use

inference_type:FLOAT or QUANTIZED_UINT8




