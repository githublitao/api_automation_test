from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.text import capfirst
from collections import OrderedDict as SortedDict

from api_test.models import Project, GroupInfo, API, Case, CaseStep, HostIP, Variables, Debugtalk, \
    TestReport, ProjectMember, DBConfig, SQLManager, ProjectDynamic


def find_model_index(name):
    count = 0
    for model, model_admin in admin.site._registry.items():
        if capfirst(model._meta.verbose_name_plural) == name:
            return count
        else:
            count += 1
    return count


def index_decorator(func):
    def inner(*args, **kwargs):
        template_response = func(*args, **kwargs)
        for app in template_response.context_data['app_list']:
            app['models'].sort(key=lambda x: find_model_index(x['name']))
        return template_response

    return inner


registry = SortedDict()
registry.update(admin.site._registry)
admin.site._registry = registry
admin.site.index = index_decorator(admin.site.index)
admin.site.app_index = index_decorator(admin.site.app_index)
admin.site.site_header = '测试平台后台管理'
admin.site.site_title = '后台管理'

display = ()


class ReadOnlyModelAdmin(admin.ModelAdmin):
    """ModelAdmin class that prevents modifications through the admin.

    The changelist and the detail view work, but a 403 is returned
    if one actually tries to edit an object.
    """

    actions = []

    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    # Allow viewing objects but not actually changing them
    def has_change_permission(self, request, obj=None):
        if request.method not in ('GET', 'HEAD'):
            return True
        return super(ReadOnlyModelAdmin, self).has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False


class ReadAndDeleteModelAdmin(admin.ModelAdmin):
    """ModelAdmin class that prevents modifications through the admin.

    The changelist and the detail view work, but a 403 is returned
    if one actually tries to edit an object.
    """

    actions = []

    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    # Allow viewing objects but not actually changing them
    def has_change_permission(self, request, obj=None):
        if request.method not in ('GET', 'HEAD'):
            return True
        return super(ReadAndDeleteModelAdmin, self).has_change_permission(request, obj)


