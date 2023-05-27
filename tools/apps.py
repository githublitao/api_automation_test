from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class ToolsConfig(AppConfig):
    name = 'tools'
    verbose_name = '测试工具管理'

    def ready(self):
        autodiscover_modules('SettingShell.py')
