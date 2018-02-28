<template>
	<section>
		<!--工具条-->
		<el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
			<el-form :inline="true" :model="filters">
				<el-form-item>
					<el-input v-model="filters.name" placeholder="名称" @keyup.enter.native="getProjectList"></el-input>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" @click="getProjectList">查询</el-button>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" @click="handleAdd">新增</el-button>
				</el-form-item>
			</el-form>
		</el-col>

		<!--列表-->
		<el-table :data="project" highlight-current-row v-loading="listLoading" @selection-change="selsChange" style="width: 100%;">
			<el-table-column type="selection" width="55">
			</el-table-column>
			<el-table-column prop="name" label="项目名称" width="700" sortable>
			</el-table-column>
			<el-table-column prop="version" label="项目版本" width="150" sortable>
			</el-table-column>
			<el-table-column prop="type" label="类型" width="100" sortable>
			</el-table-column>
			<el-table-column prop="LastUpdateTime" label="最后修改时间" width="220" sortable>
			</el-table-column>
			<el-table-column prop="status" label="状态" width="190" sortable>
			    <template slot-scope="scope">
			        {{scope.row.status===true?'启用':'禁用'}}
                </template>
			</el-table-column>
            <el-table-column label="操作" width="215">
                <template slot-scope="scope">
                    <el-button size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
                    <el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
                    <el-button type="info" size="small" @click="handleChangeStatus(scope.$index, scope.row)">{{scope.row.status===false?'启用':'禁用'}}</el-button>
                </template>
            </el-table-column>
		</el-table>

		<!--工具条-->
		<el-col :span="24" class="toolbar">
			<el-button type="danger" @click="batchRemove" :disabled="this.sels.length===0">批量删除</el-button>
			<el-pagination layout="prev, pager, next" @current-change="handleCurrentChange" :page-size="20" :page-count="total" style="float:right;">
			</el-pagination>
		</el-col>

		<!--编辑界面-->
		<el-dialog title="编辑" v-model="editFormVisible" :close-on-click-modal="false">
		    <el-form :model="editForm" label-width="80px"  :rules="editFormRules" ref="editForm">
                <el-form-item label="项目名称" prop="name">
                    <el-input v-model="editForm.name" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="类型" prop='type'>
                    <el-radio-group v-model="editForm.type">
                        <el-radio label="Web">Web</el-radio>
                        <el-radio label="App">App</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="版本号" prop='version'>
                    <el-input v-model="editForm.version" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="描述">
                    <el-input type="textarea" :rows="7" v-model="editForm.description"></el-input>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click.native="editFormVisible = false">取消</el-button>
                <el-button type="primary" @click.native="editSubmit" :loading="editLoading">提交</el-button>
            </div>
		</el-dialog>

		<!--新增界面-->
		<el-dialog title="新增" v-model="addFormVisible" :close-on-click-modal="false">
		    <el-form :model="addForm" label-width="80px" :rules="addFormRules" ref="addForm">
                <el-form-item label="项目名称" prop="name">
                    <el-input v-model="addForm.name" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="类型" prop='type'>
                    <el-radio-group v-model="addForm.type">
                        <el-radio label="Web">Web</el-radio>
                        <el-radio label="App">App</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="版本号" prop='version'>
                    <el-input v-model="addForm.version" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="描述">
                    <el-input type="textarea" :rows="7" v-model="addForm.description"></el-input>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click.native="addFormVisible = false">取消</el-button>
                <el-button type="primary" @click.native="addSubmit" :loading="addLoading">提交</el-button>
            </div>
		</el-dialog>
	</section>
</template>

<script>
	//import NProgress from 'nprogress'
