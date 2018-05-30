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
import os


def logout_wechat():
    """
    退出微信
    :return:
    """
    itchat.auto_login(hotReload=True)
    commond = "rm -rf %s/itchat.pkl" % os.getcwd()
    os.system(commond)
    itchat.logout()
    return True


if __name__ == '__main__':
    logout_wechat()
