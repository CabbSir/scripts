"""
将 ".ply", ".pcd", ".txt" 三种点云格式转换成其他任意四种
"""

import os
import tkinter
from tkinter import *
from tkinter.filedialog import askdirectory, askopenfilenames

import open3d as o3d
import numpy as np

# 常量设置
input_type = ["点云", "网格"]
category = [".ply", ".pcd", ".xyz"]
is_dir = False
files = ()


def select_input_path():
    global is_dir
    is_dir = True
    input_path_ = askdirectory()
    input_path.set(input_path_)


def select_input_files():
    global is_dir
    is_dir = False
    input_files_ = askopenfilenames()
    global files
    files = input_files_
    input_path.set(input_files_)


def select_output_path():
    output_path_ = askdirectory()
    output_path.set(output_path_)


def mesh_to_pc():
    if is_dir:
        temp = os.listdir(input_path.get())
    else:
        temp = files
    for file in temp:
        # 只有这四种文件处理
        if ".ply" in file or ".pcd" in file or ".obj" in file or ".txt" in file:
            if is_dir:
                mesh = o3d.io.read_triangle_mesh(os.path.join(input_path.get(), file))
            else:
                mesh = o3d.io.read_triangle_mesh(file)
            points = np.asarray(mesh.vertices)
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(points)
            if is_dir:
                output = os.path.join(output_path.get(), file.split(".")[0] + category[output_var.get()])
            else:
                output = os.path.join(output_path.get(),
                                      os.path.split(file)[1].split(".")[0] + category[output_var.get()])
            o3d.io.write_point_cloud(output, pcd)


def pc_to_pc():
    if is_dir:
        temp = os.listdir(input_path.get())
    else:
        temp = files
    for file in temp:
        # 只有这四种文件处理
        if ".ply" in file or ".pcd" in file or ".obj" in file or ".txt" in file:
            if is_dir:
                pcd = o3d.io.read_point_cloud(os.path.join(input_path.get(), file))
                output = os.path.join(output_path.get(), file.split(".")[0] + category[output_var.get()])
            else:
                pcd = o3d.io.read_point_cloud(file)
                output = os.path.join(output_path.get(),
                                      os.path.split(file)[1].split(".")[0] + category[output_var.get()])
            o3d.io.write_point_cloud(output, pcd, print_progress=True)


def format():
    # 验证是否选择的没有问题
    if input_var.get() == 0:
        pc_to_pc()
    else:
        mesh_to_pc()
    tkinter.messagebox.showinfo('提示', '所有转换完成')


root = Tk()
input_var = IntVar()
output_var = IntVar()
input_path = StringVar()
output_path = StringVar()

Label(root, text="目标路径:").grid(row=0, column=0)
Entry(root, textvariable=input_path).grid(row=0, column=1)
Button(root, text="路径选择", command=select_input_path).grid(row=0, column=2)
Button(root, text="文件选择", command=select_input_files).grid(row=0, column=3)
Label(root, text="输入点云格式:").grid(row=1, column=0)

for i in range(len(input_type)):
    Radiobutton(root, text=input_type[i], variable=input_var, value=i).grid(row=1, column=i + 1)

Label(root, text="输出路径:").grid(row=3, column=0)
Entry(root, textvariable=output_path).grid(row=3, column=1)
Button(root, text="路径选择", command=select_output_path).grid(row=3, column=2)
Label(root, text="输出点云格式:").grid(row=4, column=0)

for i in range(len(category)):
    Radiobutton(root, text=category[i], variable=output_var, value=i).grid(row=4, column=i + 1)

Button(root, text="开始转换", command=format).grid(row=5, column=4)

root.mainloop()