import { test } from '../api/api'
import $ from 'jquery'
export default {
	data() {
		return {
			filters: {
				name: ''
			},
			radio: '',
			project: [],
			total: 0,
			page: 1,
			listLoading: false,
			sels: [],//列表选中列

			editFormVisible: false,//编辑界面是否显示
			editLoading: false,
			editFormRules: {
				name: [
					{ required: true, message: '请输入名称', trigger: 'blur' }
				],
				type: [
                    { required: true, message: '请选择类型', trigger: 'blur' }
                ],
				version: [
                    { required: true, message: '请输入版本号', trigger: 'blur' }
                ]
			},
			//编辑界面数据
			editForm: {
			    name: '',
			    version: '',
			    type: '',
			    description: ''
			},

			addFormVisible: false,//新增界面是否显示
			addLoading: false,
			addFormRules: {
				name: [
					{ required: true, message: '请输入名称', trigger: 'blur' }
				],
				type: [
                    { required: true, message: '请选择类型', trigger: 'blur' }
                ],
				version: [
                    { required: true, message: '请输入版本号', trigger: 'blur' }
                ]
			},
			//新增界面数据
			addForm: {
			    name: '',
                version: '',
                type: '',
                description: ''
			}

		}
	},
methods: {
		// 获取项目列表
		getProjectList() {
			this.listLoading = true;
			var self = this
			$.ajax({
				type: "get",
				url: test+"/api/project/project_list",
				async: true,
				data: { page: self.page, name: self.filters.name},
				headers: {
					Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
				},
				timeout: 5000,
				success: function(data) {
					self.listLoading = false
					if (data.code === '999999') {
						self.total = data.data.total,
						self.project = data.data.data
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
                url: test+"/api/project/del_project",
                async: true,
                data: {ids: row.id},
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
                    self.getProjectList()
                },
            })

			}).catch(() => {
			});
		},
		handleChangeStatus: function(index, row) {
		    let self = this
		    this.listLoading = true;
		    if (row.status) {
		        $.ajax({
                    type: "post",
                    url: test+"/api/project/disable_project",
                    async: true,
                    data: { project_id: row.id},
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: function(data) {
                        self.listLoading = false
                        if (data.code === '999999') {
                            self.$message({
                                message: '禁用成功',
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
                    },
                })
		    } else {
		        $.ajax({
                    type: "post",
                    url: test+"/api/project/enable_project",
                    async: true,
                    data: { project_id: row.id},
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: function(data) {
                        self.listLoading = false
                        if (data.code === '999999') {
                            self.$message({
                                message: '启用成功',
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
                    },
                })
		    }
		    self.getProjectList()
		},
	    handleCurrentChange(val) {
            this.page = val;
            this.getProjectList()
        },
		//显示编辑界面
		handleEdit: function (index, row) {
			this.editFormVisible = true;
			this.editForm = Object.assign({}, row);
		},
		//显示新增界面
		handleAdd: function () {
			this.addFormVisible = true;
		},
		//编辑
		editSubmit: function () {
		    let self = this
			this.$refs.editForm.validate((valid) => {
				if (valid) {
					this.$confirm('确认提交吗？', '提示', {}).then(() => {
						self.editLoading = true;
						//NProgress.start();
						$.ajax({
                            type: "post",
                            url: test+"/api/project/update_project",
                            async: true,
                            data: { project_id: self.editForm.id, name: self.editForm.name, type: self.editForm.type, v: self.editForm.version, description: self.editForm.description },
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
                                    })
                                    self.$refs['editForm'].resetFields();
                                    self.editFormVisible = false;  
                                    self.getProjectList()
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
		//新增
		addSubmit: function () {
			this.$refs.addForm.validate((valid) => {
				if (valid) {
				    let self = this
					this.$confirm('确认提交吗？', '提示', {}).then(() => {
						self.addLoading = true;
						//NProgress.start();
                        $.ajax({
                            type: "post",
                            url: test+"/api/project/add_project",
                            async: true,
                            data: { name: self.addForm.name, type: self.addForm.type, v: self.addForm.version, description: self.addForm.description },
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
                                    })
                                    self.$refs['addForm'].resetFields();
                                    self.addFormVisible = false;  
                                    self.getProjectList()
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
                                    self.$refs['addForm'].resetFields();
                                    self.addFormVisible = false;  
                                    self.getProjectList()
                                }
                            },
                        })
					});
				}
			});
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
				let para = { ids: ids };
                $.ajax({
                    type: "post",
                    url: test+"/api/project/del_project",
                    async: true,
                    data:{ids: ids},
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
                        self.getProjectList()
                    },
                })
			}).catch(() => {

			});
		}
	},
	mounted() {
		this.getProjectList();
	}
}

</script>

<style>

</style>