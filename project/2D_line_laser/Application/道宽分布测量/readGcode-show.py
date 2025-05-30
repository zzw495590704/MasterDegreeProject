import numpy as np
import open3d as o3d
import os
import sys
sys.path.append(r'D:\Project\Software\Pycharm\AAI\AM\MyFunc')
import my_open3D
import my_plot
import my_gcode
if __name__ == '__main__':
    Path = './data/Pattern/arrow/'
    filePath = Path+'arrow.gocde'
    path_pcd, match_e = my_open3D.readGcode('arrow.gcode')
    path_pcd = my_open3D.insertPoint(path_pcd,match_e,interval=0.1)
    o3d.visualization.draw_geometries([path_pcd], window_name='path_pcd')
    path_np = np.array(path_pcd.points)
    path_order = np.arange(1, len(path_np) + 1) /100
    my_plot.draw_scatter_plot_weight_path(path_np,path_order,[min(path_order),max(path_order)],clabel='time/s')
    aa = 1