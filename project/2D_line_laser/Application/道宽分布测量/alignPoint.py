#点云与Gcode路径融合
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
import os
mplstyle.use('fast')
from scipy.spatial.distance import pdist,squareform
import sys
sys.path.append(r'D:\Project\Software\Pycharm\AAI\AM\MyFunc')
import my_open3D
from insertPoint import insertPoint

def movePoint(path,pcd):
    # 4. 计算data1和data2的质心
    center_data1 = np.mean(np.asarray(pcd.points), axis=0)
    center_data2 = np.mean(np.asarray(path.points), axis=0)

    # 5. 计算变换矩阵
    translation = center_data1 - center_data2
    transformation = np.identity(4)
    transformation[:3, 3] = translation

    # 6. 应用变换
    path.transform(transformation)
    return path

def calPathWidth(path,pcd,savePath,interval=0.1):
    save_path = savePath+'photo/'
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    #读取点云文件
    path_np = np.array(path.points)
    path_widths = np.array([0])
    #读取最大高度差
    h = my_open3D.getMaxDiffZ(pcd)
    print("高度差：",h)
    for i in range(len(path_np) - 2):

        point1 = path_np[i]
        point2 = path_np[i+1]
        show_point = my_open3D.drawPoints(path_np[i+1:i+2],color=[0,0,0])
        # 定义包围盒的半长轴
        extent = [6, h, interval]
        # 定义方向向量
        direction_vector = point2-point1
        vertical_vector = np.array([-direction_vector[1], direction_vector[0],0])
        # print("方向:",direction_vector)
        # print("法线方向:",vertical_vector)
        obb_cut = my_open3D.get_orientBoxVertical(point2,extent,direction_vector)
        cropped = pcd.crop(obb_cut)
        cropped.paint_uniform_color([0.4,0.4,0])
        cropped_np = np.array(cropped.points)
        if(len(cropped_np)==0):
            path_widths = np.append(path_widths, path_widths[-1])
            continue
        # o3d.visualization.draw_geometries([pcd,path])
        # ##################点云聚类#############################
        cropped_cluster = my_open3D.clusterPointDBSCAN(cropped)
        if(len(cropped_cluster)>1):
            cluster_index,_,_ = my_open3D.find_nearest_point_in_point_clouds(cropped_cluster,point2)
            path_cluster = cropped_cluster[cluster_index]

        elif len(cropped_cluster)==1:
            path_cluster = cropped_cluster[0]
        else:
            path_widths = np.append(path_widths, path_widths[-1])
            continue
        # ##################道宽计算##############################
        # distances = my_open3D.minimum_bounding_rectangle(cropped)

        path_cluster_np = np.array(path_cluster.points)
        path_cluster_centroid = np.mean(path_cluster_np, axis=0)
        distances, p1, p2 = my_open3D.getVectorDistance(path_cluster_np,vertical_vector)
        distances_h = my_open3D.getMaxDiffZ(path_cluster)
        distance_extent = [distances, distances_h, interval]
        distance_obb =my_open3D.get_orientBox(path_cluster_centroid,distance_extent,obb_cut.R)
        print(f"[{i}]道宽:",distances)
        # # # 创建直线
        # line_set1 = o3d.geometry.LineSet()
        # line_set1.points = o3d.utility.Vector3dVector([p1, p2])
        # line_set1.lines = o3d.utility.Vector2iVector([[0, 1]])
        # line_set1.colors = o3d.utility.Vector3dVector([[1, 0, 0]])  # 设置为红色和绿色

        # ##################显示##############################
        # if(i>=750):
        show_pcd = [pcd,path,
                    # distance_obb,
                    cropped,
                    obb_cut,
                    show_point]
        # show_pcd = [distance_obb, obb_cut]
        show_pcd.extend(cropped_cluster)
        o3d.visualization.draw_geometries(show_pcd)
        # ##################保存数据###########################
        path_widths = np.append(path_widths, distances)
        # # 创建渲染器和窗口
        # vis = o3d.visualization.Visualizer()
        # vis.create_window(width=640, height=480)
        # # 添加点云到渲染器
        # vis.add_geometry(path)
        # vis.add_geometry(pcd)
        # vis.add_geometry(distance_obb)
        # # 渲染并保存图像
        # vis.poll_events()
        # vis.update_renderer()
        # print("save_path:",save_path+f"{i}_{distances}.png")
        # vis.capture_screen_image(save_path+f"{i}_{distances}.png")
    path_widths = np.append(path_widths,0)
    mean_width = np.mean(path_widths[1:-1])
    print("平均道宽：",mean_width)

    return path_widths
def get2Dcloud(path):
    # #读取点云文件
    # pcd = o3d.io.read_point_cloud("../../data/20240331/6.ply")
    pcd = o3d.io.read_point_cloud(path)
    # o3d.visualization.draw_geometries([pcd], window_name="pcd")
    object_pcd = my_open3D.get_object(pcd)
    # o3d.visualization.draw_geometries([object_pcd],window_name="object_pcd")
    object_pcd = my_open3D.fix_z(object_pcd,0.6)
    return object_pcd
def showWidthPlot(path,weights):
    # loaded_data_npz = np.load('../../data/save/width_weight.npz')
    # width = loaded_data_npz['width']
    # projection = loaded_data_npz['projection']
    # weights = projection
    points = np.array(path.points)
    # # 可视化点云
    # o3d.visualization.draw_geometries([path])
    # 提取点的坐标
    x = points[:, 0]
    y = points[:, 1]
    z = points[:, 2]
    # 创建一个图形窗口
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # 设置俯视视角
    ax.view_init(elev=90, azim=-90)
    # 绘制点
    sc = ax.scatter(x, y, z, c=weights, cmap='viridis', s=100)

    # 添加颜色条
    cbar = plt.colorbar(sc)
    cbar.set_label('Weight')

    # 设置坐标轴标签
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # 显示图形
    plt.show()
if __name__ == '__main__':
    obj_pcd = get2Dcloud("../../data/20240411/paten/line-180temp-1.ply")
    # path_pcd = insertPoint()
    # obj_pcd.paint_uniform_color([0, 1, 0])
    # path_pcd.paint_uniform_color([1, 0, 0])
    # # o3d.visualization.draw_geometries([obj_pcd])
    # # o3d.visualization.draw_geometries([path_pcd])
    #
    # path_pcd = movePoint(path_pcd,obj_pcd)
    #
    # o3d.io.write_point_cloud("../../data/save/path_pcd.ply", path_pcd)
    # o3d.io.write_point_cloud("../../data/save/obj_pcd.ply", obj_pcd)
    # o3d.visualization.draw_geometries([path_pcd,obj_pcd])
    # calPathWidth(path_pcd,obj_pcd)
    # showWidthPlot(path_pcd)
