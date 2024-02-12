from django.contrib import admin

from backend.models import Projects, Modules, Cases


@admin.register(Projects)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'zh_name', 'type', 'update_time', 'create_time', 'description')
    list_per_page = 20
    ordering = ('-create_time',)
    list_display_links = ('name',)
    # 筛选器
    list_filter = ("type",)  # 过滤器
    search_fields = ('name',)  # 搜索字段
    date_hierarchy = 'update_time'  # 详细时间分层筛选　
    fieldsets = ([
                     '项目', {
            'fields': ('name', 'zh_name', "type", 'description')
        }],
    )


@admin.register(Modules)
class ModulesAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'name', 'zh_name', 'update_time', 'create_time', 'description')
    list_per_page = 20
    ordering = ('-create_time',)
    list_display_links = ('name',)
    search_fields = ('name',)  # 搜索字段
    date_hierarchy = 'update_time'  # 详细时间分层筛选　
    fieldsets = ([
                     '模块', {
            'fields': ('project', "name", 'zh_name', 'description')
        }],
    )


@admin.register(Cases)
class CasesAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'custom_id', 'name', 'owner', 'type', 'version', 'status', 'modules', 'update_time', 'create_time',
        'description')
    list_per_page = 20
    ordering = ('-create_time',)
    list_display_links = ('custom_id', 'name')
    # 筛选器
    list_filter = ("type", "status")  # 过滤器
    search_fields = ('name',)  # 搜索字段
    date_hierarchy = 'update_time'  # 详细时间分层筛选　
    fieldsets = ([
                     '用例', {
            'fields': (
                'custom_id', 'name', 'owner', "type", 'write_time', 'version', 'status', 'modules', "path",
                'description')
        }],
    )

#
# @admin.register(Plans)
# class PlansAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'status', 'type', 'owner', 'update_time', 'create_time', 'project', 'description')
#     list_per_page = 20
#     ordering = ('-create_time',)
#     list_display_links = ('name',)
#     # 筛选器
#     list_filter = ("type", 'status')  # 过滤器
#     search_fields = ('name',)  # 搜索字段
#     date_hierarchy = 'update_time'  # 详细时间分层筛选　
#     fieldsets = ([
#                      '测试计划', {
#             'fields': ('name', 'status', 'type', 'owner', 'project')
#         }],
#     )
#
#
# @admin.register(PlanRelatedCase)
# class PlanRelatedCaseAdmin(admin.ModelAdmin):
#     list_display = ('id', 'plan', 'case', 'update_time', 'create_time')
#     list_per_page = 20
#     ordering = ('-create_time',)
#     list_display_links = ('plan', 'case')
#     # 筛选器
#     # list_filter = ("type", 'status')  # 过滤器
#     search_fields = ('name',)  # 搜索字段
#     date_hierarchy = 'update_time'  # 详细时间分层筛选　
#     fieldsets = ([
#                      '计划用例关联', {
#             'fields': ('plan', 'case')
#         }],
#     )
#
#
# @admin.register(Jobs)
# class JobsAdmin(ReadOnlyModelAdmin):
#     list_display = ('id', 'status', 'plan', 'executor', 'report_path', 'take_hours', 'update_time', 'create_time')
#     list_per_page = 20
#     ordering = ('-create_time',)
#     list_display_links = ('plan',)
#     search_fields = ('plan', 'status')  # 搜索字段
#     date_hierarchy = 'update_time'  # 详细时间分层筛选　
#     fieldsets = ([
#                      '任务', {
#             'fields': (
#             'status', 'plan', 'executor', 'report_path', 'take_hours', 'result')
#         }],
#     )
#
#
# @admin.register(ActionLog)
# class ActionLogAdmin(ReadOnlyModelAdmin):
#     list_display = ('id', 'project', 'action_type', 'action', 'user', 'description', 'update_time', 'create_time')
#     list_per_page = 20
#     ordering = ('-create_time',)
#     list_display_links = ('action_type', 'action', 'user')
#     search_fields = ('action_type', 'action', 'user')  # 搜索字段
#     date_hierarchy = 'update_time'  # 详细时间分层筛选　
#     fieldsets = ([
#                      '动态', {
#             'fields': ('project', 'action_type', 'action', 'user', 'description')
#         }],
#     )
