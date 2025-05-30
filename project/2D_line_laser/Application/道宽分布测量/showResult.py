# -*- coding: utf-8 -*-
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
mplstyle.use('fast')
from scipy.spatial.distance import pdist,squareform
import sys
sys.path.append(r'D:\Project\Software\Pycharm\AAI\AM\MyFunc')
import my_open3D
import my_plot
import my_math
def showWidthPlot(points,weights):
    # # 可视化点云
    # o3d.visualization.draw_geometries([path])
    # 提取点的坐标
    x = points[:, 0]
    y = points[:, 1]
    z = points[:, 2]
    # 创建一个图形窗口
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # # 设置俯视视角
    # ax.view_init(elev=90, azim=-90)
    # 绘制点
    sc = ax.scatter(x, y, c=weights, cmap='RdYlGn', s=10,  vmin=0.3, vmax=1.3)

    # 添加颜色条
    cbar = plt.colorbar(sc)
    cbar.set_label('Width/mm')

    # 设置坐标轴标签
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    # ax.set_zlabel('Z')

    # 显示图形
    plt.show()

if __name__ == '__main__':
    # loaded_coordinate = np.load('./data/ChangeExtrusion/50/coordinate.npz')
    # loaded_width = np.load('./data/ChangeExtrusion/50/width_weight.npz')
    # coordinate = loaded_coordinate['coordinate']
    # coordinate_ = loaded_width['coordinate']
    # width = loaded_width['width']
    # weight_path = '../../data/20240701/Foam/Line-180-2/width_weight.npz'
    weight_path = '../../data/20240709/ChangeExtrusion/210temp/130/width_weight.npz'
    # weight_path = './data/Pattern/width_weight.npz'
    loaded_data = np.load(weight_path)
    coordinate = loaded_data['coordinate']
    width = loaded_data['width']
    ###############查看直方图#####################
    my_plot.draw_histogram(width)
    ###############5%数据#########################
    replaced_data = my_math.replaceAnormalData(width,0.1)
    delect_data = my_math.replaceAnormalData(width,0.1)
    my_plot.draw_histogram(delect_data)
    average_value = np.mean(delect_data)
    print("道宽均值:",average_value,"mm")
    showWidthPlot(coordinate,replaced_data)