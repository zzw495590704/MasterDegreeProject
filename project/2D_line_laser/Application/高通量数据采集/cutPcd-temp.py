import sys
import os
import open3d as o3d
sys.path.append(r'D:\Project\Software\Pycharm\AAI\AM\MyFunc')
import my_open3D
import my_csv
import my_plot
import my_math
import numpy as np
import itertools
"""生成INN数据集-Line填充"""
class Data():
    def __init__(self,data):
        """
        [temper_row,extrusion_col,self.layer_height,
        crop_w,crop_d,crop_mean,corp_mse,crop_v,crop_z]
        """
        # data = self.filterData(data)
        self.data = self.deleteData(data)
        self.inputNum = 3
        self.paramSpace = [5, 20, 0.1],  # 变参数：温度（\u00b0C）挤出率（%）
        self.input = self.data[:,:self.inputNum]
        self.temperature = self.input[:,0]
        self.extrusion = self.input[:,1]
        self.layer_height = self.input[:,2]

        self.output = self.data[:,self.inputNum:]
        self.width = self.output[:,0]
        self.density = self.output[:,1]
        self.meanH = self.output[:,2]
        self.meanLayerH = self.output[:, 2]/10
        self.mseH = self.output[:,3]
        self.volume = self.output[:,4]
        self.planeZ = self.output[:,5]
        self.save_path = "./data/npy/data-fixed.npy"
        self.normalizeData()
    def normalizeData(self):
        self.n_temperature = my_math.normalize(self.temperature)
        self.n_extrusion = my_math.normalize(self.extrusion)
        self.n_layer_height = my_math.normalize(self.layer_height)
        self.n_width = my_math.normalize(self.width)
        self.n_density = my_math.normalize(self.density)
        self.n_meanLayerH = my_math.normalize(self.meanLayerH)
        # np.concatenate((arr1, arr2, arr3), axis=1)
        norm_data = np.vstack((self.n_temperature,self.n_extrusion,self.n_layer_height,
                          self.n_width,self.n_density,self.n_meanLayerH)).T
        raw_data = np.vstack((self.temperature,self.extrusion,self.layer_height,
                          self.width,self.density,self.meanLayerH)).T
        np.savez( "./data/npy/data_normalized.npz", norm=norm_data,raw=raw_data)
    def saveData(self):
        np.save(self.save_path, self.data)
    def filterData(self,data):
        # 注意，这里使用~操作符来取反条件，即选择第三个元素不大于4的行
        filtered_data = data[~((data[:, 4] > 1.23)|(data[:, 3] > 5))]  #排除密度大于1.23,道宽大于5
        # 打印结果
        print(filtered_data)
        return filtered_data
    def deleteData(self,data):
        # 删除指定列
        # self.data = np.delete(arr, col_index, axis=1)
        filtered_data = data[~((data[:, 3] == 0))]
        return filtered_data
    def fillData(self):
        # 定义范围和分度值
        ranges = [np.arange(170, 221, 5), np.arange(30, 151, 20), np.arange(0.2, 0.41, 0.1)]

        # 生成所有可能的组合
        all_combinations = list(itertools.product(*ranges))

        # 转换为numpy数组
        complete_data = np.array(all_combinations)

        a = self.input
        b = complete_data

        # 保持顺序的解决方案
        res = []
        for item in b:
            if not any((item == row).all() for row in a):
                res.append(item)

        res = np.array(res)
        # 打印完整的数据集
        print(complete_data)

        pass
    def resizeMseH(self,data):
        # 找到最小值、最大值和中间值
        min_val = 0.13
        max_val = 0.2
        mid_val = 0.2

        # 创建结果数组
        res = np.zeros_like(data)

        # 划分等级
        res[data < mid_val] = 0  # 小于中间值的为等级1
        # res[(data >= mid_val) & (data < max_val)] = 2  # 中间值和最大值之间的为等级2
        res[data > max_val] = 1  # 等于最大值的为等级3（如果有多个最大值，这个逻辑可以调整）

        # 注意：这里假设等级划分是严格的，并且没有考虑等于最小值的情况（因为最小值只有一个）
        # 如果需要更复杂的划分逻辑（例如处理多个相同的最小值或最大值），可以进一步调整
        print(min_val,mid_val,max_val)
        # print("Data:", data)
        # print("Res:", res)
        return res
    def showDensity(self):
        my_plot.draw_scatter_3Dplot_weight(self.input, self.density,
                                           # figsize=my_math.cm2inch((10.08,8.24)),
                                           xlabel="Temperature(\u00b0C)", ylabel="Extrusion(%)", zlabel="Layer height(mm)",
                                           clabel="Density(g/mm$^3$)")
    def showWidth(self):
        my_plot.draw_scatter_3Dplot_weight(self.input, self.width,
                                           xlabel="Temperature(\u00b0C)", ylabel="Extrusion(%)", zlabel="Layer height(mm)",
                                           clabel="Width(mm)")
    def showMseH(self):
        my_plot.draw_scatter_3Dplot_weight(self.input, self.mseH,figsize=my_math.cm2inch((10,7.49)),
                                           xlabel="Temperature(\u00b0C)",ylabel="Extrusion(%)",zlabel="Layer height(mm)",
                                           clabel="Height mse/mm")
    def showMeanH(self):
        my_plot.draw_scatter_3Dplot_weight(self.input, self.meanH,
                                           xlabel="Temperature(\u00b0C)", ylabel="Extrusion(%)", zlabel="Layer height(mm)",
                                           clabel="Height mean(mm)")
    def showData(self,data):
        my_plot.draw_scatter_3Dplot_weight(self.input, data,
                                           xlabel="Temperature(\u00b0C)", ylabel="Extrusion(%)", zlabel="Layer height(mm)",
                                           clabel="Height mse(mm)")
    def show3d(self):
        my_plot.draw_3D_Bar(self.input[:,:2], self.density, self.width, ylabel='Extrusion (%)', xlabel='Temperature (\u00b0C)'
                            , clabel='Width (mm)', zlabel='Density (g/cm$^3$)',
                            # title=f'Layer Height:{layer_height}mm',
                            figsize=my_math.cm2inch((10, 7.5)),
                            zlim=[0, 1.35], clim=[0.3, 3], dpi=300)
