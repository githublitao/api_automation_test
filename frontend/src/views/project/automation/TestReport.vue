<template>
    <section>
        <el-button class="return-list" @click="back"><i class="el-icon-d-arrow-left" style="margin-right: 5px"></i>用例列表</el-button>
        <div class="number-pass" style="background-color: #43CD80;">
            <div style="font-size: 40px;padding-top: 15px">{{pass}}</div>
            <div>Passed</div>
        </div>
        <div class="number-fail" style="background-color: #DC143C;">
            <div style="font-size: 40px;padding-top: 15px">{{fail}}</div>
            <div>Failed</div>
        </div>
        <div class="number-error" style="background-color: #DC143C;">
            <div style="font-size: 40px;padding-top: 15px">{{error}}</div>
            <div>Error</div>
        </div>
        <div class="number-total">
            <div style="font-size: 40px;padding-top: 15px">{{total}}</div>
            <div>Total</div>
        </div>
        <div>
            <el-table :data="tableData" v-loading="listLoading" :row-style="tableRowStyle" @expand-change="showJson">
                <el-table-column type="expand">
                    <template slot-scope="props">
                        <el-form label-position="left" inline class="demo-table-expand">
                            <el-form-item label="名称: ">
                                <span>{{ props.row.name }}</span>
                            </el-form-item>
                            <el-form-item>
                            </el-form-item>
                            <el-form-item label="测试环境： ">
                                <span>{{ props.row.host }}</span>
                            </el-form-item>
                            <el-form-item label="接口地址： ">
                                <span>{{ props.row.apiAddress }}</span>
                            </el-form-item>
                            <el-form-item label="请求方式： ">
                                <span>{{ props.row.requestType }}</span>
                            </el-form-item>
                            <el-form-item label="测试结果： ">
                                <span>{{ props.row.result }}</span>
                            </el-form-item>
                            <el-form-item label="请求参数： ">
                                <span style="word-break: break-all;overflow:auto;overflow-x:hidden">{{ props.row.parameter }}</span>
                            </el-form-item>
                            <el-form-item label="测试时间">
                                <span>{{ props.row.testTime}}</span>
                            </el-form-item>
                            <el-form-item label="返回结果： ">
                                <span>
                                    <pre style="word-break: break-all;overflow:auto;overflow-x:hidden" v-highlightA><code>{{props.row.responseData}}</code></pre>
                                </span>
                            </el-form-item>
                        </el-form>
                    </template>
                </el-table-column>
                <el-table-column type="index" label="#" width="100">
                </el-table-column>
                <el-table-column prop="name" label="接口名称" min-width="27%" sortable show-overflow-tooltip>
                </el-table-column>
                <el-table-column prop="automationTestCase" label="用例名称" min-width="29%" sortable show-overflow-tooltip>
                </el-table-column>
                <el-table-column prop="apiAddress" label="请求地址" min-width="20%" sortable show-overflow-tooltip>
                </el-table-column>
                <el-table-column prop="examineType" label="校验方式" min-width="13%" sortable show-overflow-tooltip>
                    <template slot-scope="scope">
                        <a v-if="scope.row.examineType === 'no_check'">不校验</a>
                        <a v-if="scope.row.examineType === 'only_check_status'">校验http状态</a>
                        <a v-if="scope.row.examineType === 'json'">JSON校验</a>
                        <a v-if="scope.row.examineType === 'entirely_check'">完全校验</a>
                        <a v-if="scope.row.examineType === 'Regular_check'">正则校验</a>
                    </template>
                </el-table-column>
                <el-table-column prop="result" label="结果" min-width="11%" :filters="resultFilter" :filter-method="filterHandler">
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
                pass: "",
                fail: "",
                not_run: "",
                error: "",
                total: "",
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
            back(){
                this.$router.go(-1); // 返回上一层
            },
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
                            self.tableData.forEach((i) =>{
                                i["responseData"] = JSON.parse(i["responseData"].replace(/'/g, "\"").replace(/None/g, "null").replace(/True/g, "true").replace(/False/g, "false"));
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
        height: 100px;
        box-sizing: border-box;
        color: #fff;
        font-size: 25px;
        text-align: center;
        width: 100px;
        top: -70px;
        right: 350px;
    }
    .number-fail {
        border-radius: 25px;
        border: 1px solid #C4C4C4;
        position: absolute;
        height: 100px;
        box-sizing: border-box;
        /*color: #fff;*/
        font-size: 25px;
        text-align: center;
        width: 100px;
        top: -70px;
        right: 240px;
    }
    .number-error {
        border-radius: 25px;
        position: absolute;
        height: 100px;
        box-sizing: border-box;
        color: #fff;
        font-size: 25px;
        text-align: center;
        width: 100px;
        top: -70px;
        right: 130px;
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
        width: 100px;
        top: -70px;
        right: 20px;
    }
    .demo-table-expand {
        font-size: 0;
      }
      .demo-table-expand label {
          width: 90px;
          color: #99a9bf;
      }
      .demo-table-expand .el-form-item {
          margin-right: 0;
          margin-bottom: 0;
          width: 50%;
      }
    .return-list {
        margin-top: 0px;
        margin-bottom: 10px;
        border-radius: 25px;
    }
</style>