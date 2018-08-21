<template>
    <section>
        <!--工具条-->
        <el-col :span="24" style="height: 46px">
            <el-form :inline="true" :model="filters" @submit.native.prevent>
                <el-form-item>
                    <el-input v-model.trim="filters.name" placeholder="名称" @keyup.enter.native="getCaseList"></el-input>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="getCaseList">查询</el-button>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="handleAdd">新增用例</el-button>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" :disabled="update" @click="changeGroup">修改分组</el-button>
                </el-form-item>
            </el-form>
        </el-col>
        <el-dialog title="编辑" :visible.sync="editFormVisible" :close-on-click-modal="false" style="width: 60%; left: 20%">
            <el-form :model="editForm"  :rules="editFormRules" ref="editForm" label-width="80px">
                <el-form-item label="名称" prop="caseName">
                    <el-input v-model.trim="editForm.caseName" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="接口分组:" label-width="83px" prop="automationGroupLevelFirst">
                    <el-select v-model="editForm.automationGroupLevelFirst" placeholder="分组">
                        <el-option v-for="(item,index) in group" :key="index+''" :label="item.name" :value="item.id"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="描述" prop='description'>
                    <el-input type="textarea" :rows="4" v-model.trim="editForm.description"></el-input>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click.native="editFormVisible = false">取消</el-button>
                <el-button type="primary" @click.native="editSubmit" :loading="editLoading">提交</el-button>
            </div>
        </el-dialog>

        <!--新增界面-->
        <el-dialog title="新增" :visible.sync="addFormVisible" :close-on-click-modal="false" style="width: 65%; left: 17.5%">
            <el-form :model="addForm" label-width="80px" :rules="addFormRules" ref="addForm">
                <el-form-item label="名称" prop="caseName">
                    <el-input v-model.trim="addForm.caseName" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="接口分组:" label-width="83px" prop="firstGroup">
                    <el-select v-model="addForm.firstGroup" placeholder="分组">
                        <el-option v-for="(item,index) in group" :key="index+''" :label="item.name" :value="item.id"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="描述" prop='description'>
                    <el-input type="textarea" :rows="4" v-model.trim="addForm.description"></el-input>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click.native="addFormVisible = false">取消</el-button>
                <el-button type="primary" @click.native="addSubmit" :loading="addLoading">提交</el-button>
            </div>
        </el-dialog>
        <el-dialog title="修改所属分组" :visible.sync="updateGroupFormVisible" :close-on-click-modal="false" style="width: 65%; left: 17.5%">
            <el-form :model="updateGroupForm" label-width="80px"  :rules="updateGroupFormRules" ref="updateGroupForm">
                <el-form-item label="分组" prop="firstGroup">
                    <el-select v-model="updateGroupForm.firstGroup" placeholder="请选择分组">
                        <el-option v-for="(item,index) in group" :key="index+''" :label="item.name" :value="item.id">
                        </el-option>
                    </el-select>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click.native="updateGroupFormVisible = false">取消</el-button>
                <el-button type="primary" @click.native="updateGroupSubmit" :loading="updateGroupLoading">提交</el-button>
            </div>
        </el-dialog>

        <!--列表-->
        <el-table :data="Case" highlight-current-row v-loading="listLoading" @selection-change="selsChange" style="width: 100%;">
            <el-table-column type="selection" min-width="5%">
            </el-table-column>
            <el-table-column prop="caseName" label="用例名称" min-width="20%" sortable show-overflow-tooltip>
                <template slot-scope="scope">
                    <el-icon name="caseName"></el-icon>
                    <router-link :to="{ name: '用例接口列表', params: {case_id: scope.row.id}}" style='text-decoration: none;'>{{ scope.row.caseName }}</router-link>
                </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="35%" sortable show-overflow-tooltip>
            </el-table-column>
            <el-table-column prop="createUser" label="创建人" min-width="10%" sortable show-overflow-tooltip>
            </el-table-column>
            <el-table-column prop="updateTime" label="更新日期" min-width="15%" sortable show-overflow-tooltip>
            </el-table-column>
            <el-table-column label="操作" min-width="15%">
                <template slot-scope="scope">
                    <el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
                    <el-button type="info" size="small" @click="handleEdit(scope.$index, scope.row)">修改</el-button>
                </template>
            </el-table-column>
        </el-table>

        <!--工具条-->
        <el-col :span="24" class="toolbar">
            <el-button type="danger" @click="batchRemove" :disabled="this.sels.length===0">批量删除</el-button>
            <el-pagination layout="prev, pager, next" @current-change="handleCurrentChange" :page-size="20" :page-count="total" style="float:right;">
            </el-pagination>
        </el-col>
    </section>
</template>

