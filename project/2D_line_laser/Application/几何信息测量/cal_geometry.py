import open3d as o3d
import numpy as np
import sys
sys.path.append(r'D:\Project\Software\Pycharm\AAI\AM\MyFunc')
import my_open3D
# 读取PLY文件
# pcd = o3d.io.read_point_cloud("../data/20240819/20x20x1.5mm/in2out/out2in-1em-223temp.ply")
# pcd = o3d.io.read_point_cloud("../data/20240819/20x20x1.5mm/rawdata-in2out/in2out-20x20x1.5mm-0.8em-223temp.ply")
# pcd = o3d.io.read_point_cloud("../data/20240819/20x20x1.5mm/fix/out2in-0.8em-180temp.ply")
pcd = o3d.io.read_point_cloud("../data/20240517/merge-plane.ply")
o3d.visualization.draw_geometries([pcd])
objec_z = my_open3D.get_objectZ(pcd,show=True)
plane_pcd = my_open3D.get_seprateZ(pcd,show=True)
pcd = my_open3D.get_object(pcd)
# pcd = my_open3D.cutX(pcd,14,pcd_l=0,pcd_r=1)
plane_z = objec_z
# pcd = my_open3D.cutX(pcd,5)
# 可视化点云


# 提取高度（z 坐标）
z_values = np.asarray(pcd.points)[:, 2]

# 计算高度的均方差
mean_height = np.mean(z_values)
std_dev_height = np.std(z_values)

volume = my_open3D.calVolume(pcd,0.02*0.02,plane_z,show=True)


print(f"Height standard deviation: {round(std_dev_height,5)}")
print(f"volume:{round(volume,5)}")
print(f"Mean height: {round(mean_height-plane_z,5) }")
print(f"绝对高度{round(mean_height,5)}")