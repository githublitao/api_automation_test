# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: CompenSation.py

# @Software: PyCharm
import io
import json
import os
import sys

import django

from Config.case_config import api_config, api_index, api_static
from RootDirectory import PROJECT_PATH

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
PathProject = os.path.split(rootPath)[0]
sys.path.append(rootPath)
sys.path.append(PathProject)
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_automation_test.settings")
# django.setup()


from django.db.models import Q
from djcelery.models import PeriodicTask
from api_test.models import Project, GroupInfo, Case, CaseStep, Debugtalk, JenkinsJob
from api_test.serializers import CaseStepSerializer
from api_test.utils.MkCasePy import mk_case_py
from api_test.utils.MkYaml import write_test_case


# 程序启动时执行该脚本，补偿缺失目录
def compensation():
    # 项目目录补偿
    try:
        project_all = Project.objects.filter(Q(status=1) | Q(status=2))  # 读取Project，可用状态和禁用状态的项目，创建项目的包名
        for project in project_all:
            project_path = api_config + project.en_name
            if not os.path.exists(project_path):
                os.makedirs(project_path)
                with open(project_path + "/__init__.py", "w") as f:
                    pass

        debugtalk_all = Debugtalk.objects.filter(Q(project__status=1) | Q(project__status=2))   # 创建debugtalk.py文件
        for debugtalk in debugtalk_all:
            if debugtalk.project.status != 3:
                debug_path = api_config + debugtalk.project.en_name + "/DebugTalk.py"
                if not os.path.exists(debug_path):
                    with io.open(debug_path, 'w',encoding='utf-8') as stream:
                        stream.write(debugtalk.code+"\n")

        # 分组目录
        group_all = GroupInfo.objects.filter(Q(project__status=1) | Q(project__status=2))
        for group in group_all:
            if group.project.status != 3:
                group_path = api_config + group.project.en_name + "/test_" + group.en_name
                if not os.path.exists(group_path):
                    os.makedirs(group_path)
                    with open(group_path + "/__init__.py", "w") as f:
                        pass
        # 用例文件补偿
        case_all = Case.objects.filter(Q(project__status=1) | Q(project__status=2))
        for case in case_all:
            if case.project.status != 3:
                case_step = CaseStep.objects.filter(case=case.id).order_by("step")
                case_length = len(case_step)
                if case.length != case_length:      # 根据CaseStep修改步骤数
                    case.length = case_length
                    case.save()
                if case_length > 0:
                    case_py = api_config + case.project.en_name + "/test_" + case.relation.en_name
                    if not os.path.exists(case_py + "/test_{}.py".format(case.en_name)):
                        serializ = CaseStepSerializer(case_step, many=True)
                        mk_case_py(case_py, case.project.id, case.en_name, serializ.data, case.tag)
                        write_test_case(
                            case_py + "/" + case.en_name + ".yaml",
                            case.project.en_name,
                            case.relation.name,
                            case.name,
                            serializ.data
                        )
        # 任务报告目录
        task = PeriodicTask.objects.filter(kwargs__contains='"project":')
        for task_id in task:
            project = json.loads(task_id.kwargs)["project"]
            html_path = "{}{}/task/{}/".format(api_index, project, task_id.id)
            static_path = "{}{}/task/{}/".format(api_static, project, task_id.id)
            if not os.path.exists(html_path):
                os.makedirs(html_path)
                with open(html_path + "/__init__.py", "w") as f:
                    pass
            if not os.path.exists(static_path):
                os.makedirs(static_path)
                with open(static_path + "/__init__.py", "w") as f:
                    pass

            index_path = "{}{}/task/{}/index.txt".format(api_static, project, task_id.id)
            if not os.path.exists(index_path):
                with open(index_path, "w") as f:
                    f.write("{}".format(task_id.total_run_count))

            history_path = "{}{}/task/{}/history_json.json".format(api_static, project, task_id.id)
            if not os.path.exists(history_path):
                with open(history_path, "w") as f:
                    json.dump([], f)
        # 监控器报告目录
        job = JenkinsJob.objects.all()
        for job_id in job:
            project = job_id.project.id
            html_path = "{}{}/job/{}/".format(api_index, project, job_id.id)
            static_path = "{}{}/job/{}/".format(api_static, project, job_id.id)
            if not os.path.exists(html_path):
                os.makedirs(html_path)
                with open(html_path + "/__init__.py", "w") as f:
                    pass
            if not os.path.exists(static_path):
                os.makedirs(static_path)
                with open(static_path + "/__init__.py", "w") as f:
                    pass

            history_path = "{}{}/job/{}/history_json.json".format(api_static, project, job_id.id)
            if not os.path.exists(history_path):
                with open(history_path, "w") as f:
                    json.dump([], f)
    except Exception:
        pass


compensation()
