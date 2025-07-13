# -*- coding: utf-8 -*-

# @Time    : 2020/1/10 5:50 下午

# @Author  : litao

# @Project : AutoTest_New

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
