"""
一种基于植物点云骨架结构和外轮廓的新型下采样方法
"""
import os

import numpy as np
import open3d as o3d
from pclpy import pcl


def extract_edge_points(points):
    # --------------------------------加载点云数据-------------------------------------
    cloud = pcl.PointCloud.PointXYZ.from_array(points)
    # ---------------------------------法向量估计--------------------------------------
    n = pcl.features.NormalEstimationOMP.PointXYZ_Normal()
    tree = pcl.search.KdTree.PointXYZ()
    # n.setViewPoint(0, 0, 0)  # 设置视点，默认为（0，0，0）
    n.setInputCloud(cloud)
    n.setSearchMethod(tree)  # 设置近邻搜索的方式
    n.setNumberOfThreads(os.cpu_count())
    n.setKSearch(10)  # 点云法向计算时，需要所搜的近邻点大小
    # n.setRadiusSearch(0.03)  # 半径搜素
    normals = pcl.PointCloud.Normal()
    n.compute(normals)  # 开始进行法向计
    # --------------------------------边界提取----------------------------------------
    boundEst = pcl.features.BoundaryEstimation.PointXYZ_Normal_Boundary()
    boundEst.setInputCloud(cloud)  # 输入点云
    boundEst.setInputNormals(normals)  # 输入法线
    boundEst.setRadiusSearch(6.5)  # 半径阈值
    boundEst.setAngleThreshold(np.pi / 2)  # 夹角阈值
    boundEst.setSearchMethod(tree)  # 设置近邻搜索方式
    boundaries = pcl.PointCloud.Boundary()
    boundEst.compute(boundaries)  # 获取边界索引
    arr = boundaries.boundary_point
    location = np.where(arr > 0)[0]
    print(len(location))
    return location.tolist()


def extract_skeleton_points(points, skeleton):
    skeleton_set = []
    sum = 0
    tmp_cloud = o3d.geometry.PointCloud()
    tmp_cloud.points = o3d.utility.Vector3dVector(points)
    # 建立临时kd-tree
    tmp_cloud_tree = o3d.geometry.KDTreeFlann(tmp_cloud)
    for i in range(len(skeleton)):
        [k, index_set, _] = tmp_cloud_tree.search_radius_vector_3d(skeleton[i], 2)
        sum += k
        for idx in index_set:
            skeleton_set.append(idx)
    print("共有{%d}个点" % sum)
    return skeleton_set


# 导入骨架点云和原始点云
ply_old = o3d.io.read_point_cloud("D:\\DataSet\\PointCloud\\tomato-downsampling.ply")
ply_skeleton = o3d.io.read_point_cloud("D:\\DataSet\\PointCloud\\tomato-skeleton.ply")

edge_index = extract_edge_points(ply_old.points)
skeleton_index = extract_skeleton_points(np.asarray(ply_old.points), np.asarray(ply_skeleton.points))
obj_index = list(set(edge_index).union(skeleton_index))
c1 = ply_old.select_by_index(obj_index)
c2 = ply_old.select_by_index(obj_index, invert=True)
c3 = ply_old.select_by_index(edge_index)
c1 = c1.uniform_down_sample(every_k_points=4)
c2 = c2.uniform_down_sample(every_k_points=7)
c3 = c3.uniform_down_sample(every_k_points=2)
c4 = ply_old.uniform_down_sample(every_k_points=6)
c4.paint_uniform_color([0.5, 0.5, 0.5])
c = c1 + c2 + c3
c.paint_uniform_color([0.5, 0.5, 0.5])
o3d.visualization.draw_geometries([c])
o3d.visualization.draw_geometries([c4])
