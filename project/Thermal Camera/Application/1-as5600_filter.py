#在txt文件中读取as5600数据
import sys
sys.path.append(r'D:\Project\Software\Pycharm\AAI\AM\MyFunc')
import re
import my_plot
import my_csv
import numpy as np
class as5600_dev:
    def __init__(self,num):
        self.dev = num
        self.max_value = 4096
        self.value = []
        self.total = []
        self.total_last = []
class Nozzle:
    def __init__(self,path,dev0,dev1):
        self.path = path
        #设备数据
        self.data0 = as5600_dev(0)
        self.data1 = as5600_dev(1)
        #坐标数据
        self.x = 0
        self.y = 0
        self.x_list = []
        self.y_list = []
        self.time = []
        self.filter_A = []
        self.filter_B = []
        #计算数据
        self.dis = []
        self.time_diff = []
        self.v_list = []
        #写入csv数据
        self.csv_path = self.path+'location.csv'
        self.csv_list = []
        print("init")
        self.read_as5600_uart_csv(self.csv_path)
    def read_as5600_uart_csv(self,path):
        # print(path)
        csv_lis = my_csv.read_csv(path)

        # self.data0.value = np.array(csv_lis[1]).astype(float).astype(int)
        self.data0.total = np.array(csv_lis[1]).astype(float).astype(int)
        # self.data1.value = np.array(csv_lis[3]).astype(float).astype(int)
        self.data1.total = np.array(csv_lis[2]).astype(float).astype(int)
        self.time = np.array(csv_lis[0]).astype(float).astype(int)
        self.dataLen = len(self.data0.total)
        # self.x = np.array(list(map(float, csv_lis[5])))
        # self.y = np.array(list(map(float, csv_lis[6])))

        self.data0.total = self.diffFilter(self.data0.total)
        self.data1.total = self.diffFilter(self.data1.total)

        aa = -1

    def draw_track(self):
        # my_plot.animation(self.x,self.y)
        # my_plot.draw_plot_point('track','x','y',self.x,self.y)
        # my_plot.draw_plot_line_weight(self.x_list, self.y_list, self.v_list)
        # th = 14500
        # start = th
        # end = len(self.x_list) - th
        start = 8000
        end = len(self.x_list)- 10000
        # 旋转角度（以弧度为单位）
        coordinate = np.vstack((self.x_list[start:end],self.y_list[start:end]))
        coordinate = coordinate.T
        theta = np.radians(180)  # 例如旋转45度
        # 旋转矩阵
        R = np.array([[np.cos(theta), -np.sin(theta)],
                      [np.sin(theta), np.cos(theta)]])

        # 使用矩阵乘法将所有点旋转指定角度
        coordinate = np.dot(coordinate, R.T)
        my_plot.draw_plot_line_weight(coordinate[:,0],coordinate[:,1],self.v_list[start:end],Range=[0,40],linewidth=4)
        # my_plot.draw_histogram(self.v)

    def diffFilter(self,data):
        temp = data
        # 一阶差分
        first_order_diff = np.diff(data)
        # 二阶差分
        second_order_diff = np.diff(first_order_diff)
        # 遍历二阶差分数据
        for i in range(len(second_order_diff) - 2):
            window = second_order_diff[i:i + 3]
            condition = (np.sign(window[0]) == np.sign(window[2]) != np.sign(window[1]) and
                    200 <= abs(window[0]) <= 290 and
                    200 <= abs(window[2]) <= 290 and
                    450 <= abs(window[1]) <= 550)
            if (condition):
                # print(self.data1.total[i], self.data1.total[i + 1], self.data1.total[i + 2], self.data1.total[i + 3],
                #       self.data1.total[i + 4], "||", second_order_diff[i], second_order_diff[i + 1], second_order_diff[i + 2])
                delta = temp[i + 1] - temp[i]
                temp[i + 2] = temp[i + 1] + delta
        return temp


    def filterDelta(self, data):
        if (len(data) >= 3):
            # 条件1：前两个数的绝对值在55-45之间
            # condition1 = np.all((40 <= np.abs(data[:2])) & (np.abs(data[:2]) <= 55))
            #
            # # 条件2：最后一个数的绝对值在200-210之间
            # condition2 = 200 <= np.abs(data[2]) <= 330
            condition1 = (abs(data[0] - data[1]) <= 15) and \
                        (abs(data[0]) > 20) and (abs(data[1]) > 20) and \
                        (abs(data[2]) > 3 * abs((data[0] + data[1]) / 2))
            condition2 = (abs(data[0] - data[1]) <= 5) and \
                         ((abs(data[0]) > 3) or (abs(data[1]) > 3)) and \
                         ((np.abs(data[2]) >= 200) and (np.abs(data[2]) <= 300))
            # 条件3：前两个数和最后一个数符号相反
            condition3 = (data[0] * data[2] < 0) and (data[1] * data[2] < 0)


            # 判断是否满足所有条件
            result = (condition1 or condition2)
        else:
            result = False
        return result
    def getCoordination(self):
        #模拟数据输入
        s = 0
        e = self.dataLen
        for i in range(s, e):
        # for i in range(1,self.dataLen):
            delta_A = self.data0.total[i] - self.data0.total[i-1]
            delta_B = self.data1.total[i] - self.data1.total[i-1]

            if (len(self.filter_A) == 4):
                self.filter_A.pop(0)
                self.filter_B.pop(0)
            self.filter_A.append(delta_A)
            self.filter_B.append(delta_B)

            # if self.filterDelta(self.filter_A):
            #     # print(self.filter_A)
            #     delta_A = self.filter_A[-2]
            #     self.filter_A[-1] = self.filter_A[-2]
            #     self.data0.total[i] = self.data0.total[i-1] + delta_A
            # if self.filterDelta(self.filter_B):
            #     # print(self.filter_B)
            #     delta_B = self.filter_B[-2]
            #     self.filter_B[-1] = self.filter_B[-2]
            #     self.data1.total[i] = self.data1.total[i-1] + delta_B


            self.x = self.x - (delta_A + delta_B) / 255.85
            self.y = self.y - (delta_A - delta_B) / 255.85
            self.x_list.append(self.x)
            self.y_list.append(self.y)
            if(abs(self.filter_A[-1])>180 or abs(self.filter_B[-1])>180):
                print(i,self.filter_A, self.filter_B, self.x, self.y,"||",np.diff(self.filter_A),np.diff(self.filter_B))
            self.data0.total_last.append(delta_A)
            self.data1.total_last.append(delta_B)

        self.x_list = np.array(self.x_list)
        self.y_list = np.array(self.y_list)

        self.dis = np.sqrt(np.diff(self.x_list) ** 2 + np.diff(self.y_list) ** 2)
        # self.time_diff = np.diff(self.time[1:])
        self.time_diff = np.full(len(self.dis), 0.01)
        self.v_list = self.dis / self.time_diff
        aa = 0
    def save(self):
        np.savez(self.path+'coordination.npz',time=self.time,x=self.x_list,y=self.y_list,v=self.v_list)
    def save_csv(self):
        my_csv.save_arrays_to_csv(self.path+'coordination.csv',self.time,self.x_list,self.y_list)
        pass

if __name__ == '__main__':
    path = './pattern/PLA-GradientTemperature/4/'
    as5600_dev0 = as5600_dev(0)
    as5600_dev1 = as5600_dev(1)
    nozzle = Nozzle(path,as5600_dev0,as5600_dev1)
    nozzle.getCoordination()
    nozzle.save()
    # nozzle.save_csv()
    nozzle.draw_track()
