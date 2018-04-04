<template>
    <el-row class="dynamic-manage">
        <el-col :span="24">
            <el-table :data="tableData" stripe style="width: 100%" v-loading="listLoading">
                <el-table-column type="index" label="#" min-width="10%">
                </el-table-column>
                <el-table-column prop="time" label="操作时间" min-width="13%">
                </el-table-column>
                <el-table-column prop="user" label="操作人" min-width="15%">
                </el-table-column>
                <el-table-column prop="description" label="描述" min-width="47%">
                </el-table-column>
            </el-table>
            <!--工具条-->
            <el-pagination layout="prev, pager, next" @current-change="handleCurrentChange" :page-size="20" :page-count="total" style="float:right;">
            </el-pagination>
        </el-col>
    </el-row>
</template>

<script>
    import { test } from '../../../../api/api'
    import $ from 'jquery'
    export default {
        data() {
            return {
                tableData: [],
                total: 0,
                page: 1,
                listLoading: false,
            }
        },
        methods: {
            handleCurrentChange(val) {
                this.page = val;
                this.getApiDynamic()
            },
            // 获取项目动态
            getApiDynamic() {
                this.listLoading = true;
                let self = this;
                $.ajax({
                    type: "get",
                    url: test+"/api/api/operation_history",
                    async: true,
                    data: { project_id: this.$route.params.project_id, page: self.page, api_id: this.$route.params.api_id},
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: function(data) {
                        self.listLoading = false;
                        if (data.code === '999999') {
                            self.total = data.data.total;
                            self.tableData = data.data.data
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
            this.getApiDynamic();

        }
    }
</script>

<style lang="scss" scoped>

</style>
