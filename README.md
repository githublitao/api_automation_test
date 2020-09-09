# 接口测试平台从开始到放弃
# python3.6.3 Django 2.0.2框架
体验地址：http://120.79.232.23  请体验用户不要删除已有数据<br>

# 版本更新：
## v2.3<br>
引入docker部署,由于采用的docker，基础镜像为centos，所以Windows下部署仍然可以使用定时任务
```
 docker-compose up
```
## v2.2<br>
1.新增钉钉登录<br>
```
1.先在钉钉开发平台上创建账号<br>
2.替换dingConfig.py里的appid和APPSECRET<br>
3.修改前段login.vue里的回调地址<br>
  ```
## V2.1.2<br>
1.增加导出测试用例功能<br>
## V2.1.1<br>
1.新增swaggerUI界面，访问地址127.0.0.1:8000/docs/<br>
## V2.1<br>
1.优化前端代码，适配屏幕分辨率，未做浏览器兼容性，目前只在chrome上浏览正常<br>
2.新增mock功能，api管理模块可启动，关闭mock，启动后，通过访问http://127.0.0.1:8000/mock/+真实url，可返回mock信息
## V2.0<br>
重构接口代码，引入反序列化方式，修改接口为基于类的方式，因修改大量后台接口代码，前端未更新，所以目前前端调用接口会出现大量问题，目前平台暂不可用，后续更新

## 系统声明：
---
1.本系统采用Django REST framework编写接口，前端页面采用比较容易上手的vue+elementUI<br>
2.初步学习web开发，接口统一采用基于方法的方式编写，后续引入权限系统，并修改成基于类的方法<br></br>

