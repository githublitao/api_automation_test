from django.contrib import admin

# Register your models here.
from api_test.models import User, Project, GlobalHost, CustomMethod, ApiGroupLevelFirst, ApiGroupLevelSecond, ApiInfo, \
    APIRequestHead, APIRequestParameter, APIRequestParameterValue, APIResponseData, APIResponseParameterValue, \
    APIRequestHistory, ApiGeneralMock, ApiOperationHistory, ProjectDynamic, ProjectMember, AutomationGroupLevelFirst, \
    AutomationGroupLevelSecond, AutomationTestCase, AutomationParameter, AutomationCaseApi


class UserForm(admin.ModelAdmin):
    search_fields = ('name', 'nick_name', 'phone')
    list_display = ('id', 'name', 'password', 'nick_name', 'token', 'permission_type', 'email', 'phone', 'last_login')
    list_display_links = ('name', 'password')


admin.site.register(User, UserForm)


class MemberInProject(admin.TabularInline):
    model = ProjectMember


class ProjectForm(admin.ModelAdmin):
    inlines = [MemberInProject]
    search_fields = ('name', 'type')
    list_display = ('id', 'name', 'version', 'type', 'description', 'status', 'last_update_time', 'create_time')
    list_display_links = ('name',)
    list_filter = ('status', 'type')
    fieldsets = ([
        '项目', {
            'fields': ('name', 'version', 'type', 'description', 'status')
        }],
    )


admin.site.register(Project, ProjectForm)


class ProjectDynamicForm(admin.ModelAdmin):
    search_fields = ('type', 'operation_object', 'user')
    list_display = ('id', 'project_id', 'time', 'type', 'operation_object', 'user', 'description')
    list_display_links = ('project_id', 'time')
    list_filter = ('project_id', 'type', 'operation_object', 'user')


admin.site.register(ProjectDynamic, ProjectDynamicForm)


class ProjectMemberForm(admin.ModelAdmin):
    list_display = ('id', 'permission_type', 'project_id', 'user_id')
    list_display_links = ('permission_type', 'project_id')
    list_filter = ('permission_type', 'project_id', 'user_id')


admin.site.register(ProjectMember, ProjectMemberForm)


class GlobalHostForm(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'project_id', 'name', 'host', 'description', 'status')
    list_display_links = ('project_id', 'name', 'host')
    list_filter = ('project_id', 'status')


admin.site.register(GlobalHost, GlobalHostForm)


class CustomMethodForm(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'project_id', 'name', 'description', 'type', 'status')
    list_display_links = ('project_id', 'name')
    list_filter = ('project_id', 'type', 'status')


admin.site.register(CustomMethod, CustomMethodForm)


class APIGroupLevelSecondInFirst(admin.TabularInline):
    model = ApiGroupLevelSecond


class ApiGroupLevelFirstForm(admin.ModelAdmin):
    inlines = [APIGroupLevelSecondInFirst]
    search_fields = ('name',)
    list_display = ('id', 'project_id', 'name')
    list_display_links = ('project_id', 'name')


admin.site.register(ApiGroupLevelFirst, ApiGroupLevelFirstForm)


class ApiInfoForm(admin.ModelAdmin):
    search_fields = ('ApiGroupLevelFirst_id', 'ApiGroupLevelSecond_id', 'name', 'http_type', 'request_type',
                     'api_address', 'request_parameter_type', 'status')
    list_display = ('id', 'ApiGroupLevelFirst_id', 'ApiGroupLevelSecond_id', 'name', 'http_type', 'request_type',
                    'api_address', 'request_parameter_type', 'status', 'last_update_time', 'user_update')
    list_display_links = ('ApiGroupLevelFirst_id', 'ApiGroupLevelSecond_id', 'name')
    list_filter = ('ApiGroupLevelFirst_id', 'ApiGroupLevelSecond_id', 'http_type', 'request_type', 'status')


admin.site.register(ApiInfo, ApiInfoForm)


class APIRequestHeadForm(admin.ModelAdmin):
    search_fields = ('api_info_id', 'key')
    list_display = ('id', 'api_info_id', 'key', 'value')
    list_display_links = ('api_info_id', 'key')


admin.site.register(APIRequestHead, APIRequestHeadForm)


class APIRequestParameterForm(admin.ModelAdmin):
    search_fields = ('api_info_id', 'name', 'type', 'required')
    list_display = ('id', 'api_info_id', 'name', 'type', 'required')
    list_display_links = ('api_info_id', 'name')


