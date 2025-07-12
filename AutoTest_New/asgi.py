# -*- coding: utf-8 -*-

# @Time    : 2020/1/17 3:55 下午

# @Author  : litao

# @Project : AutoTest_New

# @FileName: asgi.py

# @Software: PyCharm
"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os
import django
from channels.routing import get_default_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AutoTest_New.settings")
django.setup()
application = get_default_application()
