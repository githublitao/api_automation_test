# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: ClientTestLink.py

# @Software: PyCharm
import re
import ssl

import testlink

ssl._create_default_https_context = ssl._create_unverified_context


class ClientTestLink:
    """
    testlink二次封装
    """
    client_url = ""

    def __init__(self, api_key, username):
        # self.project_id = project_id
        # self.catalogue = catalogue
        self.name = username
        self.tlc = testlink.TestlinkAPIClient(self.client_url, api_key)

    def __enter__(self):
        """
        判断 用户key是否认证
        :return:
        """
        try:
            self.tlc.checkDevKey()
            self.tlc.doesUserExist(self.name)
            return self
        except testlink.testlinkerrors.TLResponseError:
            return False

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def is_exist_project(self, project_id, catalogue):
        """
        判断项目和目录是否存在
        :param catalogue:
        :param project_id:
        :return:
        """
        projects = self.get_projects()
        result = False
        for project in projects:
            if project['id'] == project_id:
                for d in project['dir']:
                    if d["id"] == catalogue:
                        result = True
                        break
        return result

    def get_projects(self):
        """获取testLink内所有项目"""
        project_list = []
        for project in self.tlc.getProjects():
            project_list.append({"id": project.get("id"),
                                 "name": project.get("name"),
                                 "dir": self.get_test_suites(project.get('id'))})
        return project_list

    def get_test_suites(self, project):
        """获取指定项目里(需要项目id)的测试用例集"""
        test_suite_list = []
        test_suites = self.tlc.getFirstLevelTestSuitesForTestProject(project)
        for test_suite in test_suites:
            test_suite_list.append({"id": test_suite.get("id"), "name": test_suite.get("name")})
        return test_suite_list

    @staticmethod
    def step_except(step, _except):
        for j in _except:
            try:
                if j[0] == step:
                    return j[1]
            except IndexError:
                pass

    def create_test_case(self, case_list_dic, project_id, catalogue, username):
        all_num = len(case_list_dic)
        fail_index = list()
        for index, case in enumerate(case_list_dic):
            _catalogue = self.create_test_suite(project_id, catalogue, case['testsuiteid'])
            _preconditions = list()
            for i_step in case['preconditions'].split('\n'):
                _preconditions.append("<p>" + i_step + "</p>")
            preconditions = ''.join(_preconditions)
            case_dict = {
                "testprojectid": project_id,
                "testsuiteid": int(_catalogue),
                "testcasename": case['testcasename'],
                "summary": case['summary'],
                "preconditions": preconditions,
                "authorlogin": username,
                "importance": self.format_info(case["level"])
            }
            _except = list()
            if len(case['except']):
                except_list = re.sub("\n（(\\d*?)）|\n\\((\\d*?)\\)", r"</p><p>(\g<1>\g<2>)", case['except']).split("\n")
                for i in except_list:
                    _except.append(re.split("[.,，、]", i, 1))
            try:
                if len(case['step']):
                    case_list = case['step'].split("\n")
                    for step in case_list:
                        if step:
                            steps = re.split('[.,，、]', step, 1)
                            self.tlc.appendStep(steps[1], self.step_except(steps[0], _except), 1)
                else:
                    self.tlc.initStep("", "", 1)
                result = self.tlc.createTestCase(**case_dict)
            except Exception as e:
                print(e)
                fail_index.append(index+2)
        return all_num, fail_index

    @staticmethod
    def format_info(source_data):
        """
        转换Excel中文关键字
        :param source_data:
        :return:
        """
        switcher = {
            "低": 1,
            "中": 2,
            "高": 3,
            "自动化": 2,
            "手工": 1
        }
        return switcher.get(source_data, "Param not defined")

    def update_project_keywords(self, project_id, test_case_id, keyword_value):
        """加关键字"""
        test_case = self.tlc.getTestCase(testcaseid=test_case_id)[0]
        args = {
            'testprojectid': project_id,
            'testcaseexternalid': test_case['full_tc_external_id'],
            'version': int(test_case['version'])
        }
        keyword = self.tlc.addTestCaseKeywords({args['testcaseexternalid']: [keyword_value]})
        return keyword

    def create_test_suite(self, project_id, catalogue, test_suit: str):
        """
        查看用例集是否存在，不存在则创建
        :param catalogue:
        :param project_id:
        :param test_suit: 用例集  1级/2级/3级
        :return:
        """
        test_suit = test_suit.split("/")
        for n in test_suit:
            suite_data = self.tlc.createTestSuite(project_id, n, n, parentid=catalogue)
            cheak_bool = isinstance(suite_data, list)
            if cheak_bool:
                catalogue = suite_data[0].get("id")
            else:
                suit_for_suit = self.get_test_suite_for_test_suite(catalogue)
                for k, v in suit_for_suit.items():
                    if isinstance(v, dict):
                        if v.get("name") == n:
                            catalogue = v.get("id")
                        else:
                            pass
                    else:
                        try:
                            catalogue = suit_for_suit.get("id")
                        except AttributeError:
                            pass
                        break
        return catalogue

    def get_test_suite_for_test_suite(self, test_suite_id):
        """
        查询用例集下是否含有某用例集
        :param test_suite_id:
        :return:
        """
        try:
            test_suite_id = self.tlc.getTestSuitesForTestSuite(test_suite_id)
            return test_suite_id
        except Exception:
            return False


if __name__ == "__main__":
    with ClientTestLink('dda1951324ff105ca9873a6039bec7b6') as f:
        # print(f)
        # print(f.create_test_suite('8', '9', '前端/APP'))
        print(f.create_test_case([], '8', '9', "tao.li1"))
        # print(f.create_test_case([], 'tao.li1'))
        # f.tlc.addTestCaseKeywords({"大前台-254": ['KeyWord01', 'KeyWord03', 'KeyWord02']})
