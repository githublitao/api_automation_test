<template>
    <section>
        <el-form :model="form" ref="form" :rules="formRules">
            <el-col :span="3" class="HOST">
                <el-form-item prop="url">
                    <el-select v-model="form.url"  placeholder="测试环境">
                        <el-option v-for="(item,index) in Host" :key="index+''" :label="item.name" :value="item.host"></el-option>
                    </el-select>
                </el-form-item>
            </el-col>
            <div style="border: 1px solid #e6e6e6;margin-bottom: 10px; padding:15px; padding-bottom: 0px">
                <el-row :gutter="10">
                    <el-col :span="3">
                        <el-form-item >
                            <el-select v-model="form.request4"  placeholder="请求方式" @change="checkRequest">
                                <el-option v-for="(item,index) in request" :key="index+''" :label="item.label" :value="item.value"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span="3">
                        <el-form-item>
                            <el-select v-model="form.Http4" placeholder="HTTP协议">
                                <el-option v-for="(item,index) in Http" :key="index+''" :label="item.label" :value="item.value"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span='16'>
                        <el-form-item prop="addr">
                            <el-input v-model.trim="form.addr" placeholder="地址" auto-complete></el-input>
                        </el-form-item>
                    </el-col>
                    <el-col :span='2'>
                        <el-button type="primary" @click="Test" :loading="loadingSend">发送</el-button>
                    </el-col>
                </el-row>
            </div>
            <el-row :span="24">
                <el-collapse v-model="activeNames" @change="handleChange">
                    <el-collapse-item title="请求头部" name="1">
                        <el-table :data="form.head" highlight-current-row ref="multipleHeadTable">
                            <el-table-column type="selection" min-width="5%" label="头部">
                            </el-table-column>
                            <el-table-column prop="name" label="标签" min-width="20%" sortable>
                                <template slot-scope="scope">
                                    <el-select placeholder="head标签" filterable v-model="scope.row.name">
                                        <el-option v-for="(item,index) in header" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                    </el-select>
                                    <el-input class="selectInput" v-model.trim="scope.row.name" :value="scope.row.name" placeholder="请输入内容"></el-input>
                                </template>
                            </el-table-column>
                            <el-table-column prop="value" label="内容" min-width="40%" sortable>
                                <template slot-scope="scope">
                                    <el-input v-model.trim="scope.row.value" :value="scope.row.value" placeholder="请输入内容"></el-input>
                                </template>
                            </el-table-column>
                            <el-table-column label="操作" min-width="7%">
                                <template slot-scope="scope">
                                    <i class="el-icon-delete" style="font-size:30px;cursor:pointer;" @click="delHead(scope.$index)"></i>
                                </template>
                            </el-table-column>
                            <el-table-column label="" min-width="10%">
                                <template slot-scope="scope">
                                    <el-button v-if="scope.$index===(form.head.length-1)" size="mini" class="el-icon-plus" @click="addHead"></el-button>
                                </template>
                            </el-table-column>
                            <el-table-column min-width="18%">

                            </el-table-column>
                        </el-table>
                    </el-collapse-item>
                    <el-collapse-item title="请求参数" name="2">
                        <div style="margin: 5px">
                            <el-row :span="24">
                                <el-col :span="4"><el-radio v-model="radio" label="form-data">表单(form-data)</el-radio></el-col>
                                <el-col v-if="request3" :span="4"><el-radio v-model="radio" label="raw">源数据(raw)</el-radio></el-col>
                                <el-col v-if="request3" :span="16"><el-checkbox v-model="radioType" label="3" v-show="ParameterTyep">表单转源数据</el-checkbox></el-col>
                            </el-row>
                        </div>
                        <el-table :data="form.parameter" highlight-current-row :class="ParameterTyep? 'parameter-a': 'parameter-b'" @selection-change="selsChangeParameter" ref="multipleParameterTable">
                            <el-table-column type="selection" min-width="5%" label="头部">
                            </el-table-column>
                            <el-table-column prop="name" label="参数名" min-width="20%" sortable>
                                <template slot-scope="scope">
                                    <el-input v-model.trim="scope.row.name" :value="scope.row.name" placeholder="请输入参数值"></el-input>
                                </template>
                            </el-table-column>
                            <el-table-column prop="value" label="参数值" min-width="40%" sortable>
                                <template slot-scope="scope">
                                    <el-input v-model.trim="scope.row.value" :value="scope.row.value" placeholder="请输入参数值"></el-input>
                                </template>
                            </el-table-column>
                            <el-table-column label="操作" min-width="7%">
                                <template slot-scope="scope">
                                    <i class="el-icon-delete" style="font-size:30px;cursor:pointer;" @click="delParameter(scope.$index)"></i>
                                </template>
                            </el-table-column>
                            <el-table-column label="" min-width="10%">
                                <template slot-scope="scope">
                                    <el-button v-if="scope.$index===(form.parameter.length-1)" size="mini" class="el-icon-plus" @click="addParameter"></el-button>
                                </template>
                            </el-table-column>
                            <el-table-column label="" min-width="18%"></el-table-column>
                        </el-table>
                        <template>
                            <el-input :class="ParameterTyep? 'parameter-b': 'parameter-a'" type="textarea" :rows="5" placeholder="请输入内容" v-model.trim="form.parameterRaw"></el-input>
                        </template>
                    </el-collapse-item>
                    <el-collapse-item title="响应结果" name="4">
                        <div style="margin-bottom: 10px">
                            <el-button @click="showBody">Body</el-button>
                            <el-button @click="showHeader">Head</el-button>
                            <el-button type="primary" @click="neatenFormat">格式转换</el-button>
                        </div>
                        <el-card class="box-card">
                            <div slot="header" class="clearfix">
                                <span v-model="form.statusCode" style="font-size: 25px">{{form.statusCode}}</span>
                            </div>
                            <div v-model="form.resultData" :class="resultShow? 'parameter-a': 'parameter-b'" v-show="!format">
                                <div style="word-break: break-all;overflow:auto;overflow-x:hidden">
                                    {{form.resultData}}
                                </div>
                            </div>
                            <div v-model="form.resultHead" :class="resultShow? 'parameter-b': 'parameter-a'">{{form.resultHead}}</div>
                            <div :class="resultShow? 'parameter-a': 'parameter-b'" v-show="format">
                            <pre style="border: 1px solid #e6e6e6;word-break: break-all;height:300px;overflow:auto;overflow-x:hidden">
                                {{form.resultData}}
                            </pre>
                            </div>
                            <div v-show="!form.resultData&&!form.resultHead" class="raw">暂无数据</div>
                        </el-card>
                    </el-collapse-item>
                    <el-collapse-item title="请求历史" name="5">
                        <el-table :data="requestHistory" stripe style="width: 100%" v-loading="listLoading">
                            <el-table-column prop="requestTime" label="操作时间" min-width="20%">
                            </el-table-column>
                            <el-table-column prop="requestType" label="请求方式" min-width="10%">
                            </el-table-column>
                            <el-table-column prop="requestAddress" label="请求地址" min-width="49%">
                            </el-table-column>
                            <el-table-column prop="httpCode" label="HTTP状态" min-width="11%">
                            </el-table-column>
                            <el-table-column min-width="10%" label="操作">
                                <template slot-scope="scope">
                                    <i class="el-icon-delete" style="font-size:30px;cursor:pointer;" @click="delHistory(scope.row)"></i>
                                </template>
                            </el-table-column>
                        </el-table>
                    </el-collapse-item>
                </el-collapse>
            </el-row>
        </el-form>
    </section>
