# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: urls.py

# @Software: PyCharm
from django.conf.urls import url

from UserInfo.views import user, DingDingLogin, UserJobManage, AuthorityManage, JobAuthorityManage

urlpatterns = [
    url(r'AuthorityReJobManager', JobAuthorityManage.AuthorityReJobManager.as_view()),
    url(r'JobAuthority', JobAuthorityManage.JobAuthorityManager.as_view()),
    url(r'Authority', AuthorityManage.AuthorityManager.as_view()),
    url(r'JobList', UserJobManage.JobListManager.as_view()),
    url(r'userJob', UserJobManage.JobManager.as_view()),
    url(r'config', DingDingLogin.DingdingManager.as_view()),
    url(r'loginOut', user.LoginOut.as_view()),
    url(r'login', user.ObtainAuthToken.as_view()),
    url(r'changePassword', user.ChangePassword.as_view()),
    url(r'changePhoto', user.UploadPhoto.as_view()),
    url(r'userList', user.UserList.as_view())
    ]
