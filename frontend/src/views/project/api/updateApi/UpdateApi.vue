<template>
    <section>
        <router-link :to="{ name: '基础信息', params: {project_id: this.$route.params.project_id,api_id:this.$route.params.api_id}}" style='text-decoration: none;color: aliceblue;'>
            <el-button class="return-list"><i class="el-icon-d-arrow-left" style="margin-right: 5px"></i>接口详情</el-button>
        </router-link>
        <router-link :to="{ name: '基础信息', params: {project_id: this.$route.params.project_id,api_id:this.$route.params.api_id}}" style='text-decoration: none;color: aliceblue;'>
            <el-button class="return-list" style="float: right">取消</el-button>
        </router-link>
        <el-button class="return-list" type="primary" style="float: right; margin-right: 15px" @click.native="updateApiInfo">保存</el-button>
        <el-form :model="form" ref="form" :rules="FormRules">
            <div style="border: 1px solid #e6e6e6;margin-bottom: 10px;padding:15px">
                <el-form-item label="接口分组:" label-width="83px" prop="firstGroup">
                    <el-select v-model="form.firstGroup" placeholder="请选择分组">
                        <el-option v-for="(item,index) in group" :key="index+''" :label="item.name" :value="item.id"></el-option>
                    </el-select>
                </el-form-item>
                <el-row :gutter="10">
                    <el-col :span='8'>
                        <el-form-item label="接口名称:" label-width="83px" prop="name">
                            <el-input v-model.trim="form.name" placeholder="名称" auto-complete></el-input>
                        </el-form-item>
                    </el-col>
                    <el-col :span="10">
                        <el-form-item label="状态:" label-width="72px">
                            <el-select v-model="form.status" placeholder="接口状态">
                                <el-option v-for="(item,index) in status" :key="index+''" :label="item.label" :value="item.value"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                </el-row>
                <el-row :gutter="10">
                    <el-col :span="4">
                        <el-form-item label="URL:" label-width="83px">
                            <el-select v-model="form.request4"  placeholder="请求方式" @change="checkRequest">
                                <el-option v-for="(item,index) in request" :key="index+''" :label="item.label" :value="item.value"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span="2">
                        <el-form-item>
                            <el-select v-model="form.Http4" placeholder="HTTP协议">
                                <el-option v-for="(item,index) in Http" :key="index+''" :label="item.label" :value="item.value"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span='18'>
                        <el-form-item prop="addr">
                            <el-input v-model.trim="form.addr" placeholder="地址" auto-complete></el-input>
                        </el-form-item>
                    </el-col>
                </el-row>
            </div>
            <el-row :span="24">
                <el-collapse v-model="activeNames" @change="handleChange">
                    <el-collapse-item title="请求头部" name="1">
                        <el-table :data="form.head" highlight-current-row>
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
                            <el-table-column label="操作" min-width="10%">
                                <template slot-scope="scope">
                                    <i class="el-icon-delete" style="font-size:30px;cursor:pointer;" @click="delHead(scope.$index)"></i>
                                </template>
                            </el-table-column>
                            <el-table-column label="" min-width="10%">
                                <template slot-scope="scope">
                                    <el-button v-if="scope.$index===(form.head.length-1)" size="mini" class="el-icon-plus" @click="addHead"></el-button>
                                </template>
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
                        <el-table :data="form.parameter" highlight-current-row :class="ParameterTyep? 'parameter-a': 'parameter-b'">
                            <el-table-column prop="name" label="参数名" min-width="25%" sortable>
                                <template slot-scope="scope">
                                    <el-input v-model.trim="scope.row.name" :value="scope.row.name" placeholder="请输入参数值"></el-input>
                                </template>
                            </el-table-column>
                            <el-table-column prop="value" label="参数值" min-width="30%" sortable>
                                <template slot-scope="scope">
                                    <el-input v-model.trim="scope.row.value" :value="scope.row.value" placeholder="请输入参数值"></el-input>
                                </template>
                            </el-table-column>
                            <el-table-column prop="_type" label="参数类型" min-width="14%" sortable>
                                <template slot-scope="scope">
                                    <el-select v-model="scope.row._type"  placeholder="请求方式">
                                        <el-option v-for="(item,index) in paramTyep" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                    </el-select>
                                </template>
                            </el-table-column>
                            <el-table-column prop="description" label="参数说明" min-width="14%" sortable>
                                <template slot-scope="scope">
                                    <el-input v-model.trim="scope.row.description" :value="scope.row.desc" placeholder="请输入参数说明"></el-input>
                                </template>
                            </el-table-column>
                            <el-table-column label="操作" min-width="13%">
                                <template slot-scope="scope">
                                    <i class="el-icon-delete" style="font-size:30px;cursor:pointer;" @click="delParameter(scope.$index)"></i>
                                    <el-button type="primary" size="mini" style="margin-bottom: 5px" @click="handleParameterEdit(scope.$index, scope.row)">更多设置</el-button>
                                </template>
                            </el-table-column>
                            <el-table-column label="" min-width="4%">
                                <template slot-scope="scope">
                                    <el-button v-if="scope.$index===(form.parameter.length-1)" size="mini" class="el-icon-plus" @click="addParameter"></el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                        <template>
                            <el-input :class="ParameterTyep? 'parameter-b': 'parameter-a'" type="textarea" :rows="5" placeholder="请输入内容" v-model.trim="parameterRaw"></el-input>
                        </template>
                    </el-collapse-item>
                    <el-dialog title="更多设置" :visible.sync="addParameterFormVisible" :close-on-click-modal="false">
                        <el-form :model="editForm" label-width="60px" :rules="FormRules" ref="editForm" >
                            <el-form-item label="参数名" prop="name" label-width="83px">
                                <el-input v-model.trim="editForm.name" auto-complete="off" placeholder="请输入参数名称"></el-input>
                            </el-form-item>
                            <el-form-item label="参数值" prop="name" label-width="83px">
                                <el-input v-model.trim="editForm.value" auto-complete="off" placeholder="请输入参数值"></el-input>
                            </el-form-item>
                            <el-form-item label="必填?" label-width="83px" prop="required">
                                <el-select v-model.trim="editForm.required" placeholder="必填？">
                                    <el-option v-for="(item,index) in required4" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                </el-select>
                            </el-form-item>
                            <el-form-item label="输入限制" prop='version' label-width="83px">
                                <el-input v-model.trim="editForm.restrict" auto-complete="off" placeholder="请输入输入限制"></el-input>
                            </el-form-item>
                            <el-form-item label="描述" prop='description' label-width="83px">
                                <el-input type="textarea" :rows="7" v-model.trim="editForm.description" placeholder="请输入描述"></el-input>
                            </el-form-item>
                        </el-form>
                        <div slot="footer" class="dialog-footer">
                            <el-button @click.native="addParameterFormVisible = false">取消</el-button>
                            <el-button type="primary" @click.native="editParameterSubmit">提交</el-button>
                        </div>
                    </el-dialog>
                    <el-collapse-item title="返回参数" name="3">
                        <el-table :data="form.response" highlight-current-row>
                            <el-table-column prop="name" label="参数名" min-width="25%" sortable>
                                <template slot-scope="scope">
                                    <el-input v-model.trim="scope.row.name" :value="scope.row.name" placeholder="请输入参数值"></el-input>
                                </template>
                            </el-table-column>
                            <el-table-column prop="value" label="参数值" min-width="30%" sortable>
                                <template slot-scope="scope">
                                    <el-input v-model.trim="scope.row.value" :value="scope.row.value" placeholder="请输入参数值"></el-input>
                                </template>
                            </el-table-column>
                            <el-table-column prop="_type" label="参数类型" min-width="14%" sortable>
                                <template slot-scope="scope">
                                    <el-select v-model.trim="scope.row._type"  placeholder="请求方式">
                                        <el-option v-for="(item,index) in paramTyep" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                    </el-select>
                                </template>
                            </el-table-column>
                            <el-table-column prop="description" label="参数说明" min-width="14%" sortable>
                                <template slot-scope="scope">
                                    <el-input v-model.trim="scope.row.description" :value="scope.row.desc" placeholder="请输入参数说明"></el-input>
                                </template>
                            </el-table-column>
                            <el-table-column label="操作" min-width="13%">
                                <template slot-scope="scope">
                                    <i class="el-icon-delete" style="font-size:30px;cursor:pointer;" @click="delResponse(scope.$index)"></i>
                                    <el-button type="primary" size="mini" style="margin-bottom: 5px" @click="handleResponseEdit(scope.$index, scope.row)">更多设置</el-button>
                                </template>
                            </el-table-column>
                            <el-table-column label="" min-width="4%">
                                <template slot-scope="scope">
                                    <el-button v-if="scope.$index===(form.response.length-1)" size="mini" class="el-icon-plus" @click="addResponse"></el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </el-collapse-item>
                    <el-dialog title="更多设置" :visible.sync="addResponseFormVisible" :close-on-click-modal="false">
                        <el-form :model="editForm" label-width="60px" :rules="FormRules" ref="editForm" >
                            <el-form-item label="参数名" prop="name" label-width="83px">
                                <el-input v-model.trim="editForm.name" auto-complete="off" placeholder="请输入参数名称"></el-input>
                            </el-form-item>
                            <el-form-item label="参数值" prop="name" label-width="83px">
                                <el-input v-model.trim="editForm.value" auto-complete="off" placeholder="请输入参数值"></el-input>
                            </el-form-item>
                            <el-form-item label="必填?" label-width="83px" prop="required">
                                <el-select v-model.trim="editForm.required" placeholder="必填？">
                                    <el-option v-for="(item,index) in required4" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                </el-select>
                            </el-form-item>
                            <el-form-item label="输入限制" prop='version' label-width="83px">
                                <el-input v-model.trim="editForm.restrict" auto-complete="off" placeholder="请输入输入限制"></el-input>
                            </el-form-item>
                            <el-form-item label="描述" prop='description' label-width="83px">
                                <el-input type="textarea" :rows="7" v-model.trim="editForm.description" placeholder="请输入描述"></el-input>
                            </el-form-item>
                        </el-form>
                        <div slot="footer" class="dialog-footer">
                            <el-button @click.native="addResponseFormVisible = false">取消</el-button>
                            <el-button type="primary" @click.native="editResponseSubmit">提交</el-button>
                        </div>
                    </el-dialog>
                    <el-collapse-item title="普通mock" name="4">
                        <el-card class="box-card">
                            <div slot="header" class="clearfix">
                                <el-select v-model="form.mockCode" placeholder="HTTP状态">
                                    <el-option v-for="(item,index) in httpCode" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                </el-select>
                            </div >
                            <el-input v-model.trim="form.mockData" type="textarea" :rows="8" placeholder="请输入mock内容"></el-input>
                        </el-card>
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
                Http: [{value: 'HTTP', label: 'HTTP'},
                    {value: 'HTTPS', label: 'HTTPS'}],
                paramTyep: [{value: 'Int', label: 'Int'},
                    {value: 'String', label: 'String'}],
                checkHeadList: [],
                checkParameterList: [],
                ParameterTyep: true,
                group: [],
                radio: "form-data",
                status: [{value: true, label: '启用'},
                    {value: false, label: '禁用'}],
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
                addParameterFormVisible: false,
                addResponseFormVisible: false,
                required4:[{value: true, label: '是'},
                    {value: false, label: '否'}],
                httpCode:[{value: '', label: ''},
                    {value: '200', label: '200'},
                    {value: '404', label: '404'},
                    {value: '400', label: '400'},
                    {value: '500', label: '500'},
                    {value: '502', label: '502'},
                    {value: '302', label: '302'}],
                radioType: "",
                result: true,
                activeNames: ['1', '2', '3', '4'],
                id: "",
                parameterRaw: "",
                request3:true,
                form: {
                    firstGroup: '',
                    name: '',
                    status: 'True',
                    request4: 'GET',
                    Http4: 'HTTP',
                    addr: '',
                    head: [{name: "", value: ""},
                        {name: "", value: ""}],
                    parameter: [{name: "", value: "", _type:"String", required:true, restrict: "", description: ""},
                        {name: "", value: "", _type:"String", required:true, restrict: "", description: ""}],
                    parameterType: "",
                    response: [{name: "", value: "", _type:"String", required:true, description: ""},
                        {name: "", value: "", _type:"String",required:true, description: ""}],
                    mockCode: '',
                    mockData: '',
                },
                FormRules: {
                    name : [{ required: true, message: '请输入名称', trigger: 'blur' },
                        { max: 50, message: '不能超过50个字', trigger: 'blur' }],
                    addr : [{ required: true, message: '请输入地址', trigger: 'blur' }],
                    required : [{ required: true, message: '是否必须', trigger: 'blur' }],
                    firstGroup : [{ type: 'number', required: true, message: '请选择分组', trigger: 'blur'},],
                },
                editForm: {
                    name: "",
                    value: "",
                    required: "",
                    restrict: "",
                    description: "",
                },
                // editLoading: false
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
                    success: function(data) {
                        if (data.code === '999999') {
                            data = data.data;
                            self.id = data.id;
                            self.form.firstGroup = data.apiGroupLevelFirst;
                            self.form.name = data.name;
                            if (data.status) {
                                self.form.status = true;
                            } else {
                                self.form.status = false
                            }
                            self.form.request4 = data.requestType;
                            self.form.Http4 = data.httpType;
                            self.form.addr = data.apiAddress;
                            if (data.headers.length) {
                                self.form.head = data.headers;
                            }
                            try {
                                self.parameterRaw = data.requestParameterRaw.data.replace(/'/g, "\"").replace(/None/g, "null").replace(/True/g, "true").replace(/False/g, "false");
                            } catch (e){

                            }
                            if (data.requestParameter.length) {
                                self.form.parameter = data.requestParameter;
                            }
                            self.form.parameterType = data.requestParameterType;
                            self.radio = self.form.parameterType;
                            if (data.response.length) {
                                self.form.response = data.response;
                            }
                            self.form.mockCode = data.mockCode;
                            self.form.mockData = data.data;
                            if (data.data) {
                                self.form.mockJsonData = JSON.parse(data.data)
                            }
                            self.checkRequest()
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
            updateApiInfo(){
                if (this.form.mockData&&this.form.mockCode) {
                    if (!this.isJsonString(this.form.mockData)) {
                        this.$message({
                            message: 'mock格式错误',
                            center: true,
                            type: 'error'
                        })
                    } else {
                        this.updateApi()
                    }
                } else if(this.form.mockData||this.form.mockCode){
                    this.$message({
                        message: 'HTTP状态或mock为空',
                        center: true,
                        type: 'warning'
                    })
                } else {
                    this.updateApi()
                }
            },
            updateApi: function () {
                this.$refs.form.validate((valid) => {
                    if (valid) {
                        let self = this;
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.form.parameterType = self.radio;
                            let _type = self.form.parameterType;
                            let _parameter = {};
                            if ( _type === 'form-data') {
                                if ( self.radioType === true) {
                                    _type = 'raw';
                                    self.form.parameter.forEach((item) => {
                                        _parameter[item.name] = item.value
                                    });
                                } else {
                                    _parameter = self.form.parameter;
                                }
                            } else {
                                _parameter = self.parameterRaw
                            }
                            let param = JSON.stringify({
                                project_id: Number(self.$route.params.project_id),
                                id: Number(self.$route.params.api_id),
                                apiGroupLevelFirst_id: Number(self.form.firstGroup),
                                name: self.form.name,
                                httpType: self.form.Http4,
                                requestType: self.form.request4,
                                apiAddress: self.form.addr,
                                status: self.form.status,
                                headDict: self.form.head,
                                requestParameterType: _type,
                                requestList: _parameter,
                                responseList: self.form.response,
                                mockCode: self.form.mockCode,
                                data: self.form.mockData,
                                description: ''
                            });
                            if (self.parameterRaw&&_type==="raw") {
                                if (!self.isJsonString(self.parameterRaw)) {
                                    self.$message({
                                        message: '源数据格式错误',
                                        center: true,
                                        type: 'error'
                                    })
                                } else {
                                    // console.log(_parameter)
                                    // console.log(typeof _parameter)
                                    $.ajax({
                                        type: "post",
                                        url: test + "/api/api/update_api",
                                        async: true,
                                        data: param,
                                        headers: {
                                            "Content-Type": "application/json",
                                            Authorization: 'Token ' + JSON.parse(sessionStorage.getItem('token'))
                                        },
                                        timeout: 5000,
                                        success: function (data) {
                                            if (data.code === '999999') {
                                                self.$router.push({
                                                    name: '基础信息', params: {
                                                        project_id: self.$route.params.project_id,
                                                        api_id: self.$route.params.api_id
                                                    }
                                                });
                                                self.$message({
                                                    message: '修改成功',
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
                                        },
                                    })
                                }
                            } else {
                                $.ajax({
                                    type: "post",
                                    url: test + "/api/api/update_api",
                                    async: true,
                                    data: param,
                                    headers: {
                                        "Content-Type": "application/json",
                                        Authorization: 'Token ' + JSON.parse(sessionStorage.getItem('token'))
                                    },
                                    timeout: 5000,
                                    success: function (data) {
                                        if (data.code === '999999') {
                                            self.$router.push({
                                                name: '基础信息', params: {
                                                    project_id: self.$route.params.project_id,
                                                    api_id: self.$route.params.api_id
                                                }
                                            });
                                            self.$message({
                                                message: '修改成功',
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
                                    },
                                })
                            }
                        })
                    }
                })
            },
            editParameterSubmit: function () {
                this.$refs.editForm.validate((valid) => {
                    if (valid) {
                        this.form.parameter[this.id] = this.editForm;
                        this.addParameterFormVisible = false
                    }
                })
            },
            handleParameterEdit: function (index, row) {
                this.addParameterFormVisible = true;
                this.id = index;
                this.editForm = Object.assign({}, row);
            },
            editResponseSubmit: function () {
                this.$refs.editForm.validate((valid) => {
                    if (valid) {
                        this.form.response[this.id] = this.editForm;
                        this.addResponseFormVisible = false
                    }
                })
            },
            handleResponseEdit: function (index, row) {
                this.addResponseFormVisible = true;
                this.id = index;
                this.editForm = Object.assign({}, row);
            },
            back(){
                this.$router.go(-1); // 返回上一层

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
                            self.group = data.data;
                            // self.form.firstGroup = self.group[0].id
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
            addHead() {
                let headers = {name: "", value: ""};
                this.form.head.push(headers)
            },
            delHead(index) {
                this.form.head.splice(index, 1);
                if (this.form.head.length === 0) {
                    this.form.head.push({name: "", value: ""})
                }
            },
            addParameter() {
                let headers = {name: "", value: "", _type:"String", required:true, restrict: "", description: ""};
                this.form.parameter.push(headers)
            },
            delParameter(index) {
                this.form.parameter.splice(index, 1);
                if (this.form.parameter.length === 0) {
                    this.form.parameter.push({name: "", value: "", _type:"String", required:true, restrict: "", description: ""})
                }
            },
            addResponse() {
                let headers = {name: "", value: "", _type:"String", required:true, description: ""};
                this.form.response.push(headers)
            },
            delResponse(index) {
                this.form.response.splice(index, 1);
                if (this.form.response.length === 0) {
                    this.form.response.push({name: "", value: "", _type:"String", required:true, description: ""})
                }
            },
            changeParameterType() {
                if (this.radio === 'form-data') {
                    this.ParameterTyep = true
                } else {
                    this.ParameterTyep = false
                }
            },
            showData() {
                this.result = true
            },
            showHead(){
                this.result = false
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
            this.getApiGroup();
            this.getApiInfo();
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
</style>
<style lang="scss">
    .selectInput{
        input{
            border-right: 0px;
            border-radius: 4px 0px 0px 4px;
        }
    }
</style>
