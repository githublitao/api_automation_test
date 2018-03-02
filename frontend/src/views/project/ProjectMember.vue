<template>
     <!--列表-->
    <el-row class="member">
        <el-col :span="24">
            <el-table :data="project" highlight-current-row v-loading="listLoading" style="width: 100%;">
                <el-table-column prop="name" label="项目名称" min-width="30%" sortable>
                    <template slot-scope="scope">
                        <el-icon name="name"></el-icon>
                        <router-link :to="{ name: '项目概况', params: {project_id: scope.row.id}}" style='text-decoration: none;color: #000000;'>{{ scope.row.name }}</router-link>
                    </template>
                </el-table-column>
                <el-table-column prop="version" label="项目版本" min-width="12%" sortable>
                </el-table-column>
                <el-table-column prop="type" label="类型" min-width="9%" sortable>
                </el-table-column>
                <el-table-column prop="LastUpdateTime" label="最后修改时间" min-width="16%" sortable>
                </el-table-column>
                <el-table-column prop="status" label="状态" min-width="9%" sortable>
                    <template slot-scope="scope">
                        {{scope.row.status===true?'启用':'禁用'}}
                    </template>
                </el-table-column>
            </el-table>
        </el-col>
    </el-row>
</template>

<script>
import { test } from '../../api/api'
import $ from 'jquery'
export default {
    data() {
        return {
            filters: {
                name: ''
            },
            project: [],
            total: 0,
            page: 1,
            listLoading: false,
        }    
    },
methods: {
        // 获取HOST列表
        getGlobalHost() {
            this.listLoading = true;
            var self = this
            $.ajax({
                type: "get",
                url: test+"/api/global/host_total",
                async: true,
                data: { project_id: this.$route.params.project_id, page: self.page, name: self.filters.name},
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
    },
    mounted() {
        this.getGlobalHost();
        
    }
}
</script>

<style>
    .member {
        width: 500px;
        border: 25px solid green;
        padding: 25px;
        margin: 25px;
    }
</style>