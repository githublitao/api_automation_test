import logging

import time
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.http import StreamingHttpResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView

from api_test.common.WriteDocx import Write
from api_test.common.api_response import JsonResponse
from api_test.common.common import record_dynamic, check_json
from api_test.common.loadSwaggerApi import swagger_api
from api_test.models import Project, ApiGroupLevelFirst, ApiInfo, \
    ApiOperationHistory, APIRequestHistory, ApiHead, ApiParameter, ApiResponse, ApiParameterRaw
from api_test.serializers import ApiGroupLevelFirstSerializer, ApiInfoSerializer, APIRequestHistorySerializer, \
    ApiOperationHistorySerializer, ApiInfoListSerializer, ApiInfoDocSerializer, ApiGroupLevelFirstDeserializer, \
    ApiInfoDeserializer, ApiHeadDeserializer, ApiParameterDeserializer, \
    ApiResponseDeserializer, APIRequestHistoryDeserializer, ProjectSerializer

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


class Group(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request):
        """
        接口分组
        :param request:
        :return:
        """
        project_id = request.GET.get("project_id")
        # 校验参数
        if not project_id:
            return JsonResponse(code="999996", msg="参数有误!")
        if not project_id.isdecimal():
            return JsonResponse(code="999996", msg="参数有误!")
        # 验证项目是否存在
        try:
            pro_data = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在!")
        # 序列化结果
        pro_data = ProjectSerializer(pro_data)
        # 校验项目状态
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        # 查找项目下所有接口信息，并按id排序，序列化结果
        obi = ApiGroupLevelFirst.objects.filter(project=project_id).order_by("id")
        serialize = ApiGroupLevelFirstSerializer(obi, many=True)
        return JsonResponse(data=serialize.data, code="999999", msg="成功!")


