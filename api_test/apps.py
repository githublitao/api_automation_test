from django.apps import AppConfig
from suit.apps import DjangoSuitConfig


class ApiTestConfig(AppConfig):
    name = 'api_test'
    verbose_name = '中文'


class SuitConfig(DjangoSuitConfig):
    layout = 'horizontal'
