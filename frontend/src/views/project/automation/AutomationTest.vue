<template>
    <section>
        <el-row :span="24" class="row-title">
            <el-col :span="4">
                <el-button class="addGroup" @click="handleAddGroup">新增分组</el-button>
                <div class="api-title"><strong>接口分组</strong></div>
                <div class="api-title" style="cursor:pointer;">
                    <router-link :to="{ name: '用例列表', params: {project_id: this.$route.params.project_id}}" style='text-decoration: none;color: aliceblue;'>
                        所有用例
                    </router-link>
                </div>
                <aside>
                    <!--导航菜单-->
                    <el-menu default-active="2" class="el-menu-vertical-demo" active-text-color="rgb(32, 160, 255)" :unique-opened="true">
                        <template v-for="(item,index) in groupData">
                            <el-submenu :index="index+''" :key="item.id" class="group">
                                <template slot="title">{{item.name}}
                                    <el-dropdown trigger="hover" class="editGroup" style="margin-right:10%">
                                        <i class="el-icon-more"></i>
                                        <el-dropdown-menu slot="dropdown">
                                            <el-dropdown-item @click.native="handleAddSecond(item.id)">新增子分组</el-dropdown-item>
                                            <el-dropdown-item @click.native="handleDelFirst(item.id)">删除</el-dropdown-item>
                                            <el-dropdown-item @click.native="handleEditFirstGroup(item.id, item.name)">修改</el-dropdown-item>
                                        </el-dropdown-menu>
                                    </el-dropdown>
                                </template>
                                <template v-for="child in item.secondGroup">
                                    <router-link :to="{ name: '分组用例列表', params: {project_id: project, firstGroup: item.id, secondGroup: child.id}}" style='text-decoration: none;color: aliceblue;'>
                                        <el-menu-item class="group" style="padding-right: 10px;" :index="child.id+''">
                                            {{child.name }}
                                            <el-dropdown trigger="hover" class="editGroup">
                                                <i class="el-icon-more"></i>
                                                <el-dropdown-menu slot="dropdown">
                                                    <el-dropdown-item @click.native="handleDelSecond(item.id, child.id)">删除</el-dropdown-item>
                                                    <el-dropdown-item @click.native="handleEditGroup(item.id, child.id, child.name)">修改</el-dropdown-item>
                                                </el-dropdown-menu>
                                            </el-dropdown>
                                        </el-menu-item>
                                    </router-link>
                                </template>
                            </el-submenu>
                        </template>
                    </el-menu>
                </aside>
            </el-col>
            <!--新增-->
            <el-dialog title="新增分组" v-model="addGroupFormVisible" :close-on-click-modal="false" style="width: 60%; left: 20%">
                <el-form :model="addGroupForm" label-width="80px"  :rules="addGroupFormRules" ref="addGroupForm">
                    <el-form-item label="父分组">
                        <el-select v-model="addGroupForm.firstgroup" placeholder="请选择">
                            <el-option v-for="(item,index) in options" :key="index+''" :label="item.label" :value="item.value">
                            </el-option>
                        </el-select>
                    </el-form-item>
                    <el-form-item label="子分组" prop='secondGroup'>
                        <el-input v-model="addGroupForm.secondGroup" auto-complete="off"></el-input>
                    </el-form-item>
                </el-form>
                <div slot="footer" class="dialog-footer">
                    <el-button @click.native="addGroupFormVisible = false">取消</el-button>
                    <el-button type="primary" @click.native="addGroupSubmit" :loading="addGroupLoading">提交</el-button>
                </div>
            </el-dialog>
                        <!--编辑父分组-->
            <el-dialog title="编辑分组" v-model="editFirstGroupFormVisible" :close-on-click-modal="false" style="width: 60%; left: 20%">
                <el-form :model="editFirstGroupForm" label-width="80px"  :rules="editFirstGroupFormRules" ref="editFirstGroupForm">
                    <el-form-item label="分组名称" prop='secondFirstGroup'>
                        <el-input v-model="editFirstGroupForm.secondFirstGroup" auto-complete="off"></el-input>
                    </el-form-item>
                </el-form>
                <div slot="footer" class="dialog-footer">
                    <el-button @click.native="editFirstGroupFormVisible = false">取消</el-button>
                    <el-button type="primary" @click.native="editFirstGroupSubmit" :loading="editFirstGroupLoading">提交</el-button>
                </div>
            </el-dialog>
            <!--编辑-->
            <el-dialog title="编辑分组" v-model="editGroupFormVisible" :close-on-click-modal="false" style="width: 60%; left: 20%">
                <el-form :model="editGroupForm" label-width="80px"  :rules="editGroupFormRules" ref="editGroupForm">
                    <el-form-item label="父分组">
                        <el-select v-model="editGroupForm.firstgroup" placeholder="请选择">
                            <el-option v-for="(item,index) in options" :key="index+''" :label="item.label" :value="item.value">
                            </el-option>
                        </el-select>
                    </el-form-item>
                    <el-form-item label="子分组" prop='secondGroup'>
                        <el-input v-model="editGroupForm.secondGroup" auto-complete="off"></el-input>
                    </el-form-item>
                </el-form>
                <div slot="footer" class="dialog-footer">
                    <el-button @click.native="editGroupFormVisible = false">取消</el-button>
                    <el-button type="primary" @click.native="editGroupSubmit" :loading="editGroupLoading">提交</el-button>
                </div>
            </el-dialog>
            <el-col :span="20">
                <div style="margin-left: 10px;margin-right: 20px">
                    <router-view></router-view>
                </div>
            </el-col>
        </el-row>
    </section>
