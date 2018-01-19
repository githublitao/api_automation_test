from django.conf.urls import url

from api_test.api.ApiDoc import group, add_group, update_group, del_group, api_list, add_api
from api_test.api.global_parameter import host_total, add_host, update_host, del_host, enable_host, disable_host
from api_test.api.projectList import project_list, add_project, update_project, del_project, disable_project, \
     enable_project
from api_test.api.projectTitle import project_info, api_total, dynamic_total, project_member

urlpatterns = [
    url(r'project/project_list', project_list),
    url(r'project/add_project', add_project),
    url(r'project/update_project', update_project),
    url(r'project/del_project', del_project),
    url(r'project/disable_project', disable_project),
    url(r'project/enable_project', enable_project),
    url(r'title/project_info', project_info),
    url(r'title/api_total', api_total),
    url(r'title/dynamic_total', dynamic_total),
    url(r'title/project_member', project_member),
    url(r'global/host_total', host_total),
    url(r'global/add_host', add_host),
    url(r'global/update_host', update_host),
    url(r'global/del_host', del_host),
    url(r'global/disable_host', disable_host),
    url(r'global/enable_host', enable_host),
    url(r'api/group', group),
    url(r'api/add_group', add_group),
    url(r'api/update_group', update_group),
    url(r'api/del_group', del_group),
    url(r'api/api_list', api_list),
    url(r'api/add_api', add_api),
]
