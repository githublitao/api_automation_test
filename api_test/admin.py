from django.contrib import admin

# Register your models here.

from api_test.models import User, Project, GlobalHost, ApiGroupLevelFirst, ApiGroupLevelSecond, ApiInfo, \
    APIRequestHead, APIRequestParameter, APIRequestParameterValue, APIResponseData, APIResponseParameterValue, \
    APIRequestHistory, ApiGeneralMock, ApiOperationHistory, ProjectDynamic, ProjectMember, AutomationGroupLevelFirst, \
    AutomationGroupLevelSecond, AutomationTestCase, AutomationParameter, AutomationCaseApi, CustomMethod

admin.site.site_header = '测试平台后台管理'
admin.site.site_title = '后台管理'


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


class UserForm(admin.ModelAdmin):
    search_fields = ('name', 'nick_name', 'phone')
    list_display = ('id', 'name', 'password', 'nick_name', 'token', 'permission_type', 'email', 'phone', 'last_login')
    list_display_links = ('name', 'password')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
                     '用户', {
                         'fields': ('name', 'password', 'nick_name', 'permission_type'),
                     }],
                 [
                     '更多', {
                         'classes': ('collapse',),
                         'fields': ('email', 'phone'),
                      }])


admin.site.register(User, UserForm)


class MemberInProject(admin.TabularInline):
    model = ProjectMember


class HostInProject(admin.TabularInline):
    model = GlobalHost


class ProjectForm(admin.ModelAdmin):
    inlines = [MemberInProject, HostInProject]
    search_fields = ('name', 'type')
    list_display = ('id', 'name', 'version', 'type', 'description', 'status', 'last_update_time', 'create_time')
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


class ProjectDynamicForm(ReadOnlyModelAdmin):
    search_fields = ('type', 'operation_object', 'user')
    list_display = ('id', 'project_id', 'time', 'type', 'operation_object', 'user', 'description')
    list_display_links = ('project_id', 'time')
    list_filter = ('project_id', 'type', 'operation_object', 'user')
    list_per_page = 20
    ordering = ('id',)


admin.site.register(ProjectDynamic, ProjectDynamicForm)


class ProjectMemberForm(admin.ModelAdmin):
    list_display = ('id', 'permission_type', 'project_id', 'user_id')
    list_display_links = ('permission_type', 'project_id')
    list_filter = ('permission_type', 'project_id', 'user_id')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '项目成员', {
            'fields': ('permission_type', 'project_id', 'user_id')
        }],
    )


admin.site.register(ProjectMember, ProjectMemberForm)


class GlobalHostForm(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'project_id', 'name', 'host', 'description', 'status')
    list_display_links = ('project_id', 'name', 'host')
    list_filter = ('project_id', 'status')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        'Host配置', {
            'fields': ('project_id', 'name', 'host', 'description', 'status')
        }],)


admin.site.register(GlobalHost, GlobalHostForm)


class CustomMethodForm(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'project_id', 'name', 'description', 'type', 'status', 'data_code')
    list_display_links = ('project_id', 'name')
    list_filter = ('project_id', 'type', 'status')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '自定义方法', {
            'fields': ('project_id', 'name', 'description', 'type', 'status', 'data_code')
        }],)


admin.site.register(CustomMethod, CustomMethodForm)


class APIGroupLevelSecondInFirst(admin.TabularInline):
    model = ApiGroupLevelSecond


class ApiGroupLevelFirstForm(admin.ModelAdmin):
    inlines = [APIGroupLevelSecondInFirst]
    search_fields = ('name',)
    list_display = ('id', 'project_id', 'name')
    list_display_links = ('project_id', 'name')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '接口分组', {
            'fields': ('project_id', 'name')
        }],)


admin.site.register(ApiGroupLevelFirst, ApiGroupLevelFirstForm)


class HeadInApi(admin.TabularInline):
    model = APIRequestHead


class RequestParameterInApi(admin.TabularInline):
    model = APIRequestParameter


class ResponseInApi(admin.TabularInline):
    model = APIResponseData