</template>

<script>
    import { test } from '../../../api/api'
    import $ from 'jquery'
    export default {
        data() {
            return {
                project: "",
                groupData: [],
                options:[{
                    value: '',
                    label: '不设置父分组',
                }],
                addGroupFormVisible: false,
                addGroupLoading: false,
                addFormVisible: false,//新增界面是否显示
                addGroupFormRules: {
                    firstgroup: [
                        { required: false, trigger: 'blur' },
                        { min: 1, max: 20, message: '长度在 1 到 20 个字符', trigger: 'blur' }
                    ],
                    secondGroup: [
                        { required: true, message: '请输入子分组名称', trigger: 'blur' },
                        { min: 1, max: 20, message: '长度在 1 到 20 个字符', trigger: 'blur' }
                    ]
                },
                //新增界面数据
                addGroupForm: {
                    firstgroup: '',
                    secondGroup: '',
                },
                editGroupFormVisible: false,
                editGroupLoading: false,
                editFormVisible: false,//编辑界面是否显示
                editGroupFormRules: {
                    firstgroup: [
                        { required: false, trigger: 'blur' },
                        { min: 1, max: 20, message: '长度在 1 到 20 个字符', trigger: 'blur' }
                    ],
                    secondGroup: [
                        { required: true, message: '请输入子分组名称', trigger: 'blur' },
                        { min: 1, max: 20, message: '长度在 1 到 20 个字符', trigger: 'blur' }
                    ]
                },
                //编辑界面数据
                editGroupForm: {
                    firstgroup: '',
                    secondGroup: '',
                    second_id: '',
                },
                editFirstGroupFormVisible: false,
                editFirstGroupLoading: false,
                editFirstFormVisible: false,//编辑界面是否显示
                editFirstGroupFormRules: {
                    secondFirstGroup: [
                        { required: true, message: '请输入分组名称', trigger: 'blur' },
                        // { min: 1, max: 20, message: '长度在 1 到 20 个字符', trigger: 'blur' }
                    ]
                },
                //编辑界面数据
                editFirstGroupForm: {
                    firstgroup: '',
                    secondGroup: '',
                    second_id: '',
                },
                filters: {
                    name: ''
                },
                api: [],
                total: 0,
                page: 1,
                listLoading: false,
                sels: [],//列表选中列
                apiView: true,
            }
        },
        methods: {
            // 初始化
            init() {
                this.options = [{
                    value: '',
                    label: '不设置父分组',
                }];
                this.editGroupForm.firstgroup = ''
            },
            // 获取自动化分组
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
                            self.groupData = data.data;
                            self.init();
                            for (let i=0; i<self.groupData.length; i++) {
                                let person = { value: self.groupData[i].id, label: self.groupData[i].name};
                                self.options.push(person)
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
            handleAddGroup() {
                this.addGroupFormVisible = true;
            },
            handleEditGroup(first_id, second_id, name) {
                this.editGroupFormVisible = true;
                // console.log(index)
                this.editGroupForm.firstgroup = first_id;
                this.editGroupForm.secondGroup = name;
                this.editGroupForm.second_id = second_id;
            },
            handleEditFirstGroup(first_id, name) {
                this.editFirstGroupFormVisible = true;
                this.editFirstGroupForm.second_id = first_id;
                this.editFirstGroupForm.secondFirstGroup = name
            },
            addGroupSubmit() {
                this.$refs.addGroupForm.validate((valid) => {
                    if (valid) {
                        let self = this;
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.addGroupLoading = true;
                            //NProgress.start();
                            $.ajax({
                                type: "post",
                                url: test+"/api/automation/add_group",
                                async: true,
                                data: { project_id: this.$route.params.project_id, name: self.addGroupForm.secondGroup, first_group_id: self.addGroupForm.firstgroup},
                                headers: {
                                    Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                                },
                                timeout: 5000,
                                success: function(data) {
                                    self.addGroupLoading = false;
                                    if (data.code === '999999') {
                                        self.$message({
                                            message: '添加成功',
                                            center: true,
                                            type: 'success'
                                        });
                                        self.$refs['addGroupForm'].resetFields();
                                        self.addGroupFormVisible = false;
                                        self.getCaseGroup();
                                        self.init()
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
                                        self.$refs['addGroupForm'].resetFields();
                                        self.addGroupFormVisible = false;
                                        self.getCaseGroup();
                                        self.init()
                                    }
                                },
                            })
                        });
                    }
                });
            },
            editFirstGroupSubmit(){
                this.$refs.editFirstGroupForm.validate((valid) => {
                    if (valid) {
                        let self = this;
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.editFirstGroupLoading = true;
                            //NProgress.start();
                            // if (!self.editFirstGroupForm.firstgroup) {
                            //     self.editFirstGroupForm.firstgroup = self.editFirstGroupForm.second_id;
                            //     self.editFirstGroupForm.second_id = ''
                            // }
                            $.ajax({
                                type: "post",
                                url: test+"/api/automation/update_name_group",
                                async: true,
                                data: { project_id: this.$route.params.project_id,
                                    name: self.editFirstGroupForm.secondFirstGroup,
                                    first_group_id: self.editFirstGroupForm.second_id,
                                    second_group_id: self.editFirstGroupForm.firstgroup},
                                headers: {
                                    Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                                },
                                timeout: 5000,
                                success: function(data) {
                                    self.editFirstGroupLoading = false;
                                    if (data.code === '999999') {
                                        self.$message({
                                            message: '修改成功',
                                            center: true,
                                            type: 'success'
                                        });
                                        self.$refs['editFirstGroupForm'].resetFields();
                                        self.editFirstGroupFormVisible = false;
                                        self.getCaseGroup();
                                        self.init()
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
                                        self.$refs['editFirstGroupForm'].resetFields();
                                        self.editFirstGroupFormVisible = false;
                                        self.getCaseGroup();
                                        self.init()
                                    }
                                },
                            })
                        });
                    }
                });
            },
            editGroupSubmit() {
                this.$refs.editGroupForm.validate((valid) => {
                    if (valid) {
                        let self = this;
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.editGroupLoading = true;
                            //NProgress.start();
                            if (!self.editGroupForm.firstgroup) {
                                self.editGroupForm.firstgroup = self.editGroupForm.second_id;
                                self.editGroupForm.second_id = ''
                            }
                            $.ajax({
                                type: "post",
                                url: test+"/api/automation/update_name_group",
                                async: true,
                                data: { project_id: this.$route.params.project_id,
                                    name: self.editGroupForm.secondGroup,
                                    first_group_id: self.editGroupForm.firstgroup,
                                    second_group_id: self.editGroupForm.second_id},
                                headers: {
                                    Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                                },
                                timeout: 5000,
                                success: function(data) {
                                    self.editGroupLoading = false;
                                    if (data.code === '999999') {
                                        self.$message({
                                            message: '修改成功',
                                            center: true,
                                            type: 'success'
                                        });
                                        self.$refs['editGroupForm'].resetFields();
                                        self.editGroupFormVisible = false;
                                        self.getCaseGroup();
                                        self.init()
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
                                        self.$refs['editGroupForm'].resetFields();
                                        self.editGroupFormVisible = false;
                                        self.getCaseGroup();
                                        self.init()
                                    }
                                },
                            })
                        });
                    }
                });
            },
            handleAddSecond(first_id){
                this.addGroupFormVisible = true;
                this.addGroupForm.firstgroup = first_id;
            },
            //删除一级分组
            handleDelFirst: function (id) {
                this.$confirm('确认删除该记录吗?', '提示', {
                    type: 'warning'
                }).then(() => {
                    //NProgress.start();
                    let self = this;
                    $.ajax({
                        type: "post",
                        url: test+"/api/automation/del_group",
                        async: true,
                        data: {first_group_id: id, project_id: this.$route.params.project_id},
                        headers: {
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
                            self.getCaseGroup()
                        },
                    })

                }).catch(() => {
                });
            },
            // 删除二级分组
            handleDelSecond: function (first_id, second_id) {
                this.$confirm('确认删除该记录吗?', '提示', {
                    type: 'warning'
                }).then(() => {
                    //NProgress.start();
                    let self = this;
                    $.ajax({
                        type: "post",
                        url: test+"/api/automation/del_group",
                        async: true,
                        data: {first_group_id: first_id, second_group_id: second_id, project_id: this.$route.params.project_id},
                        headers: {
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
                            self.getCaseGroup()
                        },
                    })

                }).catch(() => {
                });
            },
        },
        mounted() {
            this.getCaseGroup();
            this.project = this.$route.params.project_id

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
</style>