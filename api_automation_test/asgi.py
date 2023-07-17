# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: asgi.py

# @Software: PyCharm
"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os
import django
from channels.routing import get_default_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_automation_test.settings")
django.setup()
application = get_default_application()
