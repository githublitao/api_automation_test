# -*- coding: utf-8 -*-

# @Time    : 2019-06-14 17:39

# @Author  : litao

# @Project : AutoTest_New

# @FileName: celery.py

# @Software: PyCharm

import os
import django
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AutoTest_New.settings')
django.setup()
app = Celery('AutoTest_New')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
