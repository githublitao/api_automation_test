from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class ApiTestConfig(AppConfig):
    name = 'api_test'
    verbose_name = '接口自动化管理'

    def ready(self):
        autodiscover_modules('SettingShell')
