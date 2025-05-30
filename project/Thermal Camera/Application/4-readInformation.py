# -*- coding: utf-8 -*-
import numpy as np
import os
import re
import sys
sys.path.append(r'D:\Project\Software\Pycharm\AAI\AM\MyFunc')
import my_csv
import my_cv2
import my_plot
import cv2
import pickle
import matplotlib.pyplot as plt
import pyqtgraph as pg
import threading
import time
import ThermalCamera

def all_same_dirction(vectors):
    # 计算每个向量的模长
    magnitudes = np.linalg.norm(vectors, axis=1)
    # 计算单位向量
    unit_vectors = vectors / magnitudes[:, np.newaxis]
    # 比较所有单位向量是否相同
    same_direction = np.all(np.isclose(unit_vectors, unit_vectors[0]))
    return same_direction

def is_same_dirction(v1, v2):
    # 计算向量的点积
    dot_product = np.dot(v1, v2)

    # 计算两个向量的模
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    res = np.isclose(dot_product, norm_v1 * norm_v2)
    # 比较点积和模的乘积
    return res

def simulate_data_addition(plotter):
    global coordinate
    while True:
        new_data = np.random.rand(4, 4) * 20 - 10
        if coordinate is not None:
            plotter.add_data(coordinate)
        time.sleep(0.1)
        print(coordinate)

def offsetDirction(dirction):
    res = all_same_dirction(dirction)
    vector = dirction[-1]
    if res:
        if(is_same_dirction(vector, np.array([1,0]))):
            return [0,0]
        elif (is_same_dirction(vector, np.array([-1,0]))):
            return [0, -2]
        elif (is_same_dirction(vector, np.array([0,1]))):
            return [0, 0]
            # return [1, 10]
        elif (is_same_dirction(vector, np.array([0,-1]))):
            return [-1, 0]
            # return [1, -9]
        elif (is_same_dirction(vector, np.array([1,-1]))):
            return [0, 0]
        else:
            return [0,0]
    else:
        return [0, 0]
def distribute_weights_interpolate(coordinate, weight):
    n = len(coordinate)
    m = len(weight)

    if m >= n:
        # 使用numpy的插值函数进行插值，使得权重数据均匀分布到坐标点上
        interpolated_weights = np.interp(np.linspace(0, m - 1, n), np.arange(m), weight)
    else:
        # 当权重数据的数量小于坐标点的数量时，同样使用插值方法
        interpolated_weights = np.interp(np.linspace(0, m - 1, n), np.arange(m), weight)

    return interpolated_weights


class Roi:
    def __init__(self):
        #每帧图片的ROI信息(列表)
        #绝对坐标点
        self.coordinate = None
        #绝对方向(编码器)向量
        self.vector = None
        #关键点像素轨迹(图像)向量
        self.vector_pixel = None
        #全部数据点像素轨迹
        self.vector_path = None
        self.start_point = None
def getTimeRoi(dict,point):
    dict = dict[::-1]
    start_point = point
    x_list = [d['match_x'] for d in dict]
    y_list = [d['match_y'] for d in dict]
    vector_list = [d['match_vector'] for d in dict]
    index_list = [d['frame'] for d in dict]
    roi_list = []
    for i in range(len(x_list)):
        roi = Roi()
        roi.start_point = start_point
        roi.coordinate = np.array([x_list[i], y_list[i]]).T
        roi.vector = vector_list[i]
        roi.vector = roi.vector[::-1]
        # [2.90424532 -3.92927308] [5.29597677, -5.15] [5.29597677 -4.78346289]
        roi.vector_pixel = np.round(roi.vector * np.array([[5.29597677, -5.29597677]])).astype(int)
        # 如果像素向量全为0则pass
        if np.all(roi.vector_pixel == [0, 0]):
            print(f"/n {index_list[i]}[{i}]像素向量全为0/n")
            continue
        roi.vector_pixel = roi.vector_pixel[~np.all(roi.vector_pixel == [0, 0], axis=1)]
        # 计算运动轨迹
        roi.vector_path = np.cumsum(np.vstack((start_point, roi.vector_pixel)), axis=0)
        # print(roi.vector_path)
        # print(f"{index_list[i]}[{i}]")
        # print("coordinate",roi.coordinate)
        # print("vector", roi.vector)

        start_point = roi.vector_path[-1]
        roi_list.append(roi)

    return roi_list


