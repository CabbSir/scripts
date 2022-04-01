'''
自动操作Metashape进行稠密重建的脚本
配置项在config变量中，在运行前请检查并修改
'''
import os
import subprocess
import time

from pywinauto import Application

config = {
    'exe_path': 'C:\\Program Files\\Agisoft\Metashape Pro\\metashape.exe',  # metashape的exe可执行文件路径
    'data_path': 'G:\\xiao\\2021tiancaidishang\\8\\汇总\\',  # 重建数据集的存放路径
    'open_waiting_time': 20, # 等待程序完成启动的时间 性能好的电脑（例如固态）可以适量减少这个时间 默认10秒
    'align_photo_time': 10 * 60,  # 对齐照片等待时间 默认最多10分钟
    'dense_time': 60 * 60,  # 稠密重建等待时间
    'save_time': 60,  # 保存 默认60秒超时时间
}
# 常量定义 与机型&植物种类无关，一般不要修改
STEP_WAIT_TIME = 0.5  # 每个步骤前后的等待时间（秒）
TOTAL_WINDOW_COUNT = 12  # metashape 没有任何操作的情况下子窗口个数，根据这个判断每一步是否正确完成，不需要更改，程序自动检测
FREE_CPU = 0.5  # cpu在空闲状态下的占用率 一般不会过高 无任务状态一般为0.0 这里设置为0.5
WAIT_CPU_SECONDS = 10  # 默认测试十秒内cpu使用率， 一般不改变


def check_step_result(w):
    if len(w.children()) == TOTAL_WINDOW_COUNT:
        return True
    return False


def s(sec=STEP_WAIT_TIME):
    time.sleep(sec)


def write_log(message):
    with open("./metashape-log/log.txt", 'a') as log:
        log.write(message + '\n')


def write_list(path, mark=True):
    if mark:
        with open("./metashape-log/success.txt", 'a') as log:
            log.write(path + '\n')
    else:
        with open("./metashape-log/error.txt", 'a') as log:
            log.write(path + '\n')


def prepare_files():
    print("准备文件")
    if not os.path.exists('./metashape-log'):
        os.makedirs('metashape-log')
    # log日志文件
    if not os.path.exists("./metashape-log/log.txt"):
        file = open("./metashape-log/log.txt", 'w')
        file.close()
    # success
    success = []
    if not os.path.exists("./metashape-log/success.txt"):
        file = open("./metashape-log/success.txt", 'w')
        file.close()
    else:
        for line in open("./metashape-log/success.txt"):
            success.append(line)
    # error
    error = []
    if not os.path.exists("./metashape-log/error.txt"):
        file = open("./metashape-log/error.txt", 'w')
        file.close()
    else:
        for line in open("./metashape-log/error.txt"):
            error.append(line)
    return success, error


def choose_folder(w, path):
    print("选择文件")
    if not check_step_result(w):
        return False
    s()
    # 选择文件夹
    w.Menu2.MenuItem4.click_input()
    w.type_keys("{VK_DOWN 1}")
    w.type_keys("{ENTER}")
    s()
    # 获取文件选择框
    pick_folder_win = w.Dialog
    name_list = []
    for k in os.listdir(path):
        name_list.append("\"" + k + "\"")
    name_list.pop(0)
    pick_folder_win.ComboBox.Edit.type_keys(path)
    pick_folder_win.ComboBox.Edit.type_keys('{ENTER}')
    pick_folder_win.ComboBox.Edit.set_text(" ".join(name_list))
    pick_folder_win.ComboBox.Edit.type_keys("{ENTER}")
    s()
    # 确定照片类型 single
    # w.Dialog.OKButton.click()
    s(3)
    return True


def align_photo(w):
    print("对齐照片")
    if not check_step_result(w):
        return False
    # 对齐照片
    w.Menu2.MenuItem4.click_input()
    w.type_keys("{a}")
    w.Dialog.OKButton.click()
    s(2)
    return True


def dense_build(w):
    print("稠密重建")
    if not check_step_result(w):
        return False
    # 密集点云
    w.Menu2.MenuItem4.click_input()
    w.type_keys("{d}")
    w.Dialog.OKButton.click()
    s(2)
    return True


