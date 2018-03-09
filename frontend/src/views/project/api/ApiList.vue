<template>
	<section>
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
					<router-link :to="{ name: '新增接口', params: {project_id: this.$route.params.project_id}}" style='text-decoration: none;color: aliceblue;'>
						<el-button type="primary">新增</el-button>
					</router-link>
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
</template>

<script>
import { test } from '../../../api/api'
import $ from 'jquery'
  export default {
    data() {
      return {
        filters: {
            name: ''
        },
        api: [],
        total: 0,
        page: 1,
        listLoading: false,
        sels: [],//列表选中列
      }
    },
methods: {
    // 获取项目列表
		getApiList() {
			this.listLoading = true;
			let self = this;
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
					self.listLoading = false;
					if (data.code === '999999') {
						self.total = data.data.total;
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
				let self = this;
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
			let ids = this.sels.map(item => item.id).toString();
			let self = this;
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
                        self.getApiList()
                    },
                })
			}).catch(() => {

			});
		},
    },
    mounted() {
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