# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: case_config.py

# @Software: PyCharm
import os

from RootDirectory import PROJECT_PATH

father_path = os.path.dirname(PROJECT_PATH)
# 用户头像路径
photo_url = 'static/photo'
# 用户头像绝对路径
photo_url_absolute = father_path + "/" + photo_url
# 测试脚本路径
script_url = "static/ShareScript/Script"
# 测试脚本绝对路径
script_absolute = father_path + "/" + script_url
# 接口用例文件夹
api_case = 'test_api_case'
# 接口用例服务器绝对路径
api_config = PROJECT_PATH + "/{}/".format(api_case)
# 报告静态文件
api_static_TestResult = "/static/TestResult/"
# 报告静态文件绝对路径
api_static = father_path + api_static_TestResult
# 报告html
api_index_testResult = "templates/TestResult/"
# 报告html绝对路径
api_index = father_path + "/" + api_index_testResult
