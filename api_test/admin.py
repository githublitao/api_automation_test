
# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from api_test.models import Project, GlobalHost, ApiGroupLevelFirst, ApiInfo, \
    APIRequestHistory, ApiOperationHistory, ProjectDynamic, ProjectMember, \
    AutomationGroupLevelFirst, AutomationTestCase, AutomationParameter, AutomationCaseApi, \
    AutomationTestResult, AutomationTestTask, AutomationHead, UserProfile, ApiHead, ApiParameter, ApiResponse, \
    ApiParameterRaw, AutomationParameterRaw, AutomationResponseJson, AutomationTaskRunTime, AutomationReportSendConfig, \
    VisitorsRecord

from django.contrib import admin
from django.utils.text import capfirst
from collections import OrderedDict as SortedDict


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
admin.site.siteTitle = '后台管理'

display = ()


class ProfileInline(admin.TabularInline):
    """
    用户模块扩展
    """
    model = UserProfile


class PhoneForm(admin.ModelAdmin):
    fieldsets = ([
        '手机号', {
            'fields': ('phone',)
        }],)


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline,]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class ReadOnlyModelAdmin(admin.ModelAdmin):
    """ModelAdmin class that prevents modifications through the admin.

    The changelist and the detail view work, but a 403 is returned
    if one actually tries to edit an object.
    """

    actions = None

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

    actions = None

    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    # Allow viewing objects but not actually changing them
    def has_change_permission(self, request, obj=None):
        if request.method not in ('GET', 'HEAD'):
            return True
        return super(ReadAndDeleteModelAdmin, self).has_change_permission(request, obj)


class MemberInProject(admin.TabularInline):
    model = ProjectMember


class HostInProject(admin.TabularInline):
    model = GlobalHost


class ProjectForm(admin.ModelAdmin):
    inlines = [MemberInProject, HostInProject]
    search_fields = ('name', 'type')
    list_display = ('id', 'name', 'version', 'type', 'status', 'LastUpdateTime', 'createTime', 'user')
    list_display_links = ('id', 'name',)
    list_filter = ('status', 'type')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '项目', {
            'fields': ('name', 'version', 'type', 'description', 'status', 'user')
        }],
    )


admin.site.register(Project, ProjectForm)


class GlobalHostForm(admin.ModelAdmin):
    search_fields = ('name', 'project')
    list_display = ('id', 'project', 'name', 'host', 'status')
    list_display_links = ('id', 'project', 'name', 'host')
    list_filter = ('project', 'status')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        'Host配置', {
            'fields': ('project', 'name', 'host', 'description', 'status')
        }],)


admin.site.register(GlobalHost, GlobalHostForm)


class CustomMethodForm(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'project', 'name', 'description', 'type', 'status', 'dataCode')
    list_display_links = ('id', 'project', 'name')
    list_filter = ('project', 'type', 'status')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '自定义方法', {
            'fields': ('project', 'name', 'description', 'type', 'status', 'dataCode')
        }],)


class ApiGroupLevelFirstForm(admin.ModelAdmin):
    search_fields = ('name', 'project')
    list_display = ('id', 'project', 'name')
    list_display_links = ('id', 'project', 'name')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '接口分组', {
            'fields': ('project', 'name')
        }],)


admin.site.register(ApiGroupLevelFirst, ApiGroupLevelFirstForm)


class ApiHeadInline(admin.TabularInline):
    model = ApiHead


class ApiParameterInline(admin.TabularInline):
    model = ApiParameter


class ApiParameterRawInline(admin.TabularInline):
    model = ApiParameterRaw


class ApiResponseInline(admin.TabularInline):
    model = ApiResponse


class ApiInfoForm(admin.ModelAdmin):
    inlines = [ApiHeadInline, ApiParameterInline, ApiParameterRawInline, ApiResponseInline]
    search_fields = ('name', 'project', 'httpType', 'requestType', 'apiAddress', 'requestParameterType')
    list_display = ('id', 'project', 'name', 'httpType', 'requestType',
                    'apiAddress', 'status', 'lastUpdateTime', 'userUpdate')
    list_display_links = ('id', 'name', 'project')
    list_filter = ('project', 'httpType', 'requestType', 'status')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '接口信息', {
            'fields': ('project', 'apiGroupLevelFirst', 'name', 'httpType',
                       'requestParameterType', 'requestType', 'apiAddress', 'status', 'mockCode', 'data', 'userUpdate')
        }],)


admin.site.register(ApiInfo, ApiInfoForm)


class APIRequestHistoryForm(ReadOnlyModelAdmin):
    search_fields = ('api', 'requestType', 'httpCode')
    list_display = ('id', 'api', 'requestType', 'requestAddress', 'httpCode', 'requestTime')
    list_display_links = ('id', 'api', 'requestTime')
    list_filter = ('requestType', 'httpCode')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '接口请求历史', {
            'fields': ('api', 'requestType', 'requestAddress', 'httpCode')
        }],)


admin.site.register(APIRequestHistory, APIRequestHistoryForm)


class ApiOperationHistoryForm(ReadOnlyModelAdmin):
    search_fields = ('api', 'user')
    list_display = ('id', 'api', 'user', 'description', 'time')
    list_display_links = ('id', 'api', 'user')
    list_filter = ('user',)
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '接口操作记录', {
            'fields': ('api', 'user', 'description')
        }],)


admin.site.register(ApiOperationHistory, ApiOperationHistoryForm)


