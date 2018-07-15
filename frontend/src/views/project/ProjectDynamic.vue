<template>
    <el-row class="dynamic-manage">
        <el-col :span="24">
            <el-table :data="tableData" stripe style="width: 100%" v-loading="listLoading">
                <el-table-column prop="time" label="操作时间" min-width="13%">
                </el-table-column>
                <el-table-column prop="type" label="类型" min-width="10%">
                </el-table-column>
                <el-table-column prop="operationObject" label="操作对象" min-width="15%">
                </el-table-column>
                <el-table-column prop="operationUser" label="操作人" min-width="15%">
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
    import { getProjectDynamicList } from '../../api/api'
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
                this.getProjectDynamic()
            },
            // 获取项目动态
            getProjectDynamic() {
                this.listLoading = true;
                let self = this;
                let params = {
                    project_id: Number(this.$route.params.project_id),
                    page: self.page
                };
                let headers = {
                    "Content-Type": "application/json",
                    Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                };
                getProjectDynamicList(headers, params).then(_data => {
                    let {msg, code, data} = _data;
                    self.listLoading = false;
                    if (code === '999999') {
                        self.total = data.total;
                        self.tableData = data.data
                    }
                    else {
                        self.$message.error({
                            message: msg,
                            center: true,
                        })
                    }
                })
            },
        },
        mounted() {
            this.getProjectDynamic();

        }
    }
</script>

<style lang="scss" scoped>
    .dynamic-manage {
        margin: 35px;
    }
</style>
