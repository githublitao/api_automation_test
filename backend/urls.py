from django.conf.urls import url

from backend.Views import UploadCase, Cases, Projects, Modules

urlpatterns = [
    url(r'upload', UploadCase.UploadCaseManager.as_view()),
    url(r'lists', Cases.CaseInfoManager.as_view()),
    url(r'projects', Projects.ProjectManager.as_view()),
    url(r'modules', Modules.ModulesManager.as_view())
    ]