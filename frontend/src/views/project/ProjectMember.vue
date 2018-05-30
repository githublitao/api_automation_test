<template>
    <!--列表-->
    <el-row class="member-manage">
        <p style="color:#999">*注<strong>: </strong>自动化测试结果会发送给所有项目成员</p>
        <div style="margin-bottom: 20px;font-size: 20px">
            <div>
                <div style="display: inline">测试报告发送账号： </div>
                <div v-if="!reportFrom" style="display: inline">未添加账号</div>
                <div v-if="reportFrom" style="display: inline">{{reportFrom}}</div>

                &nbsp;&nbsp;
                <i class="el-icon-edit" style="cursor:pointer;display: inline" @click="editFormVisible=true"></i>
                                &nbsp;&nbsp;
                <i v-if="reportFrom" class="el-icon-delete" style="cursor:pointer;display: inline" @click="DelEmail()"></i>
            </div>
        </div>
        <el-dialog title="编辑" v-model="editFormVisible" :close-on-click-modal="false" style="width: 60%; left: 20%">
		    <el-form :model="editForm" label-width="100px"  :rules="editFormRules" ref="editForm">
                <el-form-item label="发送人邮箱:" prop="reportFrom">
                    <el-input v-model="editForm.reportFrom" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="用户名:" prop="mailUser">
                    <el-input v-model="editForm.mailUser" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="口令:" prop="mailPass">
                    <el-input v-model="editForm.mailPass" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="邮箱服务器:" prop="mailSmtp">
                    <el-input v-model="editForm.mailSmtp" auto-complete="off"></el-input>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click.native="editFormVisible = false">取消</el-button>
                <el-button type="primary" @click.native="editSubmit" :loading="editLoading">提交</el-button>
            </div>
		</el-dialog>
        <el-col :span="24">
            <el-table :data="memberData" highlight-current-row v-loading="listLoading" style="width: 100%;">
                <el-table-column prop="username" label="姓名" min-width="30%" sortable>
                </el-table-column>
                <el-table-column prop="permissionType" label="权限" min-width="30%" sortable>
                </el-table-column>
                <el-table-column prop="userPhone" label="手机号" min-width="20%" sortable>
                </el-table-column>
                <el-table-column prop="userEmail" label="邮箱地址" min-width="20%" sortable>
                </el-table-column>
            </el-table>
            <!--工具条-->
            <el-pagination layout="prev, pager, next" @current-change="handleCurrentChange" :page-size="20" :page-count="total" style="float:right;">
            </el-pagination>
        </el-col>
    </el-row>
</template>

<script>
    import { test } from '../../api/api'
    import $ from 'jquery'
    export default {
        data() {
            return {
                memberData: [],
                total: 0,
                page: 1,
                listLoading: false,
                reportFrom: "",
                editFormVisible: false,//编辑界面是否显示
                editLoading: false,
                editFormRules: {
                    reportFrom: [
                        { required: true, message: '请输入发送人', trigger: 'blur' },
                        { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
                    ],
                    mailUser: [
                        { required: true, message: '请输入用户名', trigger: 'blur' },
                        { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
                    ],
                    mailPass: [
                        { required: true, message: '请输入口令', trigger: 'blur' },
                        { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
                    ],
                    mailSmtp: [
                        { required: false, message: '请输入邮件服务器', trigger: 'blur' },
                        { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
                    ]
                },
                //编辑界面数据
                editForm: {
                },
            }
        },
        methods: {
            handleCurrentChange(val) {
                this.page = val;
                this.getProjectMember()
            },
            // 获取HOST列表
            getProjectMember() {
                this.listLoading = true;
                let self = this;
                $.ajax({
                    type: "get",
                    url: test+"/api/member/project_member",
                    async: true,
                    data: { project_id: this.$route.params.project_id, page: self.page},
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: function(data) {
                        self.listLoading = false;
                        if (data.code === '999999') {
                            self.total = data.data.total;
                            self.memberData = data.data.data
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
            getEmailConfig(){
                let self = this;
                $.ajax({
                    type: "get",
                    url: test+"/api/member/get_email",
                    async: true,
                    data: { project_id: this.$route.params.project_id},
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: function(data) {
                        self.listLoading = false;
                        if (data.code === '999999') {
                            if (data.data.length) {
                                self.reportFrom = data.data[0].reportFrom;
                                self.editForm = data.data[0]
                            } else {
                                self.reportFrom = "";
                                self.editForm = {}
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
            DelEmail(){
                let self = this;
                $.ajax({
                    type: "post",
                    url: test+"/api/member/del_email",
                    async: true,
                    data: { project_id: this.$route.params.project_id},
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: function(data) {
                        self.listLoading = false;
                        if (data.code === '999999') {
                            self.$message.success({
                                message: "删除成功",
                                center: true,
                            })
                            self.getEmailConfig()
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
            editSubmit: function () {
                let self = this;
                this.$refs.editForm.validate((valid) => {
                    if (valid) {
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.editLoading = true;
                            //NProgress.start();
                            console.log(this.editForm)
                            $.ajax({
                                type: "post",
                                url: test+"/api/member/email_config",
                                async: true,
                                data: {
                                    project_id: this.$route.params.project_id,
                                    from: this.editForm.reportFrom,
                                    user: this.editForm.mailUser,
                                    mailPass: this.editForm.mailPass,
                                    mailSmtp: this.editForm.mailSmtp,
                                },
                                headers: {
                                    Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                                },
                                timeout: 5000,
                                success: function(data) {
                                    self.editLoading = false;
                                    if (data.code === '999999') {
                                        self.$message({
                                            message: '修改成功',
                                            center: true,
                                            type: 'success'
                                        });
                                        self.$refs['editForm'].resetFields();
                                        self.editFormVisible = false;
                                        self.getEmailConfig()
                                    } else if (data.code === '999997'){
                                        self.$message.error({
                                            message: data.msg,
                                            center: true,
                                        })
                                    } else {
                                        self.$message.error({
                                            message: data.msg,
                                            center: true,
                                        })
                                    }
                                },
                            })
                        });
                    }
                });
            },
        },
        mounted() {
            this.getProjectMember();
            this.getEmailConfig();

        }
    }
</script>

<style lang="scss" scoped>
    .member-manage {
        margin: 35px;
    }
</style>