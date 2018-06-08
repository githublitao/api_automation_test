import logging

import time
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.http import StreamingHttpResponse
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.common import GlobalStatusCode
from api_test.common.WriteDocx import Write
from api_test.common.api_response import JsonResponse
from api_test.common.common import record_dynamic
from api_test.common.loadSwaggerApi import swagger_api
from api_test.models import Project, ApiGroupLevelFirst, ApiInfo, \
    ApiOperationHistory, APIRequestHistory, ApiHead, ApiParameter, ApiResponse, ApiParameterRaw
from api_test.serializers import ApiGroupLevelFirstSerializer, ApiInfoSerializer, APIRequestHistorySerializer, \
    ApiOperationHistorySerializer, ApiInfoListSerializer, ApiInfoDocSerializer, ApiGroupLevelFirstDeserializer, \
    ApiInfoDeserializer, ApiHeadDeserializer, ApiParameterDeserializer, \
    ApiResponseDeserializer, APIRequestHistoryDeserializer

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


class Group(APIView):

    def get(self, request):
        """
        接口分组
        :param request:
        :return:
        """
        project_id = request.GET.get("project_id")
        if not project_id:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        if not project_id.isdecimal():
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        try:
            Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        obi = ApiGroupLevelFirst.objects.filter(project=project_id).order_by("id")
        serialize = ApiGroupLevelFirstSerializer(obi, many=True)
        return JsonResponse(data=serialize.data, code_msg=GlobalStatusCode.success())


