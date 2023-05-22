from django.contrib import admin

# Register your models here.
from tools.models import DBConfig, SQLHistory, ScriptInfo, ScriptRunHistory

#
# @admin.register(DBConfig)
# class DBConfigAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'db_type', 'host', 'port')
#     list_per_page = 20
#     list_display_links = ('name', )
#     # 筛选器
#     # list_filter = ('type', "status")  # 过滤器
#     search_fields = ('name', )  # 搜索字段
#     # date_hierarchy = 'update_time'  # 详细时间分层筛选　
#
#
# @admin.register(SQLHistory)
# class SQLHistoryAdmin(admin.ModelAdmin):
#     list_display = ('id', 'server', 'db', 'table', 'SQL_type', 'history')
#     list_per_page = 20
#     list_display_links = ('server', )
#     # 筛选器
#     # list_filter = ('type', "status")  # 过滤器
#     search_fields = ('server', )  # 搜索字段
#     # date_hierarchy = 'update_time'  # 详细时间分层筛选　
#
#
# @admin.register(ScriptInfo)
# class ScriptInfoAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'type', 'script_path', 'desc', 'user')
#     list_per_page = 20
#     list_display_links = ('name', )
#     # 筛选器
#     # list_filter = ('type', "status")  # 过滤器
#     search_fields = ('name', 'type', 'user')  # 搜索字段
#     # date_hierarchy = 'update_time'  # 详细时间分层筛选　
#
#
# @admin.register(ScriptRunHistory)
# class ScriptRunHistoryAdmin(admin.ModelAdmin):
#     list_display = ('id', 'script', 'user')
#     list_per_page = 20
#     list_display_links = ('script', )
#     # 筛选器
#     # list_filter = ('type', "status")  # 过滤器
#     search_fields = ('script', )  # 搜索字段
#     # date_hierarchy = 'update_time'  # 详细时间分层筛选　
