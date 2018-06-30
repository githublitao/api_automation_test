<template>
  <el-form :model="ruleForm2" :rules="rules2" ref="ruleForm2" label-position="left" label-width="0px" class="demo-ruleForm login-container">
    <h3 class="title">系统登录</h3>
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
  </el-form>
</template>

<script>
    /* eslint-disable */
    import { test } from '../../api/api'
    import $ from 'jquery'
    // import NProgress from 'nprogress'
    export default {
        data () {
            return {
                logining: false,
                ruleForm2: {
                    account: '',
                    checkPass: ''
                },
                rules2: {
                    account: [
                        { required: true, message: '请输入账号', trigger: 'blur' }
                        // { validator: validaePass }
                    ],
                    checkPass: [
                        { required: true, message: '请输入密码', trigger: 'blur' }
                        // { validator: validaePass2 }
                    ]
                },
                checked: true
            }
        },
        methods: {
            handleReset2 () {
                this.$refs.ruleForm2.resetFields()
            },
            handleSubmit2 (ev) {
                var _this = this
                // var _this = this
                this.$refs.ruleForm2.validate((valid) => {
                    if (valid) {
                        // _this.$router.replace('/table')
                        _this.logining = true
                        // NProgress.start()
                        $.ajax({
                            type: "post",
                            url: test+"/api/user/login",
                            async: true,
                            data: {'username': this.ruleForm2.account, 'password': this.ruleForm2.checkPass},
                            timeout: 5000,
                            success: function(data) {
                                _this.logining = false
                                if (data.code === '999999') {
                                    sessionStorage.setItem('username', JSON.stringify(data.data.first_name));
                                    sessionStorage.setItem('token', JSON.stringify(data.data.key));
                                    console.log(_this.$route)
                                    if (_this.$route.query.url) {
                                        _this.$router.push(_this.$route.query.url);
                                    } else {
                                        _this.$router.push('/projectList');
                                    }
                                }
                                else {
                                    _this.$message.error({
                                        message: data.msg,
                                        center: true
                                    })
                                }
                            },
                        })
                    } else {
                        console.log('error submit!!');
                        return false
                    }
                })
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
                var str=['定位成功'];
                str.push('经度：' + data.position.getLng());
                str.push('纬度：' + data.position.getLat());
                console.log(str);
                if(data.accuracy){
                    str.push('精度：' + data.accuracy + ' 米');
                }//如为IP精确定位结果则没有精度信息
                str.push('是否经过偏移：' + (data.isConverted ? '是' : '否'));
                var param = {
                    "success": 0,
                    "longitude": data.position.getLng(),
                    "latitude": data.position.getLat(),
                };
                $.ajax({
                    type: "post",
                    url: test+"/api/user/VisitorRecord",
                    async: true,
                    data: JSON.stringify(param),
                    headers: {
                        "Content-Type": "application/json"
                    },
                    timeout: 5000,
                    success: function(data) {
                        if (data.code === '999999') {
                            console.log("成功")
                            // self.total = data.data.total;
                            // self.project = data.data.data
                        }
                        else {
                            console.log("失败")
                            // self.$message.error({
                            //     message: data.msg,
                            //     center: true,
                            // })
                        }
                    },
                })
                // document.getElementById('tip').innerHTML = str.join('<br>');
            },
            //解析定位错误信息
            onError(data) {
                console.log("定位失败")
                var param = {
                    "success": 0,
                };
                $.ajax({
                    type: "post",
                    url: test+"/api/user/VisitorRecord",
                    async: true,
                    data: JSON.stringify(param),
                    headers: {
                        "Content-Type": "application/json"
                    },
                    timeout: 5000,
                    success: function(data) {
                        if (data.code === '999999') {
                            console.log("成功")
                            // self.total = data.data.total;
                            // self.project = data.data.data
                        }
                        else {
                            console.log("失败")
                            // self.$message.error({
                            //     message: data.msg,
                            //     center: true,
                            // })
                        }
                    },
                })
                // document.getElementById('tip').innerHTML = '定位失败';
            }
        },
        mounted() {
            this.getVisitor();
        }
    }

</script>

<style lang="scss" scoped>
  .login-container {
    /*box-shadow: 0 0px 8px 0 rgba(0, 0, 0, 0.06), 0 1px 0px 0 rgba(0, 0, 0, 0.02);*/
    -webkit-border-radius: 5px;
    border-radius: 5px;
    -moz-border-radius: 5px;
    background-clip: padding-box;
    margin: 180px auto;
    width: 350px;
    padding: 35px 35px 15px 35px;
    background: #fff;
    border: 1px solid #eaeaea;
    box-shadow: 0 0 25px #cac6c6;
    .title {
      margin: 0px auto 40px auto;
      text-align: center;
      color: #505458;
    }
    .remember {
      margin: 0px 0px 35px 0px;
    }
  }
</style>