class AddGroup(APIView):

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id类型为int
            if not isinstance(data["project_id"], int):
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            # 必传参数 name, host
            if not data["name"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        新增接口分组
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            obj = Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        serializer = ApiGroupLevelFirstDeserializer(data=data)
        if serializer.is_valid():
            serializer.save(project=obj)
        else:
            return JsonResponse(code_msg=GlobalStatusCode.fail())
        record_dynamic(project=serializer.data.get("id"),
                       _type="添加", operationObject="接口分组", user=request.user.pk,
                       data="新增接口分组“%s”" % data["name"])
        return JsonResponse(data={
            "group_id": serializer.data.get("id")
        }, code_msg=GlobalStatusCode.success())


class UpdateNameGroup(APIView):

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not isinstance(data["project_id"], int) or not isinstance(data["id"], int):
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            # 必传参数 name, host
            if not data["name"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        修改接口分组名称
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        try:
            obj = ApiGroupLevelFirst.objects.get(id=data["id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
        serializer = ApiGroupLevelFirstDeserializer(data=data)
        if serializer.is_valid():
            serializer.update(instance=obj, validated_data=data)
        else:
            return JsonResponse(code_msg=GlobalStatusCode.fail())
        record_dynamic(project=serializer.data.get("id"),
                       _type="修改", operationObject="接口分组", user=request.user.pk,
                       data="修改接口分组“%s”" % data["name"])
        return JsonResponse(code_msg=GlobalStatusCode.success())


class DelGroup(APIView):

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not isinstance(data["project_id"], int) or not isinstance(data["id"], int):
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        修改接口分组名称
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        obi = ApiGroupLevelFirst.objects.filter(id=data["id"], project=data["project_id"])
        if obi:
            name = obi[0].name
            obi.delete()
        else:
            return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
        record_dynamic(project=data["project_id"],
                       _type="删除", operationObject="接口分组", user=request.user.pk, data="删除接口分组“%s”" % name)
        return JsonResponse(code_msg=GlobalStatusCode.success())


class ApiList(APIView):

    def get(self, request):
        """
        获取接口列表
        :param request:
        :return:
        """
        try:
            page_size = int(request.GET.get("page_size", 20))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError):
            return JsonResponse(code_msg=GlobalStatusCode.page_not_int())
        project_id = request.GET.get("project_id")
        first_group_id = request.GET.get("apiGroupLevelFirst_id")
        if not project_id:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        name = request.GET.get("name")
        if not project_id.isdecimal():
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        try:
            Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        if first_group_id:
            if not first_group_id.isdecimal():
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if name:
                obi = ApiInfo.objects.filter(project=project_id, name__contains=name, apiGroupLevelFirst=first_group_id,
                                             ).order_by("id")
            else:
                obi = ApiInfo.objects.filter(project=project_id, apiGroupLevelFirst=first_group_id,
                                             ).order_by("id")
        else:
            if name:
                obi = ApiInfo.objects.filter(project=project_id, name__contains=name).order_by("id")
            else:
                obi = ApiInfo.objects.filter(project=project_id).order_by("id")
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = ApiInfoListSerializer(obm, many=True)
        return JsonResponse(data={"data": serialize.data,
                                  "page": page,
                                  "total": total
                                  }, code_msg=GlobalStatusCode.success())


class AddApi(APIView):

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["name"] or not data["httpType"] or not \
                    data["requestType"] or not data["apiAddress"] or not data["requestParameterType"] or not data["status"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if data["status"] not in [True, False]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if not isinstance(data["project_id"], int):
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if data["httpType"] not in ["HTTP", "HTTPS"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if data["requestType"] not in ["POST", "GET", "PUT", "DELETE"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if data["requestParameterType"] not in ["form-data", "raw", "Restful"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        新增接口
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        data["userUpdate"] = request.user.pk
        try:
            obj = Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        try:
            ApiInfo.objects.get(name=data["name"], project=data["project_id"])
            return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
        except ObjectDoesNotExist:
            with transaction.atomic():
                try:
                    serialize = ApiInfoDeserializer(data=data)
                    if serialize.is_valid():
                        try:
                            if not isinstance(data["apiGroupLevelFirst_id"], int):
                                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                            obi = ApiGroupLevelFirst.objects.get(id=data["apiGroupLevelFirst_id"], project=data["project_id"])
                            serialize.save(project=obj, apiGroupLevelFirst=obi)
                        except KeyError:
                            serialize.save(project=obj)
                        api_id = serialize.data.get("id")
                        try:
                            if len(data["headDict"]):
                                for i in data["headDict"]:
                                    try:
                                        if i["name"]:
                                            i["api"] = api_id
                                            head_serialize = ApiHeadDeserializer(data=i)
                                            if head_serialize.is_valid():
                                                head_serialize.save(api=ApiInfo.objects.get(id=api_id))
                                    except KeyError:
                                        return JsonResponse(GlobalStatusCode.parameter_wrong())
                        except KeyError:
                            pass
                        if data["requestParameterType"] == "form-data":
                            try:
                                if len(data["requestList"]):
                                    for i in data["requestList"]:
                                        try:
                                            if i["name"]:
                                                i["api"] = api_id
                                                param_serialize = ApiParameterDeserializer(data=i)
                                                if param_serialize.is_valid():
                                                    param_serialize.save(api=ApiInfo.objects.get(id=api_id))
                                                else:
                                                    return JsonResponse(code_msg=GlobalStatusCode.fail())
                                        except KeyError:
                                            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                            except KeyError:
                                pass
                        else:
                            try:
                                if len(data["requestList"]):
                                    ApiParameterRaw(api=ApiInfo.objects.get(id=api_id), data=data["requestList"]).save()
                            except KeyError:
                                pass
                        try:
                            if len(data["responseList"]):
                                for i in data["responseList"]:
                                    try:
                                        if i["name"]:
                                            i["api"] = api_id
                                            response_serialize = ApiResponseDeserializer(data=i)
                                            if response_serialize.is_valid():
                                                response_serialize.save(api=ApiInfo.objects.get(id=api_id))
                                            else:
                                                return JsonResponse(code_msg=GlobalStatusCode.fail())
                                    except KeyError:
                                        logging.exception("Error")
                                        return JsonResponse(code_msg=GlobalStatusCode.fail())
                        except KeyError:
                            pass
                        record_dynamic(project=data["project_id"],
                                       _type="新增", operationObject="接口", user=request.user.pk,
                                       data="新增接口“%s”" % data["name"])
                        api_record = ApiOperationHistory(apiInfo=ApiInfo.objects.get(id=api_id),
                                                         user=User.objects.get(id=request.user.pk),
                                                         description="新增接口\"%s\"" % data["name"])
                        api_record.save()
                        return JsonResponse(code_msg=GlobalStatusCode.success(), data={"api_id": api_id})
                    return JsonResponse(code_msg=GlobalStatusCode.fail())
                except ObjectDoesNotExist:
                    return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())


class LeadSwagger(APIView):

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["url"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if not isinstance(data["project_id"], int):
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        导入swagger接口信息
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        try:
            swagger_api(data["url"], data["project_id"], request.user)
            return JsonResponse(code_msg=GlobalStatusCode.success())
        except:
            return JsonResponse(code_msg=GlobalStatusCode.fail())


class UpdateApi(APIView):

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["name"] or not data["httpType"] or not \
                    data["requestType"] or not data["apiAddress"] or not data["requestParameterType"] \
                    or not data["status"] or not data["id"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if data["status"] not in [True, False]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if not isinstance(data["project_id"], int) or not isinstance(data["id"], int):
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if data["httpType"] not in ["HTTP", "HTTPS"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if data["requestType"] not in ["POST", "GET", "PUT", "DELETE"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if data["requestParameterType"] not in ["form-data", "raw", "Restful"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        修改接口
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        data["userUpdate"] = request.user.pk
        try:
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        try:
            ApiInfo.objects.get(name=data["name"], project=data["project_id"])
            return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
        except ObjectDoesNotExist:
            pass
        try:
            obi = ApiInfo.objects.get(id=data["id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.api_not_exist())
        with transaction.atomic():
            try:
                serialize = ApiInfoDeserializer(data=data)
                if serialize.is_valid():
                    data["userUpdate"] = request.user
                    try:
                        if not isinstance(data["apiGroupLevelFirst_id"], int):
                            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                        ApiGroupLevelFirst.objects.get(id=data["apiGroupLevelFirst_id"], project=data["project_id"])
                        User.objects.get(id=request.user.pk)
                        serialize.update(instance=obi, validated_data=data)
                    except KeyError:
                        User.objects.get(id=request.user.pk)
                        serialize.update(instance=obi, validated_data=data)
                    try:
                        if len(data["headDict"]):
                            ApiHead.objects.filter(api=data["id"]).delete()
                            for i in data["headDict"]:
                                try:
                                    if i["name"]:
                                        i["api"] = data['id']
                                        head_serialize = ApiHeadDeserializer(data=i)
                                        if head_serialize.is_valid():
                                            head_serialize.save(api=ApiInfo.objects.get(id=data["id"]))
                                except KeyError:
                                    return JsonResponse(GlobalStatusCode.parameter_wrong())
                    except KeyError:
                        pass
                    if data["requestParameterType"] == "form-data":
                        try:
                            if len(data["requestList"]):
                                ApiParameter.objects.filter(api=data["id"]).delete()
                                ApiParameterRaw.objects.filter(api=data["id"]).delete()
                                for i in data["requestList"]:
                                    try:
                                        if i["name"]:
                                            i["api"] = data['id']
                                            param_serialize = ApiParameterDeserializer(data=i)
                                            if param_serialize.is_valid():
                                                param_serialize.save(api=ApiInfo.objects.get(id=data["id"]))
                                            else:
                                                return JsonResponse(code_msg=GlobalStatusCode.fail())
                                    except KeyError:
                                        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                        except KeyError:
                            pass
                    else:
                        try:
                            if len(data["requestList"]):
                                ApiParameter.objects.filter(api=data["id"]).delete()
                                ApiParameterRaw.objects.filter(api=data["id"]).delete()
                                ApiParameterRaw(api=ApiInfo.objects.get(id=data['id']), data=data["requestList"]).save()
                        except KeyError:
                            pass
                    try:
                        if len(data["responseList"]):
                            ApiResponse.objects.filter(api=data["id"]).delete()
                            for i in data["responseList"]:
                                try:
                                    if i["name"]:
                                        i["api"] = data['id']
                                        response_serialize = ApiResponseDeserializer(data=i)
                                        if response_serialize.is_valid():
                                            response_serialize.save(api=ApiInfo.objects.get(id=data['id']))
                                        else:
                                            return JsonResponse(code_msg=GlobalStatusCode.fail())
                                except KeyError:
                                    return JsonResponse(code_msg=GlobalStatusCode.fail())
                    except KeyError:
                        pass
                    record_dynamic(project=data["project_id"],
                                   _type="新增", operationObject="接口", user=request.user.pk,
                                   data="新增接口“%s”" % data["name"])
                    api_record = ApiOperationHistory(apiInfo=ApiInfo.objects.get(id=data['id']),
                                                     user=User.objects.get(id=request.user.pk),
                                                     description="新增接口\"%s\"" % data["name"])
                    api_record.save()
                    return JsonResponse(code_msg=GlobalStatusCode.success())
                return JsonResponse(code_msg=GlobalStatusCode.fail())
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())


class DelApi(APIView):

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["ids"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if not isinstance(data["project_id"], int) or not isinstance(data["ids"], list):
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            for i in data["ids"]:
                if not isinstance(i, int):
                    return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        删除接口
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        id_list = Q()
        for i in data["ids"]:
            id_list = id_list | Q(id=i)
        api_list = ApiInfo.objects.filter(id_list, project=data["project_id"])
        name_list = []
        for j in api_list:
            name_list.append(str(j.name))
        with transaction.atomic():
            api_list.delete()
            record_dynamic(project=data["project_id"],
                           _type="删除", operationObject="接口", user=request.user.pk, data="删除接口分组，列表“%s”" % name_list)
            return JsonResponse(code_msg=GlobalStatusCode.success())


class UpdateGroup(APIView):

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["ids"] or not data["apiGroupLevelFirst_id"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if not isinstance(data["project_id"], int) or not isinstance(data["ids"], list) \
                    or not isinstance(data["apiGroupLevelFirst_id"], int):
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            for i in data["ids"]:
                if not isinstance(i, int):
                    return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        修改接口所属分组
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        id_list = Q()
        for i in data["ids"]:
            id_list = id_list | Q(id=i)
        api_list = ApiInfo.objects.filter(id_list, project=data["project_id"])
        with transaction.atomic():
            api_list.update(apiGroupLevelFirst=ApiGroupLevelFirst.objects.get(id=data["apiGroupLevelFirst_id"]))
            name_list = []
            for j in api_list:
                name_list.append(str(j.name))
            record_dynamic(project=data["project_id"],
                           _type="修改", operationObject="接口", user=request.user.pk, data="修改接口分组，列表“%s”" % name_list)
            return JsonResponse(code_msg=GlobalStatusCode.success())


class ApiInfoDetail(APIView):

    def get(self, request):
        """
        获取接口详情
        :return:
        """
        project_id = request.GET.get("project_id")
        api_id = request.GET.get("api_id")
        if not project_id.isdecimal() or not api_id.isdecimal():
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        try:
            Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        try:
            obi = ApiInfo.objects.get(id=api_id, project=project_id)
            serialize = ApiInfoSerializer(obi)
            return JsonResponse(data=serialize.data, code_msg=GlobalStatusCode.success())
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.api_not_exist())


class AddHistory(APIView):

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["api_id"] or not data["requestType"] \
                    or not data["url"] or not data["httpStatus"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if not isinstance(data["project_id"], int) or not isinstance(data["api_id"], int):
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if data["requestType"] not in ["POST", "GET", "PUT", "DELETE"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if data["httpStatus"] not in ["200", "404", "400", "502", "500", "302"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        添加接口请求历史
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        try:
            obj = ApiInfo.objects.get(id=data["api_id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.api_not_exist())
        serialize = APIRequestHistoryDeserializer(data=data)
        if serialize.is_valid():
            serialize.save(api=obj)
            return JsonResponse(code_msg=GlobalStatusCode.success())
        return JsonResponse(code_msg=GlobalStatusCode.fail())


class HistoryList(APIView):

    def get(self, request):
        """
        获取请求历史
        project_id 项目ID
        api_id 接口ID
        :return:
        """
        project_id = request.GET.get("project_id")
        api_id = request.GET.get("api_id")
        if not project_id.isdecimal() or not api_id.isdecimal():
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        try:
            Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        try:
            obj = ApiInfo.objects.get(id=api_id, project=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.api_not_exist())
        history = APIRequestHistory.objects.filter(api=obj).order_by("-requestTime")[:10]
        data = APIRequestHistorySerializer(history, many=True).data
        return JsonResponse(data=data, code_msg=GlobalStatusCode.success())


class DelHistory(APIView):

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["api_id"] or not data["id"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if not isinstance(data["project_id"], int) or not isinstance(data["api_id"], int) or not isinstance(data["id"], int):
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        删除接口请求历史
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        try:
            obj = ApiInfo.objects.get(id=data["api_id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.api_not_exist())
        obm = APIRequestHistory.objects.filter(id=data["id"], apiInfo=data["api_id"])
        if obm:
            obm.delete()
            api_record = ApiOperationHistory(api=obj,
                                             user=User.objects.get(id=request.user.pk),
                                             description="删除请求历史记录")
            api_record.save()
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.history_not_exist())


class OperationHistory(APIView):

    def get(self, request):
        """
        接口操作历史
        :param request:
        :return:
        """
        try:
            page_size = int(request.GET.get("page_size", 20))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError):
            return JsonResponse(code_msg=GlobalStatusCode.page_not_int())
        project_id = request.GET.get("project_id")
        api_id = request.GET.get("api_id")
        if not project_id.isdecimal() or not api_id.isdecimal():
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        try:
            Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        try:
            ApiInfo.objects.get(id=api_id, project=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.api_not_exist())
        obn = ApiOperationHistory.objects.filter(api=api_id).order_by("-time")
        paginator = Paginator(obn, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = ApiOperationHistorySerializer(obm, many=True)
        return JsonResponse(data={"data": serialize.data,
                                  "page": page,
                                  "total": total
                                  }, code_msg=GlobalStatusCode.success())


class DownLoad(APIView):

    def get(self, request):
        """
        获取Api下载文档路径
        :param request:
        :return:
        """
        project_id = request.GET.get("project_id")
        if not project_id.isdecimal():
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        try:
            obj = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        obi = ApiGroupLevelFirst.objects.filter(project=project_id)
        data = ApiInfoDocSerializer(obi, many=True).data
        obn = ApiInfoSerializer(ApiInfo.objects.filter(project=project_id), many=True).data
        url = Write().write_api(str(obj), group_data=data, data=obn)
        return JsonResponse(code_msg=GlobalStatusCode.success(), data=url)


class DownLoadDoc(APIView):

    def get(self, request):
        url = request.GET.get("url")
        file_name = str(int(time.time())) + ".doc"

        def file_iterator(_file, chunk_size=512):
            while True:
                c = _file.read(chunk_size)
                if c:
                    yield c
                else:
                    break

        _file = open(url, "rb")
        response = StreamingHttpResponse(file_iterator(_file))
        response["Content-Type"] = "application/octet-stream"
        response["Content-Disposition"] = "attachment;filename=\"{0}\"".format(file_name)
        return response
