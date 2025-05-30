# -*- coding: utf-8 -*-
import os
import re

# 定义文件夹路径
path = './pattern/angle/30/'
img_dir = path + 'data'

# 获取文件夹中的所有文件
files = os.listdir(img_dir)

# 定义正则表达式匹配文件名中的帧数和时间戳
pattern = re.compile(r'frame_(\d+)_(\d+)\.png')

for file in files:
    match = pattern.match(file)
    if match:
        frame_num = match.group(1)
        timestamp = match.group(2)

        # 将帧数格式化为5位数
        new_frame_num = frame_num.zfill(5)

        # 生成新的文件名
        new_file_name = f'frame_{new_frame_num}_{timestamp}.png'

        # 获取旧文件的完整路径和新文件的完整路径
        old_file_path = os.path.join(img_dir, file)
        new_file_path = os.path.join(img_dir, new_file_name)

        # 重命名文件
        os.rename(old_file_path, new_file_path)

        print(f'Renamed {file} to {new_file_name}')

