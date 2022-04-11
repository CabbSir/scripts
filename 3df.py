import os.path
import time

from pywinauto import Application

config = {
    "exe_path": "C:\\Program Files\\3DF Zephyr Aerial\\3DF Zephyr Aerial.exe",  # 3df的exe文件路径
    "data_path": "D:\\data\\",  # 数据存放路径
    "use_mask": True,  # 是否使用蒙版
    "dense_time": 70 * 60,  # 重建最大时长 默认70分钟 根据情况调节
}

# 常量定义
FREE_CPU = 8  # 空闲情况下的cpu利用率
WIN_NUM = 25  # 刚打开软件的时候，窗口数量


def s(t=0.5):
    time.sleep(t)


def prepare_files():
    if not os.path.exists('./3df-log'):
        os.makedirs('3df-log')
    if not os.path.exists('./3df-log/success.txt'):
        file = open("./3df-log/success.txt", 'w')
        file.close()
    if not os.path.exists('./3df-log/error.txt'):
        file = open("./3df-log/error.txt", 'w')
        file.close()
    if not os.path.exists('./3df-log/log.txt'):
        file = open("./3df-log/log.txt", 'w')
        file.close()
    s_list = []
    f_list = []
    for line in open("./3df-log/success.txt"):
        s_list.append(line)
    for line in open("./3df-log/error.txt"):
        f_list.append(line)
    return s_list, f_list


def open_app():
    app1 = Application(backend='uia').start(config['exe_path'])
    win1 = app1.Dialog
    win1.wait("ready", timeout=10)
    global WIN_NUM
    WIN_NUM = len(win1.children())
    return app1, win1


def write_log(msg, is_success=True, is_log=False):
    if is_log:
        with open(".\\3df-log\\log.txt", 'a') as log:
            log.write(msg + '\n')
        return
    if is_success:
        with open(".\\3df-log\\success.txt", 'a') as log:
            log.write(msg + '\n')
    else:
        with open(".\\3df-log\\error.txt", 'a') as log:
            log.write(msg + '\n')


def build_workflow(n):
    success = False
    win.type_keys("^n")
    s()
    for j in range(0, 5):
        print("第" + str(j + 1) + "次检查")
        if len(win.children()) == n + 1:
            success = True
            print("成功")
            break
        if j >= 2:
            # 从第三次开始重复发送
            win.type_keys("^n")
        s(1)
    return success


def pick_files(path, window):
    if window.class_name() != 'ProjectWizard':
        return False

    window.CheckBox1.click_input()
    window.CheckBox5.click_input()
    if config['use_mask']:
        window.CheckBox6.click_input()
    window.Button4.click_input()
    s()
    window.Button5.click_input()
    s()
    open_file_win = window.Dialog

    first_file = True
    name_list = []
    for filename in os.listdir(path):
        if len(filename.split(".")) == 3 or filename.split(".")[1] == '.ply':
            continue
        if first_file:
            first_file = False
            continue
        name_list.append("\"" + filename + "\"")
    open_file_win.ComboBox.Edit.type_keys(path)
    open_file_win.ComboBox.Edit.type_keys("{ENTER}")
    open_file_win.ComboBox.Edit.set_edit_text(" ".join(name_list))
    open_file_win.ComboBox.Edit.type_keys("{ENTER}")
    s(1)

    if config['use_mask']:
        window.Button4.click_input()
    window.Button4.click_input()
    window.Button4.click_input()
    window.Button4.click_input()
    window.Button4.click_input()
    window.Button4.click_input()

    window.Button5.click()
    s(1)
    return True


