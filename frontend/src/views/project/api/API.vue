<template>
    <section>
    <el-row :span="24" class="row-title">
        <el-col :span="4">
            <el-button class="addGroup" @click="handleAddGroup">新增分组</el-button>
                <router-link :to="{ name: '快速测试', params: {project_id: this.$route.params.project_id}}" style='text-decoration: none;color: aliceblue;'>
                    <el-button class="addGroup" @click="fastTest">快速测试</el-button>
                </router-link>
            <div class="api-title"><strong>接口分组</strong></div>
            <div class="api-title" style="cursor:pointer;">
                <strong @click="group">所有接口</strong>
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
                                        <el-dropdown-item @click.native="handleDelFirst(item.id)">删除</el-dropdown-item>
                                        <el-dropdown-item @click.native="handleEditFirstGroup(item.id, item.name)">修改</el-dropdown-item>
                                    </el-dropdown-menu>
                                </el-dropdown>
                            </template>
							<el-menu-item v-for="child in item.secondGroup" :index="child.id+''" :key="child.id" class="group" style="padding-right: 10px;">
                                {{child.name}}
                                    <el-dropdown trigger="hover" class="editGroup">
				                        <i class="el-icon-more"></i>
                                        <el-dropdown-menu slot="dropdown">
                                            <el-dropdown-item @click.native="handleDelSecond(item.id, child.id)">删除</el-dropdown-item>
                                            <el-dropdown-item @click.native="handleEditGroup(item.id, child.id, child.name)">修改</el-dropdown-item>
                                        </el-dropdown-menu>
                                    </el-dropdown>
                            </el-menu-item>
						</el-submenu>
					</template>
				</el-menu>
			</aside>
        </el-col>
    	<!--新增-->
        <el-dialog title="新增分组" v-model="addGroupFormVisible" :close-on-click-modal="false">
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
        <!--编辑-->
        <el-dialog title="编辑分组" v-model="editGroupFormVisible" :close-on-click-modal="false">
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
            <section :class="apiView? 'api-view-a':'api-view-b'">
                <!--工具条-->
                <el-col :span="24" style="height: 46px">
                    <el-form :inline="true" :model="filters">
                        <el-form-item>
                            <el-input v-model="filters.name" placeholder="名称" @keyup.enter.native="getApiList"></el-input>
                        </el-form-item>
                        <el-form-item>
                            <el-button type="primary" @click="getApiList">查询</el-button>
                        </el-form-item>
                        <el-form-item>
                            <el-button type="primary">新增</el-button>
                        </el-form-item>
                        <el-form-item>
                            <el-button type="primary">修改分组</el-button>
                        </el-form-item>
                    </el-form>
                </el-col>

                <!--列表-->
                <el-table :data="api" highlight-current-row v-loading="listLoading" @selection-change="selsChange" style="width: 100%;">
                    <el-table-column type="selection" min-width="5%">
                    </el-table-column>
                    <el-table-column prop="name" label="接口名称" min-width="17%" sortable>
                        <template slot-scope="scope">
                            <el-icon name="name"></el-icon>
                            <router-link :to="{ name: '项目概况', params: {project_id: scope.row.id}}" style='text-decoration: none;color: #000000;'>{{ scope.row.name }}</router-link>
                        </template>
                    </el-table-column>
                    <el-table-column prop="requestType" label="请求方式" min-width="10%" sortable>
                    </el-table-column>
                    <el-table-column prop="apiAddress" label="接口地址" min-width="24%" sortable>
                    </el-table-column>
                    <el-table-column prop="userUpdate" label="最近更新者" min-width="9%" sortable>
                    </el-table-column>
                    <el-table-column prop="lastUpdateTime" label="更新日期" min-width="16%" sortable>
                    </el-table-column>
                    <el-table-column label="操作" min-width="19%">
                        <template slot-scope="scope">
                            <el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
                            <el-button type="info" size="small">修改</el-button>
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
            <div :class="apiView? 'api-view-b':'api-view-a'">
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
            ],
            secondGroup: [
                { required: true, message: '请输入子分组名称', trigger: 'blur' }
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
            ],
            secondGroup: [
                { required: true, message: '请输入子分组名称', trigger: 'blur' }
            ]
        },
        //编辑界面数据
        editGroupForm: {
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
        // 获取api分组
        getApiGroup() {
            var self = this
            $.ajax({
                type: "get",
                url: test+"/api/api/group",
                async: true,
                data: { project_id: this.$route.params.project_id},
                headers: {
                    Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                },
                timeout: 5000,
                success: function(data) {
                    if (data.code === '999999') {
                        self.groupData = data.data
                        for (var i=0; i<self.groupData.length; i++) {
                            var person = { value: self.groupData[i].id, label: self.groupData[i].name}
                            self.options.push(person)
                        };
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
            console.log(first_id, second_id, name)
            this.editGroupForm.firstgroup = first_id
            this.editGroupForm.secondGroup = name
            this.editGroupForm.second_id = second_id
        },
        handleEditFirstGroup(first_id, name) {
            this.editGroupFormVisible = true;
            this.editGroupForm.second_id = first_id
            this.editGroupForm.secondGroup = name
        },
        addGroupSubmit() {
            this.$refs.addGroupForm.validate((valid) => {
				if (valid) {
				    let self = this
					this.$confirm('确认提交吗？', '提示', {}).then(() => {
						self.addGroupLoading = true;
                        //NProgress.start();
                        $.ajax({
                            type: "post",
                            url: test+"/api/api/add_group",
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
                                    })
                                    self.$refs['addGroupForm'].resetFields();
                                    self.addGroupFormVisible = false;  
                                    self.getApiGroup()
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
                                    })
                                    self.$refs['addGroupForm'].resetFields();
                                    self.addGroupFormVisible = false;  
                                    self.getApiGroup()
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
				    let self = this
					this.$confirm('确认提交吗？', '提示', {}).then(() => {
						self.editGroupLoading = true;
                        //NProgress.start();
                        if (!self.editGroupForm.firstgroup) {
                            self.editGroupForm.firstgroup = self.editGroupForm.second_id
                            self.editGroupForm.second_id = ''
                        }
                        $.ajax({
                            type: "post",
                            url: test+"/api/api/update_name_group",
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
                                        message: '添加成功',
                                        center: true,
                                        type: 'success'
                                    })
                                    self.$refs['editGroupForm'].resetFields();
                                    self.editGroupFormVisible = false;  
                                    self.getApiGroup()
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
                                    })
                                    self.$refs['editGroupForm'].resetFields();
                                    self.editGroupFormVisible = false;  
                                    self.getApiGroup()
                                    self.init()
                                }
                            },
                        })
					});
				}
			});
        },
        //删除一级分组
		handleDelFirst: function (id) {
			this.$confirm('确认删除该记录吗?', '提示', {
				type: 'warning'
			}).then(() => {
				//NProgress.start();
				let self = this
				$.ajax({
                type: "post",
                url: test+"/api/api/del_group",
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
                    self.getApiGroup()
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
				let self = this
				$.ajax({
                type: "post",
                url: test+"/api/api/del_group",
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
                    self.getApiGroup()
                },
            })

			}).catch(() => {
			});
		},
    // 获取项目列表
		getApiList() {
			this.listLoading = true;
			var self = this
			$.ajax({
				type: "get",
				url: test+"/api/api/api_list",
				async: true,
				data: { project_id: this.$route.params.project_id, page: self.page},
				headers: {
					Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
				},
				timeout: 5000,
				success: function(data) {
					self.listLoading = false
					if (data.code === '999999') {
						self.total = data.data.total,
						self.api = data.data.data
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
		//删除
		handleDel: function (index, row) {
			this.$confirm('确认删除该记录吗?', '提示', {
				type: 'warning'
			}).then(() => {
				this.listLoading = true;
				//NProgress.start();
				let self = this
				$.ajax({
                type: "post",
                url: test+"/api/api/del_api",
                async: true,
                data: { project_id: this.$route.params.project_id, api_ids: row.id },
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
                    self.getApiList()
                },
            })

			}).catch(() => {
			});
		},
	    handleCurrentChange(val) {
            this.page = val;
            this.getApiList()
        },
		selsChange: function (sels) {
			this.sels = sels;
		},
		//批量删除
		batchRemove: function () {
			var ids = this.sels.map(item => item.id).toString();
			let self = this
			this.$confirm('确认删除选中记录吗？', '提示', {
				type: 'warning'
			}).then(() => {
				self.listLoading = true;
				//NProgress.start();
                $.ajax({
                    type: "post",
                    url: test+"/api/api/del_api",
                    async: true,
                    data:{ project_id: this.$route.params.project_id, api_ids: ids},
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: function(data) {
                        self.listLoading = false
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
                        self.getApiList()
                    },
                })
			}).catch(() => {

			});
		},
        fastTest() {
            this.apiView = false
        },
        group() {
            this.apiView = true
        }
    },
    mounted() {
        this.getApiGroup();
        this.getApiList();
        
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