import logging

import requests
from django.contrib.auth.models import User

from api_test.common.common import record_dynamic
from api_test.models import Project, ApiInfo, ApiHead, ApiParameter, ApiParameterRaw, ApiResponse, ApiOperationHistory
from django.db import transaction

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。

def swagger_api(url, project, user):
    """
    请求swagger地址，数据解析
    :param url: swagger地址
    :param project: 项目ID
    :param user: 用户model
    :return:
    """
    req = requests.get(url)
    data = req.json()
    apis = data["paths"]
    params = data["definitions"]
    for api, m in apis.items():
        requestApi = {"project_id": project, "status": True, "mockStatus": "200", "code": "", "desc": "", "httpType": "HTTP",
                      "responseList": []}
        requestApi["address"] = api
        for requestType, data in m.items():
            requestApi["requestType"] = requestType.upper()
            requestApi["name"] = data["summary"]
            if data["consumes"][0] == "application/json":
                requestApi["requestParameterType"] = "raw"
            else:
                requestApi["requestParameterType"] = "form-data"
            requestApi["headDict"] = [{"name": "Content-Type", "value": data["consumes"][0]}]
            for j in data["parameters"]:
                if j["in"] == "header":
                    requestApi["headDict"].append({"name": j["name"].title(), "value": "String"})
                elif j["in"] == "body":
                    dto = j["name"][:1].upper() + j["name"][1:]
                    try:
                        if requestApi["requestParameterType"] == "raw":
                            parameter = {}
                            for key, value in params[dto]["properties"].items():
                                parameter[key] = value['type']
                                requestApi["requestList"] = str(parameter)
                        else:
                            parameter = []
                            for key, value in params[dto]["properties"].items():
                                parameter.append({"name": key, "value": value["type"], "_type": value["tyep"],
                                                  "required": True, "restrict": "", "description": ""})
                            requestApi["requestList"] = parameter
                        # print(requestApi)
                        add_swagger_api(requestApi, user)
                    except:
                        pass


def add_swagger_api(data, user):
    """
    swagger接口写入数据库
    :param data:  json数据
    :param user:  用户model
    :return:
    """
    obj = Project.objects.filter(id=data["project_id"])
    if obj:
        try:
            with transaction.atomic():
                oba = ApiInfo(project=Project.objects.get(id=data["project_id"]),
                              name=data["name"], httpType=data["httpType"], status=data["status"],
                              requestType=data["requestType"], apiAddress=data["address"],
                              requestParameterType=data["requestParameterType"],
                              mockCode=data["mockStatus"], data=data["code"],
                              userUpdate=User.objects.get(id=user.pk), description=data["desc"])
                oba.save()
                if len(data["headDict"]):
                    for i in data["headDict"]:
                        try:
                            if i["name"]:
                                ApiHead(api=ApiInfo.objects.get(id=oba.pk), name=i["name"],
                                        value=i["value"]).save()
                        except KeyError:
                            logging.exception("Error")
                if data["requestParameterType"] == "form-data":
                    if len(data["requestList"]):
                        for i in data["requestList"]:
                            try:
                                # i = i.replace("true", "True").replace("false", "False")
                                if i["name"]:
                                    ApiParameter(api=ApiInfo.objects.get(id=oba.pk), name=i["name"],
                                                 value=i["value"], required=i["required"],
                                                 _type=i["_type"],
                                                 restrict=i["restrict"],
                                                 description=i["description"]).save()
                            except KeyError:
                                logging.exception("Error")
                else:
                    if len(data["requestList"]):
                        _data = data["requestList"].replace("\'", "\"")
                        ApiParameterRaw(api=ApiInfo.objects.get(id=oba.pk), data=_data).save()
                if len(data["responseList"]):
                    for i in data["responseList"]:
                        try:
                            # i = i.replace("true", "True").replace("false", "False")
                            if i["name"]:
                                ApiResponse(api=ApiInfo.objects.get(id=oba.pk), name=i["name"],
                                            value=i["value"], required=i["required"], _type=i["_type"],
                                            description=i["description"]).save()
                        except KeyError:
                            logging.exception("Error")
                record_dynamic(data["project_id"], "新增", "接口", "新增接口“%s”" % data["name"])
                api_record = ApiOperationHistory(apiInfo=ApiInfo.objects.get(id=oba.pk),
                                                 user=User.objects.get(id=user.pk),
                                                 description="新增接口\"%s\"" % data["name"])
                api_record.save()
        except Exception as e:
            logging.exception("error")
            logging.error(e)