def densing(app2):
    st = time.time()
    while True:
        app2.wait_cpu_usage_lower(threshold=FREE_CPU, timeout=config['dense_time'], usage_interval=2)
        # cpu使用率下降之后，检测三次
        dense_success = False
        if '3DF Zephyr Aerial 4.507' == app2.top_window().texts()[0]:
            for i in range(0, 3):
                print("第" + str(i + 1) + "次检测重建结果")
                if '3DF Zephyr Aerial 4.507' == app2.top_window().texts()[0]:
                    if i == 2:
                        dense_success = True
                        break
                    s(1)
                    continue
                else:
                    print("仍在重建中")
                    break
        else:
            if int(time.time()) - st > 5 * 60 + config['dense_time']:  # 5分钟
                break
            s(10)
        if dense_success:
            break
    return dense_success


def export_points(win, path):
    win.Menu2.MenuItem4.click_input()
    win.type_keys("{VK_DOWN 2}")
    win.type_keys("{ENTER}")

    s(1)
    if len(win.children()) != WIN_NUM + 1:
        win.type_keys("{ESC 3}")
        # 重试一次
        win.Menu2.MenuItem4.click_input()
        win.type_keys("{VK_DOWN 2}")
        win.type_keys("{ENTER}")

    export_win = win.Dialog
    if export_win.class_name() != "ExportMVSPointDialog":
        return False

    export_win.Button3.click()  # 导出
    s()

    save_file_win = app.Dialog

    if save_file_win.class_name() != "QFileDialog":
        return False

    save_file_win.Edit.type_keys(path + "\\" + str(int(time.time())))
    save_file_win.Edit.type_keys("{ENTER}")
    time.sleep(0.5)

    if len(win.children()) != WIN_NUM:
        return False
    return True


def build_dense(a, w, path):
    # 新建项目
    try:
        num = len(w.children())
        if num != WIN_NUM:
            return False

        if not build_workflow(num):
            return False

        work_flow_win = w.Dialog

        if not pick_files(path, work_flow_win):
            return False

        if not densing(a):
            return False

        work_flow_win.Button3.click()
        s(1)

        if len(w.children()) != WIN_NUM:
            return False

        if not export_points(w, path):
            return False

        w.type_keys("^{F4}")
        if len(w.children()) == WIN_NUM + 1:
            w.Dialog.GroupBox.NoButton.click()
        return True
    except Exception as e:
        write_log(path + " 错误信息如下\n" + e, False, True)
        return False


if __name__ == '__main__':
    success_list, error_list = prepare_files()
    app, win = open_app()

    # 读取目录
    for folder in os.listdir(config['data_path']):
        if folder in success_list:
            continue
        begin = int(time.time())
        if app is None:
            app, win = open_app()
        if build_dense(app, win, config['data_path'] + folder):
            write_log(msg="success  " + config['data_path'] + folder, is_success=False, is_log=True)
            write_log(folder)
            success_list.append(folder)
            print(folder + " 重建用时" + str(int(time.time() - begin)))
            write_log(msg=folder + " 重建用时" + str(int(time.time() - begin)), is_success=False, is_log=True)
        else:
            try_again_success = False
            # 失败重试两次
            for i in range(0, 2):
                print(folder + " 数据重建失败，重试第 " + str(i + 1) + " 次")
                if app is not None:
                    app.kill()
                app, win = open_app()
                if build_dense(app, win, config['data_path'] + folder):
                    try_again_success = True
                    write_log(msg="success  " + config['data_path'] + folder, is_success=False, is_log=True)
                    write_log(folder)
                    success_list.append(folder)
                    print(folder + " 重建用时" + str(int(time.time() - begin)))
                    write_log(msg=folder + " 重建用时" + str(int(time.time() - begin)), is_success=False, is_log=True)
                    break
                else:
                    continue
            if try_again_success:
                continue
            write_log(msg="error  " + config['data_path'] + folder, is_success=False, is_log=True)
            write_log(folder, False)
            error_list.append(folder)
            print(folder + " 重建失败 用时" + str(int(time.time() - begin)))
            write_log(msg=folder + " 重建失败 用时" + str(int(time.time() - begin)), is_success=False, is_log=True)
