<template>
    <section style="padding: 10px">
        <el-row :span="24">
            <el-col :span="12">
                <div style="padding-left: 50px;">
                    <p style="color:#999">*注<strong>: </strong>昵称不得包含emoji</p>
                    <div>
                        <el-row :span="24">
                            <el-col :span="3">
                                <img style="width: 60px" src="../../assets/wx.jpg"/>
                            </el-col>
                            <el-col :span="21">
                                <el-row :gutter="20" v-if="WXLoginStatus">
                                    <el-col :span="6">
                                        <el-button style="margin:10px" type="primary" @click.native="addWXRobot()">添加微信机器人</el-button>
                                    </el-col>
                                    <el-col :span="8">
                                        <el-input v-model="name" style="margin-top:10px" placeholder="微信群或个人微信名称"></el-input>
                                        <p v-if="!name" style="margin-top:0px;color: red">请输入消息接收方</p>
                                    </el-col>
                                    <el-col :span="10">
                                        <el-select v-if="!WXData.length" style="margin-top:10px" v-model="type" placeholder="请选择群聊或个人">
                                            <el-option
                                                    v-for="item in options"
                                                    :key="item.value"
                                                    :label="item.label"
                                                    :value="item.value">
                                            </el-option>
                                        </el-select>
                                        <p v-if="!type" style="margin-top:0px;color: red">请选择</p>
                                    </el-col>
                                </el-row>
                                <el-row :gutter="20" v-if="!WXLoginStatus">
                                    <el-col :span="6">
                                        <el-button style="margin:10px" type="primary" @click.native="logOutWx()">退出微信机器人</el-button>
                                    </el-col>
                                    <el-col :span="8">
                                        <div style="margin-top:20px;margin-bottom: 20px">微信账号：{{WXData.nickName}}</div>
                                    </el-col>
                                    <el-col :span="4">
                                        <div style="margin-top:20px;margin-bottom: 20px">类型：{{WXData.role_type==='person'? "个人": "群聊"}}</div>
                                    </el-col>
                                    <el-col :span="6">
                                        <div style="margin-top:20px;margin-bottom: 20px">消息接收方：{{WXData.name}}</div>
                                    </el-col>
                                </el-row>
                            </el-col>
                        </el-row>
                    </div>
                </div>
                <el-dialog title="扫码登录" v-model="WXQRcode" style="width: 50%; left: 20%">
                    <p style="color:#999">*注<strong>: </strong>微信昵称不得包含emoji, 微信接收到“微信机器人接入成功”，表示已成功添加</p>
                    <img :src="QRcode" style="max-width:100%">
                </el-dialog>
            </el-col>
            <el-col :span="12">
            </el-col>
        </el-row>
    </section>
</template>

<script>
    import { test } from '../../api/api'
    import $ from 'jquery'
    export default {
        props: ['src'],
        data() {
            return {
                options: [
                    { value: "group", label: "群聊"},
                    { value: "person", label: "个人"},
                ],
                type: "",
                WXQRcode: false,
                WXData: {},
                WXLoginStatus: true,
                name: "",
                QRcode: "http://www.86y.org/images/loading.gif",
                // QRloading: false,
            }
        },
        methods: {
            getRobot(){
                let self =this;
                $.ajax({
                    type: "get",
                    url: test+"/api/robot/get_robot",
                    async: true,
                    data: {},
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: function(data) {
                        if (data.code === '999999') {
                            if (data.data.length) {
                                data.data.forEach((item) => {
                                    if (item.robotType === "WX") {
                                        if (item.nickName) {
                                            self.WXData = item;
                                            self.WXLoginStatus = false
                                        }
                                    }
                                });
                            }
                        }
                        else {
                            self.$message.error({
                                message: data.msg,
                                center: true,
                            })
                        }
                    },
                })
            },
            logOutWx(){
                let self =this;
                $.ajax({
                    type: "get",
                    url: test+"/api/robot/logout_wx",
                    async: true,
                    data: {},
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: function(data) {
                        if (data.code === '999999') {
                            self.$message.success({
                                message: "退出微信机器人成功！",
                                center: true,
                            })
                        }
                        else {
                            self.$message.error({
                                message: data.msg,
                                center: true,
                            })
                        }
                    },
                })
            },
            addWXRobot(){
                let self =this;
                if (this.name && this.type) {
                    $.ajax({
                        type: "get",
                        url: test+"/api/robot/wx_robot",
                        async: true,
                        data: {name: self.name, type: this.type},
                        headers: {
                            Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                        },
                        timeout: 5000,
                        success: function(data) {
                            self.listLoading = false;
                            if (data.code === '999999') {
                                self.WXQRcode = true;
                                self.getQRcode()
                                self.getRobot();
                            }
                            else {
                                self.$message.error({
                                    message: data.msg,
                                    center: true,
                                })
                            }
                        },
                    })
                }
            },
            getQRcode() {
                let self =this;
                $.ajax({
                    type: "get",
                    url: test+"/api/robot/get_wx_QRcode",
                    async: true,
                    data: {type: "WX"},
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: function(data) {
                        self.listLoading = false;
                        if (data.code === '999999') {
                            self.WXQRcode = true;
                            console.log(data.data)
                            self.QRcode = data.data[0].img
                            console.log(self.QRcode)
                            self.getRobot();
                        }
                        else {
                            self.$message.error({
                                message: data.msg,
                                center: true,
                            })
                        }
                    },
                })
            }
        },
        mounted(){
            this.getRobot();
            // this.getQRcode();
        }
    }
</script>