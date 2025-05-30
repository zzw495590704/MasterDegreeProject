import numpy as np
import open3d as o3d
import os
import sys
sys.path.append(r'D:\Project\Software\Pycharm\AAI\AM\MyFunc')
import my_open3D
from readGcode import readGcode
from insertPoint import insertPoint
from alignPoint import get2Dcloud, movePoint, calPathWidth, showWidthPlot
# transformation = np.array([
#     [1.000000, 0.000000, 0.000000, 126.973419],
#     [0.000000, 1.000000, 0.000000, 66.343636],
#     [0.000000, 0.000000, 1.000000, 0.000000],
#     [0.000000, 0.000000, 0.000000, 1.000000],
# ])
#110Extrution
# transformation = np.array([
#     [0.999920, -0.012683, 0.000000, 127.098366],
#     [0.012683, 0.999920, 0.000000, 65.774338],
#     [0.000000, 0.000000, 1.000000, 0.000000],
#     [0.000000, 0.000000, 0.000000, 1.000000],
# ])
# #30Extriton
# transformation = np.array([
#     [1.000000, 0.000000, 0.000000, 124.817215],
#     [0.000000, 1.000000, 0.000000, 66.499725],
#     [0.000000, 0.000000, 1.000000, 0.000000],
#     [0.000000, 0.000000, 0.000000, 1.000000],
# ])
if __name__ == '__main__':
    Path = '../../data/20240701/Foam/Line-180/'
    # Path = './data/Pattern/loop/in-out/'
    # Path = '../../data/20240710/v5/'
    ##########################读取Gcode点云################################
    # 文件路径
    # filePath = '../../data/gcode/loop.gcode'
    # filePath = Path+'LOOP-40x40-20speed-v5.gcode'
    filePath = Path+'Line-220temp-40x40.gcode'
    path_pcd, match_e = my_open3D.readGcode(filePath)
    path_pcd = my_open3D.insertPointGcode(path_pcd,match_e,interval=0.5)
    # path_insert_pcd = my_open3D.insertPointGcode(path_pcd, match_e, interval=0.1)
    ##########################读取样件点云################################
    pcdPath = Path+'point_cloud.ply'
    pcd = o3d.io.read_point_cloud(pcdPath)
    o3d.visualization.draw_geometries([pcd], window_name='obj_pcd')
    # obj_pcd = my_open3D.fix_plane(pcd)
    obj_pcd = my_open3D.get_object(pcd)
    o3d.visualization.draw_geometries([path_pcd], window_name='path_pcd')
    # obj_pcd = my_open3D.fix_z(obj_pcd,0.6)
    # obj_pcd = obj_pcd.transform(transformation)


    # obj_pcd = my_open3D.rotate_pointscloud(obj_pcd,90)
    # path_pcd = movePoint(path_pcd, obj_pcd)
    obj_pcd = my_open3D.alignmentCentroid(obj_pcd,path_pcd)
    obj_pcd.paint_uniform_color([0, 1, 0])
    path_pcd.paint_uniform_color([1, 0, 0])

    # o3d.visualization.draw_geometries([obj_pcd],window_name='2D_obj_pcd')
    # o3d.visualization.draw_geometries([path_pcd],window_name='2D_path_pcd')

    # o3d.io.write_point_cloud(Path+"path_pcd.ply", path_pcd)
    # o3d.io.write_point_cloud(Path+"obj_pcd.ply", obj_pcd)
    o3d.visualization.draw_geometries([path_pcd, obj_pcd],window_name='align_pcd')
    width_list = calPathWidth(path_pcd, obj_pcd, Path, interval=0.5)
    # ################################保存数据#########################
    coordinate = np.asarray(path_pcd.points)
    # np.savez(Path + 'coordinate.npz', coordinate=coordinate)
    np.savez(Path+'width_weight.npz', width=width_list, coordinate=coordinate)
    # showWidthPlot(path_pcd,width_list)