def export_ply(w, path):
    print("输出")
    if not check_step_result(w):
        return False
    # 导出点云
    w.Menu2.MenuItem1.click_input()
    w.type_keys("{VK_DOWN 7}")
    w.type_keys("{ENTER 2}")
    save_ply_win = w.Dialog
    save_ply_win.ComboBox.Edit.type_keys(path + "\\" + str(int(time.time()))) # 文件名以当前时间戳
    s()
    save_ply_win.ComboBox.Edit.type_keys('{ENTER}')
    w.Dialog.OKButton.click()
    s()
    while True:
        if check_step_result(w):
            break
        print("仍在保存中...")
        time.sleep(5)  # 5秒轮询时间
    s(2)
    return True



def build_dense(window, path):
    try:
        if not choose_folder(window, path):
            return False

        if not align_photo(window):
            return False

        # 等待CPU，
        app.wait_cpu_usage_lower(FREE_CPU, config['align_photo_time'], WAIT_CPU_SECONDS)
        # 等待dialog消失
        time1 = int(time.time())
        s1 = True
        while True:
            if check_step_result(window):
                break
            if int(time.time()) - time1 > 60 * 5:
                s1 = False
                break
            if window.Dialog.class_name() == "ModernMessageBox":
                window.Dialog.OKButton.click()
                s1 = True
                break
            print("仍在对齐中...")
            time.sleep(2)  # 2秒轮询时间
        if not s1:
            return False
        s(2)

        if not dense_build(window):
            return False

        # 等待CPU
        app.wait_cpu_usage_lower(FREE_CPU, config['dense_time'], WAIT_CPU_SECONDS)
        # 等待dialog消失
        time2 = int(time.time())
        s2 = True
        while True:
            if check_step_result(window):
                break
            if int(time.time()) - time2 > 60 * 10:
                s2 = False
                break
            print("仍在重建中...")
            time.sleep(5)  # 5秒轮询时间
        if not s2:
            return False
        s(2)

        if not export_ply(window, path):
            return False

        if not check_step_result(window):
            return False
        # 新建一个，不保存
        window.type_keys("^n")
        s()
        window.Dialog.DiscardButton.click()
        return True
    except Exception as e:
        # 写入log
        write_log(str(e))
        return False


def open_app():
    # 打开程序
    subprocess.Popen(config['exe_path'])
    time.sleep(config['open_waiting_time'])
    app1 = Application(backend="uia").connect(path=config['exe_path'])
    win1 = app1.Dialog
    win1.wait("ready", timeout=10)  # 10s等待时间
    global TOTAL_WINDOW_COUNT
    TOTAL_WINDOW_COUNT = len(win1.children())
    return app1, win1


if __name__ == '__main__':
    # 读取上次的数据
    success_list, error_list = prepare_files()
    app, win = open_app()

    # 读取文件夹
    for folder in os.listdir(config['data_path']):
        if folder in success_list:
            continue
        begin = int(time.time())
        ply_exist = False
        for x in os.listdir(config['data_path'] + folder):
            if '.ply' in x:
                print(config['data_path'] + folder + " 已经存在，跳过即可")
                ply_exist = True
                break
        if ply_exist:
            continue
        if build_dense(win, config['data_path'] + folder):
            write_log("success  " + config['data_path'] + folder + " 用时 " + str(int(time.time())-begin))
            write_list(folder)
            success_list.append(folder)
        else:
            try_again_success = False
            for x in os.listdir(config['data_path'] + folder):
                if '.ply' in x:
                    print(config['data_path'] + folder + " 已经存在，跳过即可")
                    try_again_success = True
                    break
            # 重试三次
            for i in range(0, 3):
                print(config['data_path'] + folder)
                print("重试第" + str(i+1) + "次")
                if app is not None:
                    app.kill()
                app, win = open_app()
                if build_dense(win, config['data_path'] + folder):
                    write_log("success  " + config['data_path'] + folder + " 用时 " + str(int(time.time())-begin))
                    write_list(folder)
                    success_list.append(folder)
                    try_again_success = True
                    break
            if try_again_success:
                continue
            write_log("error  " + config['data_path'] + folder)
            error_list.append(folder)
            write_list(folder, False)
        end = int(time.time())
        diff = end - begin
        print("构建 " + folder + " 数据用时： " + str(diff) + " 秒")
        write_log("构建 " + folder + " 数据用时： " + str(diff) + " 秒")
