from django.conf.urls import url

from api_test import views

urlpatterns = [
    url(r'login', views.login),
    url(r'project_list', views.project_list),
    url(r'add_project', views.add_project),
    url(r'geta', views.geta)
]