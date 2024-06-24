# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: MkCasePy.py

# @Software: PyCharm
import os

# 公共头
CASE_HEAD = '''
import logging
import os
import sys

import allure
import pytest

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
PathProject = os.path.split(rootPath)[0]
root = os.path.split(PathProject)[0]
sys.path.append(rootPath)
sys.path.append(PathProject)
sys.path.append(root)

from TestScript.common.logs import logInit
from TestScript.common.IniCase import ini_case
from TestScript.common.ReadHostIP import read_host_ip
from TestScript.common.ReadVariables import read_variables
from TestScript.common.TestAndCheck import api_send_check

PATH = os.path.split(os.path.realpath(__file__))[0]

case_dict = ini_case(PATH+"/{name}.yaml")

session = dict()

result = dict()
result["result"] = True
logInit()
logger = logging.getLogger()


@allure.feature(case_dict["testinfo"]["moudle"])  # feature定义功能
class TestApi:

    @pytest.fixture(scope="class")
    def setup_class(self):
        global session, result
        host_ip = read_host_ip({project})
        if not result.get("step"):
            with allure.step("执行setupClass"):
                relevance = dict(read_variables({project}), **session)
                if case_dict["setUpClass"]:
                    for setup_case in case_dict["setUpClass"]:
                        with allure.step(setup_case["test_name"]):
                            if not result["result"]:
                                pytest.xfail("执行<{{}}>失败".format(setup_case["test_name"]))
                            session = api_send_check(setup_case, case_dict["testinfo"]["project"], [relevance, host_ip],
                                                 result)
                else:
                    session = relevance
        yield session, host_ip
        
        with allure.step("执行teardownClass"):
            result["result"] = True
            if case_dict["teardownClass"]:
                for tear_case in case_dict["teardownClass"]:
                    with allure.step(tear_case["test_name"]):
                        if not result["result"]:
                            pytest.xfail("执行<{{}}>失败，请手动执行".format(tear_case["test_name"]))
                        session = api_send_check(tear_case, case_dict["testinfo"]["project"], [session, host_ip],
                                                 result)

    @pytest.fixture()
    def setup_function(self):
        with allure.step("执行setup"):
            pass

        with allure.step("执行teardown"):
            pass
'''

# 单接口用例模板
SINGE_CASE_PY = '''
    @allure.story(case_dict["testinfo"]["title"])  # moudle
    @allure.title(case_dict["test_case"][{index}]["test_name"])  # 步骤名称
    @pytest.mark.repeat({try_num})  # 重复次数
    def test_{num}(self, setup_class):
        """
        {info}
        """
        global session, result
        session = api_send_check(case_dict["test_case"][{index}], case_dict["testinfo"]["project"], setup_class, result)
'''

# 业务链用例模板
INTEGRATION_CASE_PY = '''
    @allure.story(case_dict["testinfo"]["title"])  # moudle
    @allure.title(case_dict["test_case"][{index}]["test_name"])  # 步骤名称
    @pytest.mark.flaky(reruns={try_num}, reruns_delay=3)   # 失败重跑
    def test_{num}(self, setup_class):
        """
        {info}
        """
        global session, result
        if result.get("step") != sys._getframe().f_code.co_name:
            if not result["result"]:
                pytest.xfail("前置接口请求失败")
        else:
            result["result"] = True
        result["step"] = sys._getframe().f_code.co_name
        session = api_send_check(case_dict["test_case"][{index}], case_dict["testinfo"]["project"], setup_class, result)
'''


def mk_case_py(path, project_id, name, body, case_type):
    """
    创建test_py 测试文件
    :param path:    分组路径
    :param project_id:  项目id
    :param name:    用例的英文名
    :param body:   用例信息
    :param case_type:   用例类型        (1, "冒烟用例"),(2, "单接口用例"),(3, "集成用例"),(4, "监控脚本")
    :return:
    """

    if case_type in [1, 2]:         # 判断用例类型
        with open('{}/test_{}.py'.format(path, name), "w", encoding="utf-8") as f:
            f.write(CASE_HEAD.format(name=name, project=project_id))
            num = 0     # 初始化一个数，起用例标题，例如 def test_001
            for i in range(0, len(body)):
                if body[i].get("config"):   # setUp，Case，teardown配置
                    if body[i]["config"] == "Case":
                        f.write(SINGE_CASE_PY.format(
                            num='{:0>3,}'.format(int(num)),
                            index=num,
                            try_num=body[i]["times"],
                            info=body[i].get("info") if body[i].get("info") else body[i].get("step_note")))
                        num = num+1
                else:
                    f.write(SINGE_CASE_PY.format(
                        num='{:0>3,}'.format(int(num)),
                        index=num,
                        try_num=body[i]["times"],
                        info=body[i].get("info") if body[i].get("info") else body[i].get("step_note")))
                    num = num + 1

    elif case_type == 3:
        with open('{}/test_{}.py'.format(path, name), "w", encoding="utf-8") as f:
            f.write(CASE_HEAD.format(name=name, project=project_id))
            num = 0
            for i in range(0, len(body)):
                if body[i].get("config"):
                    if body[i]["config"] == "Case":     # setUp，Case，teardown配置
                        f.write(INTEGRATION_CASE_PY.format(
                            num='{:0>3,}'.format(int(num)),
                            index=num,
                            try_num=body[i].get("times", 1),
                            info=body[i].get("info") if body[i].get("info") else body[i].get("step_note")))
                        num = num+1
                else:
                    f.write(INTEGRATION_CASE_PY.format(
                        num='{:0>3,}'.format(int(num)),
                        index=num,
                        try_num=body[i].get("times", 1),
                        info=body[i].get("info") if body[i].get("info") else body[i].get("step_note")))
                    num = num + 1
    if not os.path.exists('{}/{}.yaml'.format(path, name)):
        with open('{}/{}.yaml'.format(path, name), "w", encoding="utf-8") as f:
            pass


if __name__ == "__main__":
    _path = 'PycharmProjects/api_automation_test/api_test/utils'
    _name = "login"
    _info = "测试"
    mk_case_py(_path, _name, _info, 2)
