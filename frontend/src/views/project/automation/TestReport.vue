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
            <el-table :data="tableData" stripe style="width: 100%" v-loading="listLoading">
                <el-table-column type="index" label="#">
                </el-table-column>
                <el-table-column prop="type" label="接口名称">
                </el-table-column>
                <el-table-column prop="operationObject" label="用例名称">
                </el-table-column>
                <el-table-column prop="operationUser" label="请求方法">
                </el-table-column>
                <el-table-column prop="operationUser" label="请求地址">
                </el-table-column>
                <el-table-column prop="operationUser" label="校验方式">
                </el-table-column>
                <el-table-column prop="description" label="结果">
                </el-table-column>
            </el-table>
        </div>
    </section>
</template>

<script>
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
                tableData: []
            }
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