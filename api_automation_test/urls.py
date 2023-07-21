"""api_automation_test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.views import static
from django.views.generic import TemplateView, RedirectView
from rest_framework.documentation import include_docs_urls
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer

from Config.case_config import api_index_testResult
from api_test import urls as api
from backend import urls as back_api
from api_test.views import GetFile
from api_test.views.GetResult import get_result
from tools import urls as tools_api
from UserInfo import urls as user

schema_view = get_schema_view(title='测试平台 API', renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer, CoreJSONRenderer]
                              )

urlpatterns = [
    url(r'^favicon\.ico$', RedirectView.as_view(url=r'static/images/favicon.ico')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    url(r'^docs/', schema_view, name="docs"),
    url(r'^{}(?P<result>.+)/$'.format(api_index_testResult), get_result),
    url(r'^TestResult/(?P<result>.+)/$', get_result),
    url(r'^Case/', include(back_api)),
    url(r'^apiTest/', include(api)),
    url(r'^testTools/', include(tools_api)),
    url(r'^user/', include(user)),
    url(r'docsx/', include_docs_urls(title="测试平台")),
    url(r'^image/(?P<news_id>.+)/$', GetFile.read_img, name="image"),
    url(r'^$', TemplateView.as_view(template_name="index.html")),
    url(r'^static/photo/(?P<path>.*)$', static.serve, {'document_root': settings.FATHER_PATH + 'photo'}),
    url(r'^static/TestResult/(?P<path>.*)$', static.serve, {'document_root': settings.FATHER_PATH + 'TestResult'}),
    url(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static'),
    # url(r'^(?P<json_id>.+)/$', GetFile.read_json),
]
