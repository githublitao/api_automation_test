# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : project

# @FileName: ConfRelevance.py

# @Software: PyCharm
#   自定义异常类，可自行添加


class ProjectDirExist(Exception):
    def __init__(self, path):
        err = '项目路径已存在，请联系管理员！{}'.format(path)
        Exception.__init__(self, err)


class ProjectDirNotExist(Exception):
    def __init__(self, path):
        err = '项目路径不存在，请联系管理员！{}'.format(path)
        Exception.__init__(self, err)


class PathError(Exception):
    def __init__(self, path):
        err = '路径错误！{}'.format(path)
        Exception.__init__(self, err)


class DBConfigNoFound(Exception):
    def __init__(self, _id):
        err = '未找到数据库配置！对应表id={}'.format(_id)
        Exception.__init__(self, err)


class DBSelect(Exception):
    def __init__(self, sql, e):
        err = '查询语句执行失败！\n Sql: {}\n错误: {}'.format(sql, e)
        Exception.__init__(self, err)


class DBOther(Exception):
    def __init__(self, sql, e):
        err = '语句执行失败！\nSql: {}\n错误: {}'.format(sql, e)
        Exception.__init__(self, err)


class NoSupportType(Exception):
    def __init__(self, e):
        err = '不支持的sql操作{}'.format(e)
        Exception.__init__(self, err)
