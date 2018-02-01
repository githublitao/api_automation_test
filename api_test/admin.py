from django.contrib import admin

# Register your models here.

from api_test.models import Project, GlobalHost, ApiGroupLevelFirst, ApiGroupLevelSecond, ApiInfo, \
    APIRequestHistory, ApiOperationHistory, ProjectDynamic, ProjectMember, CustomMethod, \
    AutomationGroupLevelSecond, AutomationGroupLevelFirst, AutomationTestCase, AutomationParameter, AutomationCaseApi, \
    AutomationTestResult, AutomationTestTask, AutomationHead

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
        templateresponse = func(*args, **kwargs)
        for app in templateresponse.context_data['app_list']:
            app['models'].sort(key=lambda x: find_model_index(x['name']))
        return templateresponse

    return inner


registry = SortedDict()
registry.update(admin.site._registry)
admin.site._registry = registry
admin.site.index = index_decorator(admin.site.index)
admin.site.app_index = index_decorator(admin.site.app_index)
admin.site.site_header = '测试平台后台管理'
admin.site.siteTitle = '后台管理'

display = ()


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


class MemberInProject(admin.TabularInline):
    model = ProjectMember


class HostInProject(admin.TabularInline):
    model = GlobalHost


class ProjectForm(admin.ModelAdmin):
    inlines = [MemberInProject, HostInProject]
    search_fields = ('name', 'type')
    list_display = ('id', 'name', 'version', 'type', 'description', 'status', 'LastUpdateTime', 'createTime')
    list_display_links = ('name',)
    list_filter = ('status', 'type')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '项目', {
            'fields': ('name', 'version', 'type', 'description', 'status')
        }],
    )


admin.site.register(Project, ProjectForm)


class GlobalHostForm(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'project', 'name', 'host', 'description', 'status')
    list_display_links = ('project', 'name', 'host')
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
    list_display_links = ('project', 'name')
    list_filter = ('project', 'type', 'status')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '自定义方法', {
            'fields': ('project', 'name', 'description', 'type', 'status', 'dataCode')
        }],)


class ApiInfoForm(admin.ModelAdmin):
    # inlines = [MockInApi, ]
    search_fields = ('apiGroupLevelFirst', 'apiGroupLevelSecond', 'name', 'http_type', 'requestType',
                     'apiAddress', 'requestParameterType', 'status')
    list_display = ('id', 'apiGroupLevelFirst', 'apiGroupLevelSecond', 'name', 'http_type', 'requestType',
                    'apiAddress', 'requestParameterType', 'status', 'lastUpdateTime', 'userUpdate')
    list_display_links = ('apiGroupLevelFirst', 'apiGroupLevelSecond', 'name')
    list_filter = ('apiGroupLevelFirst', 'apiGroupLevelSecond', 'http_type', 'requestType', 'status')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '接口信息', {
            'fields': ('project', 'apiGroupLevelFirst', 'apiGroupLevelSecond', 'name', 'http_type',
                       'requestType', 'apiAddress', 'request_head', 'requestParameterType', 'requestParameter',
                       'status', 'response', 'mock_code', 'data')
        }],)


admin.site.register(ApiInfo, ApiInfoForm)


class APIGroupLevelSecondInFirst(admin.TabularInline):
    model = ApiGroupLevelSecond


class ApiGroupLevelFirstForm(admin.ModelAdmin):
    inlines = [APIGroupLevelSecondInFirst]
    search_fields = ('name',)
    list_display = ('id', 'project', 'name')
    list_display_links = ('project', 'name')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '接口分组', {
            'fields': ('project', 'name')
        }],)


admin.site.register(ApiGroupLevelFirst, ApiGroupLevelFirstForm)


class APIRequestHistoryForm(ReadOnlyModelAdmin):
    search_fields = ('apiInfo',)
    list_display = ('id', 'apiInfo', 'requestTime', 'requestType', 'requestAddress', 'httpCode')
    list_display_links = ('apiInfo', 'requestTime')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '接口请求历史', {
            'fields': ('apiInfo', 'requestType', 'requestAddress', 'httpCode')
        }],)


admin.site.register(APIRequestHistory, APIRequestHistoryForm)


class ApiOperationHistoryForm(ReadOnlyModelAdmin):
    search_fields = ('apiInfo', 'user')
    list_display = ('id', 'apiInfo', 'user', 'time', 'description')
    list_display_links = ('apiInfo', 'user')
    list_filter = ('user',)
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '接口操作记录', {
            'fields': ('apiInfo', 'user', 'description')
        }],)