class AutomationGroupLevelFirstForm(admin.ModelAdmin):
    search_fields = ('project', 'name')
    list_display = ('id', 'project', 'name')
    list_display_links = ('id', 'project', 'name')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '用例分组', {
            'fields': ('project', 'name')
        }],
    )


admin.site.register(AutomationGroupLevelFirst, AutomationGroupLevelFirstForm)


class AutomationTestCaseForm(admin.ModelAdmin):
    search_fields = ('caseName', 'project')
    list_display = ('id', 'project', 'caseName', 'updateTime')
    list_display_links = ('id', 'caseName', 'project')
    list_filter = ('project',)
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '用例接口列表', {
            'fields': ('project', 'automationGroupLevelFirst',
                       'caseName', 'user', 'description')
        }],)


admin.site.register(AutomationTestCase, AutomationTestCaseForm)


class AutomationParameterInCase(admin.TabularInline):
    model = AutomationParameter


class AutomationHeadInCase(admin.TabularInline):
    model = AutomationHead


class AutomationRawInCase(admin.TabularInline):
    model = AutomationParameterRaw


class AutomationResponseJsonInCase(admin.TabularInline):
    model = AutomationResponseJson


class AutomationCaseApiForm(admin.ModelAdmin):
    inlines = [AutomationHeadInCase, AutomationParameterInCase, AutomationRawInCase, AutomationResponseJsonInCase]
    search_fields = ('automationTestCase', 'name', 'apiAddress')
    list_display = ('id', 'automationTestCase', 'name', 'httpType', 'requestType', 'apiAddress', 'examineType')
    list_display_links = ('id', 'automationTestCase', 'name', 'httpType')
    list_filter = ('httpType', 'requestType', 'requestParameterType', 'examineType')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '接口详情', {
            'fields': ('automationTestCase', 'name', 'httpType', 'requestType', 'apiAddress',
                       'requestParameterType', 'formatRaw', 'examineType', 'httpCode', 'responseData')
        }],)


admin.site.register(AutomationCaseApi, AutomationCaseApiForm)


class AutomationParameterForm(admin.ModelAdmin):
    fieldsets = ([
        '参数详情', {
            'fields': ('automationCaseApi', 'key', 'value', 'interrelate')
        }],)


class AutomationTestResultForm(ReadOnlyModelAdmin):
    search_fields = ('automationCaseApi',)
    list_display = ('id', 'automationCaseApi', 'result', 'httpStatus', 'testTime')
    list_display_links = ('id', 'automationCaseApi', 'result')
    list_filter = ('id', 'httpStatus', 'result')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '测试结果', {
            'fields': ('automationCaseApi', 'testTime', 'url', 'requestType', 'header', 'parameter', 'statusCode',
                       'examineType', 'data', 'result', 'httpStatus', 'responseData')
        }],)


admin.site.register(AutomationTestResult, AutomationTestResultForm)


class AutomationTestTaskForm(admin.ModelAdmin):
    search_fields = ('project', 'name')
    list_display = ('id', 'project', 'Host', 'name', 'type', 'startTime', 'endTime')
    list_display_links = ('id', 'project', 'Host', 'name')
    list_filter = ('type',)
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
          '测试任务', {
                'fields': ('project', 'Host', 'name', 'type', 'frequency',
                           'unit', 'startTime', 'endTime')
            }],)


admin.site.register(AutomationTestTask, AutomationTestTaskForm)


class AutomationTaskRunTimeForm(admin.ModelAdmin):
    list_display = ('id', 'project', 'startTime', 'elapsedTime')
    list_display_links = ('id', 'project')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '任务执行时间', {
            'fields': ('project', 'startTime', 'elapsedTime', 'host')
        }],)


admin.site.register(AutomationTaskRunTime, AutomationTaskRunTimeForm)


class ProjectMemberForm(admin.ModelAdmin):
    search_fields = ('user', 'project')
    list_display = ('id', 'permissionType', 'project', 'user')
    list_display_links = ('permissionType', 'project')
    list_filter = ('permissionType', 'project', 'user')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '项目成员', {
            'fields': ('permissionType', 'project', 'user')
        }],
    )


admin.site.register(ProjectMember, ProjectMemberForm)


class ProjectDynamicForm(ReadOnlyModelAdmin):
    search_fields = ('operationObject', 'user')
    list_display = ('id', 'project', 'time', 'type', 'operationObject', 'description', 'user')
    list_display_links = ('id', 'project', 'time')
    list_filter = ('project', 'type')
    list_per_page = 20
    ordering = ('-id',)


admin.site.register(ProjectDynamic, ProjectDynamicForm)


class AutomationReportSendConfigForm(ReadOnlyModelAdmin):
    list_display = ('id', 'project', 'reportFrom', 'mailUser', 'mailPass', 'mailSmtp')
    list_display_links = ('id', 'project', 'reportFrom', 'mailUser', 'mailPass', 'mailSmtp')
    list_per_page = 20
    ordering = ('-id',)


admin.site.register(AutomationReportSendConfig, AutomationReportSendConfigForm)


class VisitorsRecordForm(ReadAndDeleteModelAdmin):
    search_fields = ('province', 'city', 'district')
    list_display = ('id', 'formattedAddress', "country", "province", "city", "district", 'callTime')
    list_display_links = ('id', 'formattedAddress', "country", "province", "city", "district", 'callTime')
    list_per_page = 20
    ordering = ('-id',)


admin.site.register(VisitorsRecord, VisitorsRecordForm)