class MockInApi(admin.TabularInline):
    model = ApiGeneralMock


class ApiInfoForm(admin.ModelAdmin):
    inlines = [HeadInApi, RequestParameterInApi, ResponseInApi, MockInApi]
    search_fields = ('ApiGroupLevelFirst_id', 'ApiGroupLevelSecond_id', 'name', 'http_type', 'request_type',
                     'api_address', 'request_parameter_type', 'status')
    list_display = ('id', 'ApiGroupLevelFirst_id', 'ApiGroupLevelSecond_id', 'name', 'http_type', 'request_type',
                    'api_address', 'request_parameter_type', 'status', 'last_update_time', 'user_update')
    list_display_links = ('ApiGroupLevelFirst_id', 'ApiGroupLevelSecond_id', 'name')
    list_filter = ('ApiGroupLevelFirst_id', 'ApiGroupLevelSecond_id', 'http_type', 'request_type', 'status')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '接口信息', {
            'fields': ('ApiGroupLevelFirst_id', 'ApiGroupLevelSecond_id', 'name', 'http_type', 'request_type',
                       'api_address', 'request_parameter_type', 'status')
        }],)


admin.site.register(ApiInfo, ApiInfoForm)


class APIRequestHeadForm(admin.ModelAdmin):
    # search_fields = ('api_info_id', 'key')
    # list_display = ('id', 'api_info_id', 'key', 'value')
    # list_display_links = ('api_info_id', 'key')
    fieldsets = ([
        '请求头', {
            'fields': ('api_info_id', 'key', 'value')
        }],)


# admin.site.register(APIRequestHead, APIRequestHeadForm)


class ValueInRequestParameter(admin.TabularInline):
    model = APIRequestParameterValue


class APIRequestParameterForm(admin.ModelAdmin):
    inlines = [ValueInRequestParameter,]
    search_fields = ('api_info_id', 'name', 'type', 'required')
    list_display = ('id', 'api_info_id', 'name', 'type', 'required')
    list_display_links = ('api_info_id', 'name')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '请求参数', {
            'fields': ('api_info_id', 'name', 'type', 'required')
        }],)


admin.site.register(APIRequestParameter, APIRequestParameterForm)


class APIRequestParameterValueForm(admin.ModelAdmin):
    # search_fields = ('APIRequestParameter_id', 'value')
    # list_display = ('id', 'APIRequestParameter_id', 'value', 'description')
    # list_display_links = ('APIRequestParameter_id', 'value')
    fieldsets = ([
        '参数可能值', {
            'fields': ('APIRequestParameter_id', 'value', 'description')
        }],)


# admin.site.register(APIRequestParameterValue, APIRequestParameterValueForm)


class ValueInApiResponse(admin.TabularInline):
    model = APIResponseParameterValue


class APIResponseDataForm(admin.ModelAdmin):
    inlines = [ValueInApiResponse, ]
    search_fields = ('api_info_id', 'name', 'type', 'required')
    list_display = ('id', 'api_info_id', 'name', 'type', 'required', 'description')
    list_display_links = ('api_info_id', 'name', 'type')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '返回结果', {
            'fields': ('api_info_id', 'name', 'type', 'required', 'description')
        }],)


admin.site.register(APIResponseData, APIResponseDataForm)


class APIResponseParameterValueForm(admin.ModelAdmin):
    # search_fields = ('APIResponseData_id', 'value')
    # list_display = ('id', 'APIResponseData_id', 'value', 'description')
    # list_display_links = ('APIResponseData_id', 'value')
    fieldsets = ([
        '返回可能值', {
            'fields': ('APIResponseData_id', 'value', 'description')
        }],)


# admin.site.register(APIResponseParameterValue, APIResponseParameterValueForm)


class APIRequestHistoryForm(ReadOnlyModelAdmin):
    search_fields = ('api_info_id',)
    list_display = ('id', 'api_info_id', 'request_time', 'request_type', 'request_address', 'http_code')
    list_display_links = ('api_info_id', 'request_time')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '接口请求历史', {
            'fields': ('api_info_id', 'request_type', 'request_address', 'http_code')
        }],)


