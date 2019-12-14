<template>
    <div class="homeBox">
        <ul class="tyg-div">
            <li>让</li>
            <li><div style="margin-left:20px;">测</div></li>
            <li><div style="margin-left:40px;">试</div></li>
            <li><div style="margin-left:60px;">变</div></li>
            <li><div style="margin-left:80px;">得</div></li>
            <li><div style="margin-left:100px;">轻</div></li>
            <li><div style="margin-left:120px;">松</div></li>
        </ul>
        <div style="width:32%;height: auto;margin-left: 30%">
            <div class="title0">自动化测试平台</div>
            <div class="title1">项目管理、接口管理、用例管理、测试报告、任务设置</div>
            <div class="lun-container">
                <div class="carouse" id="carouse">
                    <div class="pic1"><img src="../../assets/page1_0.png" alt="pic1"></div>
                    <div class="pic2"><img src="../../assets/page1_1.png" alt="pic2"></div>
                    <div class="pic3"><img src="../../assets/page1_2.png" alt="pic3"></div>
                </div>
            </div>
            <img class="img-login" src="../../assets/page1_3.jpg"/>
        </div>
        <el-form :model="ruleForm2" :rules="rules2" ref="ruleForm2" label-position="left" label-width="0px" class="demo-ruleForm login-container">
            <h3 class="title">系统登录</h3>
            <el-tabs v-model="activeName" @tab-click="handleClick" :stretch="true">
                <el-tab-pane label="钉钉登录" name="first">
                    <div id="login_container"></div>
                </el-tab-pane>
                <el-tab-pane label="账号登录" name="second">
                    <el-form-item prop="account">
                        <el-input type="text" v-model.trim="ruleForm2.account" auto-complete="off" placeholder="账号"></el-input>
                    </el-form-item>
                    <el-form-item prop="checkPass">
                        <el-input type="password" v-model.trim="ruleForm2.checkPass" auto-complete="off" placeholder="密码"></el-input>
                    </el-form-item>
                    <el-checkbox v-model="checked" checked class="remember">记住密码</el-checkbox>
                    <el-form-item style="width:100%;">
                        <el-button type="primary" style="width:100%;" @click.native.prevent="handleSubmit2" :loading="logining">登录</el-button>
                        <!--<el-button @click.native.prevent="handleReset2">重置</el-button>-->
                    </el-form-item>
                </el-tab-pane>
            </el-tabs>
        </el-form>
    </div>
</template>