admin.site.register(ApiOperationHistory, ApiOperationHistoryForm)


class AutomationTestCaseForm(admin.ModelAdmin):
    search_fields = ('automationGroupLevelFirst', 'automationGroupLevelSecond', 'caseName')
    list_display = ('id', 'project', 'automationGroupLevelFirst', 'automationGroupLevelSecond', 'caseName',
                    'description', 'updateTime')
    list_display_links = ('automationGroupLevelFirst', 'automationGroupLevelSecond', 'caseName')
    list_filter = ('automationGroupLevelFirst', 'automationGroupLevelSecond')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '用例接口列表', {
            'fields': ('project', 'automationGroupLevelFirst', 'automationGroupLevelSecond',
                       'caseName', 'description')
        }],)


admin.site.register(AutomationTestCase, AutomationTestCaseForm)


class AutomationGroupLevelSecondInFirst(admin.TabularInline):
    model = AutomationGroupLevelSecond


class AutomationGroupLevelFirstForm(admin.ModelAdmin):
    inlines = [AutomationGroupLevelSecondInFirst]
    search_fields = ('project', 'name')
    list_display = ('id', 'project', 'name')
    list_display_links = ('project', 'name')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '用例分组', {
            'fields': ('project', 'name')
        }],
    )


admin.site.register(AutomationGroupLevelFirst, AutomationGroupLevelFirstForm)


class AutomationParameterInCase(admin.TabularInline):
    model = AutomationParameter


class AutomationHeadInCase(admin.TabularInline):
    model = AutomationHead


class AutomationCaseApiForm(admin.ModelAdmin):
    inlines = [AutomationHeadInCase, AutomationParameterInCase]
    search_fields = ('automationTestCase', 'name', 'http_type', 'requestType', 'address',
                     'requestParameterType', 'examineType', 'httpCode')
    list_display = ('id', 'automationTestCase', 'name', 'http_type', 'requestType', 'address',
                    'requestParameterType', 'examineType', 'httpCode')
    list_display_links = ('automationTestCase', 'name', 'http_type')
    list_filter = ('automationTestCase', 'http_type', 'requestType',
                   'requestParameterType', 'examineType', 'httpCode')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '接口详情', {
            'fields': ('automationTestCase', 'name', 'http_type', 'requestType', 'address',
                       'requestParameterType', 'examineType', 'httpCode', 'responseData')
        }],)


admin.site.register(AutomationCaseApi, AutomationCaseApiForm)


class AutomationHead(admin.ModelAdmin):
    fieldsets = ([
        '参数详情', {
            'fields': ('automationCaseApi', 'key', 'value', 'interrelate')
        }],)


class AutomationParameterForm(admin.ModelAdmin):
    fieldsets = ([
        '参数详情', {
            'fields': ('automationCaseApi', 'key', 'value', 'interrelate')
        }],)


class AutomationTestResultForm(ReadOnlyModelAdmin):
    search_fields = ('result', 'automationCaseApi', 'http_status')
    list_display = ('id', 'automationCaseApi', 'result', 'http_status', 'test_time')
    list_filter = ('http_status', 'result')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '测试结果', {
            'fields': ('automationCaseApi', 'result', 'http_status', 'response_data')
        }],)


admin.site.register(AutomationTestResult, AutomationTestResultForm)


class AutomationTestTaskForm(admin.ModelAdmin):
    search_fields = ('name', 'type')
    list_display = ('id', 'automationTestCase', 'Host', 'name', 'type', 'frequency', 'unit', 'startTime', 'endTime')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
          '测试任务', {
                'fields': ('automationTestCase', 'Host', 'name', 'type', 'frequency',
                           'unit', 'startTime', 'endTime')
            }],)


admin.site.register(AutomationTestTask, AutomationTestTaskForm)


class ProjectDynamicForm(ReadOnlyModelAdmin):
    search_fields = ('type', 'operationObject', 'user')
    list_display = ('id', 'project', 'time', 'type', 'operationObject', 'user', 'description')
    list_display_links = ('project', 'time')
    list_filter = ('project', 'type', 'operationObject', 'user')
    list_per_page = 20
    ordering = ('id',)


admin.site.register(ProjectDynamic, ProjectDynamicForm)


class ProjectMemberForm(admin.ModelAdmin):
    list_display = ('id', 'permission_type', 'project', 'user')
    list_display_links = ('permission_type', 'project')
    list_filter = ('permission_type', 'project', 'user')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '项目成员', {
            'fields': ('permission_type', 'project', 'user')
        }],
    )


admin.site.register(ProjectMember, ProjectMemberForm)
