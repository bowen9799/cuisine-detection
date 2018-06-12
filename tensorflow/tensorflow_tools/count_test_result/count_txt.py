# coding=utf-8

import uniout

results = []
predict = []
line_num = 0
label = ''

result_dict = dict()

for line in open("mobilenet_v2_result.txt"):

    if line_num % 6 == 0:
        label = line.replace("\n", "").split('/')[1]
        predict = []
    elif line_num % 6 == 5:
        predict.append(line.replace("\n", ""))
        if result_dict.has_key(label):
            result_dict[label].append(predict)
        else:
            result_dict[label] = [predict]
    else:
        predict.append(line.replace("\n", ""))

    line_num += 1

for key in result_dict:
    num = 0.0
    top5 = 0.0
    top1 = 0.0
    for predicts in result_dict[key]:
        #print predicts
        num += 1.0
        if predicts[0].split(' ')[0]==key:
            top1 += 1.0 
        for predict in predicts:
            #print predict
            if predict.split(' ')[0]==key:
                top5 += 1.0
    print key,'top1:',top1/num,'top5:',top5/num