<script>
    /* eslint-disable */
    import {requestLogin, recordVisitor, dingConfig, test, url} from '../../api/api';

    export default {
        data() {
            return {
                activeName: 'first',
                logining: false,
                ruleForm2: {
                    account: '',
                    checkPass: ''
                },
                rules2: {
                    account: [
                        {required: true, message: '请输入账号', trigger: 'blur'}
                        // { validator: validaePass }
                    ],
                    checkPass: [
                        {required: true, message: '请输入密码', trigger: 'blur'}
                        // { validator: validaePass2 }
                    ]
                },
                checked: true
            }
        },
        methods: {
            handleReset2() {
                this.$refs.ruleForm2.resetFields()
            },
            handleSubmit2(ev) {
                var _this = this;
                this.$refs.ruleForm2.validate((valid) => {
                    if (valid) {
                        //_this.$router.replace('/table');
                        this.logining = true;
                        //NProgress.start();
                        var loginParams = {username: this.ruleForm2.account, password: this.ruleForm2.checkPass};
                        requestLogin(loginParams).then(_data => {
                            _this.logining = false;
                            let {msg, code, data} = _data;
                            console.log(_data);
                            if (code === '999999') {
                                sessionStorage.setItem('username', JSON.stringify(data.first_name));
                                sessionStorage.setItem('token', JSON.stringify(data.key));
                                console.log(_this.$route);
                                if (_this.$route.query.url) {
                                    _this.$router.push(_this.$route.query.url);
                                } else {
                                    _this.$router.push('/projectList');
                                }
                            }
                            else {
                                _this.$message.error({
                                    message: msg,
                                    center: true
                                })
                            }
                        });
                    } else {
                        console.log('error submit!!');
                        return false;
                    }
                });
            },
            getVisitor() {
                let self = this;
                var map, geolocation;
                //加载地图，调用浏览器定位服务
                map = new AMap.Map('container', {
                    resizeEnable: true
                });
                map.plugin('AMap.Geolocation', function () {
                    geolocation = new AMap.Geolocation({
                        enableHighAccuracy: true,//是否使用高精度定位，默认:true
                        timeout: 10000,          //超过10秒后停止定位，默认：无穷大
                        buttonOffset: new AMap.Pixel(10, 20),//定位按钮与设置的停靠位置的偏移量，默认：Pixel(10, 20)
                        zoomToAccuracy: true,      //定位成功后调整地图视野范围使定位位置及精度范围视野内可见，默认：false
                        buttonPosition: 'RB'
                    });
                    map.addControl(geolocation);
                    geolocation.getCurrentPosition();
                    console.log(geolocation)
                    AMap.event.addListener(geolocation, 'complete', self.onComplete);//返回定位信息
                    AMap.event.addListener(geolocation, 'error', self.onError);      //返回定位出错信息
                });
            },
            //解析定位结果
            onComplete(data) {
                var str = ['定位成功'];
                str.push('经度：' + data.position.getLng());
                str.push('纬度：' + data.position.getLat());
                console.log(str);
                if (data.accuracy) {
                    str.push('精度：' + data.accuracy + ' 米');
                }//如为IP精确定位结果则没有精度信息
                str.push('是否经过偏移：' + (data.isConverted ? '是' : '否'));
                var param = {
                    "success": 1,
                    "longitude": data.position.getLng(),
                    "latitude": data.position.getLat(),
                };
                recordVisitor(param).then(_data => {
                    let {msg, code, data} = _data;
                    if (code === '999999') {
                        console.log("成功")
                    }
                    else {
                        console.log("失败")
                    }
                });
            },
            //解析定位错误信息
            onError(data) {
                console.log("定位失败");
                var param = {
                    "success": 0,
                };
                recordVisitor(param).then(_data => {
                    let {msg, code, data} = _data;
                    if (code === '999999') {
                        console.log("成功")
                    }
                    else {
                        console.log("失败")
                    }
                });
                // document.getElementById('tip').innerHTML = '定位失败';
            },
            carouselPicture() {
                this.ab(1)
            },
            ab(num) {
                var carouse = document.getElementsByClassName("carouse");
                carouse.item(0).id = 'carouse' + num;
            },
            login_ding() {
                dingConfig({}).then(_data => {
                    let _this = this;
                    let {msg, code, data} = _data;
                    if (code === '999999') {
                        var _url = encodeURIComponent(url+'/#/register');
                        console.log(_url)
                        // var url = encodeURIComponent('http://127.0.0.1:8080/#/register');
                        var goto = encodeURIComponent('https://oapi.dingtalk.com/connect/oauth2/sns_authorize?appid=' + data.app_id + '&response_type=code&scope=snsapi_login&state=STATE&redirect_uri=' + _url);

                        var obj = DDLogin({
                            id: "login_container",//这里需要你在自己的页面定义一个HTML标签并设置id，例如<div id="login_container"></div>或<span id="login_container"></span>
                            goto: goto, //请参考注释里的方式
                            style: "border:none;background-color:#FFFFFF;",
                            width: "300",
                            height: "300"
                        });
                        var handleMessage = function (event) {
                            var origin = event.origin;
                            console.log("origin", event.origin);
                            if (origin === "https://login.dingtalk.com") { //判断是否来自ddLogin扫码事件。
                                var loginTmpCode = event.data; //拿到loginTmpCode后就可以在这里构造跳转链接进行跳转了
                                console.log("loginTmpCode", loginTmpCode);
                                var url2 = 'https://oapi.dingtalk.com/connect/oauth2/sns_authorize?appid='+data.app_id+'&response_type=code&scope=snsapi_login&state=STATE&redirect_uri=' + _url + "&loginTmpCode=" + loginTmpCode;
                                window.location.href = url2;
                            }
                        };
                        if (typeof window.addEventListener !== 'undefined') {
                            window.addEventListener('message', handleMessage, false);
                        } else if (typeof window.attachEvent !== 'undefined') {
                            window.attachEvent('onmessage', handleMessage);
                        }
                    } else {
                        _this.$message.error({
                            message: "服务器钉钉配置错误",
                            center: true
                        })
                    }
                })

            }

        },
        mounted() {
            this.getVisitor();
            this.carouselPicture();
            this.login_ding();
        }
    }