admin.site.register(APIRequestHistory, APIRequestHistoryForm)


class ApiGeneralMockForm(admin.ModelAdmin):
    search_fields = ('api_info_id', 'http_code')
    list_display = ('id', 'api_info_id', 'http_code')
    list_display_links = ('api_info_id', 'http_code')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '普通Mock', {
            'fields': ('api_info_id', 'http_code', 'data')
        }],)


admin.site.register(ApiGeneralMock, ApiGeneralMockForm)


class ApiOperationHistoryForm(admin.ModelAdmin):
    search_fields = ('api_info_id', 'user')
    list_display = ('id', 'api_info_id', 'user', 'time', 'description')
    list_display_links = ('api_info_id', 'user')
    list_filter = ('user',)
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '接口操作记录', {
            'fields': ('api_info_id', 'user', 'description')
        }],)


admin.site.register(ApiOperationHistory, ApiOperationHistoryForm)


class AutomationGroupLevelSecondInFirst(admin.TabularInline):
    model = AutomationGroupLevelSecond


class AutomationGroupLevelFirstForm(admin.ModelAdmin):
    inlines = [AutomationGroupLevelSecondInFirst]
    search_fields = ('project_id', 'name')
    list_display = ('id', 'project_id', 'name')
    list_display_links = ('project_id', 'name')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '用例分组', {
            'fields': ('project_id', 'name')
        }],
    )


admin.site.register(AutomationGroupLevelFirst, AutomationGroupLevelFirstForm)


class AutomationTestCaseForm(admin.ModelAdmin):
    search_fields = ('AutomationGroupLevelFirst_id', 'AutomationGroupLevelSecond_id', 'case_name')
    list_display = ('id', 'AutomationGroupLevelFirst_id', 'AutomationGroupLevelSecond_id', 'case_name',
                    'description', 'update_time')
    list_display_links = ('AutomationGroupLevelFirst_id', 'AutomationGroupLevelSecond_id', 'case_name')
    list_filter = ('AutomationGroupLevelFirst_id', 'AutomationGroupLevelSecond_id')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '用例接口列表', {
            'fields': ('AutomationGroupLevelFirst_id', 'AutomationGroupLevelSecond_id', 'case_name', 'description')
        }],)


admin.site.register(AutomationTestCase, AutomationTestCaseForm)


class AutomationParameterInCase(admin.TabularInline):
    model = AutomationParameter


class AutomationCaseApiForm(admin.ModelAdmin):
    inlines = [AutomationParameterInCase, ]
    search_fields = ('AutomationTestCase_id', 'name', 'http_type', 'request_type', 'address',
                     'request_parameter_type', 'examine_type', 'http_code')
    list_display = ('id', 'AutomationTestCase_id', 'name', 'http_type', 'request_type', 'address',
                    'request_parameter_type', 'examine_type', 'http_code')
    list_display_links = ('AutomationTestCase_id', 'name', 'http_type')
    list_filter = ('AutomationTestCase_id', 'http_type', 'request_type',
                   'request_parameter_type', 'examine_type', 'http_code')
    list_per_page = 20
    ordering = ('id',)
    fieldsets = ([
        '接口详情', {
            'fields': ('AutomationTestCase_id', 'name', 'http_type', 'request_type', 'address',
                       'request_parameter_type', 'examine_type', 'http_code')
        }],)


admin.site.register(AutomationCaseApi, AutomationCaseApiForm)


class AutomationParameterForm(admin.ModelAdmin):
    # search_fields = ('AutomationCaseApi_id', 'key')
    # list_display = ('id', 'AutomationCaseApi_id', 'key', 'value', 'interrelate')
    # list_display_links = ('AutomationCaseApi_id', 'key', 'value')
    fieldsets = ([
        '参数详情', {
            'fields': ('AutomationCaseApi_id', 'key', 'value', 'interrelate')
        }],)


# admin.site.register(AutomationParameter, AutomationParameterForm)