admin.site.register(APIRequestParameter, APIRequestParameterForm)


class APIRequestParameterValueForm(admin.ModelAdmin):
    search_fields = ('APIRequestParameter_id', 'value')
    list_display = ('id', 'APIRequestParameter_id', 'value', 'description')
    list_display_links = ('APIRequestParameter_id', 'value')


admin.site.register(APIRequestParameterValue, APIRequestParameterValueForm)


class APIResponseDataForm(admin.ModelAdmin):
    search_fields = ('api_info_id', 'name', 'type', 'required')
    list_display = ('id', 'api_info_id', 'name', 'type', 'required', 'description')
    list_display_links = ('api_info_id', 'name', 'type')


admin.site.register(APIResponseData, APIResponseDataForm)


class APIResponseParameterValueForm(admin.ModelAdmin):
    search_fields = ('APIResponseData_id', 'value')
    list_display = ('id', 'APIResponseData_id', 'value', 'description')
    list_display_links = ('APIResponseData_id', 'value')


admin.site.register(APIResponseParameterValue, APIResponseParameterValueForm)


class APIRequestHistoryForm(admin.ModelAdmin):
    search_fields = ('api_info_id',)
    list_display = ('id', 'api_info_id', 'request_time', 'request_type', 'request_address', 'http_code')
    list_display_links = ('api_info_id', 'request_time')


admin.site.register(APIRequestHistory, APIRequestHistoryForm)


class ApiGeneralMockForm(admin.ModelAdmin):
    search_fields = ('api_info_id', 'http_code')
    list_display = ('id', 'api_info_id', 'http_code')
    list_display_links = ('api_info_id', 'http_code')


admin.site.register(ApiGeneralMock, ApiGeneralMockForm)


class ApiOperationHistoryForm(admin.ModelAdmin):
    search_fields = ('api_info_id', 'user')
    list_display = ('id', 'api_info_id', 'user', 'time', 'description')
    list_display_links = ('api_info_id', 'user')
    list_filter = ('user',)


admin.site.register(ApiOperationHistory, ApiOperationHistoryForm)


class AutomationGroupLevelSecondInFirst(admin.TabularInline):
    model = AutomationGroupLevelSecond


class AutomationGroupLevelFirstForm(admin.ModelAdmin):
    inlines = [AutomationGroupLevelSecondInFirst]
    search_fields = ('project_id', 'name')
    list_display = ('id', 'project_id', 'name')
    list_display_links = ('project_id', 'name')


admin.site.register(AutomationGroupLevelFirst, AutomationGroupLevelFirstForm)


class AutomationTestCaseForm(admin.ModelAdmin):
    search_fields = ('AutomationGroupLevelFirst_id', 'AutomationGroupLevelSecond_id', 'case_name')
    list_display = ('id', 'AutomationGroupLevelFirst_id', 'AutomationGroupLevelSecond_id', 'case_name',
                    'description', 'update_time')
    list_display_links = ('AutomationGroupLevelFirst_id', 'AutomationGroupLevelSecond_id', 'case_name')
    list_filter = ('AutomationGroupLevelFirst_id', 'AutomationGroupLevelSecond_id')


admin.site.register(AutomationTestCase, AutomationTestCaseForm)


class AutomationCaseApiForm(admin.ModelAdmin):
    search_fields = ('AutomationTestCase_id', 'name', 'http_type', 'request_type', 'address',
                     'request_parameter_type', 'examine_type', 'http_code')
    list_display = ('id', 'AutomationTestCase_id', 'name', 'http_type', 'request_type', 'address',
                    'request_parameter_type', 'examine_type', 'http_code')
    list_display_links = ('AutomationTestCase_id', 'name', 'http_type')
    list_filter = ('AutomationTestCase_id', 'http_type', 'request_type',
                   'request_parameter_type', 'examine_type', 'http_code')


admin.site.register(AutomationCaseApi, AutomationCaseApiForm)


class AutomationParameterForm(admin.ModelAdmin):
    search_fields = ('AutomationCaseApi_id', 'key')
    list_display = ('id', 'AutomationCaseApi_id', 'key', 'value', 'interrelate')
    list_display_links = ('AutomationCaseApi_id', 'key', 'value')


admin.site.register(AutomationParameter, AutomationParameterForm)