<script>
    import { test } from '../../../api/api'
    import $ from 'jquery'
    import moment from "moment"
    export default {
        data() {
            return {
                filters: {
                    name: ''
                },
                Case: [],
                total: 0,
                page: 1,
                listLoading: false,
                sels: [],//列表选中列
                delLoading: false,
                disDel: true,
                updateGroupFormVisible: false,
                updateGroupForm: {
                    firstGroup: "",
                },
                updateGroupFormRules: {
                    firstGroup : [{ type: 'number', required: true, message: '请选择父分组', trigger: 'blur'}],
                },
                group: [],
                updateGroupLoading: false,
                update: true,
                editFormVisible: false,//编辑界面是否显示
                editLoading: false,
                editFormRules: {
                    caseName: [
                        { required: true, message: '请输入名称', trigger: 'blur' },
                        { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
                    ],
                    automationGroupLevelFirst: [
                        { type: 'number', required: true, message: '请选择分组', trigger: 'blur'}
                    ],
                    description: [
                        { required: false, message: '请输入描述', trigger: 'blur' },
                        { max: 1024, message: '不能超过1024个字符', trigger: 'blur' }
                    ]
                },
                //编辑界面数据
                editForm: {
                    caseName: '',
                    automationGroupLevelFirst: '',
                    description: ''
                },

                addFormVisible: false,//新增界面是否显示
                addLoading: false,
                addFormRules: {
                    caseName: [
                        { required: true, message: '请输入名称', trigger: 'blur' },
                        { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
                    ],
                    firstGroup: [
                        { type: 'number', required: true, message: '请选择父分组', trigger: 'blur'}
                    ],
                    description: [
                        { required: false, message: '请输入版本号', trigger: 'blur' },
                        { max: 1024, message: '不能超过1024个字符', trigger: 'blur' }
                    ]
                },
                //新增界面数据
                addForm: {
                    caseName: '',
                    firstGroup: '',
                    description: ''
                }
            }
        },
        methods: {
            // 获取用例列表
            getCaseList() {
                this.listLoading = true;
                let self = this;
                let param = { project_id: this.$route.params.project_id, page: self.page, name: self.filters.name};
                if (this.$route.params.firstGroup) {
                    param['first_group_id'] = this.$route.params.firstGroup;
                    if (this.$route.params.secondGroup) {
                        param['second_group_id'] = this.$route.params.secondGroup
                    }
                }

                $.ajax({
                    type: "get",
                    url: test+"/api/automation/case_list",
                    async: true,
                    data: param,
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: function(data) {
                        self.listLoading = false;
                        if (data.code === '999999') {
                            self.total = data.data.total;
                            self.Case = data.data.data
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
            // 修改用例所属分组
            updateGroupSubmit() {
                let ids = this.sels.map(item => item.id);
                let self = this;
                this.$confirm('确认修改所属分组吗？', '提示', {
                    type: 'warning'
                }).then(() => {
                    self.updateGroupLoading = true;
                    //NProgress.start();
                    let params = JSON.stringify({
                        project_id: Number(this.$route.params.project_id),
                        automationGroupLevelFirst_id: self.updateGroupForm.firstGroup,
                        ids:ids
                    });
                    $.ajax({
                        type: "post",
                        url: test+"/api/automation/update_case_group",
                        async: true,
                        data: params,
                        headers: {
                            "Content-Type": "application/json",
                            Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                        },
                        timeout: 5000,
                        success: function(data) {
                            self.updateGroupLoading = false;
                            if (data.code === '999999') {
                                self.$message({
                                    message: '修改成功',
                                    center: true,
                                    type: 'success'
                                });
                                self.$router.push({ name: '分组用例列表', params: { project_id: self.$route.params.project_id, firstGroup: self.updateGroupForm.firstGroup}});
                            }
                            else {
                                self.$message.error({
                                    message: data.msg,
                                    center: true,
                                })
                            }
                            self.updateGroupFormVisible = false;
                            self.getCaseList();
                        },
                    })
                }).catch(() => {

                });
            },
            // 获取用例分组
            getCaseGroup() {
                let self = this;
                $.ajax({
                    type: "get",
                    url: test+"/api/automation/group",
                    async: true,
                    data: { project_id: this.$route.params.project_id},
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: function(data) {
                        if (data.code === '999999') {
                            self.group = data.data;
                            self.updateGroupForm.firstGroup = self.group[0].id;
                            self.addForm.firstGroup = self.group[0].id
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
            changeGroup() {
                this.getCaseGroup();
                this.updateGroupFormVisible = true

            },
            //删除
            handleDel: function (index, row) {
                this.$confirm('确认删除该记录吗?', '提示', {
                    type: 'warning'
                }).then(() => {
                    this.listLoading = true;
                    //NProgress.start();
                    let self = this;
                    $.ajax({
                        type: "post",
                        url: test+"/api/automation/del_case",
                        async: true,
                        data: JSON.stringify({
                                project_id: Number(this.$route.params.project_id),
                                ids: [row.id] }),
                        headers: {
                            "Content-Type": "application/json",
                            Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                        },
                        timeout: 5000,
                        success: function(data) {
                            if (data.code === '999999') {
                                self.$message({
                                    message: '删除成功',
                                    center: true,
                                    type: 'success'
                                })
                            } else {
                                self.$message.error({
                                    message: data.msg,
                                    center: true,
                                })
                            }
                            self.getCaseList();
                        },
                    })

                }).catch(() => {
                });
            },
            handleCurrentChange(val) {
                this.page = val;
                this.getCaseList()
            },
            selsChange: function (sels) {
                if (sels.length>0) {
                    this.sels = sels;
                    this.update = false
                } else {
                    this.update = true
                }
            },
            //批量删除
            batchRemove: function () {
                let ids = this.sels.map(item => item.id);
                let self = this;
                this.$confirm('确认删除选中记录吗？', '提示', {
                    type: 'warning'
                }).then(() => {
                    self.listLoading = true;
                    //NProgress.start();
                    $.ajax({
                        type: "post",
                        url: test+"/api/automation/del_case",
                        async: true,
                        data:JSON.stringify({ project_id: Number(this.$route.params.project_id), ids: ids}),
                        headers: {
                            "Content-Type": "application/json",
                            Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                        },
                        timeout: 5000,
                        success: function(data) {
                            self.listLoading = false;
                            if (data.code === '999999') {
                                self.$message({
                                    message: '删除成功',
                                    center: true,
                                    type: 'success'
                                })
                            }
                            else {
                                self.$message.error({
                                    message: data.msg,
                                    center: true,
                                })
                            }
                            self.getCaseList();
                        },
                    })
                }).catch(() => {

                });
            },
            //显示编辑界面
            handleEdit: function (index, row) {
                this.getCaseGroup();
                this.editFormVisible = true;
                this.editForm = Object.assign({}, row);
            },
            //显示新增界面
            handleAdd: function () {
                this.getCaseGroup();
                this.addFormVisible = true;
            },
            // 修改用例
            editSubmit: function () {
                let self = this;
                this.$refs.editForm.validate((valid) => {
                    if (valid) {
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.editLoading = true;
                            //NProgress.start();
                            let param = JSON.stringify({
                                project_id: Number(this.$route.params.project_id),
                                id: Number(self.editForm.id),
                                caseName: self.editForm.caseName,
                                automationGroupLevelFirst_id: Number(this.editForm.automationGroupLevelFirst),
                                description: self.editForm.description });
                            $.ajax({
                                type: "post",
                                url: test+"/api/automation/update_case",
                                async: true,
                                data: param,
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
                                        self.getCaseList()
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
            //新增用例
            addSubmit: function () {
                this.$refs.addForm.validate((valid) => {
                    if (valid) {
                        let self = this;
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.addLoading = true;
                            //NProgress.start();
                            let param = JSON.stringify({
                                project_id: Number(this.$route.params.project_id),
                                automationGroupLevelFirst_id: this.addForm.firstGroup,
                                caseName: self.addForm.caseName,
                                description: self.addForm.description });
                            $.ajax({
                                type: "post",
                                url: test+"/api/automation/add_case",
                                async: true,
                                data: param,
                                headers: {
                                    Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                                },
                                timeout: 5000,
                                success: function(data) {
                                    self.addLoading = false;
                                    if (data.code === '999999') {
                                        self.$message({
                                            message: '添加成功',
                                            center: true,
                                            type: 'success'
                                        });
                                        self.$refs['addForm'].resetFields();
                                        self.addFormVisible = false;
                                        self.getCaseList()
                                    } else if (data.code === '999997'){
                                        self.$message.error({
                                            message: data.msg,
                                            center: true,
                                        })
                                    } else {
                                        self.$message.error({
                                            message: data.msg,
                                            center: true,
                                        });
                                        self.$refs['addForm'].resetFields();
                                        self.addFormVisible = false;
                                        self.getCaseList()
                                    }
                                },
                            })
                        });
                    }
                });
            },
        },
        watch: {
            '$route': function (to, from) {
                if (to !== from) {
                    this.getCaseList();
                }
            }
        },
        mounted() {
            this.getCaseList();

        }
    }
</script>

<style lang="scss" scoped>
    .api-title {
        padding: 15px;
        margin: 0px;
        text-align: center;
        border-radius:5px;
        font-size: 15px;
        color: aliceblue;
        background-color: rgb(32, 160, 255);
        font-family: PingFang SC;
    }
    .group .editGroup {
        float:right;
    }
    .row-title {
        margin: 35px;
    }
    .addGroup {
        margin-top: 0px;
        margin-bottom: 10px;
        border-radius: 25px;
    }
    .api-view-a {
        margin-left: 15px;
        margin-right: 15px;
        display: block;
    }
    .api-view-b {
        margin-left: 15px;
        margin-right: 15px;
        display: none;
    }
</style>