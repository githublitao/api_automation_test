# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: urls.py

# @Software: PyCharm
from django.conf.urls import url

from tools.views import DBManager, SQLManager, VenvLibraryManager, Script, ScriptRunHistory, AllUser, TestLinkLoading, \
    IDCard

urlpatterns = [
    url(r'db/DB', DBManager.DBConfigManager.as_view()),
    url(r'db/connectTest', DBManager.TestDBConnect.as_view()),
    url(r'db/sqlHistory', SQLManager.SqlHistoryManager.as_view()),
    url(r'script/Library', VenvLibraryManager.VenvLibraryManager.as_view()),
    url(r'script/InstallLibraryLog', VenvLibraryManager.InstallLibraryLog.as_view()),
    url(r'script/Script', Script.ScriptManager.as_view()),
    url(r'script/upload', Script.ScriptPost.as_view()),
    url(r'Download', Script.download_doc),
    url(r'script/run', Script.RunScript.as_view()),
    url(r'script/history', ScriptRunHistory.ScriptHistoryManager.as_view()),
    url(r'script/allUser', AllUser.AllUserManager.as_view()),
    url(r'testLink/project', TestLinkLoading.TestLinkManager.as_view()),
    url(r'testLink/template', TestLinkLoading.TemplateManager.as_view()),
    url(r'IDCard', IDCard.IDCardManager.as_view()),
]
