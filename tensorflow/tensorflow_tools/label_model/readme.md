预先安装软件：1.jpeginfo
             2.gthumb （快捷键 space/pgon下一张图片 backspac/pgup上一张图片 delete删除 ese退出）
             3.tensorflow
             4.python2.7
             5.自定义快捷键win+e  打开trash （setting-keyboard-shortcut-custom shortcuts） NAME:win+e, Command:nautilus PHICOMM/.Trash-1000/files(或易进入垃圾箱的快捷方式)
	     6.sudo apt install dconf-editor, open"dconf-editor", org->gnome->gthumb->dialogs->messages->confirm-deletion (not use)



————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
爬虫端自动化脚本(非菜品筛选)：

目录介绍：
.
├── dataset
├   └── food(用户放入)
├       └── baidu(本级目录可不存在)
├           └── 1.jpg
├──         └── 1.jpg
├       └── 360(本级目录可不存在)
├           └── 1.jpg
├──         └── 1.jpg
├── div_tool
├── logger
│   └── __pycache__
├── scripts
│   └── __pycache__
├── tf_files
│   ├── bottlenecks
│   ├── flower_photos
│   │   └── daisy
│   ├── models
│   │   ├── mobilenet_v1_0.50_224
│   │   └── mobilenet_v1_1.0_224
│   ├── training_summaries
│   │    ├── inception_v3
│   │    │   ├── train
│   │    │   └── validation
│   │    └── mobilenet_1.0_224
│   │        ├── train
│   │        └── validation
│   └── pbs
│       └───crawler
│            ├── dish_first.pb
│
│── result_pass
│   └── food（清洗后的成功数据集）
│── result_failed
│   └── food（清洗后的失败数据集） 
└── train
    ├── train_first
    ├   └──truefood
    ├   └──mixedthing
    ├──


div_tool：放置分类工具
logger  ：放置日志模块
scripts ：放置迁移训练和label模块
tffiles ：放置预训练和迁移学习模型
train   ：放置筛选的正样本和其他样本　（正样本需要大于３０张）

执行步骤：
1.sh ./div_tool/data_prepocess_crawler.sh [dataset_dir]（执行1脚本会自动执行2,3脚本）
#2.sh div_tool/retrain_first_model_crawler.sh  （训练模型1）
#3.test_model_crawler.sh


1.将数据集放于dataset目录中，数据集必须为双层目录（food+baidu/bing/360）。执行sh ./div_tool/data_prepocess_crawler.sh [dataset_dir]，等待数据清洗结果，通过清洗的数据集会复制到result_pass目录中,未通过清洗的数据会复制到result_failed目录中.

注：若需要重新生成非菜清洗模型,将data_prepocess_crawler.sh的第55,56,57,58行
	"if [ ! -f "$PB_DIR/$CRAWLER_DIR/$DISH_PB_FIRST" ] ; then
	    tar -zxf CRAWLER_PB_FIRST_TAR
	    mv ./pbs ./tf_files
	fi"
    注释,并将tf_files/pbs删除即可进入正常的生成模型的流程。



————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
爬虫端三分类脚本：

目录介绍：
.
├── dataset
├   └── food(用户放入)
├       └── baidu
├           └── 1.jpg
├──         └── 1.jpg
├       └── 360
├           └── 1.jpg
├──         └── 1.jpg
├── div_tool
├── logger
│   └── __pycache__
├── scripts
│   └── __pycache__
├── tf_files
│   ├── bottlenecks
│   ├── flower_photos
│   │   └── daisy
│   ├── models
│   │   ├── mobilenet_v1_0.50_224
│   │   └── mobilenet_v1_1.0_224
│   ├── training_summaries
│   │    ├── inception_v3
│   │    │   ├── train
│   │    │   └── validation
│   │    └── mobilenet_1.0_224
│   │        ├── train
│   │        └── validation
│   └── pbs
│       └───food
│            ├── dish_first.pb
│
│── result_pass
│   └── food（清洗后的成功数据集）
│── result_failed
│   └── food（清洗后的失败数据集,） 
└── train
    ├── train_first
    ├   └──truefood
    ├   └──falsefood
    ├   └──mixedthing
    ├──


