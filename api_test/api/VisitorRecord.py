import logging

import requests
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.common.api_response import JsonResponse
from api_test.models import VisitorsRecord

logger = logging.getLogger(__name__) # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


class Record(APIView):
    # authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 必传参数 success
            if data["success"] not in [0, 1]:
                return JsonResponse(code="999996", msg="参数有误！")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误！")

    def ip_get_city(self, ip):
        """
        通过ip获取城市信息
        :param ip:
        :return:
        """
        params = {
            "output": "json",
            # "location": "104.06151"+","+"30.54852",
            "key": "2200d7985fd43582411687abaa5b01eb",
            "ip": ip
        }
        headers = {"Content-Type": "application/json;charset=utf-8"}
        response = requests.get(url="http://restapi.amap.com/v3/ip",
                                params=params, headers=headers, allow_redirects=False,
                                timeout=8)
        if response.status_code == 301:
            response = requests.get(url=response.headers["location"])
        return response.json()

    def post(self, request):
        """
        记录访客
        :param request:
        :return:
        """
        if request.environ["REMOTE_ADDR"] == "127.0.0.1":
            return JsonResponse(code="999999", msg="成功！")
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        if data["success"] == 0:
            ip = self.ip_get_city(request.environ["REMOTE_ADDR"])
            VisitorsRecord(formattedAddress=request.environ["REMOTE_ADDR"], province=ip["province"],
                           city=ip["city"],
                           success="失败", reason="获取用户经纬度失败！").save()
        else:
            try:
                longitude = data["longitude"]
                latitude = data["latitude"]
            except KeyError:
                return JsonResponse(code="999996", msg="参数有误")
            params = {
                "output": "json",
                # "location": "104.06151"+","+"30.54852",
                "key": "2200d7985fd43582411687abaa5b01eb",
                "location": str(longitude)+","+str(latitude)
                      }
            headers = {"Content-Type": "application/json;charset=utf-8"}
            response = requests.get(url="http://restapi.amap.com/v3/geocode/regeo",
                                    params=params, headers=headers, allow_redirects=False,
                                    timeout=8)
            if response.status_code == 301:
                response = requests.get(url=response.headers["location"])
            try:
                visitor_addr = response.json()
                if visitor_addr["status"] == "1":
                    VisitorsRecord(
                        formattedAddress=visitor_addr["regeocode"]["formatted_address"],
                        country=visitor_addr["regeocode"]["addressComponent"]["country"],
                        province=visitor_addr["regeocode"]["addressComponent"]["province"],
                        city=visitor_addr["regeocode"]["addressComponent"]["city"],
                        district=visitor_addr["regeocode"]["addressComponent"]["district"],
                        township=visitor_addr["regeocode"]["addressComponent"]["township"],
                        street=visitor_addr["regeocode"]["addressComponent"]["streetNumber"]["street"],
                        number=visitor_addr["regeocode"]["addressComponent"]["streetNumber"]["number"],
                        success="成功",
                        reason=visitor_addr["info"]
                    ).save()
                else:
                    ip = self.ip_get_city(request.environ["REMOTE_ADDR"])
                    VisitorsRecord(formattedAddress=request.environ["REMOTE_ADDR"], province=ip["province"],
                                   city=ip["city"],
                                   success="失败", reason=ip["info"]).save()
            except Exception as e:
                ip = self.ip_get_city(request.environ["REMOTE_ADDR"])
                VisitorsRecord(formattedAddress=request.environ["REMOTE_ADDR"], province=ip["province"],
                               city=ip["city"],
                               success="失败", reason=e).save()

        return JsonResponse(code="999999", msg="成功！")