## 使用方法：
---
### 1.安装Python3环境（未在Python2上运行后，不知道有没有问题）<br>
### 2.下载代码到本地并解压<br>
### 3.cmd到根目录下安装相关依赖包<br>
```bash
pip install -r requirements.txt<br>
pip install https://github.com/darklow/django-suit/tarball/v2
```
### 4.安装mysql数据库，配置数据库连接，进入api_automation_test/settings.py<br>
```python
DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE':'django.db.backends.mysql',     # 数据库类型，mysql
        'NAME':'api_test',            #  database名
        'USER':'root',               # 登录用户
        'PASSWORD':'123456',        #  登录用户名
        'HOST':'127.0.0.1',        # 数据库地址
        'PORT':'3306'              # 数据库端口
    }
}
```
### 5.cmd到根目录下，让 Django 知道我们在我们的模型有一些变更<br>
```bash
python manage.py makemigrations
```
### 6.创造或修改表结构<br>
```bash
python manage.py migrate 
```
### 7.创建超级用户，用于登录后台管理<br>
```bash
python manage.py createsuperuser
```
### 8.安装VUE环境，下载node.js并配置环境，下载npm包管理器<br>
### 9.cmd进入frontend目录下，运行npm install安装相关依赖包<br>
### 10.打包<br>
```bash
npm run build
```
### 11.运行启动django服务<br>
```bash
python manage.py runserver 0.0.0.0:8000
```
### 12.现在就可以访问 http://127.0.0.1:8000/login 进行登录， http://127.0.0.1:8000/admin 为后台管理平台<br>
## 微信打赏：<br>
![微信打赏](https://github.com/githublitao/api_automation_test/blob/master/img/%E6%94%B6%E6%AC%BE%E7%A0%81.png)<br>
<br>
## 系统图解：<br>
![系统图](https://github.com/githublitao/api_automation_test/blob/master/img/%E7%B3%BB%E7%BB%9F%E5%9B%BE%E8%A7%A3.png)<br>
<br>
项目讲解：
----
1、登录页面，只提供了登录方法，并没有注册和忘记密码功能，账号由后台管理系统直接创建分配<br>
![登录页面](https://github.com/githublitao/api_automation_test/blob/master/img/%E7%99%BB%E5%BD%95%E9%A1%B5%E9%9D%A2.png)<br>
<br>
2、目前只开放了接口测试，所有只有项目列表页面，可完成项目的新增，删除，查询，修改，批量删除<br>
![首页](https://github.com/githublitao/api_automation_test/blob/master/img/%E9%A6%96%E9%A1%B5.png)<br>
<br>
3、新增项目<br>
![新增项目](https://github.com/githublitao/api_automation_test/blob/master/img/%E6%96%B0%E5%A2%9E%E9%A1%B9%E7%9B%AE.png)<br>
<br>
4、点击项目名称后，进入项目概况界面，总的展示一些项目的基本情况<br>
![项目概况](https://github.com/githublitao/api_automation_test/blob/master/img/%E9%A1%B9%E7%9B%AE%E6%A6%82%E5%86%B5.png)<br>
<br>
5、HOST配置页面，提供了，增删改查，批量修改HOST，作为执行自动化测试时的全局变量<br>
![HOST配置](https://github.com/githublitao/api_automation_test/blob/master/img/HOST%E9%85%8D%E7%BD%AE.png)<br>
<br>
6、新增Host<br>
![新增Host](https://github.com/githublitao/api_automation_test/blob/master/img/%E6%96%B0%E5%A2%9EHost.png)<br>
<br>
7、API页面，可执行快速测试，类似于postman，新增修改删除接口分组，新增修改删除项目接口，后续计划根据输入的接口搭建mockserver和下载接口文档<br>
![API页面](https://github.com/githublitao/api_automation_test/blob/master/img/API%E5%88%97%E8%A1%A8.png)<br>
<br>
8、快速测试界面，类似于postman的功能，后续怎么json格式显示的样式<br>
![快速测试界面](https://github.com/githublitao/api_automation_test/blob/master/img/%E5%BF%AB%E9%80%9F%E6%B5%8B%E8%AF%95.png)<br><br>
9、新增接口分组，用于按模块对接口进行分类，更好的管理接口<br>
![新增接口分组](https://github.com/githublitao/api_automation_test/blob/master/img/%E6%96%B0%E5%A2%9E%E5%88%86%E7%BB%84.png)<br><br>
10、新增API，用户可新增的API，目前只支持源数据格式和form-data格式<br>
![新增API](https://github.com/githublitao/api_automation_test/blob/master/img/%E6%96%B0%E5%A2%9EAPI.png)<br><br>
11、接口详情界面，查看接口基本内容，可对接口进行测试，修改，删除，查看接口历史动态<br>
![接口详情界面](https://github.com/githublitao/api_automation_test/blob/master/img/%E6%8E%A5%E5%8F%A3%E8%AF%A6%E6%83%85.png)<br>
12、下载的接口文档模板<br><br>
![接口文档](https://github.com/githublitao/api_automation_test/blob/master/img/%E6%8E%A5%E5%8F%A3%E6%96%87%E6%A1%A3%E6%A8%A1%E5%9D%97.png)<br><br>
13、自动化测试页面，实现自动化用例的分组，增删改查用例，并添加自动化定时任务定时任务<br>
![自动化测试页面](https://github.com/githublitao/api_automation_test/blob/master/img/%E7%94%A8%E4%BE%8B%E5%88%97%E8%A1%A8.png)<br><br>
14、新增测试用例<br>
![新增测试用例](https://github.com/githublitao/api_automation_test/blob/master/img/%E6%96%B0%E5%A2%9E%E7%94%A8%E4%BE%8B.png)<br><br>
15、用例下的接口列表，可添加用例接口，选择不同的环境测试接口，以及下载测试报告和设置定时任务<br>
![用例下的接口列表](https://github.com/githublitao/api_automation_test/blob/master/img/%E7%94%A8%E4%BE%8B%E5%88%97%E8%A1%A8.png)<br><br>
16、用例下添加已有的接口，可添加在api模块中，已添加的接口，默认校验方式为不校验<br>
![用例下添加已有的接口](https://github.com/githublitao/api_automation_test/blob/master/img/%E6%B7%BB%E5%8A%A0%E7%94%A8%E4%BE%8B%E4%B8%8B%E5%B7%B2%E6%9C%89%E7%9A%84%E6%8E%A5%E5%8F%A3.png)<br><br>
17、项目成员，只做一个展示项目组成员页面，成员添加删除由后台管理操作，后续引入权限系统，分配权限角色<br>
![项目成员](https://github.com/githublitao/api_automation_test/blob/master/img/%E6%88%90%E5%91%98%E7%AE%A1%E7%90%86.png)<br>
<br>
18、展示项目三天内的动态情况<br>
![项目动态](https://github.com/githublitao/api_automation_test/blob/master/img/%E9%A1%B9%E7%9B%AE%E5%8A%A8%E6%80%81.png)<br>
<br>
18、自动化测试生成的报告，保留最近10次测试结果<br>
![自动化测试报告](https://github.com/githublitao/api_automation_test/blob/master/img/%E8%87%AA%E5%8A%A8%E5%8C%96%E6%B5%8B%E8%AF%95%E6%8A%A5%E5%91%8A.png)<br>
<br>
20、退出登录，跳转至登录页面<br>
![退出登录](https://github.com/githublitao/api_automation_test/blob/master/img/%E9%80%80%E5%87%BA%E7%99%BB%E5%BD%95.png)<br>
<br>
21、后台管理页面，主要用作数据管理，及项目人员添加删除<br>
![后台管理](https://github.com/githublitao/api_automation_test/blob/master/img/%E5%90%8E%E5%8F%B0%E7%AE%A1%E7%90%86%E9%A1%B5%E9%9D%A2.png)