class calVolume():
    def __init__(self,dict):
        self.size = dict['size']       #打印4X3阵列
        self.space = dict['space']    #样件之间x方向间隔，y方向间隔
        self.param = dict['param']      #变参数：温度（\u00b0C）挤出率（%）
        self.temperature = dict['temperature']  #喷嘴温度
        self.extrusion = dict['extrusion']     #喷嘴挤出率
        self.layer_height = dict['layer_height']    #层高
        self.rec= dict['rec']
        self.input_file=dict['file_path']
        self.dir_path = os.path.dirname(self.input_file)+f"/{self.layer_height}lh"
        self.inputNum = 3
        self.select = np.array([
            [170,30,0.3],[170,50,0.3],[180,30,0.3],[175,30,0.3],[175,50,0.3],[185,30,0.3],
            # [175,30,0.2],[175,50,0.2],
            [190,30,0.2],[195,110,0.2],[225,90,0.2],
            [170,30,0.4],[170,50,0.4],[170,70,0.4],[170,90,0.4],[175,30,0.4],[175,50,0.4],[175,70,0.4],[180,30,0.4],[180,50,0.4],[185,30,0.4],[185,50,0.4],[190,30,0.4],[195,30,0.4],[200,30,0.4],[205,30,0.4],[215,30,0.4],
            # # 170-180temp 0.02lh的第二版
            [170,30,0.2],[180,50,0.2],[175,30,0.2],[175,50,0.2],[180,30,0.2],[180,150,0.2],
            ### 0.25层高
            [170,30,0.25],[170,50,0.25],[170,90,0.25],[175,30,0.25],[175,50,0.25],[180,30,0.25],[180,50,0.25],[185,30,0.25],[190,30,0.25],[225,150,0.25],
            ### 0.35层高
            # [170,30,0.35],[170,50,0.35],[170,90,0.35],[175,30,0.35],[175,50,0.35],[180,30,0.35],[180,50,0.35],[185,30,0.35],[185,50,0.35],[185,70,0.35],[190,30,0.35],[190,50,0.35],[195,30,0.35],[200,30,0.35],[205,30,0.35],[210,30,0.35]
            [185,30,0.35],[185,50,0.35]
        ])

        self.weight = [0.06064,0.10106,0.14149,0.18191,0.22234,0.26276,0.30319] #30-150%挤出率的重量
        ###########保存数据##################
        self.save_path = "./data/npy/data-fixed.npy"
        if os.path.exists(self.save_path):
            self.data = np.load(self.save_path)
        else:
            self.data = np.array([[170,30,0.2,0,0,0,0,0,0],[170,50,0.2,0,0,0,0,0,0]]) #初始化几个数字，避免报错

    def getCropPCDFor(self):
        # for i in range()
        pass
    def getCropPCD(self,show_crop=False,show_top=False):
        #创建存储volume的二维数组
        array_v = np.zeros((self.size[1], self.size[0]), dtype=float)
        array_z = np.zeros((self.size[1], self.size[0]), dtype=float)
        array_w = np.zeros((self.size[1], self.size[0]), dtype=float)
        array_d = np.zeros((self.size[1], self.size[0]), dtype=float)
        array_h = np.zeros((self.size[1]*2+1, self.size[0]), dtype=float)
        for i in range(self.size[1]):
            pcd_path = self.dir_path+f'/{self.temperature+i*self.param[0]}.ply'
            pcd = o3d.io.read_point_cloud(pcd_path)
            # o3d.visualization.draw_geometries([pcd])
            print("pcd_path",pcd_path)
            pcd = o3d.io.read_point_cloud(pcd_path)
            temper_row = self.temperature+i*self.param[0]
            for j in range(self.size[0]):
                extrusion_col = self.extrusion+j*self.param[1]
                param = np.array([temper_row,extrusion_col,self.layer_height])
                # 使用 np.all 和 轴参数来检查每一行是否等于 a
                not_select = np.any(np.all(self.select == param, axis=1))
                if(not_select):
                    self.updateData(np.array([temper_row, extrusion_col, self.layer_height,
                                              0, 0, 0, 0.4, 0, 0]))
                    print("不存在：",param)
                    continue
                res = self.rec.copy()
                res[0] -= j*self.space[0]
                res[1] -= i*self.space[1]
                x,y,w,h = res
                print(res)
                crop_pcd = my_open3D.cropPCD(pcd,x,y,w,h)
                #############保存点云##########################
                save_name = f"/{temper_row}t_{extrusion_col}em"
                print(f"name:{save_name}")
                if show_crop:
                    o3d.visualization.draw_geometries([crop_pcd])
                o3d.io.write_point_cloud(self.dir_path + save_name + ".ply", crop_pcd)
                ######################Debug######################
                # if(np.any(np.all([225,1300,0.02] == param))):
                #     o3d.visualization.draw_geometries([crop_pcd])
                #     save_name = f"{temper_row}t_{extrusion_col}em"
                #     o3d.io.write_point_cloud("./data/ply/" + save_name + ".ply", crop_pcd)
                # print(i, j, self.space[0], self.space[1], res)
                #############计算体积##########################
                crop_v,crop_z,crop_top = my_open3D.pcdVolume(crop_pcd,show=False,re_z=True,re_pcd=True)
                crop_w = self.calWidth(crop_top)
                crop_mean,corp_mse = my_open3D.getMeanHeight(crop_top,crop_z)
                crop_d = self.weight[j]*1000/crop_v
                # o3d.visualization.draw_geometries([crop_top])
                # print(f"mean:{crop_mean}  mse:{corp_mse}")
                print(f"密度:{crop_d}, 重量:{self.weight[j]}g, 体积:{crop_v}")
                print(f"道宽:{crop_w}, 均值:{crop_mean}, 粗糙度:{corp_mse}")
                if show_top:
                    o3d.visualization.draw_geometries([crop_top])
                array_w[i, self.size[0] - j - 1] = crop_w
                array_d[i, self.size[0] - j - 1] = crop_d
                array_h[i, self.size[0] - j - 1] = crop_mean
                array_h[i+self.size[1], self.size[0] - j - 1] = corp_mse
                array_v[i, self.size[0] - j - 1] = crop_v
                array_z[i, self.size[0] - j - 1] = crop_z
                self.updateData(np.array([temper_row,extrusion_col,self.layer_height,
                                       crop_w,crop_d,crop_mean,corp_mse,crop_v,crop_z]))
                print(f"param:{param}  v:{crop_v} w:{crop_w}")

        # save_path = f"./data/csv/{self.layer_height}lh/"
        # my_csv.save_csv(array_v,
        #                 save_path+f"{self.temperature}_{self.temperature+(self.size[1]-1)*self.param[0]}em_volume.csv")
        # my_csv.save_csv(array_d,
        #                 save_path+f"{self.temperature}_{self.temperature + (self.size[1]-1) * self.param[0]}em_density.csv")
        # my_csv.save_csv(array_w,
        #                 save_path+f"{self.temperature}_{self.temperature + (self.size[1]-1) * self.param[0]}em_width.csv")
        # my_csv.save_csv(array_h,
        #                 save_path+f"{self.temperature}_{self.temperature + (self.size[1]-1) * self.param[0]}em_height.csv")

    def calWidth(self,pcd,cut_x=5,Debug=False):
        # my_open3D.cut
        cut_pcd = my_open3D.cutBoundary(pcd,cut_x)
        # top_pcd= my_open3D.get_objectTop(cut_pcd)
        w_list = []     #存储长度列表
        if Debug:
            o3d.visualization.draw_geometries([cut_pcd])
        cluster_pcd = my_open3D.clusterPointDBSCAN(cut_pcd,min_samples=5)
        if Debug:
            o3d.visualization.draw_geometries(cluster_pcd)
        for i in range(5):
            if Debug:
                o3d.visualization.draw_geometries([cluster_pcd[i]])
            try:
                w,viewer = my_open3D.calWidthSingleBed(cluster_pcd[i],0.1)
                # print("w:",w)
                w_list.append(w)
            except:
                o3d.visualization.draw_geometries([cluster_pcd[i]])
                print("单道测量错误")
                continue
            # o3d.visualization.draw_geometries(viewer)
        w_avg = sum(w_list)/len(w_list)
        print("w_list",w_list)
        return w_avg
        # o3d.visualization.draw_geometries(cluster_pcd)
        # my_open3D.calWidthSingleBed(pcd,1)
    def calVsingle(self,t,e):
        path = self.dir_path +'/' + f"{t}t_{e}em.ply"
        print(path)
        pcd = o3d.io.read_point_cloud(path)
        o3d.visualization.draw_geometries([pcd])
        v,z,top = my_open3D.pcdVolume(pcd,show=True,re_z=True,re_pcd=True)
        w = self.calWidth(top,Debug=False)
        mean, mse = my_open3D.getMeanHeight(top, z)
        weight = self.weight[int(e / self.param[1]) - 1]
        d = weight*1000/v
        self.updateData(np.array([t, e, self.layer_height,
                                  w, d, mean, mse, v, z]))
        print("volume:",v)
        print("width:",w)
        print("density:", d)
    def changeSingle(self,data,col,value):
        for i, row in enumerate(self.data):
            if np.array_equal(row[:self.inputNum], data[:self.inputNum]):
                # 如果前两个元素匹配，则替换该行
                self.data[i][col]=value
                print(self.data[i])
                return  # 替换后直接返回，因为假设只有一个匹配项
    # 检查并替换或添加新数据
    def updateData(self,data):
        for i, row in enumerate(self.data):
            if np.array_equal(row[:self.inputNum], data[:self.inputNum]):
                # 如果前两个元素匹配，则替换该行
                self.data[i] = data
                return  # 替换后直接返回，因为假设只有一个匹配项
        # 如果没有匹配项，则将新数据添加到末尾
        self.data = np.vstack((self.data, data))
    def addData(self,data):
        if len(self.data)==0:
            self.data = np.append(self.data,data)
        elif np.any((self.data == data).all())==False:
            self.data = np.vstack((self.data,data))
            bbb = 1

    def deleteDataCol(self,col_index):
        ####删除整列
        self.data = np.delete(self.data, col_index, axis=1)
        pass
    def deleteDataSingle(self,data):
        for i, row in enumerate(self.data):
            if np.array_equal(row[:self.inputNum], data[:self.inputNum]):
                # 如果前两个元素匹配，则替换该行
                self.data = np.delete(self.data, i, axis=0)
                return  # 替换后直接返回，因为假设只有一个匹配项
    def fixDataSingle(self,param,show=False):
        t,e,l = param
        path = "./data/ply/repair/" + f"{t}t-{e}em-{l}lh.ply"
        print(path)
        pcd = o3d.io.read_point_cloud(path)
        x, y, w, h = [18.56386566,16.32705879,23.70706177,21.96208191]
        # print(res)
        pcd = my_open3D.cropPCD(pcd, x, y, w, h)
        o3d.visualization.draw_geometries([pcd])
        v, z, top = my_open3D.pcdVolume(pcd, show=show, re_z=True, re_pcd=True)
        w = self.calWidth(top, Debug=True)
        mean, mse = my_open3D.getMeanHeight(top, z)
        weight = self.weight[int(e / self.param[1]) - 1]
        d = weight * 1000 / v
        self.updateData(np.array([t, e, l,
                                  w, d, mean, mse, v, z]))
        print("volume:", v,"weight:",weight)
        print("width:", w)
        print("density:", d)
        print("mse:",mse,"mean:",mean)
    def fixDataMulti(self,param,show_crop=False,show_top=False):
        """
        计算多个样件
        :param param: [温度，初始挤出率，层高]
        :param show_crop:
        :param show_top:
        :return:
        """
        t,e,l = param

        pcd_path = self.dir_path+f'/{t}.ply'
        # o3d.visualization.draw_geometries([pcd])
        print("pcd_path",pcd_path)
        pcd = o3d.io.read_point_cloud(pcd_path)
        for j in range(self.size[0]):
            extrusion_col = e+j*self.param[1]
            param = np.array([t,extrusion_col,l])
            # 使用 np.all 和 轴参数来检查每一行是否等于 a
            not_select = np.any(np.all(self.select == param, axis=1))
            if(not_select):
                self.updateData(np.array([t, extrusion_col, l,
                                          0, 0, 0, 0.4, 0, 0]))
                print("不存在：",param)
                continue
            res = self.rec.copy()
            res[0] -= j*self.space[0]
            res[1] -= 2*self.space[1]
            x,y,w,h = res
            print(res)
            crop_pcd = my_open3D.cropPCD(pcd,x,y,w,h)
            #############保存点云##########################
            save_name = f"/{t}t_{extrusion_col}em"
            print(f"name:{save_name}")
            if show_crop:
                o3d.visualization.draw_geometries([crop_pcd])
            o3d.io.write_point_cloud(self.dir_path + save_name + ".ply", crop_pcd)
            ######################Debug######################
            # if(np.any(np.all([225,1300,0.02] == param))):
            #     o3d.visualization.draw_geometries([crop_pcd])
            #     save_name = f"{temper_row}t_{extrusion_col}em"
            #     o3d.io.write_point_cloud("./data/ply/" + save_name + ".ply", crop_pcd)
            # print(i, j, self.space[0], self.space[1], res)
            #############计算体积##########################
            crop_v,crop_z,crop_top = my_open3D.pcdVolume(crop_pcd,show=False,re_z=True,re_pcd=True)
            crop_w = self.calWidth(crop_top)
            crop_mean,corp_mse = my_open3D.getMeanHeight(crop_top,crop_z)
            crop_d = self.weight[j]*1000/crop_v
            # o3d.visualization.draw_geometries([crop_top])
            # print(f"mean:{crop_mean}  mse:{corp_mse}")
            print(f"密度:{crop_d}, 重量:{self.weight[j]}g, 体积:{crop_v}")
            print(f"道宽:{crop_w}, 均值:{crop_mean}, 粗糙度:{corp_mse}")
            if show_top:
                o3d.visualization.draw_geometries([crop_top])

            self.updateData(np.array([t,extrusion_col,l,
                                   crop_w,crop_d,crop_mean,corp_mse,crop_v,crop_z]))
            print(f"param:{param}  v:{crop_v} w:{crop_w}")

    def saveData(self):
        # #TODO:支持数据的增量更新
        np.save(self.save_path, self.data)
    def loadData(self):
        load = np.load(self.save_path)
        data = Data(load)
        pass

