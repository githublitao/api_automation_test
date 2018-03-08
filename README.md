# 接口测试平台从开始到放弃
第一次学习做的项目，有许多不足，望各位大神佐证<br>
本系统采用Python的Django Web框架，因开始打算由前端写页面，本人只负责写后台，所以使用的是前后端分离，后来还是由本人自己写前端页面<br>
目前并未开发完成，核心部分API管理和自动化测试前端页面未完成<br>

系统声明：
---
1.本系统采用Django REST framework编写接口，前端页面采用比较容易上手的vue+elementUI<br>
2.初步学习web开发，接口统一采用基于方法的方式编写，后续引入权限系统，并修改成基于类的方法<br>
<br>
使用方法：
---
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

项目讲解：
----
1.登录页面，只提供了登录方法，并没有注册和忘记密码功能，账号由后台管理系统直接创建分配<br>
![登录页面](https://github.com/githublitao/api_automation_test/blob/master/img/%E7%99%BB%E5%BD%95%E9%A1%B5%E9%9D%A2.png)<br>
2.目前只开放了接口测试，所有只有项目列表页面，可完成项目的新增，删除，查询，修改，批量删除<br>
![首页](https://github.com/githublitao/api_automation_test/blob/master/img/%E9%A6%96%E9%A1%B5.png)<br>
3.点击项目名称后，进入项目概况界面，总的展示一些项目的基本情况<br>
![项目概况](https://github.com/githublitao/api_automation_test/blob/master/img/%E9%A1%B9%E7%9B%AE%E6%A6%82%E5%86%B5.png)<br>
4.HOST配置页面，提供了，增删改查，批量修改HOST，作为执行自动化测试时的全局变量<br>
![HOST配置](https://github.com/githublitao/api_automation_test/blob/master/img/HOST%E9%85%8D%E7%BD%AE.png)<br>
5.API页面，可执行快速测试，类似于postman，新增修改删除接口分组，新增修改删除项目接口，后续计划根据输入的接口搭建mockserver和下载接口文档<br>
![API页面](https://github.com/githublitao/api_automation_test/blob/master/img/API%E5%88%97%E8%A1%A8.png)<br>
6.自动化测试页面，实现自动化用例的分组，增删改查用例，并添加自动化定时任务定时任务<br>
![自动化测试页面]()<br>
7.项目成员，目前只是一个展示项目组成员，后续引入权限系统，分配权限角色<br>
![项目成员](https://github.com/githublitao/api_automation_test/blob/master/img/%E6%88%90%E5%91%98%E7%AE%A1%E7%90%86.png)<br>
8.展示项目三天内的动态情况<br>
![项目动态](https://github.com/githublitao/api_automation_test/blob/master/img/%E9%A1%B9%E7%9B%AE%E5%8A%A8%E6%80%81.png)<br>