</template>
<script>
    import { test } from '../../../../api/api'
    import $ from 'jquery'
    export default {
        data() {
            return {
                request: [{value: 'GET', label: 'GET'},
                    {value: 'POST', label: 'POST'},
                    {value: 'PUT', label: 'PUT'},
                    {value: 'DELETE', label: 'DELETE'}],
                Http: [{value: 'http', label: 'HTTP'},
                    {value: 'https', label: 'HTTPS'}],
                ParameterTyep: true,
                radio: "form-data",
                loadingSend: false,
                header: [{value: 'Accept', label: 'Accept'},
                    {value: 'Accept-Charset', label: 'Accept-Charset'},
                    {value: 'Accept-Encoding', label: 'Accept-Encoding'},
                    {value: 'Accept-Language', label: 'Accept-Language'},
                    {value: 'Accept-Ranges', label: 'Accept-Ranges'},
                    {value: 'Authorization', label: 'Authorization'},
                    {value: 'Cache-Control', label: 'Cache-Control'},
                    {value: 'Connection', label: 'Connection'},
                    {value: 'Cookie', label: 'Cookie'},
                    {value: 'Content-Length', label: 'Content-Length'},
                    {value: 'Content-Type', label: 'Content-Type'},
                    {value: 'Content-MD5', label: 'Content-MD5'},
                    {value: 'Date', label: 'Date'},
                    {value: 'Expect', label: 'Expect'},
                    {value: 'From', label: 'From'},
                    {value: 'Host', label: 'Host'},
                    {value: 'If-Match', label: 'If-Match'},
                    {value: 'If-Modified-Since', label: 'If-Modified-Since'},
                    {value: 'If-None-Match', label: 'If-None-Match'},
                    {value: 'If-Range', label: 'If-Range'},
                    {value: 'If-Unmodified-Since', label: 'If-Unmodified-Since'},
                    {value: 'Max-Forwards', label: 'Max-Forwards'},
                    {value: 'Origin', label: 'Origin'},
                    {value: 'Pragma', label: 'Pragma'},
                    {value: 'Proxy-Authorization', label: 'Proxy-Authorization'},
                    {value: 'Range', label: 'Range'},
                    {value: 'Referer', label: 'Referer'},
                    {value: 'TE', label: 'TE'},
                    {value: 'Upgrade', label: 'Upgrade'},
                    {value: 'User-Agent', label: 'User-Agent'},
                    {value: 'Via', label: 'Via'},
                    {value: 'Warning', label: 'Warning'}],
                header4: "",
                radioType: "",
                result: true,
                activeNames: ['1', '2', '3', '4', '5'],
                id: "",
                Host: [],
                request3:true,
                form: {
                    url: "",
                    request4: 'POST',
                    Http4: 'http',
                    addr: '',
                    head: [],
                    parameterRaw: "",
                    parameter: [],
                    parameterType: "",
                    statusCode: "",
                    resultData: "",
                    resultHead: "",
                },
                formRules: {
                    url: [
                        { required: true, message: '请选择测试环境', trigger: 'blur'}
                    ],
                    addr: [
                        { required: true, message: '请输入地址', trigger: 'blur' },
                    ]
                },
                requestHistory: [],
                listLoading: false,
                headers: "",
                parameters: "",
                resultShow: true,
                format: false,
            }
        },
        methods: {
            checkRequest(){
                let request = this.form.request4;
                if (request==="GET" || request==="DELETE"){
                    this.request3=false
                } else {
                    this.request3=true
                }
            },
            isJsonString(str) {
                try {
                    if (typeof JSON.parse(str) === "object") {
                        return true;
                    }
                } catch(e) {
                }
                return false;
            },
            getApiInfo() {
                let self = this;
                let param = {project_id: self.$route.params.project_id, api_id: self.$route.params.api_id};
                $.ajax({
                    type: "get",
                    url: test+"/api/api/api_info",
                    async: true,
                    data: param,
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: (data) => {

                        if (data.code === '999999') {
                            self.form.request4 = data.data.requestType;
                            self.form.Http4 = data.data.httpType.toLowerCase();
                            self.form.addr = data.data.apiAddress;
                            if (data.data.headers.length) {
                                data.data.headers.forEach((item) => {
                                    self.form.head.push(item);
                                });
                            } else {
                                var param = [{name: "", value: ""}, {name: "", value: ""}];
                                param.forEach((item) => {
                                    self.form.head.push(item);
                                });
                            }
                            if (data.data.requestParameter.length) {
                                data.data.requestParameter.forEach((item) => {
                                    self.form.parameter.push(item);
                                });
                            } else {
                                var param = [{name: "", value: "", required:true, restrict: "", description: ""},
                                    {name: "", value: "", required:true, restrict: "", description: ""}];
                                param.forEach((item) => {
                                    self.form.parameter.push(item);
                                });
                            }
                            try {
                                self.form.parameterRaw = data.data.requestParameterRaw[0].data;
                            } catch (e) {

                            }
                            self.form.parameterType = data.data.requestParameterType;
                            self.radio = data.data.requestParameterType;
                            self.toggleHeadSelection(self.form.head);
                            self.toggleParameterSelection(self.form.parameter);
                        }
                        else {
                            self.$message.error({
                                message: data.msg,
                                center: true,
                            })
                        }
                    },
                });
            },
            getHistory() {
                let self = this;
                this.listLoading = true;
                $.ajax({
                    type: "get",
                    url: test+"/api/api/history_list",
                    async: true,
                    data: { project_id: this.$route.params.project_id, api_id: self.$route.params.api_id,},
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: (data) => {
                        self.listLoading = false;
                        if (data.code === '999999') {
                            self.requestHistory = data.data
                            // data.data.data.forEach((item) => {
                            //     self.requestHistory.push(item)
                            // })
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
            AddHistroy(code) {
                let self = this;
                this.listLoading = true;
                let param = JSON.stringify({ project_id: Number(this.$route.params.project_id),
                    api_id: Number(self.$route.params.api_id),
                    requestType :self.form.request4,
                    requestAddress: self.form.Http4 + "://" + self.form.url + self.form.addr,
                    httpCode: code
                });
                console.log(param)
                $.ajax({
                    type: "POST",
                    url: test+"/api/api/add_history",
                    async: true,
                    data: param,
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: (data) => {
                        self.listLoading = false;
                        if (data.code === '999999') {
                            self.getHistory()
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
            delHistory(row) {
                let self = this;
                let param = JSON.stringify({
                    project_id: Number(self.$route.params.project_id),
                    api_id: Number(self.$route.params.api_id),
                    id: Number(row.id)
                });
                $.ajax({
                    type: "POST",
                    url: test+"/api/api/del_history",
                    async: true,
                    data: param,
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: (data) => {
                        if (data.code === '999999') {
                            this.getHistory();
                            self.$message.success({
                                message: "删除成功！",
                                center: true,
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
            getHost() {
                let self = this;
                $.ajax({
                    type: "get",
                    url: test+"/api/global/host_total",
                    async: true,
                    data: { project_id: this.$route.params.project_id, page: this.page,},
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
            toggleHeadSelection(rows) {
                rows.forEach(row => {
                    this.$refs.multipleHeadTable.toggleRowSelection(row, true);
                });
            },
            toggleParameterSelection(rows) {
                rows.forEach(row => {
                    this.$refs.multipleParameterTable.toggleRowSelection(row, true);
                });
            },
            selsChangeHead: function (sels) {
                this.headers = sels
            },
            selsChangeParameter: function (sels) {
                this.parameters = sels
            },
            Test: function() {
                let host = this.form.addr;
                if (host.indexOf("http://") ===0){
                    this.form.addr = host.slice(7)
                }
                if (host.indexOf("https://") ===0){
                    this.form.addr = host.slice(8)
                }
                this.$refs.form.validate((valid) => {
                    if (valid) {
                        this.loadingSend = true;
                        let self = this;
                        let _parameter = new Object();
                        let headers = new Object();
                        self.form.statusCode = '';
                        self.form.resultData = '';
                        self.form.resultHead = '';
                        console.log(self.form.head)
                        for (let i = 0; i < self.form.head.length; i++) {
                            var a = self.form.head[i]["name"];
                            if (a) {
                                headers[a] = self.form.head[i]["value"]
                            }
                        }
                        console.log(headers)
                        let url = self.form.Http4 + "://" + self.form.url + host;
                        let _type = self.radio;
                        if (_type === 'form-data') {
                            if (self.radioType) {
                                for (let i = 0; i < self.parameters.length; i++) {
                                    var a = self.parameters[i]["name"];
                                    if (a) {
                                        _parameter[a] = self.parameters[i]["value"];
                                    }
                                }
                                _parameter = JSON.stringify(_parameter)
                            } else {
                                _parameter = self.form.parameter
                            }
                        } else {
                            // POST(url, self.form.parameterRaw, headers)
                            _parameter = self.form.parameterRaw;
                        }
                        if (self.form.parameterRaw && _type === "raw") {
                            if (!self.isJsonString(self.form.parameterRaw)) {
                                self.$message({
                                    message: '源数据格式错误',
                                    center: true,
                                    type: 'error'
                                })
                            } else {
                                $.ajax({
                                    type: self.form.request4,
                                    url: url,
                                    async: true,
                                    data: _parameter,
                                    headers: headers,
                                    timeout: 5000,
                                    success: function (data, status, jqXHR) {
                                        self.loadingSend = false;
                                        self.form.statusCode = jqXHR.status;
                                        self.form.resultData = data;
                                        self.form.resultHead = jqXHR.getAllResponseHeaders()
                                        self.AddHistroy(jqXHR.status)
                                    },
                                    error: function (jqXHR, error, errorThrown) {
                                        self.loadingSend = false;
                                        self.form.statusCode = jqXHR.status;
                                        self.form.resultData = jqXHR.responseJSON;
                                        self.form.resultHead = jqXHR.getAllResponseHeaders()
                                    }
                                })
                            }
                        } else {
                            $.ajax({
                                type: self.form.request4,
                                url: url,
                                async: true,
                                data: _parameter,
                                headers: headers,
                                timeout: 5000,
                                success: function (data, status, jqXHR) {
                                    self.loadingSend = false;
                                    self.form.statusCode = jqXHR.status;
                                    self.form.resultData = data;
                                    self.form.resultHead = jqXHR.getAllResponseHeaders()
                                    self.AddHistroy(jqXHR.status)
                                },
                                error: function (jqXHR, error, errorThrown) {
                                    self.loadingSend = false;
                                    self.form.statusCode = jqXHR.status;
                                    self.form.resultData = jqXHR.responseJSON;
                                    self.form.resultHead = jqXHR.getAllResponseHeaders()
                                }
                            })
                        }
                    }
                })
            },
            neatenFormat() {
                let demo = document.getElementsByTagName('pre')[0];
                console.log(demo)
                hljs.highlightBlock(demo);
                this.format = !this.format
            },
            addHead() {
                let headers = {name: "", value: ""};
                this.form.head.push(headers);
                let rows = [this.form.head[this.form.head.length-1]];
                this.toggleHeadSelection(rows)
            },
            delHead(index) {
                if (this.form.head.length !== 1) {
                    this.form.head.splice(index, 1)
                }
            },
            addParameter() {
                let headers = {name: "", value: "", required:"True", restrict: "", description: ""};
                this.form.parameter.push(headers);
                let rows = [this.form.parameter[this.form.parameter.length-1]];
                this.toggleParameterSelection(rows)
            },
            delParameter(index) {
                if (this.form.parameter.length !== 1) {
                    this.form.parameter.splice(index, 1)
                }
            },
            addResponse() {
                let headers = {name: "", value: "", required:"True", restrict: "", description: ""};
                this.form.response.push(headers)
            },
            delResponse(index) {
                if (this.form.response.length !== 1) {
                    this.form.response.splice(index, 1)
                }
            },
            changeParameterType() {
                if (this.radio === 'form-data') {
                    this.ParameterTyep = true
                } else {
                    this.ParameterTyep = false
                }
            },
            showBody() {
                this.resultShow = true
            },
            showHeader() {
                this.resultShow = false
            },
            handleChange(val) {
            },
            onSubmit() {
                console.log('submit!');
            },
        },
        watch: {
            radio() {
                this.changeParameterType()
            }
        },
        mounted() {
            this.getApiInfo();
            this.getHost();
            this.getHistory()
        }
    }
</script>

<style lang="scss" scoped>
    .return-list {
        margin-top: 0px;
        margin-bottom: 10px;
        border-radius: 25px;
    }
    .head-class {
        font-size: 17px
    }
    .parameter-a {
        display: block;
    }
    .parameter-b {
        display: none;
    }
    .selectInput {
        position: absolute;
        /*margin-left: 7px;*/
        padding-left: 9px;
        width: 180px;
        /*border-radius:0px;*/
        /*height: 38px;*/
        left: 1px;
        border-right: 0px;
    }
    .HOST {
        position: absolute;
        right: 30px;
        top: 0px;
    }
    .raw {
        border: 1px solid #e6e6e6;
        margin-bottom: 10px;
        padding:15px;
        text-align: center
    }
</style>
<style lang="scss">
    .selectInput{
        input{
            border-right: 0px;
            border-radius: 4px 0px 0px 4px;
        }
    }
</style>
