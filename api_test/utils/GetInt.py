# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: GetInt.py

# @Software: PyCharm


def get_int(x):
    """
    目录下文件名，返回int-list
    :param x:
    :return:
    """
    _list = list()
    for i in x:
        if i.isdigit():
            _list.append(int(i))
        elif i.endswith(".html"):
            if i.split(".")[0].isdigit():
                _list.append(int(i.split(".")[0]))
    return _list


if __name__ == "__main__":
    x1 = ["3", "1", "4", "6"]
    x2 = ["3.html", "1.html", "4.html", "6.html"]
    print(get_int(x1))
    print(get_int(x2))