class AddGroup(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id类型为int
            if not isinstance(data["project_id"], int):
                return JsonResponse(code="999996", msg="参数有误!")
            # 必传参数 name
            if not data["name"]:
                return JsonResponse(code="999996", msg="参数有误!")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误!")

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
        # 校验项目状态
        try:
            obj = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and obj.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在!")
        pro_data = ProjectSerializer(obj)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        # 反序列化
        serializer = ApiGroupLevelFirstDeserializer(data=data)
        # 校验反序列化正确，正确则保存，外键为project
        if serializer.is_valid():
            serializer.save(project=obj)
        else:
            return JsonResponse(code="999998", msg="失败!")
        # 新增接口操作
        record_dynamic(project=serializer.data.get("id"),
                       _type="添加", operationObject="接口分组", user=request.user.pk,
                       data="新增接口分组“%s”" % data["name"])
        return JsonResponse(data={
            "group_id": serializer.data.get("id")
        }, code="999999", msg="成功!")


class UpdateNameGroup(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not isinstance(data["project_id"], int) or not isinstance(data["id"], int):
                return JsonResponse(code="999996", msg="参数有误!")
            # 必传参数 name
            if not data["name"]:
                return JsonResponse(code="999996", msg="参数有误!")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误!")

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
            pro_data = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and pro_data.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在!")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            obj = ApiGroupLevelFirst.objects.get(id=data["id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999991", msg="分组不存在!")
        serializer = ApiGroupLevelFirstDeserializer(data=data)
        if serializer.is_valid():
            serializer.update(instance=obj, validated_data=data)
        else:
            return JsonResponse(code="999998", msg="失败!")
        record_dynamic(project=serializer.data.get("id"),
                       _type="修改", operationObject="接口分组", user=request.user.pk,
                       data="修改接口分组“%s”" % data["name"])
        return JsonResponse(code="999999", msg="成功!")


class DelGroup(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not isinstance(data["project_id"], int) or not isinstance(data["id"], int):
                return JsonResponse(code="999996", msg="参数有误!")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误!")

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
            pro_data = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and pro_data.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在!")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        # 根据项目id和host id查找，若存在则删除
        obi = ApiGroupLevelFirst.objects.filter(id=data["id"], project=data["project_id"])
        if obi:
            name = obi[0].name
            obi.delete()
        else:
            return JsonResponse(code="999991", msg="分组不存在!")
        record_dynamic(project=data["project_id"],
                       _type="删除", operationObject="接口分组", user=request.user.pk, data="删除接口分组“%s”" % name)
        return JsonResponse(code="999999", msg="成功!")


class ApiList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

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
            return JsonResponse(code="999985", msg="page and page_size must be integer!")
        project_id = request.GET.get("project_id")
        first_group_id = request.GET.get("apiGroupLevelFirst_id")
        if not project_id:
            return JsonResponse(code="999996", msg="参数有误!")
        name = request.GET.get("name")
        if not project_id.isdecimal():
            return JsonResponse(code="999996", msg="参数有误!")
        try:
            pro_data = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在!")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        # 判断是否传分组id，则为所有接口列表
        if first_group_id:
            if not first_group_id.isdecimal():
                return JsonResponse(code="999996", msg="参数有误!")
            # 判断是否传name，这是根据name查找
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
                                  }, code="999999", msg="成功!")


class AddApi(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验必传参数
            if not data["project_id"] or not data["name"] or not data["httpType"] or not \
                    data["requestType"] or not data["apiAddress"] or not data["requestParameterType"] or not data["status"]:
                return JsonResponse(code="999996", msg="参数有误!")
            if data["status"] not in [True, False]:
                return JsonResponse(code="999996", msg="参数有误!")
            if not isinstance(data["project_id"], int):
                return JsonResponse(code="999996", msg="参数有误!")
            if data["httpType"] not in ["HTTP", "HTTPS"]:
                return JsonResponse(code="999996", msg="参数有误!")
            if data["requestType"] not in ["POST", "GET", "PUT", "DELETE"]:
                return JsonResponse(code="999996", msg="参数有误!")
            if data["requestParameterType"] not in ["form-data", "raw", "Restful"]:
                return JsonResponse(code="999996", msg="参数有误!")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误!")

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
            if not request.user.is_superuser and obj.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在!")
        pro_data = ProjectSerializer(obj)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        api_name = ApiInfo.objects.filter(name=data["name"], project=data["project_id"])
        if len(api_name):
            return JsonResponse(code="999997", msg="存在相同名称!")
        else:
            with transaction.atomic():  # 执行错误后，帮助事物回滚
                serialize = ApiInfoDeserializer(data=data)
                if serialize.is_valid():
                    try:
                        if not isinstance(data.get("apiGroupLevelFirst_id"), int):
                            return JsonResponse(code="999996", msg="参数有误!")
                        obi = ApiGroupLevelFirst.objects.get(id=data["apiGroupLevelFirst_id"], project=data["project_id"])
                        serialize.save(project=obj, apiGroupLevelFirst=obi)
                    except KeyError:
                        serialize.save(project=obj)
                    except ObjectDoesNotExist:
                        return JsonResponse(code="999991", msg="分组不存在!")
                    api_id = serialize.data.get("id")
                    if len(data.get("headDict")):
                        for i in data["headDict"]:
                            if i.get("name"):
                                i["api"] = api_id
                                head_serialize = ApiHeadDeserializer(data=i)
                                if head_serialize.is_valid():
                                    head_serialize.save(api=ApiInfo.objects.get(id=api_id))
                    if data["requestParameterType"] == "form-data":
                        if len(data.get("requestList")):
                            for i in data["requestList"]:
                                if i.get("name"):
                                    i["api"] = api_id
                                    param_serialize = ApiParameterDeserializer(data=i)
                                    if param_serialize.is_valid():
                                        param_serialize.save(api=ApiInfo.objects.get(id=api_id))
                    else:
                        if len(data.get("requestList")):
                            ApiParameterRaw(api=ApiInfo.objects.get(id=api_id), data=data["requestList"]).save()
                    if len(data.get("responseList")):
                        for i in data["responseList"]:
                            if i.get("name"):
                                i["api"] = api_id
                                response_serialize = ApiResponseDeserializer(data=i)
                                if response_serialize.is_valid():
                                    response_serialize.save(api=ApiInfo.objects.get(id=api_id))
                    record_dynamic(project=data["project_id"],
                                   _type="新增", operationObject="接口", user=request.user.pk,
                                   data="新增接口“%s”" % data["name"])
                    api_record = ApiOperationHistory(api=ApiInfo.objects.get(id=api_id),
                                                     user=User.objects.get(id=request.user.pk),
                                                     description="新增接口“%s”" % data["name"])
                    api_record.save()
                    return JsonResponse(code="999999", msg="成功!", data={"api_id": api_id})
                return JsonResponse(code="999996", msg="参数有误!")


class UpdateApiMockStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["id"]:
                return JsonResponse(code="999996", msg="参数有误!")
            if not isinstance(data["project_id"], int) or not isinstance(data["id"], int):
                return JsonResponse(code="999996", msg="参数有误!")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误!")

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
        try:
            pro_data = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and pro_data.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在!")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            obi = ApiInfo.objects.get(id=data["id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999990", msg="接口不存在!")
        obi.mockStatus = not obi.mockStatus
        obi.save()
        if obi.mockStatus:
            record_dynamic(project=data["project_id"],
                           _type="mock", operationObject="接口", user=request.user.pk,
                           data="关闭“%s”Mock" % obi.name)
        else:
            record_dynamic(project=data["project_id"],
                           _type="mock", operationObject="接口", user=request.user.pk,
                           data="启动“%s”Mock" % obi.name)
        return JsonResponse(code="999999", msg="成功!")


class MockRequest(APIView):
    # throttle_classes = ()
    permission_classes = ()

    def get(self, request, apiAdr=None):
        """
        get请求
        :param request:
        :param apiAdr:
        :return:
        """
        url = "/"+apiAdr
        try:
            obj = ApiInfo.objects.get(apiAddress=url, mockStatus=1)
        except ObjectDoesNotExist:
            return JsonResponse(code="999984", msg="未匹配到mock地址或未开启!")
        head_data = ApiHead.objects.filter(api=obj)
        if len(head_data):
            for i in head_data:
                head = i.name.upper().replace("-", "_")
                try:
                    if head == "CONTENT_TYPE":
                        if request.environ[head] != i.value:
                            return Response(status=400)
                    else:
                        if request.environ["HTTP_"+head] != i.value:
                            return Response(status=400)
                except KeyError:
                    return Response(status=400)
        param = ApiParameter.objects.filter(api=obj)
        if len(param):
            for j in param:
                if j.required:
                    if request.GET.get(j.name) is None:
                        return Response(status=400)

        return Response(json.loads(obj.data), status=obj.mockCode)

    def post(self, request, apiAdr=None):
        """
        post请求
        :param request:
        :param apiAdr:
        :return:
        """
        url = "/"+apiAdr
        try:
            obj = ApiInfo.objects.get(apiAddress=url, mockStatus=True)
        except ObjectDoesNotExist:
            return JsonResponse(code="999984", data="未匹配到mock地址或未开启!")
        head_data = ApiHead.objects.filter(api=obj)
        if len(head_data):
            for i in head_data:
                head = i.name.upper().replace("-", "_")
                try:
                    if head == "CONTENT_TYPE":
                        if request.environ[head] != i.value:
                            return Response(status=400)
                    else:
                        if request.environ["HTTP_"+head] != i.value:
                            return Response(status=400)
                except KeyError:
                    return Response(status=400)
        if obj.requestParameterType == "form-data":
            param = ApiParameter.objects.filter(api=obj)
            if len(param):
                for j in param:
                    if j.required:
                        if request.POST.get(j.name) is None:
                            return Response(status=400)
        else:
            param = ApiParameterRaw.objects.filter(api=obj)
            if len(param):
                data = JSONParser().parse(request)
                result = check_json(data, json.loads(param[0].data))
                if result == "fail":
                    return Response(status=400)

        return Response(json.loads(obj.data), status=obj.mockCode)


class LeadSwagger(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["url"]:
                return JsonResponse(code="999996", msg="参数有误!")
            if not isinstance(data["project_id"], int):
                return JsonResponse(code="999996", msg="参数有误!")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误!")

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
            pro_data = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and pro_data.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在!")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            swagger_api(data["url"], data["project_id"], request.user)
            return JsonResponse(code="999999", msg="成功!")
        except Exception as e:
            logging.exception(e)
            return JsonResponse(code="999998", msg="失败!")


class UpdateApi(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

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
                return JsonResponse(code="999996", msg="参数有误!")
            if data["status"] not in [True, False]:
                return JsonResponse(code="999996", msg="参数有误!")
            if not isinstance(data["project_id"], int) or not isinstance(data["id"], int):
                return JsonResponse(code="999996", msg="参数有误!")
            if data["httpType"] not in ["HTTP", "HTTPS"]:
                return JsonResponse(code="999996", msg="参数有误!")
            if data["requestType"] not in ["POST", "GET", "PUT", "DELETE"]:
                return JsonResponse(code="999996", msg="参数有误!")
            if data["requestParameterType"] not in ["form-data", "raw", "Restful"]:
                return JsonResponse(code="999996", msg="参数有误!")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误!")

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
            pro_data = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and pro_data.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在!")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        api_name = ApiInfo.objects.filter(name=data["name"], project=data["project_id"]).exclude(id=data["id"])
        if len(api_name):
            return JsonResponse(code="999997", msg="存在相同名称!")
        try:
            obi = ApiInfo.objects.get(id=data["id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999990", msg="接口不存在!")
        with transaction.atomic():
            serialize = ApiInfoDeserializer(data=data)
            if serialize.is_valid():
                data["userUpdate"] = request.user
                try:
                    if not isinstance(data.get("apiGroupLevelFirst_id"), int):
                        return JsonResponse(code="999996", msg="参数有误!")
                    ApiGroupLevelFirst.objects.get(id=data["apiGroupLevelFirst_id"], project=data["project_id"])
                    User.objects.get(id=request.user.pk)
                    serialize.update(instance=obi, validated_data=data)
                except KeyError:
                    User.objects.get(id=request.user.pk)
                    serialize.update(instance=obi, validated_data=data)
                except ObjectDoesNotExist:
                    return JsonResponse(code="999991", msg="分组不存在!")
                header = Q()
                if len(data.get("headDict")):
                    for i in data["headDict"]:
                        if i.get("api") and i.get("id"):
                            header = header | Q(id=i["id"])
                            if i["name"]:
                                head_serialize = ApiHeadDeserializer(data=i)
                                if head_serialize.is_valid():
                                    i["api"] = ApiInfo.objects.get(id=i["api"])
                                    head_serialize.update(instance=ApiHead.objects.get(id=i["id"]), validated_data=i)
                        else:
                            if i.get("name"):
                                i["api"] = data['id']
                                head_serialize = ApiHeadDeserializer(data=i)
                                if head_serialize.is_valid():
                                    head_serialize.save(api=ApiInfo.objects.get(id=data["id"]))
                                    header = header | Q(id=head_serialize.data.get("id"))
                ApiHead.objects.exclude(header).filter(api=data["id"]).delete()
                api_param = Q()
                api_param_raw = Q()
                if len(data.get("requestList")):
                    if data["requestParameterType"] == "form-data":
                        ApiParameterRaw.objects.filter(api=data["id"]).delete()
                        for i in data["requestList"]:
                            if i.get("api") and i.get("id"):
                                api_param = api_param | Q(id=i["id"])
                                if i["name"]:
                                    param_serialize = ApiParameterDeserializer(data=i)
                                    if param_serialize.is_valid():
                                        i["api"] = ApiInfo.objects.get(id=i["api"])
                                        param_serialize.update(instance=ApiParameter.objects.get(id=i["id"]),
                                                               validated_data=i)
                            else:
                                if i.get("name"):
                                    i["api"] = data['id']
                                    param_serialize = ApiParameterDeserializer(data=i)
                                    if param_serialize.is_valid():
                                        param_serialize.save(api=ApiInfo.objects.get(id=data["id"]))
                                        api_param = api_param | Q(id=param_serialize.data.get("id"))
                    else:
                        try:
                            obj = ApiParameterRaw.objects.get(api=data["id"])
                            obj.data = data["requestList"]
                            obj.save()
                        except ObjectDoesNotExist:
                            obj = ApiParameterRaw(api=ApiInfo.objects.get(id=data['id']), data=data["requestList"])
                            obj.save()
                        api_param_raw = api_param_raw | Q(id=obj.id)
                ApiParameter.objects.exclude(api_param).filter(api=data["id"]).delete()
                ApiParameterRaw.objects.exclude(api_param_raw).filter(api=data["id"]).delete()
                api_response = Q()
                if len(data.get("responseList")):
                    for i in data["responseList"]:
                        if i.get("api") and i.get("id"):
                            api_response = api_response | Q(id=i["id"])
                            if i["name"]:
                                response_serialize = ApiResponseDeserializer(data=i)
                                if response_serialize.is_valid():
                                    i["api"] = ApiInfo.objects.get(id=i["api"])
                                    response_serialize.update(instance=ApiResponse.objects.get(id=i["id"]),
                                                              validated_data=i)
                        else:
                            if i.get("name"):
                                i["api"] = data['id']
                                response_serialize = ApiResponseDeserializer(data=i)
                                if response_serialize.is_valid():
                                    response_serialize.save(api=ApiInfo.objects.get(id=data["id"]))
                                    api_response = api_response | Q(id=response_serialize.data.get("id"))
                ApiResponse.objects.exclude(api_response).filter(api=data["id"]).delete()
                record_dynamic(project=data["project_id"],
                               _type="修改", operationObject="接口", user=request.user.pk,
                               data="修改接口“%s”" % data["name"])
                api_record = ApiOperationHistory(api=ApiInfo.objects.get(id=data['id']),
                                                 user=User.objects.get(id=request.user.pk),
                                                 description="修改接口\"%s\"" % data["name"])
                api_record.save()
                return JsonResponse(code="999999", msg="成功!")
            return JsonResponse(code="999996", msg="参数有误!")


class DelApi(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["ids"]:
                return JsonResponse(code="999996", msg="参数有误!")
            if not isinstance(data["project_id"], int) or not isinstance(data["ids"], list):
                return JsonResponse(code="999996", msg="参数有误!")
            for i in data["ids"]:
                if not isinstance(i, int):
                    return JsonResponse(code="999996", msg="参数有误!")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误!")

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
            pro_data = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and pro_data.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在!")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
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
            return JsonResponse(code="999999", msg="成功!")


class UpdateGroup(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["ids"] or not data["apiGroupLevelFirst_id"]:
                return JsonResponse(code="999996", msg="参数有误!")
            if not isinstance(data["project_id"], int) or not isinstance(data["ids"], list) \
                    or not isinstance(data["apiGroupLevelFirst_id"], int):
                return JsonResponse(code="999996", msg="参数有误!")
            for i in data["ids"]:
                if not isinstance(i, int):
                    return JsonResponse(code="999996", msg="参数有误!")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误!")

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
            pro_data = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and pro_data.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在!")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
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
            return JsonResponse(code="999999", msg="成功!")


class ApiInfoDetail(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request):
        """
        获取接口详情
        :return:
        """
        project_id = request.GET.get("project_id")
        api_id = request.GET.get("api_id")
        if not project_id or not api_id:
            return JsonResponse(code="999996", msg="参数有误!")
        if not project_id.isdecimal() or not api_id.isdecimal():
            return JsonResponse(code="999996", msg="参数有误!")
        try:
            pro_data = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在!")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            obi = ApiInfo.objects.get(id=api_id, project=project_id)
            serialize = ApiInfoSerializer(obi)
            return JsonResponse(data=serialize.data, code="999999", msg="成功!")
        except ObjectDoesNotExist:
            return JsonResponse(code="999990", msg="接口不存在!")


class AddHistory(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["api_id"] or not data["requestType"] \
                    or not data["requestAddress"] or not data["httpCode"]:
                return JsonResponse(code="999996", msg="参数有误!")
            if not isinstance(data["project_id"], int) or not isinstance(data["api_id"], int):
                return JsonResponse(code="999996", msg="参数有误!")
            if data["requestType"] not in ["POST", "GET", "PUT", "DELETE"]:
                return JsonResponse(code="999996", msg="参数有误!")
            if data["httpCode"] not in [200, 404, 400, 502, 500, 302]:
                return JsonResponse(code="999996", msg="参数有误!")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误!")

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
            pro_data = Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在!")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            obj = ApiInfo.objects.get(id=data["api_id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999990", msg="接口不存在!")
        serialize = APIRequestHistoryDeserializer(data=data)
        if serialize.is_valid():
            serialize.save(api=obj)
            return JsonResponse(code="999999", msg="成功!")
        return JsonResponse(code="999998", msg="失败!")


class HistoryList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

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
            return JsonResponse(code="999996", msg="参数有误!")
        try:
            pro_data = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在!")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            obj = ApiInfo.objects.get(id=api_id, project=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999990", msg="接口不存在!")
        history = APIRequestHistory.objects.filter(api=obj).order_by("-requestTime")[:10]
        data = APIRequestHistorySerializer(history, many=True).data
        return JsonResponse(data=data, code="999999", msg="成功!")


class DelHistory(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["api_id"] or not data["id"]:
                return JsonResponse(code="999996", msg="参数有误!")
            if not isinstance(data["project_id"], int) or not isinstance(data["api_id"], int) or not isinstance(data["id"], int):
                return JsonResponse(code="999996", msg="参数有误!")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误!")

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
            pro_data = Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在!")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            obj = ApiInfo.objects.get(id=data["api_id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999990", msg="接口不存在!")
        obm = APIRequestHistory.objects.filter(id=data["id"], api=data["api_id"])
        if obm:
            obm.delete()
            api_record = ApiOperationHistory(api=obj,
                                             user=User.objects.get(id=request.user.pk),
                                             description="删除请求历史记录")
            api_record.save()
            return JsonResponse(code="999999", msg="成功!")
        else:
            return JsonResponse(code="999988", msg="请求历史不存在!")


class OperationHistory(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

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
            return JsonResponse(code="999985", msg="page and page_size must be integer!")
        project_id = request.GET.get("project_id")
        api_id = request.GET.get("api_id")
        if not project_id or not api_id:
            return JsonResponse(code="999996", msg="参数有误!")
        if not project_id.isdecimal() or not api_id.isdecimal():
            return JsonResponse(code="999995", msg="参数有误!")
        try:
            pro_data = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在!")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            ApiInfo.objects.get(id=api_id, project=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999990", msg="接口不存在!")
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
                                  }, code="999999", msg="成功!")


class DownLoad(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request):
        """
        获取Api下载文档路径
        :param request:
        :return:
        """
        project_id = request.GET.get("project_id")
        try:
            if not project_id.isdecimal():
                return JsonResponse(code="999996", msg="参数有误!")
        except AttributeError:
            return JsonResponse(code="999996", msg="参数有误！")
        try:
            obj = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在!")
        pro_data = ProjectSerializer(obj)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        obi = ApiGroupLevelFirst.objects.filter(project=project_id)
        data = ApiInfoDocSerializer(obi, many=True).data
        obn = ApiInfoSerializer(ApiInfo.objects.filter(project=project_id), many=True).data
        url = Write().write_api(str(obj), group_data=data, data=obn)
        return JsonResponse(code="999999", msg="成功!", data=url)


def download_doc(request):
    url = request.GET.get("url")
    format_doc = url.split(".")
    if format_doc[-1] == "docx":
        file_name = str(int(time.time())) + ".docx"
    else:
        file_name = str(int(time.time())) + ".xlsx"

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