# @admin.register(Project)
# class ProjectAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'type', 'status', 'update_time', 'create_time', 'user')
#     list_per_page = 20
#     ordering = ('-create_time',)
#     list_display_links = ('name',)
#     # 筛选器
#     list_filter = ("status", "type")  # 过滤器
#     search_fields = ('name', 'user')  # 搜索字段
#     date_hierarchy = 'update_time'  # 详细时间分层筛选　
#     # fieldsets = ([
#     #     '项目', {
#     #         'fields': ('name', "en_"'type', 'status', 'user', "note")
#     #     }],
#     # )
#
#
# @admin.register(ProjectMember)
# class ProjectMemberForm(admin.ModelAdmin):
#     search_fields = ('user', 'project')
#     list_display = ('id', 'permissionType', 'project', 'user')
#     list_display_links = ('permissionType', 'project')
#     list_filter = ('permissionType', 'project', 'user')
#     list_per_page = 20
#     ordering = ('id',)
#     fieldsets = ([
#         '项目成员', {
#             'fields': ('permissionType', 'project', 'user')
#         }],
#     )
#
#
# @admin.register(GroupInfo)
# class GroupInfoAdmin(admin.ModelAdmin):
#     list_display = ('id', 'project', 'name', 'update_time', 'create_time')
#     list_per_page = 20
#     ordering = ('-create_time',)
#     list_display_links = ('name',)
#     # 筛选器
#     search_fields = ('name', 'project')  # 搜索字段
#     date_hierarchy = 'update_time'  # 详细时间分层筛选
#
#
# @admin.register(API)
# class APIAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'url', 'method', 'header', 'body', 'status', 'project', 'group')
#     list_per_page = 20
#     ordering = ('-group',)
#     list_display_links = ('name', 'project')
#     # 筛选器
#     list_filter = ('group', "method")  # 过滤器
#     search_fields = ('name', 'url')  # 搜索字段
#     # date_hierarchy = 'update_time'  # 详细时间分层筛选　
#
#
# @admin.register(Case)
# class CaseAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'project', 'relation', 'length', 'tag')
#     list_per_page = 20
#     ordering = ('-tag',)
#     list_display_links = ('name',)
#     # 筛选器
#     # list_filter = ('type', "status")  # 过滤器
#     search_fields = ('name', )  # 搜索字段
#     # date_hierarchy = 'update_time'  # 详细时间分层筛选　
#
#
# @admin.register(CaseStep)
# class CaseStepAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'url', 'method', 'header', 'body', 'case', 'step')
#     list_per_page = 20
#     ordering = ('-case', 'step')
#     list_display_links = ('name', 'case')
#     # 筛选器
#     # list_filter = ('type', "status")  # 过滤器
#     search_fields = ('name', )  # 搜索字段
#     # date_hierarchy = 'update_time'  # 详细时间分层筛选　
#
#
# @admin.register(HostIP)
# class HostIPAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'value', "IP", 'project')
#     list_per_page = 20
#     list_display_links = ('name', )
#     # 筛选器
#     # list_filter = ('type', "status")  # 过滤器
#     search_fields = ('project', 'name')  # 搜索字段
#     # date_hierarchy = 'update_time'  # 详细时间分层筛选　
#
#
# @admin.register(SQLManager)
# class SQLManagerAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'SQL_type', 'sql', 'relation', 'DB')
#     list_per_page = 20
#     list_display_links = ('SQL_type', )
#     # 筛选器
#     # list_filter = ('type', "status")  # 过滤器
#     search_fields = ('relation', 'SQL_type')  # 搜索字段
#     # date_hierarchy = 'update_time'  # 详细时间分层筛选　
#
#
# @admin.register(DBConfig)
# class DBConfigAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'db_type', 'host', 'port', 'project')
#     list_per_page = 20
#     list_display_links = ('name', )
#     # 筛选器
#     # list_filter = ('type', "status")  # 过滤器
#     search_fields = ('project', 'name')  # 搜索字段
#     # date_hierarchy = 'update_time'  # 详细时间分层筛选　
#
#
# @admin.register(Variables)
# class VariablesAdmin(admin.ModelAdmin):
#     list_display = ('id', 'key', 'value', 'project')
#     list_per_page = 20
#     list_display_links = ('key', )
#     # 筛选器
#     # list_filter = ('type', "status")  # 过滤器
#     search_fields = ('key', 'project')  # 搜索字段
#     # date_hierarchy = 'update_time'  # 详细时间分层筛选　
#
#
# @admin.register(Debugtalk)
# class DebugtalkAdmin(admin.ModelAdmin):
#     list_display = ('project', 'code')
#     list_per_page = 20
#     list_display_links = ('project', )
#     # 筛选器
#     # list_filter = ('type', "status")  # 过滤器
#     search_fields = ('project',)  # 搜索字段
#     # date_hierarchy = 'update_time'  # 详细时间分层筛选　
#
#
# @admin.register(TestReport)
# class TestReportAdmin(admin.ModelAdmin):
#     list_display = ('id', 'url', 'project', 'result')
#     list_per_page = 20
#     list_display_links = ('project', )
#     # 筛选器
#     # list_filter = ('type', "status")  # 过滤器
#     search_fields = ('id', 'project',)  # 搜索字段
#     # date_hierarchy = 'update_time'  # 详细时间分层筛选　
#
#
# @admin.register(ProjectDynamic)
# class ProjectDynamicForm(ReadOnlyModelAdmin):
#     search_fields = ('operationObject', 'user')
#     list_display = ('id', 'project', 'create_time', 'type', 'operationObject', 'description', 'user')
#     list_display_links = ('id', 'project', 'create_time')
#     list_filter = ('project', 'type')
#     list_per_page = 20
#     ordering = ('-id',)
