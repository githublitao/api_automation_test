# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: celery.py

# @Software: PyCharm

import os
import django
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_automation_test.settings')
django.setup()
app = Celery('api_automation_test')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
