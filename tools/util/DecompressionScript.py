# -*- coding: utf-8 -*-

# @Time    : 2019/11/12 6:26 下午

# @Author  : litao

# @Project : api_automation_test

# @FileName: DecompressionScript.py

# @Software: PyCharm
import os
import shutil
import sys
import tarfile
import zipfile

import rarfile


# 解压tgz文件
def un_tgz(filename):
    with tarfile.open(filename) as tar:
        # 判断同名文件夹是否存在，若不存在则创建同名文件夹
        if os.path.isdir(os.path.splitext(filename)[0]):
            return False
        else:
            os.mkdir(os.path.splitext(filename)[0])
            tar.extractall(os.path.splitext(filename)[0])
            return True


# 解压rar压缩包
def un_rar(filename):
    with rarfile.RarFile(filename) as rar:
        # 判断同名文件夹是否存在，若不存在则创建同名文件夹
        if os.path.isdir(os.path.splitext(filename)[0]):
            return False
        else:
            os.mkdir(os.path.splitext(filename)[0])
            rar.extractall(os.path.splitext(filename)[0])
            return True


# 解压缩zip压缩包
def un_zip(filename):
    with zipfile.ZipFile(filename) as zip_file:
        # 判断同名文件夹是否存在，若不存在则创建同名文件夹
        if os.path.isdir(os.path.splitext(filename)[0]):
            return False
        else:
            os.mkdir(os.path.splitext(filename)[0])
        for names in zip_file.namelist():
            zip_file.extract(names, os.path.abspath(os.path.dirname(os.path.splitext(filename)[0])))
        if os.path.isfile(filename):
            os.remove(filename)
        return True


# 移动文件
def move_file(orgin_path, moved_path):
    dir_files = os.listdir(orgin_path)  # 得到该文件夹下所有的文件
    for file in dir_files:
        file_path = os.path.join(orgin_path, file)  # 路径拼接成绝对路径
        if os.path.isfile(file_path):  # 如果是文件，就打印这个文件路径
            if file.endswith(".txt"):
                if os.path.exists(os.path.join(moved_path, file)):
                    continue
                else:
                    shutil.move(file_path, moved_path)
        if os.path.isdir(file_path):  # 如果目录，就递归子目录
            move_file(file_path, moved_path)


if __name__ == '__main__':
    # un_tgz()
    # un_rar()
    if os.path.splitext(sys.argv[1])[1] == '.zip':
        print(un_zip(sys.argv[1]))
    elif os.path.splitext(sys.argv[1])[1] == '.rar':
        print(un_rar(sys.argv[1]))
    elif os.path.splitext(sys.argv[1])[1] == '.tgz':
        print(un_tgz(sys.argv[1]))
    else:
        print("不支持的压缩文件")
    # print(os.path.abspath(os.path.dirname('/Users/jumei/PycharmProjects/api_automation_test/tools/util/allure-2.7.0.zip')))
