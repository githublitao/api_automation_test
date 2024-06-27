# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: Mkdir.py

# @Software: PyCharm
import logging
import os
import shutil

from api_test.utils.CustomException import ProjectDirExist, ProjectDirNotExist, PathError

logger = logging.getLogger("api_automation_test")


def mk_py_dir(path):
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    is_exists = os.path.exists(path)

    # 判断结果
    if not is_exists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)
        with open(path+"/__init__.py", "w") as f:
            pass
    else:
        raise ProjectDirExist(path)


def update_py_dir(path, new_name):
    """
    修改项目文件夹名称
    :param path:
    :param new_name:
    :return:
    """
    if os.path.exists(path):
        if os.path.isdir(path):
            os.rename(path, os.path.split(path)[0]+"/"+new_name)
        else:
            raise PathError(path)
    else:
        raise ProjectDirNotExist(path)


def update_py_file(file, new_name):
    """
    修改项目文件名称
    :param file:
    :param new_name:
    :return:
    """
    if os.path.exists(file):
        if os.path.isfile(file):
            os.rename(file, os.path.split(file)[0]+"/"+new_name)
        else:
            raise PathError(file)
    else:
        raise ProjectDirNotExist(file)


def delete_dir(path):
    """
    删除文件夹
    :param path:
    :return:
    """
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            raise PathError(path)
    else:
        raise ProjectDirNotExist(path)


if __name__ == "__main__":
    mk_py_dir("/PycharmProjects/api_automation_test/1/1/1/1")
