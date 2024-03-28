# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: routing.py

# @Software: PyCharm

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/log/(?P<token>\w+)/$', consumers.ChatConsumer),
]
