<template>
    <section>
        <div style="position: absolute;top: -50px;font-size: 20px;padding-left: 10px"><strong>Start Time： 2018-04-03 10:27:00</strong></div>
        <div style="position: absolute;top: -10px;font-size: 20px;padding-left: 10px"><strong>End Time： 2018-04-04 10:27:00</strong></div>
        <div class="number-pass" style="background-color: #43CD80;">
            <div style="font-size: 40px;padding-top: 15px">{{pass}}</div>
            <div>Passed</div>
        </div>
        <div class="number-fail" style="background-color: #DC143C;">
            <div style="font-size: 40px;padding-top: 15px">{{fail}}</div>
            <div>Failed</div>
        </div>
        <div class="number-not_run">
            <div style="font-size: 40px;padding-top: 15px">{{not_run}}</div>
            <div>Not Run</div>
        </div>
        <div class="number-error" style="background-color: #DC143C;">
            <div style="font-size: 40px;padding-top: 15px">{{error}}</div>
            <div>Error</div>
        </div>
        <div class="number-total">
            <div style="font-size: 40px;padding-top: 15px">{{total}}</div>
            <div>Total</div>
        </div>
        <div style="padding-left: 10px; padding-top: 45px">
            <el-table :data="tableData" v-loading="listLoading" :row-style="tableRowStyle">
                <el-table-column type="index" label="#">
                </el-table-column>
                <el-table-column prop="name" label="接口名称" min-width="20%" sortable show-overflow-tooltip>
                </el-table-column>
                <el-table-column prop="automationTestCase" label="用例名称" min-width="20%" sortable show-overflow-tooltip>
                </el-table-column>
                <el-table-column prop="requestType" label="请求方法" min-width="8%" sortable show-overflow-tooltip>
                </el-table-column>
                <el-table-column prop="address" label="请求地址" min-width="30%" sortable show-overflow-tooltip>
                </el-table-column>
                <el-table-column prop="examineType" label="校验方式" min-width="12%" sortable show-overflow-tooltip>
                    <template slot-scope="scope">
                        <a v-if="scope.row.examineType === 'no_check'">不校验</a>
                        <a v-if="scope.row.examineType === 'only_check_status'">校验http状态</a>
                        <a v-if="scope.row.examineType === 'json'">JSON校验</a>
                        <a v-if="scope.row.examineType === 'entirely_check'">完全校验</a>
                        <a v-if="scope.row.examineType === 'Regular_check'">正则校验</a>
                    </template>
                </el-table-column>
                <el-table-column prop="result" label="结果" min-width="10%" :filters="resultFilter" :filter-method="filterHandler">
                    <template slot-scope="scope">
                        {{scope.row.result? scope.row.result: "NotRun"}}
                    </template>
                </el-table-column>
            </el-table>
        </div>
    </section>
</template>

<script>
    import { test } from '../../../api/api'
    import $ from 'jquery'
    export default {
        name: "test-report",
        data(){
            return {
                pass: 11,
                fail: 11,
                not_run: 11,
                error: 11,
                total: 44,
                start_time: "",
                end_time: "",
                listLoading: false,
                resultFilter: [
                    {text: 'ERROR', value: 'ERROR'},
                    {text: 'FAIL', value: 'FAIL'},
                    {text: 'NotRun', value: 'NotRun'},
                    {text: 'PASS', value: 'PASS'},
                ],
                tableData: []
            }
        },
        methods: {
            tableRowStyle(row) {
                if (row.result === 'ERROR' || row.result === 'FAIL') {
                    return "background-color: #DC143C;"
                } else if(row.result === 'TimeOut'){
                    return "background-color: #FFE4C4;"
                }
              },
            filterHandler(value, row, column) {
                return row.result === value;
            },
            getTestResult() {
                this.listLoading = true;
                let self = this;
                $.ajax({
                    type: "get",
                    url: test + "/api/automation/test_report",
                    async: true,
                    data: { project_id: this.$route.params.project_id},
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: function(data) {
                        self.listLoading = false;
                        if (data.code === '999999') {
                            self.total = data.data.total;
                            self.pass = data.data.pass;
                            self.fail = data.data.fail;
                            self.not_run = data.data.NotRun;
                            self.error = data.data.error;
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
            this.getTestResult();

        }
    }
</script>

<style scoped>
    .number-pass {
        border-radius: 25px;
        position: absolute;
        padding-right: 10px;
        padding-left: 10px;
        height: 100px;
        box-sizing: border-box;
        color: #fff;
        font-size: 25px;
        text-align: center;
        width: 6%;
        top: -70px;
        right: 26%;
    }
    .number-fail {
        border-radius: 25px;
        position: absolute;
        height: 100px;
        box-sizing: border-box;
        color: #fff;
        font-size: 25px;
        text-align: center;
        width: 6%;
        top: -70px;
        right: 19.5%;
    }
    .number-not_run {
        border-radius: 25px;
        border: 1px solid #C4C4C4;
        position: absolute;
        height: 100px;
        box-sizing: border-box;
        /*color: #fff;*/
        font-size: 25px;
        text-align: center;
        width: 6%;
        top: -70px;
        right: 13%;
    }
    .number-error {
        border-radius: 25px;
        position: absolute;
        height: 100px;
        box-sizing: border-box;
        color: #fff;
        font-size: 25px;
        text-align: center;
        width: 6%;
        top: -70px;
        right: 6.5%;
    }
    .number-total {
        border-radius: 25px;
        border: 1px solid #C4C4C4;
        position: absolute;
        height: 100px;
        box-sizing: border-box;
        /*color: #fff;*/
        font-size: 25px;
        text-align: center;
        width: 6%;
        top: -70px;
        right: 0px;
    }
</style>