from PIL import Image
import os
@staticmethod
def replace_color(img_path, target_color, replacement_color, tolerance=50):
    img = Image.open(img_path).convert("RGBA")
    data = img.getdata()

    new_data = []
    for item in data:
        r, g, b, a = item
        if a != 0:  # 保留透明像素
            if (abs(r - target_color[0]) <= tolerance and
                abs(g - target_color[1]) <= tolerance and
                abs(b - target_color[2]) <= tolerance):
                new_data.append((*replacement_color, a))
            else:
                new_data.append(item)
        else:
            new_data.append(item)

    img.putdata(new_data)
    return img
@staticmethod
def list_files_in_directory(directory):
    files_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            files_list.append((file_path, file))
    return files_list
@staticmethod
def change_button_color(path_mid_result = "self_deifnte_button",replacement_color = (120, 120, 120)):
    path_fore = "resource/photo"
    path_mid_process = "black_button"
    directory_path =path_fore+"\\"+path_mid_process # 替换为你的文件夹路径
    files = list_files_in_directory(directory_path)
    for file_path, file_name in files:
        img_path = path_fore+"\\"+path_mid_process+"\\"+file_name
        target_color = (20, 20, 20)  # 要替换的颜色
        tolerance = 50  # 颜色容差范围
        result_img = replace_color(img_path, target_color, replacement_color, tolerance)
        result_img.save(path_fore+"\\"+path_mid_result+"\\"+file_name)  # 保存处理后的图片
def relenish():
    path_fore = "_internal/use_resource"
    path_mid_process = "black_button"
    path_mid_result = ["white_button"]
    replacement_color = [(240,240,240)]
    for i in range(0,len(path_mid_result)):
        directory_path = path_fore + "\\" + path_mid_process  # 替换为你的文件夹路径
        files = list_files_in_directory(directory_path)
        for file_path, file_name in files:
            # if file_name =="xl_shauxin.png":
                img_path = path_fore + "\\" + path_mid_process + "\\" + file_name
                target_color = (20, 20, 20)  # 要替换的颜色
                tolerance = 50  # 颜色容差范围
                result_img = replace_color(img_path, target_color, replacement_color[i], tolerance)
                result_img.save(path_fore + "\\" + path_mid_result[i] + "\\" + file_name)  # 保存处理后的图片

def relenish2():
    path_fore = "_internal/use_resource"
    path_mid_process = "white_button"
    path_mid_result = ["black_button"]
    replacement_color = [(10, 10, 10)]
    for i in range(0, len(path_mid_result)):
        directory_path = path_fore + "\\" + path_mid_process  # 替换为你的文件夹路径
        files = list_files_in_directory(directory_path)
        for file_path, file_name in files:
            # if file_name =="xl_shauxin.png":
            img_path = path_fore + "\\" + path_mid_process + "\\" + file_name
            target_color = (240, 240, 240)  # 要替换的颜色
            tolerance = 50  # 颜色容差范围
            result_img = replace_color(img_path, target_color, replacement_color[i], tolerance)
            result_img.save(path_fore + "\\" + path_mid_result[i] + "\\" + file_name)  # 保存处理后的图片
# relenish()
relenish2()