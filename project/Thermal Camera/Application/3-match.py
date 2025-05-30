# -*- coding: utf-8 -*-
import numpy as np
import os
import re
import sys
sys.path.append(r'D:\Project\Software\Pycharm\AAI\AM\MyFunc')
import my_csv
import my_plot
import my_csv
import pickle

path = './pattern/angle/30/'
path_npz = path + 'coordination.npz'
path_photo = path + 'data'
path_save = path + 'temp.pkl'
data = np.load(path_npz)
x = data['x']
y = data['y']
time = data['time']
# 创建一个字典来存储图像文件名及其对应的时间戳索引
timestamp_index_map = {}

# 定义正则表达式来提取文件名中的帧数和时间戳
pattern = re.compile(r'frame_(\d+)_(\d+)\.png')

# 存储结果的列表
result = []

start_index = 0
# 遍历图像文件夹
for filename in os.listdir(path_photo):
    match = pattern.match(filename)
    if match:
        #todo:跳过第一张图片
        frame_number = int(match.group(1))

        timestamp = int(match.group(2))
        # 查找时间戳在time数组中最接近的数的索引
        closest_index = np.argmin(np.abs(time - timestamp))
        closest_timestamp = time[closest_index]
        if (frame_number == 0):
            start_index = closest_index
            continue
        # 创建字典并添加到结果列表中
        temp_x = x[start_index-1: closest_index]
        temp_y = y[start_index-1: closest_index]
        temp_coordinate = np.array([temp_x, temp_y]).T
        match_vector = np.diff(temp_coordinate, axis=0)
        match_x = temp_x[1:]
        match_y = temp_y[1:]
        bin_name = 'frame_'+ str(frame_number) + '_1.bin'
        result.append({
            'frame': frame_number,
            'file': filename,
            'bin': bin_name,
            'time': closest_timestamp,  # 使用 closest_timestamp
            'index': int(closest_index),
            'match_x': match_x,
            'match_y': match_y,
            'match_vector':match_vector,
            'time_diff':closest_timestamp-timestamp
        })
        start_index = closest_index
        if frame_number >= 2327:
            aa =1

with open(path_save, 'wb') as f:
    pickle.dump(result, f)
# 从 pickle 文件读取字典列表
with open(path_save, 'rb') as f:
    dict_list = pickle.load(f)

for i in range(len(dict_list)):
        frame = dict_list[i]['frame']
        if(frame==8380):
            print(i)


# my_plot.draw_histogram(timeDiffList)
# # 将一维数组写入 CSV 文件
# np.savetxt('./pattern/synTest/timeDiff.csv', timeDiffList, delimiter=',')
# my_csv.list_to_csv('./pattern/synTest/timeDiff.csv',timeDiffList,'timeDiff')
aa = 0
