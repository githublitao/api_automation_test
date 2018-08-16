<template>
    <section>
        <el-row :span="24" class="row-title">
            <el-col :span="4">
                <el-button class="addGroup" @click="handleAddGroup">新增分组</el-button>
                <router-link :to="{ name: '快速测试', params: {project_id: this.$route.params.project_id}}" style='text-decoration: none;color: aliceblue;'>
                    <el-button class="addGroup">快速测试</el-button>
                </router-link>
                <div class="api-title"><strong>接口分组</strong></div>
                <div class="api-title" style="cursor:pointer;">
                    <router-link :to="{ name: '接口列表', params: {project_id: this.$route.params.project_id}}" style='text-decoration: none;color: aliceblue;'>
                        所有接口
                    </router-link>
                </div>
                <aside>
                    <!--导航菜单-->
                    <el-menu default-active="2" class="el-menu-vertical-demo" active-text-color="rgb(32, 160, 255)" :unique-opened="true">
                        <template v-for="(item,index) in groupData">
                            <router-link :to="{ name: '分组接口列表', params: {project_id: project, firstGroup: item.id}}" style="text-decoration:none;">
                                <el-menu-item :index="index+''" :key="item.id" class="group">
                                    <template slot="title">{{item.name}}
                                        <el-dropdown trigger="hover" class="editGroup" style="margin-right:10%">
                                            <i class="el-icon-more"></i>
                                            <el-dropdown-menu slot="dropdown">
                                                <el-dropdown-item @click.native="handleDelFirst(item.id)">删除</el-dropdown-item>
                                                <el-dropdown-item @click.native="handleEditFirstGroup(item.id, item.name)">修改</el-dropdown-item>
                                            </el-dropdown-menu>
                                        </el-dropdown>
                                    </template>
                                </el-menu-item>
                            </router-link>
                        </template>
                    </el-menu>
                </aside>
            </el-col>
            <!--新增-->
            <el-dialog title="新增分组" :visible.sync="addGroupFormVisible" :close-on-click-modal="false" style="width: 60%; left: 20%">
                <el-form :model="addGroupForm" label-width="80px"  :rules="addGroupFormRules" ref="addGroupForm">
                    <el-form-item label="分组名称" prop='firstgroup'>
                        <el-input v-model.trim="addGroupForm.firstgroup" auto-complete="off" style="width: 90%"></el-input>
                    </el-form-item>
                </el-form>
                <div slot="footer" class="dialog-footer">
                    <el-button @click.native="addGroupFormVisible = false">取消</el-button>
                    <el-button type="primary" @click.native="addGroupSubmit" :loading="addGroupLoading">提交</el-button>
                </div>
            </el-dialog>
            <!--编辑父分组-->
            <el-dialog title="编辑分组" :visible.sync="editFirstGroupFormVisible" :close-on-click-modal="false" style="width: 60%; left: 20%">
                <el-form :model="editFirstGroupForm" label-width="80px"  :rules="editFirstGroupFormRules" ref="editFirstGroupForm">
                    <el-form-item label="分组名称" prop='secondFirstGroup'>
                        <el-input v-model.trim="editFirstGroupForm.secondFirstGroup" auto-complete="off"></el-input>
                    </el-form-item>
                </el-form>
                <div slot="footer" class="dialog-footer">
                    <el-button @click.native="editFirstGroupFormVisible = false">取消</el-button>
                    <el-button type="primary" @click.native="editFirstGroupSubmit" :loading="editFirstGroupLoading">提交</el-button>
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
    import {addApiGroup, delApiGroup, getApiGroupList, updateApiGroup} from '../../../api/api'
    export default {
        data() {
            return {
                project: "",
                groupData: [],
                addGroupFormVisible: false,
                addGroupLoading: false,
                addFormVisible: false,//新增界面是否显示
                addGroupFormRules: {
                    firstgroup: [
                        { required: true, message: '请输入子分组名称', trigger: 'blur' },
                        // { min: 1, max: 20, message: '长度在 1 到 20 个字符', trigger: 'blur' }
                    ]
                },
                //新增界面数据
                addGroupForm: {
                    firstgroup: '',
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
                this.addGroupForm.firstgroup = ''
            },
            // 获取api分组
            getApiGroup() {
                let self = this;
                let params = {
                    project_id: this.$route.params.project_id
                };
                let headers = {
                    "Content-Type": "application/json",
                    Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                };
                getApiGroupList(headers, params).then(_data => {
                    let {msg, code, data} = _data;
                    if (code === '999999') {
                        self.groupData = data;
                        self.init();
                    }
                    else {
                        self.$message.error({
                            message: msg,
                            center: true,
                        })
                    }
                })
            },
            // 添加分组弹窗显示
            handleAddGroup() {
                this.addGroupFormVisible = true;
            },
            // 修改分组弹窗显示
            handleEditFirstGroup(first_id, name) {
                this.editFirstGroupFormVisible = true;
                this.editFirstGroupForm.second_id = first_id;
                this.editFirstGroupForm.secondFirstGroup = name
            },
            // 添加分组
            addGroupSubmit() {
                this.$refs.addGroupForm.validate((valid) => {
                    if (valid) {
                        let self = this;
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.addGroupLoading = true;
                            //NProgress.start();
                            let params = {
                                project_id: Number(this.$route.params.project_id),
                                name: self.addGroupForm.firstgroup
                            };
                            let headers = {
                                "Content-Type": "application/json",
                                Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                            };
                            addApiGroup(headers, params).then(_data => {
                                let {msg, code, data} = _data;
                                self.addGroupLoading = false;
                                    if (code === '999999') {
                                        self.$message({
                                            message: '添加成功',
                                            center: true,
                                            type: 'success'
                                        });
                                        self.$refs['addGroupForm'].resetFields();
                                        self.addGroupFormVisible = false;
                                        self.getApiGroup();
                                        self.init()
                                    } else if (code === '999997'){
                                        self.$message.error({
                                            message: msg,
                                            center: true,
                                        })
                                    } else {
                                        self.$message.error({
                                            message: msg,
                                            center: true,
                                        });
                                        self.$refs['addGroupForm'].resetFields();
                                        self.addGroupFormVisible = false;
                                        self.getApiGroup();
                                        self.init()
                                    }
                            })
                        });
                    }
                });
            },
            // 修改分组
            editFirstGroupSubmit(){
                this.$refs.editFirstGroupForm.validate((valid) => {
                    if (valid) {
                        let self = this;
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.editFirstGroupLoading = true;
                            let params = {
                                project_id: Number(this.$route.params.project_id),
                                name: self.editFirstGroupForm.secondFirstGroup,
                                id: self.editFirstGroupForm.second_id
                            };
                            let headers = {
                                "Content-Type": "application/json",
                                Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                            };
                            updateApiGroup(headers, params).then(_data => {
                                let {msg, code, data} = _data;
                                self.editFirstGroupLoading = false;
                                if (code === '999999') {
                                    self.$message({
                                        message: '修改成功',
                                        center: true,
                                        type: 'success'
                                    });
                                    self.$refs['editFirstGroupForm'].resetFields();
                                    self.editFirstGroupFormVisible = false;
                                    self.getApiGroup();
                                    self.init()
                                } else if (code === '999997'){
                                    self.$message.error({
                                        message: msg,
                                        center: true,
                                    })
                                } else {
                                    self.$message.error({
                                        message: msg,
                                        center: true,
                                    });
                                    self.$refs['editFirstGroupForm'].resetFields();
                                    self.editFirstGroupFormVisible = false;
                                    self.getApiGroup();
                                    self.init()
                                }
                            })
                        });
                    }
                });
            },
            //删除分组
            handleDelFirst: function (id) {
                this.$confirm('确认删除该记录吗?', '提示', {
                    type: 'warning'
                }).then(() => {
                    //NProgress.start();
                    let self = this;
                    let params = {
                        id: Number(id),
                        project_id: Number(this.$route.params.project_id)
                    };
                    let headers = {
                        "Content-Type": "application/json",
                        Authorization: 'Token ' + JSON.parse(sessionStorage.getItem('token'))
                    };
                    delApiGroup(headers, params).then(_data => {
                        let {msg, code, data} = _data;
                        if (code === '999999') {
                            self.$message({
                                message: '删除成功',
                                center: true,
                                type: 'success'
                            })
                        } else {
                            self.$message.error({
                                message: msg,
                                center: true,
                            })
                        }
                        self.getApiGroup()
                    })
                })
            }
        },
        mounted() {
            this.getApiGroup();
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