import datetime
import logging
from collections import Counter

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from jsonpath import jsonpath
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from UserInfo.Util.CheckPermissions import check_permissions
from api_test.utils import response
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from backend.Config.CaseType import case_type
from backend.models import Projects, Modules, Cases
from backend.serializers import ProjectsSerializer, ModulesSerializer, CasesSerializer

logger = logging.getLogger("api_automation_test")


class UploadCaseManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    uploadCase = 'ADMIN_UPLOAD_CASE'

    def post(self, request):
        permiss = check_permissions(request.user, self.uploadCase)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        if isinstance(data, list):
            if len(set(jsonpath(data, expr="$..custom_id"))) != len(data):
                repe = [key for key, value in dict(Counter(jsonpath(data, expr="$..custom_id"))).items() if value > 1]
                return JsonResponse(code_msg=response.MAP_CASE_ERROR, data={"msg": f"用例唯一ID重复，用例同步中止！请检查用例ID！！！, 重复列表：{repe}"})
            try:
                with transaction.atomic():
                    add = 0
                    update = 0
                    for case in data:
                        try:
                            path = case["path"].split('/')
                            project_name = path[1]
                            modules_name = path[2]
                            _type = case['type']
                        except (IndexError, KeyError) as e:
                            raise KeyError('{}, 缺少参数{}'.format(case, e))
                        try:
                            case['type'] = case_type(_type)
                        except KeyError as e:
                            raise KeyError('{}, 不存在的用例类型{}'.format(case, e))
                        try:
                            pro_obj = Projects.objects.get(name=project_name)
                            pro_obj = ProjectsSerializer(pro_obj).data
                        except ObjectDoesNotExist:
                            project_serializer = ProjectsSerializer(data={"name": project_name})
                            if project_serializer.is_valid():
                                project_serializer.save()
                                pro_obj = project_serializer.data
                            else:
                                logger.error(project_serializer)
                                raise KeyError("项目创建失败, 请确认参数 {}, 或联系管理员处理！！".format(project_serializer.errors))
                        try:
                            modules_obj = Modules.objects.get(name=modules_name, project=pro_obj['id'])
                            modules_obj = ModulesSerializer(modules_obj).data
                        except ObjectDoesNotExist:
                            modules_serializer = ModulesSerializer(data={"name": modules_name, "project": pro_obj['id']})
                            if modules_serializer.is_valid():
                                modules_serializer.save()
                                modules_obj = modules_serializer.data
                            else:
                                logger.error(modules_serializer)
                                raise KeyError("模块创建失败, 请确认参数 {}, 或联系管理员处理！！！".format(modules_serializer.errors))
                        case['modules'] = modules_obj['id']
                        case['project'] = pro_obj['id']
                        case['write_time'] = datetime.datetime.strptime(case['create_time'], '%Y-%m-%d')
                        del case['create_time']
                        try:
                            case_id = Cases.objects.get(custom_id=case['custom_id'])
                            case_obj = Cases.objects.filter(**case)
                            if not len(case_obj):
                                case_id.delete()
                                _case_serializer = CasesSerializer(data=case)
                                if _case_serializer.is_valid():
                                    update += 1
                                    _case_serializer.save()
                                else:
                                    logger.error(_case_serializer)
                                    raise KeyError("用例更新失败{}".format(_case_serializer.errors))
                        except ObjectDoesNotExist:
                            case_serializer = CasesSerializer(data=case)
                            if case_serializer.is_valid():
                                case_serializer.save()
                                add += 1
                            else:
                                logger.error(case_serializer)
                                raise KeyError('用例写入失败， 请确认参数 {}'.format(case_serializer.errors))
            except Exception as e:
                logger.error(e)
                logger.exception(e)
                return JsonResponse(code_msg=response.MAP_CASE_ERROR, data={"msg": str(e)})
            return JsonResponse(code_msg=response.SUCCESS, data={"msg": f'共 {len(data)} 条用例， 新增 {add} 条, 修改 {update} 条!'})
        else:
            return JsonResponse(code_msg=response.MAP_CASE_ERROR)
