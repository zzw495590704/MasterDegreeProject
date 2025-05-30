#读取Gcode并转关键点点云
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import sys
sys.path.append(r'D:\Project\Software\Pycharm\AAI\AM\MyFunc')
import my_open3D
import my_csv
import open3d as o3d
# 提取坐标和挤出量的函数
def extractValues(inputString):
    # 使用正则表达式查找X、Y、E后的数字
    xMatch = re.search(r'X([\d.]+)', inputString)
    yMatch = re.search(r'Y([\d.]+)', inputString)
    eMatch = re.search(r'E([\d.]+)', inputString)

    # 提取匹配的数字
    x = float(xMatch.group(1))
    y = float(yMatch.group(1))
    e = float(eMatch.group(1))

    return x, y, e


def extractZ(inputString):
    # 使用正则表达式查找Z后的数字
    zMatch = re.search(r'Z([\d.]+)', inputString)

    # 提取匹配的数字
    z = float(zMatch.group(1))

    return z


def extractXY(inputString):
    # 使用正则表达式查找X、Y后的数字
    xMatch = re.search(r'X([\d.]+)', inputString)
    yMatch = re.search(r'Y([\d.]+)', inputString)

    # 提取匹配的数字
    x = float(xMatch.group(1))
    y = float(yMatch.group(1))

    return x, y


def readGcode(filePath):
    # 初始化变量
    coordinates = []
    x = []
    y = []
    z = []
    e = []
    l = []
    temp_x = 0
    temp_y = 0
    temp_z = 0
    temp_e = 0
    lineNumber = 0

    # 打开文件
    with open(filePath, 'r', encoding='utf-8') as fid:
        # 逐行读取文件
        for line in fid:
            lineNumber += 1
            if line == "; End Code\n":
                break
            if line.startswith(';'):
                # 如果是以';'字符开头，则跳过读取该行
                continue
            if line=='\n':
                continue
            # 检查是否包含特定样式的语句
            if 'G1' in line and 'X' in line and 'Y' in line and 'E' in line and len(line) <= 100:
                # 从语句中提取坐标和挤出量信息
                temp_x, temp_y, temp_e = extractValues(line)
                # 将坐标和挤出量添加到相应的数组中
                x.append(temp_x)
                y.append(temp_y)
                z.append(temp_z)
                e.append(temp_e)
                l.append(lineNumber)
            elif 'G1' in line and 'X' in line and 'Y' in line and 'F' in line and len(line) <= 100:
                temp_x, temp_y = extractXY(line)
                x.append(temp_x)
                y.append(temp_y)
                z.append(temp_z)
                e.append(0)
                l.append(lineNumber)
            elif 'G1' in line and 'X' in line and 'Y' in line and len(line) <= 30:
                temp_x, temp_y = extractXY(line)
                x.append(temp_x)
                y.append(temp_y)
                z.append(temp_z)
                e.append(0)
                l.append(lineNumber)
            elif 'G1' in line and 'Z' in line and len(line) <= 15:
                temp_z = extractZ(line)
                x.append(temp_x)
                y.append(temp_y)
                z.append(temp_z)
                e.append(0)
                l.append(lineNumber)

    # 关闭文件
    fid.close()

    # 可视化
    # 生成颜色映射
    colormap_parula = cm.summer  # 可以根据需要选择不同的颜色映射

    # # # 提取坐标信息
    layer_height = z[5]  # 层高
    layer = int(z[-3]/z[5])# 层数
    z_layer = np.linspace(layer_height, layer_height * layer, layer)
    match_index = np.isin(z, z_layer[1:2])
    match_x = np.array(x)[match_index]  # x坐标
    match_y = np.array(y)[match_index]  # y坐标
    match_z = np.array(z)[match_index]  # z坐标
    match_e = np.array(e)[match_index]  # 挤出量

    match_e_normalize = (match_e - np.min(match_e)) / (np.max(match_e) - np.min(match_e))  # 归一化数据
    match_sort = np.arange(len(match_x))
    match_sort_normalize = (match_sort - np.min(match_sort)) / (np.max(match_sort) - np.min(match_sort))  # 归一化数据
    match_l = np.array(l)[match_index]  # gcode行数
    match_size = len(match_e)

    #####保存数据#####
    # 保存多个数组到.npz文件
    np.savez('../../data/save/gcodeXYZ.npz', x=match_x, y=match_y, z=match_z, e=match_e)

    # 绘制点云
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # 设置俯视视角
    ax.view_init(elev=90, azim=0)

    ax.scatter(match_x, match_y, match_z, c=match_sort_normalize, cmap=colormap_parula, s=5)

    # 连接空间点
    for i in range(1, match_size):
        if match_e[i] > 0:
            # 根据挤出量值在颜色映射中插值得到颜色
            colorIndex = int(match_sort_normalize[i] * (colormap_parula.N - 1))
            lineColor = colormap_parula(colorIndex)
            ax.plot(match_x[i - 1:i + 1], match_y[i - 1:i + 1], match_z[i - 1:i + 1], color=lineColor, linewidth=2.0)
        else: 
            ax.plot(match_x[i - 1:i + 1], match_y[i - 1:i + 1], match_z[i - 1:i + 1], '--b', linewidth=1.5)

    ax.scatter(match_x[0], match_y[0], match_z[0], c='b', marker='o', s=100)  # 起始点
    ax.scatter(match_x[-1], match_y[-1], match_z[-1], c='r', marker='o', s=100)  # 终点

    # 设置图形属性
    ax.grid(False)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    # ax.set_zlabel('Z')
    # 关闭z轴坐标轴显示
    ax.zaxis.set_visible(False)
    ax.set_title('Gcode Visualization')
    # plt.colorbar(cm.ScalarMappable(cmap=colormap_parula), ax=ax, label='Normalized Extrusion')
    plt.colorbar(cm.ScalarMappable(cmap=colormap_parula), ax=ax, label='Printing order')
    plt.show()

if __name__ == '__main__':
    # # 文件路径
    filePath = './data/Pattern/line/line6.gcode'
    readGcode(filePath)
    ##########################读取Gcode点云################################

    # pcd = o3d.io.read_point_cloud('../../data/20240411/paten/line-180temp-2.ply')
    # o3d.visualization.draw_geometries([pcd], window_name='obj_pcd')