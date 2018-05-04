<template>
    <section>
        <el-button class="return-list" @click="back"><i class="el-icon-d-arrow-left" style="margin-right: 5px"></i>用例列表</el-button>
        <el-button type="primary" @click.native="addOldApi"><i class="el-icon-plus" style="margin-right: 5px"></i>已有接口</el-button>
        <router-link :to="{ name: '添加新接口'}" style='text-decoration: none;color: #000000;'>
            <el-button type="primary"><i class="el-icon-plus" style="margin-right: 5px"></i>新建接口</el-button>
        </router-link>
        <el-button type="primary" @click.native="TestAll"><div>测试全部</div></el-button>
        <el-select v-model="url"  placeholder="测试环境" style="float: right">
            <el-option v-for="(item,index) in Host" :key="index+''" :label="item.name" :value="item.id"></el-option>
        </el-select>
        <el-dialog title="选择创建的API" v-model="searchApiListVisible" :close-on-click-modal="false" >
            <el-row :gutter="10">
                <el-col :span="6">
                    <div style="height:400px;line-height:100px;overflow:auto;overflow-x:hidden;border: 1px solid #e6e6e6">
                        <el-menu default-active="2" class="el-menu-vertical-demo" active-text-color="rgb(32, 160, 255)" :unique-opened="true">
                            <el-menu-item index="-1" @click.native="getApiList([])"><i class="el-icon-menu"></i>所有接口</el-menu-item>
                            <template v-for="(item,index) in groupData">
                                <el-submenu :index="index+''" :key="item.id" class="group">
                                    <template slot="title">{{item.name}}
                                    </template>
                                    <template v-for="child in item.secondGroup">
                                        <el-menu-item class="group" style="padding-right: 10px;" :index="child.id+''" @click.native="getApiList([item.id, child.id])">
                                            {{child.name }}
                                        </el-menu-item>
                                    </template>
                                </el-submenu>
                            </template>
                        </el-menu>
                    </div>
                </el-col>
                <el-col :span="18">
                    <el-table :data="searchApiList" highlight-current-row v-loading="apiListLoading"
                              style="width: 100%;" :show-header="false" max-height="400" @selection-change="selsChange">
                        <el-table-column type="selection" width="55">
                        </el-table-column>
                        <el-table-column prop="name" label="名称" min-width="25%" sortable>
                        </el-table-column>
                        <el-table-column prop="requestType" label="HTTP方式" min-width="15%" sortable>
                        </el-table-column>
                        <el-table-column prop="apiAddress" label="地址" min-width="60%" sortable>
                        </el-table-column>
                    </el-table>
                </el-col>
            </el-row>
            <el-col :span="24" class="toolbar">
                <el-pagination layout="prev, pager, next" @current-change="handleCurrentChangeApi" :page-size="20" :page-count="total" style="float:right;">
                </el-pagination>
            </el-col>
            <div slot="footer" class="dialog-footer">
                <el-button @click.native="searchApiListVisible = false">取消</el-button>
                <el-button type="primary" @click.native="addOldApiSubmit" :loading="searchApi">提交</el-button>
            </div>
        </el-dialog>
        <el-table :data="ApiList" highlight-current-row v-loading="listLoading" style="width: 100%;">
            <el-table-column type="index" width="55">
            </el-table-column>
            <el-table-column prop="name" label="接口名称" min-width="20%" sortable show-overflow-tooltip>
                <template slot-scope="scope">
                    <el-icon name="name"></el-icon>
                    <router-link :to="{ name: '修改接口', params: {api_id: scope.row.id}}" style='text-decoration: none;color: #000000;'>{{ scope.row.name }}
                    </router-link>
                </template>
            </el-table-column>
            <el-table-column prop="address" label="接口地址" min-width="50%" sortable show-overflow-tooltip>
                <template slot-scope="scope">
                    <span class="HttpStatus">{{scope.row.requestType}}</span><span style="font-size: 16px">{{scope.row.address}}</span>
                </template>
            </el-table-column>
            <el-table-column prop="result" label="测试结果" min-width="10%" sortable show-overflow-tooltip>
                <template slot-scope="scope">
                    <span v-show="!scope.row.result">尚无测试结果</span>
                    <span v-show="scope.row.result==='success'" style="color: #11b95c;cursor:pointer;" @click="resultShow(scope.row)">成功,查看详情</span>
                    <span v-show="scope.row.result==='fail'" style="color: #cc0000;cursor:pointer;" @click="resultShow(scope.row)">失败,查看详情</span>
                    <span v-show="scope.row.result==='timeout'" style="color: #cc0000;cursor:pointer;" @click="resultShow(scope.row)">请求超时</span>
                </template>
            </el-table-column>
            <el-table-column label="操作" min-width="20%">
                <template slot-scope="scope">
                    <el-button type="primary" size="small" @click="Test(scope.$index, scope.row)">测试</el-button>
                    <router-link :to="{ name: '修改接口', params: {api_id: scope.row.id}}" style='text-decoration: none;color: #000000;'>
                        <el-button size="small">修改</el-button>
                    </router-link>
                    <el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
                </template>
            </el-table-column>
        </el-table>
        <el-col :span="24" class="toolbar">
            <el-pagination layout="prev, pager, next" @current-change="handleCurrentChange" :page-size="20" :page-count="total" style="float:right;">
            </el-pagination>
        </el-col>
        <el-dialog title="测试结果" v-model="TestResult" :close-on-click-modal="false">
            <div style="height:700px;overflow:auto;overflow-x:hidden;border: 1px solid #e6e6e6">
                <div style="font-size: 25px;" class="resultStyle">{{result.name}}</div>
                <div class="lin"></div>
                <div class="resultStyle">请求地址:&nbsp&nbsp{{result.url}}</div>
                <div class="resultStyle">请求方式:&nbsp&nbsp{{result.requestType}}</div>
                <div class="resultStyle">状态码:&nbsp&nbsp{{result.statusCode}}</div>
                <div class="resultStyle" style="padding-bottom: 10px">请求时间:&nbsp&nbsp{{result.testTime}}</div>
                <div class="lin"></div>
                <div style="font-size: 25px;" class="resultStyle">请求头部</div>
                <div v-for="(item,value) in result.header" class="resultStyle">{{value}}:&nbsp&nbsp{{item}}</div>
                <div class="lin" style="margin-top: 10px"></div>
                <div style="font-size: 25px;" class="resultStyle">请求参数</div>
                <div class="resultStyle" style="padding-bottom: 10px">{{result.parameter}}</div>
                <div class="lin"></div>
                <div style="font-size: 25px;" class="resultStyle">返回结果</div>
                <div class="resultStyle">HTTP状态码:&nbsp&nbsp{{result.statusCode}}</div>
                <div class="resultStyle">匹配规则:&nbsp&nbsp{{result.examineType}}</div>
                <div class="resultStyle">规则内容</div>
                <div v-show="result.data" class="resultStyle" style="overflow:auto;overflow-x:hidden;border: 1px solid #e6e6e6;padding: 10px;width: 90%;word-break: break-all;line-height:25px"><span>{{result.data}}</span></div>
                <div v-show="!result.data" class="resultStyle" style="overflow:auto;overflow-x:hidden;border: 1px solid #e6e6e6;padding: 10px;width: 90%;word-break: break-all;line-height:25px;text-align: center">无校验规则</div>
                <div style="font-size: 25px;" class="resultStyle">实际结果</div>
                <div class="resultStyle">HTTP状态码:&nbsp&nbsp{{result.httpStatus}}</div>
                <div class="resultStyle">实际返回内容</div>
                <div v-show="result.responseData" class="resultStyle" style="overflow:auto;overflow-x:hidden;border: 1px solid #e6e6e6;padding: 10px;width: 90%;word-break: break-all;line-height:25px">{{result.responseData}}</div>
                <div v-show="!result.responseData" class="resultStyle" style="overflow:auto;overflow-x:hidden;border: 1px solid #e6e6e6;padding: 10px;width: 90%;word-break: break-all;line-height:25px;text-align: center">无返回内容</div>
            </div>
        </el-dialog>
    </section>
