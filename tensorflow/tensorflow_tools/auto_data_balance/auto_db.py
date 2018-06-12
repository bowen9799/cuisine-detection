import random
from matplotlib import pyplot as plt
import pygal
import xlrd


def sum_low(data, low):
    suml = 0.0
    for d in data:
        if d < low:
            suml = suml + low

    return suml 



def sum_high(data, high):
    sumh = 0.0
    for d in data:
        if d > high:
            sumh = sumh + high

    return sumh



def sum_low_to_high(data, low, high):
    suml2h = 0.0
    for d in data:
        if d >= low and d <= high:
            suml2h = suml2h + d

    return suml2h
            

def data_mean(data):
    sumd = 0.0
    for d in data:
        sumd = sumd + d

    sumd = int(sumd*1.0/len(data))

    return sumd

def balance_data(data, low, high):
    for i in xrange(len(data)):
        if data[i] < low:
            data[i] = low
        elif data[i] > high:
            data[i] = high

    return data
        

def draw_hist(myList,Title,Xlabel,Ylabel,Xmin,Xmax,Ymin,Ymax):
    plt.hist(myList,100)
    plt.xlabel(Xlabel)
    plt.xlim(Xmin,Xmax)
    plt.ylabel(Ylabel)
    plt.ylim(Ymin,Ymax)
    plt.title(Title)
    plt.show()


#read excel file
excel = xlrd.open_workbook('transfer_v1.1.1.0512.xlsx')
table = excel.sheet_by_index(0)
#acquire distribution of original data
data = [table.cell(i,6).value for i in range(1,table.nrows)]
labels = []
for i in xrange(len(data)):
    data[i] = int(data[i])
    labels.append(str(data[i]))


random.shuffle(data)
data_original = list(data)
data_balanced = list(data)
data.sort()

max_num = data[-1]
min_num = data[0]

#given imbalance ratio
ratio = 1.75

#delta for iterative optimazation
delta = 1
high = int(max_num)
low = int(high / ratio)
mean_balanced = 0.
mean_original = 0.

#iterative optimization
upper = 1
lower = 1
while 1 :
    mean_balanced = int((sum_low(data,low) + sum_high(data,high) + sum_low_to_high(data,low,high))/len(data))
    mean_original = int(data_mean(data))

    if mean_balanced >= mean_original:
        high = high - delta
        low = int(high / ratio)
    else:
        lower = -1

    if lower*upper < 0:
        break


#print Num(min) & Num(max), and Num(max)/Num(min) ~= ratio
print('Num(min): %g' % low)
print('Num(max): %g' % high)

#print mean of original and balanced distribution
print('Balanced mean: %g' % mean_balanced)
print('Original mean: %g' % mean_original)

data_balanced = balance_data(data_balanced, low, high)

hist_o = pygal.Bar()
hist_o.title = 'Original Data'
hist_o.x_labels = labels 
hist_o.x_title = 'Class'
hist_o.y_title = 'Number' 
hist_o.add('DataNumber', data_original)
hist_o.render_to_file('data_original.svg')

hist_b = pygal.Bar()
hist_b.title = 'Balanced Data'
hist_b.x_labels = labels 
hist_b.x_title = 'Class'
hist_b.y_title = 'Number' 
hist_b.add('DataNumber', data_balanced)
hist_b.render_to_file('data_balanced.svg')

data_original.sort()
data_balanced.sort()

hist_os = pygal.Bar()
hist_os.title = 'Original Sorted Data'
hist_os.x_labels = labels 
hist_os.x_title = 'Class'
hist_os.y_title = 'Number' 
hist_os.add('DataNumber', data_original)
hist_os.render_to_file('data_sorted_original.svg')

hist_bs = pygal.Bar()
hist_bs.title = 'Balanced Sorted Data'
hist_bs.x_labels = labels 
hist_bs.x_title = 'Class'
hist_bs.y_title = 'Number' 
hist_bs.add('DataNumber', data_balanced)
hist_bs.render_to_file('data_sorted_balanced.svg')

