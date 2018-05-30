import django
import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
PathProject = os.path.split(rootPath)[0]
sys.path.append(rootPath)
sys.path.append(PathProject)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_automation_test.settings")
django.setup()

import itchat
from api_test.models import Robot
import sys


def test_connect_wechat(data, name, _type):
    """
    测试连接微信
    :param data: 发送内容
    :param name: 发送目标人
    :param _type: 群或个人 group/person
    :return:
    """
    itchat.auto_login(hotReload=True)
    user = itchat.get_friends()
    nickName = user[:1][0]["NickName"]
    obi = Robot.objects.filter(robotType='WX')
    if obi:
        obi.update(nickName=nickName, role_type=_type, name=name)
    else:
        Robot(nickName=nickName, role_type=_type, name=name, robotType="WX").save()
    if _type == "group":
        users = itchat.search_chatrooms(name=name)
    else:
        users = itchat.search_friends(name=name)
    if len(users):
        use_name = users[0]['UserName']
        itchat.send(data, toUserName=use_name)


if __name__ == "__main__":
    test_connect_wechat(sys.argv[1], sys.argv[2], sys.argv[3])
