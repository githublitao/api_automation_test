import logging

import coreapi
import coreschema
from django.core.exceptions import ObjectDoesNotExist

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models.query_utils import Q
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from Config.case_config import api_config, api_static, api_index
from UserInfo.Util.CheckPermissions import check_permissions
from UserInfo.models import UserProfile
from api_test.models import Project, Debugtalk, ProjectMember
from api_test.serializers import ProjectSerializer, ProjectDeserializer
from api_test.tasks import del_project_task
from api_test.utils import response
from api_test.utils.CustomException import ProjectDirExist
from api_test.utils.Mkdir import mk_py_dir, update_py_dir, delete_dir
from api_test.utils.RecordDynamic import record_dynamic
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from api_test.utils.permissions import permission_judge

logger = logging.getLogger("api_automation_test")


class ProjectCustomSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        """Example adding per-method fields."""

        extra_fields = []
        if method == 'GET':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='name', required=False, location='query', description='',
                              schema=coreschema.String(), type="string", example="name"),
                coreapi.Field(name='type', required=False, location='query', description='',
                              schema=coreschema.String(), type="string", example="web"),
            ]

        if method == 'PUT':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='name', required=True, location='', description='名称',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='en_name', required=True, location='', description='英文名称',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='type', required=True, location='', description='项目类型',
                              schema=coreschema.String(), type="string", example="Web"),
                coreapi.Field(name='note', required=True, location='', description='项目描述',
                              schema=coreschema.String(), type="string", example=""),
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
                coreapi.Field(name='id', required=True, location='', description='项目id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='name', required=False, location='', description='名称',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='en_name', required=True, location='', description='英文名称',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='type', required=False, location='', description='项目类型',
                              schema=coreschema.String(), type="string", example="Web"),
                coreapi.Field(name='note', required=False, location='', description='项目描述',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='status', required=False, location='', description='项目状态',
                              schema=coreschema.Integer(), type="interger", example=""),
            ]
        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class ProjectManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = ProjectCustomSchema()
    project_get = 'PROJECT_GET'
    project_put = 'PROJECT_PUT'
    project_post = 'PROJECT_POST'
    project_delete = 'PROJECT_DELETE'

    def get(self, request):
        """
        获取项目列表
        """
        permiss = check_permissions(request.user, self.project_get)
        if not isinstance(permiss, bool):
            return permiss
        try:
            page_size = int(request.GET.get("page_size", 11))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError, KeyError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
        name = request.GET.get("name")
        _type = request.GET.get("type")
        if name and _type:
            obi = Project.objects.filter(name__contains=name, type__contains=_type).order_by("id").exclude(status=3)
        elif name and not _type:
            obi = Project.objects.filter(name__contains=name).order_by("id").exclude(status=3)
        elif not name and _type:
            obi = Project.objects.filter(type__contains=_type).order_by("id").exclude(status=3)
        else:
            obi = Project.objects.all().order_by("id").exclude(status=3)
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = ProjectSerializer(obm, many=True).data
        data = []
        for i in serialize:
            if request.user.is_superuser:
                i['get'] = True
            else:
                try:
                    ProjectMember.objects.get(project=i['id'], user=request.user.pk)
                    i['get'] = True
                except ObjectDoesNotExist:
                    i['get'] = False
            data.append(i)
        return JsonResponse(data={"data": data,
                                  "page": page,
                                  "total": total
                                  }, code_msg=response.SUCCESS)

    def put(self, request):
        """
        新增项目
        """
        permiss = check_permissions(request.user, self.project_put)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        data["user"] = request.user.pk
        project_serializer = ProjectDeserializer(data=data)
        try:
            select = Q(status=1) | Q(status=2)
            Project.objects.filter(select).get(name=data["name"])
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        except ObjectDoesNotExist:
            try:
                data["en_name"] = data["en_name"].replace(" ", "")
                # if not data["en_name"].isalpha():
                #     return JsonResponse(code_msg=response.EN_NAME_ERROR)
                select = Q(status=1) | Q(status=2)
                Project.objects.filter(select).get(en_name=data["en_name"])
                return JsonResponse(code_msg=response.EN_DUPLICATE_NAME)
            except ObjectDoesNotExist:
                if project_serializer.is_valid():
                    # 保持新项目
                    try:
                        with transaction.atomic():
                            project_serializer.save()
                            Debugtalk(project=Project.objects.get(id=project_serializer.data.get("id"))).save()
                            ProjectMember(permissionType=UserProfile.objects.get(user=request.user.pk).job, project=Project.objects.get(id=project_serializer.data.get("id")), user=request.user).save()
                            record_dynamic(project=project_serializer.data.get("id"),
                                           _type="添加", operationObject="项目", user=request.user.pk, data="创建项目《{}》".format(data["name"]))
                            mk_py_dir(api_config+data["en_name"])
                            mk_py_dir("{}{}".format(api_static, project_serializer.data.get("id")))
                            mk_py_dir("{}{}".format(api_index, project_serializer.data.get("id")))
                        return JsonResponse(data={
                                "project_id": project_serializer.data.get("id")
                            }, code_msg=response.SUCCESS)
                    except ProjectDirExist as e:
                        logging.exception(e)
                        return JsonResponse(code_msg=response.PROJECT_DIR_EXIST)
                    except Exception as e:
                        logging.exception(e)
                        return JsonResponse(code_msg=response.MKDIR_PROJECT_ERROR)
                else:
                    logger.error(project_serializer)
                    return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)

    @staticmethod
    def parameter_check(data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id类型为int
            if not isinstance(data["ids"], list):
                return JsonResponse(code_msg=response.KEY_ERROR)
            for i in data["ids"]:
                if not isinstance(i, int):
                    return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(response.KEY_ERROR)

    def delete(self, request):
        """
        删除项目
        """
        permiss = check_permissions(request.user, self.project_delete)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        for i in data["ids"]:
            try:
                Project.objects.get(id=i)
                project_permiss = permission_judge(i, request)
                if not isinstance(project_permiss, bool):
                    return project_permiss
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.PROJECT_NOT_EXIST)
            except (KeyError, ValueError, TypeError):
                logger.error(data["ids"])
                return JsonResponse(response.KEY_ERROR)
        for j in data["ids"]:
            obj = Project.objects.get(id=j)
            obj.status = 3
            obj.save()
            del_project_task.delay(obj.id)
            record_dynamic(project=j,
                           _type="删除", operationObject="项目", user=request.user.pk, data="删除项目《{}》".format(obj.name))
            delete_dir(api_config+obj.en_name)
        return JsonResponse(code_msg=response.SUCCESS)

    def post(self, request):
        """
        修改项目
        """
        permiss = check_permissions(request.user, self.project_post)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            obj = Project.objects.get(id=data["id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.PROJECT_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(data['id'], request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        # 查找是否相同名称的项目
        try:
            pro_name = Project.objects.filter(name=data["name"]).exclude(id=data["id"]).exclude(status=3)
            pro_en_name = Project.objects.filter(en_name=data["en_name"]).exclude(id=data["id"]).exclude(status=3)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(response.KEY_ERROR)
        data["en_name"] = data["en_name"].replace(" ", "")
        # if not data["en_name"].isalpha():
        #     return JsonResponse(code_msg=response.EN_NAME_ERROR)
        if len(pro_name):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        elif len(pro_en_name):
            return JsonResponse(code_msg=response.EN_DUPLICATE_NAME)
        else:
            serializer = ProjectDeserializer(data=data)
            if serializer.is_valid():
                # 修改项目
                try:
                    with transaction.atomic():
                        update_py_dir(api_config+obj.en_name, data["en_name"])
                        update_data = ""
                        if obj.name != data["name"]:
                            update_data = update_data+'修改名称"{}"为"{}", '.format(obj.name, data["name"])
                        if obj.en_name != data["en_name"]:
                            update_data = update_data + '修改项目包名"{}"为"{}", '.format(obj.en_name, data["en_name"])
                        if obj.type != data["type"]:
                            update_data = update_data + '修改项目类型"{}"为"{}", '.format(obj.type, data["type"])
                        if obj.note != data['note']:
                            update_data = update_data + '修改项目详情"{}"为"{}", '.format(obj.note, data["note"])
                        if update_data == "":
                            update_data = "未修改任何内容！"
                        serializer.update(instance=obj, validated_data=data)
                        record_dynamic(project=obj.id,
                                       _type="修改", operationObject="项目", user=request.user.pk,
                                       data=update_data)
                except Exception as e:
                    logger.error(e)
                    return JsonResponse(code_msg=response.PROJECT_DIR_UPDATE_ERROR)
                return JsonResponse(code_msg=response.SUCCESS)
            else:
                logger.error(serializer)
                return JsonResponse(code_msg=response.KEY_ERROR)


class DisableProject(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(name='Authorization', required=True, location='header', description='token',
                          schema=coreschema.String(), type="string", example="Token string"),
            coreapi.Field(name='id', required=True, location='', description='用户名',
                          schema=coreschema.Integer(), type="integer", example="admin"),
        ]
    )
    disable_project = 'DISABLE_PROJECT'

    def post(self, request):
        """
        修改项目状态
        """
        permiss = check_permissions(request.user, self.disable_project)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        # 查找项目是否存在
        try:
            obj = Project.objects.get(id=data["id"])
            if obj.status == 1:
                obj.status = 2
            elif obj.status == 2:
                obj.status = 1
            else:
                raise ObjectDoesNotExist
            project_permiss = permission_judge(data['id'], request)
            if not isinstance(project_permiss, bool):
                return project_permiss
            obj.save()
            record_dynamic(project=obj.id,
                           _type="修改", operationObject="项目", user=request.user.pk,
                           data="启用" if obj.status == 1 else "禁用")
            return JsonResponse(code_msg=response.SUCCESS)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.PROJECT_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
