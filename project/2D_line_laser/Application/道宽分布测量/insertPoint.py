##用open3D读取Gcode坐标并进行差值，保存新的点云
import numpy as np
import open3d as o3d
import sys
sys.path.append(r'D:\Project\Software\Pycharm\AAI\AM\MyFunc')
import my_open3D

def insertPoint(fix_z=0.6002):
    # 加载数据
    loaded_data_npz = np.load('../../data/save/gcodeXYZ.npz')
    x = loaded_data_npz['x']
    y = loaded_data_npz['y']
    z = loaded_data_npz['z']
    e = loaded_data_npz['e']
    # 创建点云对象
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(np.vstack((x, y, z)).T)
    # 线性插值生成新的点
    new_x = []
    new_y = []
    new_z = []

    for i in range(len(x) - 1):
        if(e[i+1]>0):
            # 计算相邻点之间的距离
            dist = np.sqrt((x[i+1] - x[i])**2 + (y[i+1] - y[i])**2 + (z[i+1] - z[i])**2)
            # 计算相邻点之间需要插入的点的个数
            num_points_to_insert = int(dist / 0.1)  # 假设插入间距为 1mm
            new_x.append(x[i])
            new_y.append(y[i])
            new_z.append(z[i])
            # 计算插入点的坐标
            for j in range(num_points_to_insert):
                t = (j + 1) / (num_points_to_insert + 1)
                new_x.append(x[i] + t * (x[i+1] - x[i]))
                new_y.append(y[i] + t * (y[i+1] - y[i]))
                new_z.append(z[i] + t * (z[i+1] - z[i]))
    new_x.append(x[-1])
    new_y.append(y[-1])
    new_z.append(z[-1])
    # 创建新点的颜色数组，用红色标记
    num_new_points = len(new_x)
    colors = np.tile([1.0, 0.0, 0.0], (num_new_points, 1))

    # 创建点云对象
    interpolation_cloud = o3d.geometry.PointCloud()
    interpolation_cloud.points = o3d.utility.Vector3dVector(np.vstack((new_x, new_y, new_z)).T)
    interpolation_cloud.colors = o3d.utility.Vector3dVector(colors)

    # #读取点云文件
    # pcd = o3d.io.read_point_cloud("../../data/20240331/6.ply")
    # object_pcd = my_open3D.get_object(pcd)
    # object_pcd = my_open3D.fix_z(object_pcd,0.6)
    # 可视化点云
    # o3d.visualization.draw_geometries([interpolation_cloud])
    # o3d.visualization.draw_geometries([object_pcd])
    interpolation_cloud = my_open3D.fix_z(interpolation_cloud, 0.6002)
    # # 保存为PLY文件
    # o3d.io.write_point_cloud("../../data/save/save1.ply", interpolation_cloud)
    # o3d.io.write_point_cloud("../../data/save/save2.ply", object_pcd)
    return interpolation_cloud
if __name__ == '__main__':
     insertPoint()