
from django.apps import AppConfig
import os

default_app_config = 'api_test.PrimaryBlogConfig'

VERBOSE_APP_NAME = '接口测试平台'


def get_current_app_name(_file):
    return os.path.split(os.path.dirname(_file))[-1]


class PrimaryBlogConfig(AppConfig):
    name = get_current_app_name(__file__)
    verbose_name = VERBOSE_APP_NAME


# from django.contrib import admin
# # from hys_operation.models import *
#
# # class MyAdminSite(admin.AdminSite):
# #     site_header = '好医生运维资源管理系统'  # 此处设置页面显示标题
# #     site_title = '好医生运维'
# #
# # # admin_site = MyAdminSite(name='management')
# # admin_site = MyAdminSite(name='adsff')
# admin.site.site_header = '修改后'
# admin.site.site_title = '哈哈'