</script>

<style lang="scss" scoped>
    .homeBox {
        position: fixed;
        width: 100%;
        height: 100%;
        top: 0px;
        background-color: #191c2c;
    }
  .login-container {
    /*box-shadow: 0 0px 8px 0 rgba(0, 0, 0, 0.06), 0 1px 0px 0 rgba(0, 0, 0, 0.02);*/
      position: absolute;
    -webkit-border-radius: 5px;
    border-radius: 5px;
    -moz-border-radius: 5px;
    background-clip: padding-box;
    /*margin: 180px auto;*/
      /*margin-top: 10%;*/
      /*right: 50px;*/
    width: 300px;
    padding: 35px 35px 15px 35px;
    background: #eaeaea;
    border: 1px solid #eaeaea;
    box-shadow: 0 0 25px #cac6c6;
      z-index: 1000;
    float: right;
    right: 4%;
    top: 25%;
    .title {
      margin: 0px auto 40px auto;
      text-align: center;
      color: #2ec0f6;
    }
    .remember {
      margin: 0px 0px 35px 0px;
        color: #eaeaea;
    }
  }
    .img-login {
        margin-top: -35%;
        width: 100%;
        height: auto;
    }
    .title0 {
        position: absolute;
        top: 10%;
        left: -41px;
        width: 100%;
        text-align: center;
        color: #2ec0f6;
        font-size: 40px;
        height: 70px;
        line-height: 70px;
        /*<!--margin: -300px 0 0 0;-->*/
        z-index: 1000;
    }
    .title1 {
        position: absolute;
        top: 16%;
        left: -41px;
        width: 100%;
        text-align: center;
        color: #eaeaea;
        font-size: 20px;
        height: 70px;
        line-height: 70px;
        /*<!--margin: -300px 0 0 0;-->*/
        z-index: 1000;
        margin-top: 25px;
    }
    .tyg-div {
        color: #2ec0f6;
        z-index: -1000;
        float: left;
        position: absolute;
        left: 5%;
        top: 20%;
        font-size: 30px;
        list-style-type:none
    }
    .lun-container{
        width: 210px;
        height:140px;
        position: relative;
        font-size: 32px;
        color: #FFFFFF;
        text-align: center;
        line-height: 90px;
        margin: 200px auto;
        margin-bottom: 0px;
        margin-top:48%;
        perspective: 1000px;
        z-index: 1000;
    }
    .carouse{
        transform-style:preserve-3d;

    }
    .carouse div{
        display: block;
        position: absolute;
        width: 140px;
        height: 90px;
    }

    .carouse .pic1{
        transform: rotateY(0deg) translateZ(160px);
    }
    .carouse .pic2{
        transform: rotateY(120deg) translateZ(160px);
    }
    .carouse .pic3{
        transform: rotateY(240deg) translateZ(160px);
    }

    /*=== 下一个动画 ===*/
    @keyframes to-scroll1 {
        0%{
            transform: rotateY(0deg);
        }

        33%{
            transform: rotateY(-120deg);

        }
        66%{
            transform: rotateY(-240deg);

        }
        100%{
            transform: rotateY(-360deg);

        }

    }
    #carouse1{
        animation: to-scroll1  10s ease infinite;
        /*animation-fill-mode: both;*/
    }
</style>
