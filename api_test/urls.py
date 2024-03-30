# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: urls.py

# @Software: PyCharm
from django.conf.urls import url

from api_test.views import Project, Group, Api, Case, HostIPManager, VariablesManager, schedule, \
    run_api, ProjectDetail, Report, Upload, DebugTalk, MemberManager, DBManager, SQLManager, ObtainAesSecretKey, \
    DynamicManager, RealTimeLog, JenkinsManager, JenkinsJobManager

urlpatterns = [
    url(r'projectStatus', Project.DisableProject.as_view()),
    url(r'projectDetail', ProjectDetail.ProjectDetailManager.as_view()),
    url(r'project', Project.ProjectManager.as_view()),
    url(r'member', MemberManager.MemberManager.as_view()),
    url(r'group', Group.GroupManager.as_view()),
    # url(r'APIStatus', Api.DisableAPI.as_view()),
    url(r'API', Api.ApiManager.as_view()),
    url(r'case', Case.CaseInfoManager.as_view()),
    url(r'hostIP', HostIPManager.HostIPManager.as_view()),
    url(r'variables', VariablesManager.VariablesManager.as_view()),
    url(r'Schedule', schedule.ScheduleView.as_view()),
    url(r'DisableTasks', schedule.DisableTasks.as_view()),
    url(r'runApi', run_api.RunApiManager.as_view()),
    url(r'report', Report.ReportManager.as_view()),
    url(r'upload/dataFile', Upload.FilePost.as_view()),
    url(r'upload/charles', Upload.ReadCharles.as_view()),
    url(r'upload', Upload.PhotoPost.as_view()),
    url(r'DebugTalk', DebugTalk.DebugTalkView.as_view()),
    url(r'DB', DBManager.DBConfigManager.as_view()),
    url(r'connectTest', DBManager.TestDBConnect.as_view()),
    url(r'SQL', SQLManager.DBSQLManager.as_view()),
    url(r'TestRun', SQLManager.TestDBSQL.as_view()),
    url(r'getAes', ObtainAesSecretKey.GetAesSecretKye.as_view()),
    url(r'dynamic', DynamicManager.DynamicManager.as_view()),
    url(r'RealTimeLoglogs', RealTimeLog.RealTimeLog.as_view()),
    url(r'JenkinsConnect', JenkinsManager.TestJenkinsConnect.as_view()),
    url(r'JenkinsJobConnect', JenkinsJobManager.TestJobConnect.as_view()),
    url(r'JenkinsJobSwitch', JenkinsJobManager.JobMonitorSwitch.as_view()),
    url(r'JenkinsJob', JenkinsJobManager.JenkinsJobManager.as_view()),
    url(r'Jenkins', JenkinsManager.JenkinsManager.as_view()),
    url(r'TouchJobCase', JenkinsJobManager.TouchJobCase.as_view()),
]
