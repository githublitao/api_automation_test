# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: JenkinsJobManager.py

# @Software: PyCharm
import json
import logging
import time
from ast import literal_eval

import coreapi
import coreschema
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from jenkins import JenkinsException
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from RootDirectory import PROJECT_PATH
from UserInfo.Util.CheckPermissions import check_permissions
from api_test.models import JenkinsJob, ProjectMember, JenkinsServer, Project
from api_test.serializers import JenkinsJobSerializer, JenkinsJobDeserializer
from api_test.tasks import monitor_job_api
from api_test.utils import response
from api_test.utils.JenkinsIni import JenkinsConfig
from api_test.utils.Mkdir import mk_py_dir
from api_test.utils.ProjectStatus import project_status_verify
from api_test.utils.RecordDynamic import record_dynamic
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from api_test.utils.permissions import permission_judge

logger = logging.getLogger("api_automation_test")


class JenkinsJobCustomSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        """Example adding per-method fields."""

        extra_fields = []
        if method == 'GET':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project', required=True, location='query', description='项目id',
                              schema=coreschema.Integer(), type="integer", example="1"),
            ]

        if method == 'PUT':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=True, location='', description='项目id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='job_name', required=True, location='', description='job名称与Jenkins上job相同',
                              schema=coreschema.String(), type="string", example="job名称"),
                coreapi.Field(name='jenkins', required=True, location='', description='jenkins服务器',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='full_url', required=True, location='', description='job地址',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='case', required=True, location='', description='执行的case',
                              schema=coreschema.String(), type="string", example="")
            ]

        if method == "DELETE":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='data', required=True, location='body', description='项目ids列表',
                              schema=coreschema.Object(), type="", example=''),
            ]

        if method == "POST":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=True, location='', description='项目id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='id', required=True, location='', description='id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='job_name', required=True, location='', description='job名称与Jenkins上job相同',
                              schema=coreschema.String(), type="string", example="job名称"),
                coreapi.Field(name='jenkins', required=True, location='', description='jenkins服务器',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='full_url', required=True, location='', description='job地址',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='case', required=True, location='', description='执行的case',
                              schema=coreschema.String(), type="string", example="")
            ]
        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class JenkinsJobManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = JenkinsJobCustomSchema()
    jenkins_job_get = 'JENKINS_JOB_GET'
    jenkins_job_put = 'JENKINS_JOB_PUT'
    jenkins_job_post = 'JENKINS_JOB_POST'
    jenkins_job_delete = 'JENKINS_JOB_DELETE'

    def get(self, request):
        """
        获取监控的job列表
        """
        permiss = check_permissions(request.user, self.jenkins_job_get)
        if not isinstance(permiss, bool):
            return permiss
        try:
            page_size = ""
            if request.GET.get("page_size"):
                page_size = int(request.GET.get("page_size"))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError, KeyError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
        key = request.GET.get("name")
        project_id = request.GET.get("project")
        # 校验参数
        if not project_id:
            return JsonResponse(code_msg=response.KEY_ERROR)
        if not project_id.isdecimal():
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(project_id, request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        # 校验项目状态
        try:
            # 判断项目是否存在
            obj = project_status_verify(project_id)
            if isinstance(obj, dict):
                return JsonResponse(code_msg=obj)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        if key:
            obi = JenkinsJob.objects.filter(project=project_id, job_name__contains=key).order_by("id")
        else:
            obi = JenkinsJob.objects.filter(project=project_id).order_by("id")
        if not page_size:
            serialize = JenkinsJobSerializer(obi, many=True)
            total = ""
        else:
            paginator = Paginator(obi, page_size)  # paginator对象
            total = paginator.num_pages  # 总页数
            try:
                obm = paginator.page(page)
            except PageNotAnInteger:
                obm = paginator.page(1)
            except EmptyPage:
                obm = paginator.page(paginator.num_pages)
            serialize = JenkinsJobSerializer(obm, many=True)
        data = serialize.data
        data = {"data": data,
                "page": page,
                "total": total,
                "all": len(obi)
                }
        return JsonResponse(data=data, code_msg=response.SUCCESS)

    def put(self, request):
        """
        新增监控的job
        """
        permiss = check_permissions(request.user, self.jenkins_job_put)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            # 校验project_id类型为int
            if not isinstance(data["project"], int) or not data["job_name"] or not data["full_url"] or \
                    not isinstance(data["case"], list) or not isinstance(data["next_job"], list) or not data["jenkins"]:
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 校验项目状态
        try:
            # 判断项目是否存在
            obj = project_status_verify(data["project"])
            if isinstance(obj, dict):
                return JsonResponse(code_msg=obj)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(data['project'], request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        try:
            obj_jenkins = JenkinsServer.objects.get(id=data["jenkins"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.JENKINS_SERVER_NOT_EXIST)
        # key关键字唯一校验
        try:
            key = JenkinsJob.objects.filter(full_url=data["full_url"], jenkins=data["jenkins"], project=data["project"])
        except (KeyError, ValueError, TypeError):
            logger.debug(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        if len(key):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        aes_key = cache.get('aes_key')
        if not aes_key:
            return JsonResponse(code_msg=response.AES_KEY_INVALID)
        data["case"] = json.dumps(data["case"], ensure_ascii=False)
        data["next_job"] = json.dumps(data["next_job"], ensure_ascii=False)
        serializer = JenkinsJobDeserializer(data=data)
        # 校验反序列化正确，正确则保存，外键为project
        if serializer.is_valid():
            logger.debug(serializer)
            record_dynamic(project=obj.pk,
                           _type="添加", operationObject="Job监控", user=request.user.pk,
                           data="添加Job监控器 <{}>, 地址 <{}>".format(data["job_name"], data["full_url"]))
            serializer.save(project=obj, jenkins=obj_jenkins)
            mk_py_dir(PROJECT_PATH + "/static/TestResult/{}/job/{}".format(obj.id, serializer.data.get("id")))
            mk_py_dir(PROJECT_PATH + "/templates/TestResult/{}/job/{}".format(obj.id, serializer.data.get("id")))
            with open(PROJECT_PATH + "/static/TestResult/{}/job/{}/history_json.json".format(
                    obj.id, serializer.data.get("id")), "w", encoding="utf-8") as f:
                f.write("[]")
        else:
            logger.error(serializer)
            return JsonResponse(code_msg=response.KEY_ERROR)
        return JsonResponse(data={
            "Jenkins_id": serializer.data.get("id")
        }, code_msg=response.SUCCESS)

    @staticmethod
    def parameter_check(data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id类型为int
            if not isinstance(data["ids"], list) or not data["project"]:
                return JsonResponse(code_msg=response.KEY_ERROR)
            for i in data["ids"]:
                if not isinstance(i, int):
                    return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(response.KEY_ERROR)

    def delete(self, request):
        """
        删除job监视器
        """
        permiss = check_permissions(request.user, self.jenkins_job_delete)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        project_id = data["project"]
        # 校验项目状态
        try:
            # 判断项目是否存在
            obj = project_status_verify(project_id)
            if isinstance(obj, dict):
                return JsonResponse(code_msg=obj)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(project_id, request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        _name = ""
        for i in data["ids"]:
            try:
                _name = _name + '<{}>, '.format(JenkinsJob.objects.get(id=i).job_name)
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.DB_NOT_EXIST)
            except (KeyError, ValueError, TypeError):
                logger.error(data["ids"])
                return JsonResponse(response.KEY_ERROR)
        for j in data["ids"]:
            obi = JenkinsJob.objects.get(id=j)
            obi.delete()
        if _name:
            record_dynamic(project=obj.id,
                           _type="删除", operationObject="Job监控", user=request.user.pk,
                           data="删除Job监视器 {}".format(_name))
        return JsonResponse(code_msg=response.SUCCESS)

    def post(self, request):
        """
        修改Job监控器
        """
        permiss = check_permissions(request.user, self.jenkins_job_post)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            # 校验project_id, id类型为int
            if not isinstance(data["project"], int) or not isinstance(data["id"], int) or not data["job_name"] \
                    or not data["full_url"] or not isinstance(data["case"], list) or \
                    not isinstance(data["next_job"], list)\
                    or not data["jenkins"]:
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 校验项目状态
        try:
            # 判断项目是否存在
            obi = project_status_verify(data["project"])
            if isinstance(obi, dict):
                return JsonResponse(code_msg=obi)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(data['project'], request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        try:
            obj_jenkins = JenkinsServer.objects.get(id=data["jenkins"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.JENKINS_SERVER_NOT_EXIST)
        try:
            obj = JenkinsJob.objects.get(id=data["id"], project=data["project"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.JENKINS_JOB_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        # key关键字唯一校验
        try:
            key = JenkinsJob.objects.filter(job_name=data["job_name"], jenkins=data["jenkins"],
                                            project=data["project"]).exclude(id=data["id"])
        except (KeyError, ValueError, TypeError):
            logger.debug(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        if len(key):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        data["case"] = json.dumps(data["case"], ensure_ascii=False)
        data["next_job"] = json.dumps(data["next_job"], ensure_ascii=False)
        serializer = JenkinsJobDeserializer(data=data)  # 反序列化
        if serializer.is_valid():
            update_data = ""
            if obj.job_name != data["job_name"]:
                update_data = update_data + '修改Job监视器名称"{}"为"{}", '.format(obj.job_name, data["job_name"])
            if obj.jenkins != data["jenkins"]:
                update_data = update_data + '修改Job监视器地址"{}"为"{}", '.format(obj.jenkins, data["jenkins"])
            if obj.full_url != data["full_url"]:
                update_data = update_data + '修改Job监视器用户名"{}"为"{}", '.format(obj.full_url, data["full_url"])
            if obj.case != data["case"]:
                update_data = update_data + '修改Job监视器执行的用例"{}"为"{}", '.format(obj.case, data["case"])
            data["project"] = obi
            data["jenkins"] = obj_jenkins
            logger.debug(serializer)
            if update_data:
                record_dynamic(project=obi.id,
                               _type="修改", operationObject="Job监视器", user=request.user.pk,
                               data=update_data)
            serializer.update(instance=obj, validated_data=data)
        else:
            logger.error(serializer)
            return JsonResponse(code_msg=response.KEY_ERROR)
        return JsonResponse(code_msg=response.SUCCESS)


class TestJobConnect(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(name='Authorization', required=True, location='header', description='token',
                          schema=coreschema.String(), type="string", example="Token string"),
            coreapi.Field(name='jenkins', required=True, location='', description='jenkins_id',
                          schema=coreschema.String(), type="string", example=""),
            coreapi.Field(name='job_name', required=True, location='', description='job名称',
                          schema=coreschema.String(), type="string", example=""),
        ]
    )
    jenkins_job_connect_test = 'JENKINS_JOB_CONNECT_TEST'

    def post(self, request):
        """
        job连接测试
        :param request:
        :return:
        """
        permiss = check_permissions(request.user, self.jenkins_job_connect_test)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            # 校验project_id类型为int
            if any([not data["jenkins"], not data["job_name"]]):
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        try:
            obj_jenkins = JenkinsServer.objects.get(id=data["jenkins"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.JENKINS_SERVER_NOT_EXIST)
        try:
            with JenkinsConfig(obj_jenkins.url, obj_jenkins.username, obj_jenkins.password) as f:
                if f.get_job_name(data["job_name"]):
                    return JsonResponse(code_msg=response.SUCCESS)
                else:
                    return JsonResponse(code_msg=response.CONNECT_FAIL)
        except JenkinsException as e:
            return JsonResponse(data=str(e), code_msg=response.CONNECT_FAIL)


class JobMonitorSwitch(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(name='Authorization', required=True, location='header', description='token',
                          schema=coreschema.String(), type="string", example="Token string"),
            coreapi.Field(name='project', required=True, location='', description='项目id',
                          schema=coreschema.String(), type="string", example=""),
            coreapi.Field(name='job_id', required=True, location='', description='job监控器id',
                          schema=coreschema.String(), type="string", example=""),
        ]
    )
    Jenkins_job_switch = 'JENKINS_JOB_SWITCH'

    def get(self, request):
        """
        job监控器开关
        :param request:
        :return:
        """
        permiss = check_permissions(request.user, self.Jenkins_job_switch)
        if not isinstance(permiss, bool):
            return permiss
        project = request.GET.get("project")
        job_id = request.GET.get("job")
        try:
            Project.objects.get(id=project)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.PROJECT_NOT_EXIST)
        project_permiss = permission_judge(project, request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        try:
            obj = JenkinsJob.objects.get(id=job_id, project=project)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.JENKINS_JOB_NOT_EXIST)
        obj.switch = not obj.switch
        obj.save()
        return JsonResponse(code_msg=response.SUCCESS)


class TouchJobCase(APIView):
    authentication_classes = ()
    permission_classes = ()

    @staticmethod
    def post(request):
        """
        job触发监视器接口
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        full_url = data["build"]["full_url"]
        url = data["build"]["url"]
        url = full_url.replace("/"+url, "").replace("https://", "").replace("http://", "")
        job_name = data["name"]
        try:
            obj = JenkinsServer.objects.get(url__contains=url)
        except ObjectDoesNotExist:
            logger.error(response.JENKINS_JOB_NOT_EXIST)
            return JsonResponse(code_msg=response.JENKINS_SERVER_NOT_EXIST)
        try:
            obj_job = JenkinsJob.objects.get(job_name=job_name, jenkins=obj.id)
        except ObjectDoesNotExist:
            logger.error(response.JENKINS_JOB_NOT_EXIST)
            return JsonResponse(code_msg=response.JENKINS_JOB_NOT_EXIST)
        if obj_job.switch:
            time_stamp = float(data["build"]["timestamp"] / 1000)
            time_array = time.localtime(time_stamp)
            other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
            obj_job.full_url = url+"/"+data["url"]
            obj_job.queue_id = data["build"]["queue_id"]
            obj_job.timestamp = other_style_time
            obj_job.status = data["build"]["status"]
            obj_job.save()
            report_path = PROJECT_PATH + "/static/TestResult/{}/job/{}/".format(obj_job.project.id, obj_job.id)
            kwargs = {
                "receiver": obj_job.receiver,
                "copy": obj_job.copy,
                "strategy": obj_job.email_strategy,
                "DingStrategy": obj_job.DingStrategy,
                "accessToken": obj_job.accessToken
            }
            url = "/TestResult/{}/job/{}/{}".format(obj_job.project.id, obj_job.id, data["build"]["queue_id"])
            monitor_job_api.delay(literal_eval(obj_job.case), data["build"]["queue_id"], report_path, kwargs,
                                  obj_job.project.id, obj_job.id, obj_job.job_name, url, "job", obj_job.next_job)
        return JsonResponse(code_msg=response.SUCCESS)

