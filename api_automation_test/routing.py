# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: routing.py

# @Software: PyCharm

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack

import api_test.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            api_test.routing.websocket_urlpatterns
        )
    ),
})