div_tool：放置分类工具
logger  ：放置日志模块
scripts ：放置迁移训练和label模块
tffiles ：放置预训练和迁移学习模型
train   ：放置筛选的正样本和其他样本　（正样本需要大于３０张）


执行步骤：
1.sh ./div_tool/data_prepocess.sh （执行1脚本会自动执行2,3脚本）
#2.sh div_tool/retrain_first_model.sh  （训练模型1）
#3.test_model.sh

1.将数据集放于dataset目录中，数据集必须为双层目录（food+baidu/bing/360）。执行sh ./div_tool/data_prepocess.sh，等待运行结果，“Congratulations! data prepocess has finished, it's time to clean food!plase go to train/train_first to clean truefood.then choose(y/n) to continue”. 对应清洗目录会弹出，请相应对train/train_first清洗。
2.将train/train_first/food中的样本进行分类，正样本放入train/train_first/truefood中,负样本中的菜品类样本放入train/train_first/falsefood..负样本中的非菜样本全部删除（或并入mixedthing?）。
3.正样本清洗完毕后交互界面输入"y".等待数据清洗结果。
5.进入result_pass/food，该目录为清洗成功的数据集，供人工清洗。  result_failed/food为清洗失败的数据集

注：流程中有清洗不成功的地方交互输入会弹出失败字样，对应清洗弹出的目录。



————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
模型优化端：

目录介绍：
.
├── dataset
├   └── food(人工标定的数据集放入)
│       ├── false
├       │   └── 1.jpg
├──     └── true
│       └── 1.jpg
│
├── div_tool
├── logger
│   └── __pycache__
├── scripts
│   └── __pycache__
├── tf_files
│   ├── bottlenecks
│   ├── flower_photos
│   │   └── daisy
│   ├── models
│   │   ├── mobilenet_v1_0.50_224
│   │   └── mobilenet_v1_1.0_224
│   └── training_summaries
│       ├── inception_v3
│       │   ├── train
│       │   └── validation
│       └── mobilenet_1.0_224
│           ├── train
│           └── validation
│
└── result
│    └── food（清洗后的数据集）
└── train
    ├── train_first
        └──truefood
        └──mixedfood


div_tool：放置分类工具
logger  ：放置日志模块
scripts ：放置迁移训练和label模块
tffiles ：放置预训练和迁移学习模型
train   ：放置筛选的正样本和其他样本　（正样本需要大于３０张）


执行步骤：
sh ./div_tool/data_preprocess_with_ground_truth.sh（执行1脚本会自动执行2,3脚本）
#sh div_tool/retrain_first_model_with_ground_truth.sh
#sh div_tool/test_model_with_ground_truth.sh

1.将数据集放于dataset目录中，数据集必须为双层目录(food+false/true)，包含true,false的子目录。
2.执行sh div_tool/data_preprocess_with_ground_truth.sh。即可完成清洗
3.进入result/food，该目录为预测后的pass数据集。原dataset中的food已被分成label_test_check_img、label_test_pass_img、label_test_fial_img目录，包含预测后的所有数据及原来的标签（false、true,有文件夹名区别）。
4.评测指标在test.log中保存。包含模型1的预测及正确率，模型2的预测及正确率。  相应代码见script/label_image_with_ground_truth.py,L334




注意：　　！！！！！！！！！！！
1.在训练迁移学习模型时，可能会导致程序挂掉。一般而言时图片有问题，挂掉时会报出错误图片是谁，删除即可。（如果删除后图片少于３０张，要补全。）
2.清洗一个菜品就要一个模型，多个菜品要多个模型
3.train中还有mixthing样本，是其他菜品或者非菜品样本。这个数据集会不断扩大。







