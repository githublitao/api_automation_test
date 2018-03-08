# 接口测试平台从开始到放弃
第一次学习做的项目，有许多不足，望各位大神佐证<br>
本系统采用Python的Django Web框架，因开始打算由前端写页面，本人只负责写后台，所以使用的是前后端分离，后来还是由本人自己写前端页面<br>
目前并未开发完成，核心部分API管理和自动化测试前端页面未完成<br>

系统声明：
---
1.本系统采用Django REST framework编写接口，前端页面采用比较容易上手的vue+elementUI<br>
2.初步学习web开发，接口统一采用基于方法的方式编写，后续引入权限系统，并修改成基于类的方法<br>
         
使用方法：
1.安装Python3环境（未在Python2上运行后，不知道有没有问题）<br>
2.下载代码到本地并解压<br>
3.cmd到根目录下pip install -r requirements.txt安装相关依赖包<br>
4.安装mysql数据库，配置数据库连接，进入api_automation_test/settings.py<br>
![数据库配置](https://github.com/githublitao/api_automation_test/blob/master/img/%E6%95%B0%E6%8D%AE%E5%BA%93%E9%85%8D%E7%BD%AE.png)<br>
5.cmd到根目录下python manage.py makemigrations 让 Django 知道我们在我们的模型有一些变更<br>
6.python manage.py migrate 创造或修改表结构<br>
7.python manage.py createsuperuser创建超级用户，用于登录后台管理<br>
8.安装VUE环境，下载node.js并配置环境，下载npm包管理器，安装vue脚手架 npm install --global vue-cli  用于生成vue工程模板<br>
9.cmd进入frontend目录下，运行npm install安装相关依赖包<br>
10.npm run build打包<br>
11.运行python manage.py runserver 0.0.0.0:8001 启动django服务<br>
12.现在就可以访问http://127.0.0.1:8001/login进行登录， http://127.0.0.1:8001/admin为后台管理平台<br>

##项目讲解：
