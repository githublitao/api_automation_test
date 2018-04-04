<template>
    <!--列表-->
    <el-row class="member-manage">
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
        },
        mounted() {
            this.getProjectMember();

        }
    }
</script>

<style lang="scss" scoped>
    .member-manage {
        margin: 35px;
    }
</style>