def display_image(plotter):
    #########################预处理#####################################
    nozzle_p = np.array([48, 54])
    nozzle = np.array([134, 95])
    start_point = nozzle_p
    # Pre
    # for i in range(9218, 10066):
    # Post
    # for i in range(8963, 9790):
    # Post shells
    for i in range(8963, 9366 ):
    # Pre shells
    # for i in range(9218, 9641):
    #LoopTemp 里->外
    # for i in range(9307, 10866):
    # for i in range(7733,9300):
        #########################预处理####################################
        initial_index = i-1
        back_index = initial_index - 5
        back_dict = Data[back_index:initial_index]
        #############################图像获取##################################
        file1 = Data[i]['file']
        img1 = cv2.imread(photo_path + file1, cv2.IMREAD_GRAYSCALE)
        img1_p = my_cv2.perspectiveImg(img1)
        # img1_p = img1
        #############################获取ROI区域##############################
        roi_list = getTimeRoi(back_dict,start_point)
        back_frame = 1
        if (len(roi_list)<back_frame+1):
            continue
        vector_path_offset = roi_list[back_frame].vector_path
        sel_coordinate = roi_list[back_frame].coordinate
        sel_vector = roi_list[back_frame].vector_pixel
        # print("vector_path_offset",vector_path_offset)
        condition1 = is_same_dirction(sel_vector[-1], np.array([1, 0]))
        condition2 = is_same_dirction(sel_vector[0], np.array([1, -1]))
        if( condition1 or condition2):
            print("盲区")
            continue

        #############################ROI区域计算#############################
        offset = offsetDirction(sel_vector)
        vector_path_offset = vector_path_offset+offset
        data_points = my_cv2.getLinePointList(vector_path_offset, img1_p)
        print(i)
        print("sel_vector", sel_vector)
        roi_line = my_cv2.perpendicular_lines(data_points,4)
        roi_img = my_cv2.lineListMask(roi_line,img1_p)
        # print("roi_line",roi_line)
        draw_track_img = img1_p.copy()
        data_points_weights = []
        ############################ROI采样区域温度计算###########################
        #获取单帧温度数据
        binFile = Data[i]['bin']
        temperFrame = ThermalCamera.readTemper(photo_path + binFile)
        #转换成二维数据与图像匹配
        temperFrame2D = ThermalCamera.getTemper2D(temperFrame)
        #同时进行透视变换
        temperFrame2D_p = my_cv2.perspectiveImg(temperFrame2D)
        # print("roi_line",roi_line)
        for j in range(1,len(roi_line)-1):    #去掉第一个数据点
            # roi_points,roi_value = my_cv2.meanLineValueImg(roi_line[j],img1_p)
            roi_points, roi_value = my_cv2.getLineValueImg(roi_line[j], temperFrame2D_p)
            roi_width_index = my_cv2.find_threshold_indices(data_points[j],roi_points,roi_value,160)
            roi_width_points = roi_points[roi_width_index[0]],roi_points[roi_width_index[1]]
            roi_width_value = roi_value[np.min(roi_width_index) : np.max(roi_width_index)]
            # roi_means = my_cv2.maxLineValue(roi_line[j], temperFrame2D_p)
            # roi_means = my_cv2.meanLineValue(roi_line[j], temperFrame2D_p)
            roi_means = my_cv2.meanLineValue(roi_width_points, temperFrame2D_p)
            # roi_means = my_cv2.getMaxValue(temperFrame2D_p)
            # _, roi_binary = cv2.threshold(roi_img, 130, 255, cv2.THRESH_BINARY)
            # print("data_points",data_points[j])
            # print("roi_value",roi_value)
            # print("roi_points", roi_points)
            # print("roi_index", roi_width_index)
            # print("roi_width_points",roi_width_points)
            # print("roi_width_value", roi_width_value)
            print("roi_means", roi_means)

            data_points_weights.append(roi_means)


            cv2.line(draw_track_img, tuple(roi_line[j][0]), tuple(roi_line[j][1]), 100, 1)
            cv2.line(draw_track_img, tuple(data_points[j]), tuple(data_points[j]), 0, 1)
            draw_track_img[nozzle_p[1],nozzle_p[0]] = 0
            # draw_track_img[roi_width_points[0][1], roi_width_points[0][0]] = 50
            # draw_track_img[roi_width_points[1][1], roi_width_points[1][0]] = 50
        print("=============================")

        if len(data_points_weights)==0:
            print("pass")
            continue

        roi_path_mean_value = np.mean(np.array(data_points_weights))
        print("整体均值:",roi_path_mean_value)
        # 创建一个与 data 大小相同的数组，所有元素都为均值
        data_points_weights_avg = np.full(np.array(data_points_weights).shape, roi_path_mean_value)
        data_points_weights_t0 = np.full(np.array(data_points_weights).shape, data_points_weights[0])
        weights = distribute_weights_interpolate(sel_coordinate,data_points_weights_avg)

        save_weights.extend(weights)
        save_coordinate.extend(sel_coordinate)
        print(sel_coordinate)
        plotter.add_data(sel_coordinate, weights)

        vector_data_points = np.diff(data_points, axis=0)
        # print("data_points",data_points)
        # print("vector_data_points",vector_data_points)
        # print("roi",roi_line)
        cv2.imshow("draw_track_img", my_cv2.scaleImg(draw_track_img, 5))

        # cv2.imshow("roi_img", my_cv2.scaleImg(roi_img, 5))

        # cv2.imshow("last_img", my_cv2.scaleImg(last_img, 5))
        # cv2.imwrite("./data/roi/"+file1,my_cv2.scaleImg(draw_track_img, 5))
        cv2.waitKey(0)
    np.savez(directory_path+"img_temperature.npz", coordinate = np.array(save_coordinate) ,weights=np.array(save_weights))
    cv2.destroyAllWindows()

if __name__ == '__main__':
    save_weights = []
    save_coordinate = []
    directory_path = './pattern/PLA-GradientTemperature/4/'
    # 从 pickle 文件读取字典列表
    with open(directory_path+'temp.pkl', 'rb') as f:
        Data = pickle.load(f)

    photo_path = directory_path + "data/"
    # 绘制轨迹相关
    coordinate = np.array([])
    coordinates = []
    plotter = my_plot.RealTimePlotter(xlim=(-10,10), ylim=(-100,-200),weightRange=[130,160],cmap='viridis')
    display_image_thread = threading.Thread(target=display_image, args=(plotter,))
    display_image_thread.start()
    plotter.start()
    # #########################图片读取#####################################

