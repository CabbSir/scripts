from tkinter import *
from tkinter.filedialog import askdirectory, askopenfilenames
import open3d as o3d
import numpy as np

# 常量设置
input_type = ["点云", "网格"]
category = [".ply", ".pcd", ".obj", ".txt"]


def select_input_path():
    input_path_ = askdirectory()
    input_path.set(input_path_)


def select_input_files():
    input_files_ = askopenfilenames()
    input_path.set(input_files_)


def select_output_path():
    output_path_ = askdirectory()
    output_path.set(output_path_)


def select_output_files():
    output_files_ = askopenfilenames()
    output_path.set(output_files_)


def set_input():
    print(input_type[input_var.get()])


def set_output():
    print(category[output_var.get()])


def format():
    print(input_var.get())
    print(output_var.get())
    mesh = o3d.io.read_triangle_mesh("/Users/cabbsir/Downloads/pcd/m82D_highlight_C_D08.obj")
    points = np.asarray(mesh.vertices)
    pcd = o3d.geometry.PointCloud()
    # pcd.colors = o3d.utility.Vector3dVector([1, 0, 0])
    pcd.points = o3d.utility.Vector3dVector(points)
    # pcd.paint_uniform_color([1, 0, 0])
    print(pcd)
    o3d.io.write_point_cloud("/Users/cabbsir/Downloads/pcd/D08.ply", pcd)
    o3d.visualization.draw_geometries([pcd])


root = Tk()
input_var = IntVar()
output_var = IntVar()
input_path = StringVar()
output_path = StringVar()

Label(root, text="目标路径:").grid(row=0, column=0)
Entry(root, textvariable=input_path).grid(row=0, column=1)
Button(root, text="路径选择", command=select_input_path).grid(row=0, column=2)
Button(root, text="文件选择", command=select_input_files).grid(row=0, column=3)
input_label = Label(root, text="输入点云格式:").grid(row=1, column=0)

for i in range(len(input_type)):
    Radiobutton(root, text=input_type[i], variable=input_var, value=i, command=set_input).grid(row=1, column=i + 1)

Label(root, text="输出路径:").grid(row=3, column=0)
Entry(root, textvariable=output_path).grid(row=3, column=1)
Button(root, text="路径选择", command=select_output_path).grid(row=3, column=2)
Button(root, text="文件选择", command=select_output_files).grid(row=3, column=3)
output_label = Label(root, text="输出点云格式:").grid(row=4, column=0)

for i in range(len(category)):
    Radiobutton(root, text=category[i], variable=output_var, value=i, command=set_input).grid(row=4, column=i + 1)

Button(root, text="开始转换", command=format).grid(row=5, column=4)

root.mainloop()
