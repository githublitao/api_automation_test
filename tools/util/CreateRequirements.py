# -*- coding: utf-8 -*-

# @Time    : 2019/11/11 5:53 下午

# @Author  : litao

# @Project : api_automation_test

# @FileName: CreateRequirements.py

# @Software: PyCharm
import os
import sys

from django.core.exceptions import ObjectDoesNotExist

from RootDirectory import PROJECT_PATH
from tools.models import ScriptLibrary


def create_requirements():
    venv_path = PROJECT_PATH + '/static/ShareScript/venv'
    requirements_path = PROJECT_PATH + '/static/ShareScript/requirements.txt'
    if not os.path.exists(venv_path):
        code = os.system('virtualenv {}'.format(venv_path))
        if code == 0:
            library_list = ScriptLibrary.objects.all()
            library = ''
            if len(library_list) > 0:
                for i in library_list:
                    library = library + '{}=={} '.format(i.name, i.version.replace("\n", ""))
            if library:
                if sys.platform == 'darwin':
                    cmd1 = 'source {}\npip3 install {}'.format(venv_path+'/bin/activate', library)
                elif sys.platform == 'linux':
                    cmd1 = 'bash {} {} {}'.format(PROJECT_PATH+"/Config/LibraryInstall.sh", venv_path, library)
                else:
                    cmd1 = 'pip install {}'.format(venv_path + '/bin/activate', library)
                os.system(cmd1)
    if sys.platform == 'darwin':
        cmd = 'source {}\npip3 freeze >{}'.format(venv_path+'/bin/activate', requirements_path)
    elif sys.platform == 'linux':
        cmd = 'bash {} {} {}'.format(PROJECT_PATH+"/Config/VenvInit.sh", venv_path, requirements_path)
    else:
        cmd = 'pip3 freeze >{}'.format(venv_path+'/bin/activate', requirements_path)
    code = os.system(cmd)
    if code == 0:
        with open(requirements_path) as f:
            data = f.readlines()
            if len(data) > 0:
                for n in data:
                    n = n.split("==")
                    try:
                        obj = ScriptLibrary.objects.get(name=n[0])
                        obj.version = n[1]
                        obj.save()
                    except ObjectDoesNotExist:
                        ScriptLibrary(name=n[0], version=n[1].replace("\n", "")).save()


if __name__ == '__main__':
    create_requirements()