</template>

<script>
    import { test } from '../../../api/api'
    import $ from 'jquery'
    import moment from "moment"
    export default {
        data() {
            return{
                project: "",
                case: "",
                ApiList: [],
                listLoading: false,
                searchName: "",
                total: 0,
                url: '',
                Host: [],
                searchApiListVisible: false,
                searchApi: false,
                searchApiList: [],
                groupData: [],
                apiListLoading: false,
                apiTotal: 0,
                pageApi: 1,
                sels: [],//列表选中列
                TestResult: false,
                result: {},
                taskVShow: false,
                editLoading: false,
                delLoading: false,
                disDel: true,
                pickerOptions1: {
                    disabledDate(time) {
                        return time.getTime() < Date.now() - 8.64e7;
                    }
                },
                pickerOptions2: {
                    disabledDate(time) {
                        return time.getTime() < Date.now() - 8.64e7;
                    },
                    shortcuts: [{
                        text: '最近一周',
                        onClick(picker) {
                            const end = new Date();
                            const start = new Date();
                            end.setTime(end.getTime() + 3600 * 1000 * 24 * 7);
                            picker.$emit('pick', [start, end]);
                        }
                    }, {
                        text: '最近一个月',
                        onClick(picker) {
                            const end = new Date();
                            const start = new Date();
                            end.setTime(end.getTime() + 3600 * 1000 * 24 * 30);
                            picker.$emit('pick', [start, end]);
                        }
                    }, {
                        text: '最近三个月',
                        onClick(picker) {
                            const end = new Date();
                            const start = new Date();
                            end.setTime(end.getTime() + 3600 * 1000 * 24 * 90);
                            picker.$emit('pick', [start, end]);
                        }
                    }]
                },
            }
        },
        methods: {
            back(){
                this.$router.go(-1); // 返回上一层
            },
            getCaseApiList() {
                this.listLoading = true;
                let self = this;
                $.ajax({
                    type: "get",
                    url: test+"/api/automation/api_list",
                    async: true,
                    data: { project_id: this.$route.params.project_id,
                        page: self.page,
                        name: self.searchName,
                        case_id: this.$route.params.case_id
                    },
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: function(data) {
                        self.listLoading = false;
                        if (data.code === '999999') {
                            self.ApiList = [];
                            self.total = data.data.total;
                            data.data.data.forEach((item) =>{
                                item.result = false;
                                self.ApiList.push(item)
                            });
                            // self.ApiList = data.data.data
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
            Test(index, row) {
                if (this.url) {
                    let self = this;
                    $.ajax({
                        type: "post",
                        url: test+"/api/automation/start_test",
                        async: true,
                        data: { project_id: this.$route.params.project_id,
                            case_id: this.$route.params.case_id,
                            host_id: this.url,
                            id: row.id
                        },
                        headers: {
                            Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                        },
                        timeout: 8000,
                        success: function(data) {
                            if (data.code === '999999') {
                                row.result = data.data.result
                            }
                            else {
                                self.$message.error({
                                    message: data.msg,
                                    center: true,
                                })
                            }
                        },
                        error: function () {
                        },
                        // complete: function(XMLHttpRequest,status){
                        //     if( status ==='timeout'){
                        //         row.result = "timeout"
                        //     }
                        // }
                    })
                } else {
                    this.$message({
                        message: '请选择测试环境',
                        center: true,
                        type: 'warning'
                    })
                }
            },
            TestAll() {
                this.ApiList.forEach((item,index) =>{
                    console.log(item,index);
                    if (this.url) {
                        let self = this;
                        $.ajax({
                            type: "post",
                            url: test+"/api/automation/start_test",
                            async: true,
                            data: { project_id: this.$route.params.project_id,
                                case_id: this.$route.params.case_id,
                                host_id: this.url,
                                id: item.id
                            },
                            headers: {
                                Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                            },
                            timeout: 5000,
                            success: function(data) {
                                if (data.code === '999999') {
                                    self.ApiList[index].result = data.data.result
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
                        this.$message({
                            message: '请选择测试环境',
                            center: true,
                            type: 'warning'
                        })
                    }
                })
            },
            handleDel(index, row){
                this.$confirm('确认删除该记录吗?', '提示', {
                    type: 'warning'
                }).then(() => {
                    this.listLoading = true;
                    //NProgress.start();
                    let self = this;
                    $.ajax({
                        type: "post",
                        url: test+"/api/automation/del_api",
                        async: true,
                        data: { project_id: this.$route.params.project_id, case_id: this.$route.params.case_id, ids: row.id },
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
                            self.getCaseApiList();
                        },
                    })

                }).catch(() => {
                });
            },
            // 获取api分组
            getApiGroup() {
                let self = this;
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
                            self.groupData = data.data;
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
            getApiList(_list) {
                this.apiListLoading = true;
                let self = this;
                let param = { project_id: this.$route.params.project_id, page: self.page};
                if (_list) {
                    param['first_group_id'] = _list[0];
                    param['second_group_id'] = _list[1];
                }
                $.ajax({
                    type: "get",
                    url: test+"/api/api/api_list",
                    async: true,
                    data: param,
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: function(data) {
                        self.apiListLoading = false;
                        if (data.code === '999999') {
                            self.searchApiList = data.data.data
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
            resultShow(row) {
                this.result["name"] = row.name;
                this.getResult(row.id);
            },
            getResult(_id){
                let self = this;
                $.ajax({
                    type: "get",
                    url: test+"/api/automation/look_result",
                    async: true,
                    data: {
                        project_id: this.$route.params.project_id,
                        case_id: this.$route.params.case_id,
                        api_id: _id
                    },
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: (data) => {
                        if (data.code === '999999') {
                            self.result["url"] = data.data.url;
                            self.result["requestType"] = data.data.requestType;
                            self.result["header"] = eval("("+data.data.header+")");
                            self.result["parameter"] = data.data.parameter;
                            self.result["statusCode"] = data.data.statusCode;
                            self.result["examineType"] = data.data.examineType;
                            self.result["data"] = data.data.data;
                            self.result["result"] = data.data.result;
                            self.result["httpStatus"] = data.data.httpStatus;
                            self.result["responseData"] = data.data.responseData;
                            self.result["testTime"] = data.data.testTime;
                            self.TestResult = true;
                        }
                        else {
                            self.$message.error({
                                message: data.msg,
                                center: true,
                            })
                        }
                    },
                    error: function () {
                        self.$message.error({
                            message: "失败",
                            center: true,
                        })
                    }
                })
            },
            getTask(){
                let self = this;
                $.ajax({
                    type: "get",
                    url: test+"/api/automation/get_time_task",
                    async: true,
                    data: {
                        project_id: self.$route.params.project_id,
                        case_id: self.$route.params.case_id
                    },
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: (data) => {
                        if (data.code === '999999') {
                            try {
                                self.form.name = data.data.name;
                                self.form.type = data.data.type;
                                self.form.frequency = data.data.frequency;
                                if (self.form.type === 'timing') {
                                    self.form.unit = 's'
                                } else {
                                    self.form.unit = data.data.unit;
                                }
                                self.form.time = data.data.startTime;
                                self.form.timeArray = [data.data.startTime, data.data.endTime];
                                self.form.Host = data.data.Host;
                                self.disDel = false
                            } catch (e){
                                self.form.name = "";
                                self.form.type = "circulation";
                                self.form.frequency = "";
                                self.form.unit = "s";
                                self.form.time = "";
                                self.form.timeArray = [];
                                self.form.Host = "";
                                self.disDel = true
                            }
                            self.taskVShow = true
                        }
                        else {
                            self.$message.error({
                                message: data.msg,
                                center: true,
                            })
                        }
                    },
                    error: function () {
                        self.editLoading = false;
                        self.$message.error({
                            message: "失败",
                            center: true,
                        })
                    }
                })
            },
            addTask(){
                let self = this;
                this.$refs.form.validate((valid) => {if (valid) {
                    this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            console.log(self.form);
                            self.editLoading = true;
                            let param = {
                                project_id: self.$route.params.project_id,
                                case_id: self.$route.params.case_id,
                                host_id: self.form.Host,
                                name: self.form.name,
                                type: self.form.type,
                                frequency: self.form.frequency,
                                unit: self.form.unit,
                            };
                            if (self.form.type === 'circulation') {
                                param['startTime'] = moment(self.form.timeArray[0]).format("YYYY-MM-DD HH:mm:ss");
                                param['endTime'] = moment(self.form.timeArray[1]).format("YYYY-MM-DD HH:mm:ss")
                            } else {
                                param['startTime'] = moment(self.form.time).format("YYYY-MM-DD HH:mm:ss");
                                param['endTime'] = moment(self.form.time).format("YYYY-MM-DD HH:mm:ss")
                            }
                            $.ajax({
                                type: "post",
                                url: test+"/api/automation/add_time_task",
                                async: true,
                                data: param,
                                headers: {
                                    Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                                },
                                timeout: 5000,
                                success: (data) => {
                                    if (data.code === '999999') {
                                        self.editLoading = false;
                                        self.taskVShow = false;
                                        self.$message({
                                            message: '添加成功',
                                            center: true,
                                            type: "success",
                                        })
                                    }
                                    else {
                                        self.editLoading = false;
                                        self.$message.error({
                                            message: data.msg,
                                            center: true,
                                        })
                                    }
                                },
                                error: function () {
                                    self.editLoading = false;
                                    self.$message.error({
                                        message: "失败",
                                        center: true,
                                    })
                                }
                            })
                        }
                    )}
                })
            },
            delTask(){
                let self = this;
                self.delLoading = true;
                $.ajax({
                    type: "post",
                    url: test+"/api/automation/del_task",
                    async: true,
                    data: {
                        project_id: self.$route.params.project_id,
                        case_id: self.$route.params.case_id
                    },
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: (data) => {
                        if (data.code === '999999') {
                            self.delLoading = false;
                            self.taskVShow = false;
                            self.$message({
                                message: "删除成功",
                                center: true,
                                type: "success"
                            })
                        }
                        else {
                            self.delLoading = false;
                            self.$message.error({
                                message: data.msg,
                                center: true,
                            })
                        }
                    },
                    error: function () {
                        self.delLoading = false;
                        self.$message.error({
                            message: "失败",
                            center: true,
                        })
                    }
                })
            },
            // 添加已有接口弹出
            addOldApi() {
                this.searchApiListVisible = true;
                this.getApiGroup();
                this.getApiList()
            },
            addOldApiSubmit() {
                let ids = this.sels.map(item => item.id).toString();
                let self = this;
                this.$confirm('确认添加选中记录吗？', '提示', {
                    type: 'warning'
                }).then(() => {
                    //NProgress.start();
                    $.ajax({
                        type: "post",
                        url: test+"/api/automation/add_old_api",
                        async: true,
                        data:{
                            project_id: this.$route.params.project_id,
                            case_id: this.$route.params.case_id,
                            api_ids: ids,
                            head: JSON.stringify({value: "1", label: '是'}),
                        },
                        headers: {
                            Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                        },
                        timeout: 5000,
                        success: function(data) {
                            self.searchApiListVisible = false;
                            if (data.code === '999999') {
                                self.$message({
                                    message: '添加成功',
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
                            self.getCaseApiList()
                        },
                    })
                }).catch(() => {

                });
            },
            handleCurrentChange(val) {
                this.page = val;
                this.getCaseApiList()
            },
            handleCurrentChangeApi(val) {
                this.page = val;
            },
            selsChange(sels){
                this.sels = sels;
            },
            getHost() {
                let self = this;
                $.ajax({
                    type: "get",
                    url: test+"/api/global/host_total",
                    async: true,
                    data: { project_id: this.$route.params.project_id},
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: (data) => {
                        if (data.code === '999999') {
                            data.data.data.forEach((item) => {
                                if (item.status) {
                                    self.Host.push(item)
                                }
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
            this.getCaseApiList();
            this.getHost();
            this.project = this.$route.params.project_id;
            this.case = this.$route.params.case_id;
        }
    }
</script>

<style lang="scss" scoped>
    .return-list {
        margin-top: 0px;
        margin-bottom: 10px;
        border-radius: 25px;
    }
    .HttpStatus {
        border-radius: 25px;
        padding: 10px;
        box-sizing: border-box;
        color: #fff;
        font-size: 15px;
        background-color: #409eff;
        text-align: center;
        margin-right: 10px;
    }
    .resultStyle{
        margin-left: 2%;
        margin-top: 10px;
    }
    .lin{
        left: 2%;
        border: 1px solid #e6e6e6;
        width: 90%;
        position: relative
    }
</style>