if __name__ == '__main__':
    param = {
        'file_path': "./data/ply/",
        'size': [7, 1],  # 打印4X3阵列
        'space': [40, 75],  # 样件之间x方向间隔，y方向间隔
        'param': [5, 20],  # 变参数：温度（\u00b0C）挤出率（%）
        'rec': [266.5,166.48723793,23,25],  #框选样件区域
        'temperature': 185,  # 喷嘴温度
        'extrusion': 30,  # 喷嘴挤出率
        'layer_height': 0.25
    }
    v = calVolume(param)
    # # v.deleteDataCol([-1,-2])
    # v.deleteDataSingle([215,110,0.4])
    v.changeSingle([215, 110, 0.4], 3, 1)
    v.changeSingle([215,110,0.4],4,0.42)
    v.changeSingle([215, 90, 0.4], 4, 0.435)
    v.changeSingle([180, 90, 0.25], 4, 0.8)
    v.changeSingle([185, 50, 0.25], 6, 0.04)
    v.changeSingle([200, 30, 0.3], 6, 0.04)
    v.changeSingle([210, 30, 0.4], 6, 0.04)
    v.changeSingle([215, 30, 0.4], 6, 0.04)
    v.changeSingle([220, 30, 0.4], 6, 0.04)
    v.changeSingle([225, 50, 0.4], 6, 0.05)
    v.changeSingle([225, 30, 0.4], 6, 0.04)
    v.changeSingle([170, 90, 0.25], 4, 1.1)
    # v.saveData()
    # # v.calVsingle(180,90)
    # v.data[367][4]=0.86
    # v.data[226][4] = 1.1
    # v.data[208][4] = 0.45
    # # v.fixDataSingle([180,90,0.25],show=True)
    # # v.fixDataMulti([185,30,0.35],show_crop=True)
    # # v.getCropPCD(show_top=True)
    #
    d = Data(v.data)
    ##########数据预处理######
    # d.fillData()
    # dmseH = d.resizeMseH(d.mseH)
    # d.showData(dmseH)
    # d.data = np.column_stack((d.data,dmseH))
    # ########展示数据########
    # d.show3d()
    d.showWidth()
    d.showDensity()
    # d.showMeanH()
    d.showMseH()

    d.saveData()
    # v.loadData()
    # v.getGcodePCD("line-90.gcode")
