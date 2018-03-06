<template>
    <section>
        <el-button class="return-list">快速新建API</el-button>
        <el-form :model="form" ref="form" :rules="FormRules">
            <div style="border: 1px solid #e6e6e6;margin-bottom: 10px;padding:15px;padding-bottom: 0px">
            <el-row :gutter="10">
                <el-col :span="3">
                    <el-form-item >
                        <el-select v-model="form.request4"  placeholder="请求方式">
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
                        <el-input v-model="form.addr" placeholder="地址" auto-complete></el-input>
                    </el-form-item>
                </el-col>
                <el-col :span='2'>
                    <el-button type="primary">发送</el-button>
                </el-col>
            </el-row>
            </div>
            <el-row :span="24">
                <el-collapse v-model="activeNames" @change="handleChange">
                    <el-collapse-item title="请求头部" name="1">
                        <el-table :data="form.head" highlight-current-row>
                            <el-table-column type="selection" min-width="5%" label="头部">
                            </el-table-column>
                            <el-table-column prop="name" label="标签" min-width="20%" sortable>
                                <template slot-scope="scope">
                                   <el-select placeholder="head标签" filterable v-model="scope.row.name">
                                       <el-option v-for="(item,index) in header" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                   </el-select>
                               </template>
                            </el-table-column>
                            <el-table-column prop="value" label="内容" min-width="40%" sortable>
                                <template slot-scope="scope">
                                   <el-input v-model="scope.row.value" :value="scope.row.value" placeholder="请输入内容"></el-input>
                               </template>
                            </el-table-column>
                            <el-table-column label="操作" min-width="10%">
                                <template slot-scope="scope">
                                    <i class="el-icon-delete" style="font-size:30px" @click="delHead(scope.$index)"></i>
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
                                <el-col :span="4"><el-radio v-model="radio" label="raw">源数据(raw)</el-radio></el-col>
                                <el-col :span="16"><el-checkbox v-model="radioType" label="3" v-show="ParameterTyep">表单转源数据</el-checkbox></el-col>
                            </el-row>
                        </div>
                        <el-table :data="form.parameter" highlight-current-row :class="ParameterTyep? 'parameter-a': 'parameter-b'">
                            <el-table-column type="selection" min-width="5%" label="头部">
                            </el-table-column>
                            <el-table-column prop="name" label="参数名" min-width="20%" sortable>
                                <template slot-scope="scope">
                                   <el-input v-model="scope.row.name" :value="scope.row.name" placeholder="请输入参数值"></el-input>
                               </template>
                            </el-table-column>
                            <el-table-column prop="value" label="参数值" min-width="40%" sortable>
                                <template slot-scope="scope">
                                   <el-input v-model="scope.row.value" :value="scope.row.value" placeholder="请输入参数值"></el-input>
                               </template>
                            </el-table-column>
                            <el-table-column label="操作" min-width="10%">
                                <template slot-scope="scope">
                                    <i class="el-icon-delete" style="font-size:30px" @click="delParameter(scope.$index)"></i>
                                </template>
                            </el-table-column>
                            <el-table-column label="" min-width="10%">
                                <template slot-scope="scope">
                                    <el-button v-if="scope.$index===(form.parameter.length-1)" size="mini" class="el-icon-plus" @click="addParameter"></el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                     <template>
                         <el-input :class="ParameterTyep? 'parameter-b': 'parameter-a'" type="textarea" :rows="5" placeholder="请输入内容" v-model="form.parameterRaw"></el-input>
                     </template>
                </el-collapse-item>
                <el-collapse-item title="响应结果" name="4">
                    <div style="margin-bottom: 10px">
                        <el-button>Body</el-button>
                        <el-button>Head</el-button>
                        <el-button type="primary">格式转换</el-button>
                    </div>
                    <el-card class="box-card">
                      <div slot="header" class="clearfix">
                        <span>200</span>
                      </div>
                        <div>{"code":"999999","msg":"成功","data":{"first_name":"李涛","last_name":"","phone":"18202886999","email":"daf@qq.com","key":"312b599e490d6d2ac20fbe66353d56f0de856180","date_joined":"2018-03-05 09:49:00"}}</div>
                    </el-card>
                </el-collapse-item>
            </el-collapse>
            </el-row>
        </el-form>
    </section>
</template>
<script>
import { test } from '../../../api/api'
import $ from 'jquery'
  export default {
    data() {
      return {
        request: [{value: 'get', label: 'GET'},
                    {value: 'post', label: 'POST'},
                    {value: 'put', label: 'PUT'},
                    {value: 'delete', label: 'DELETE'}],
        Http: [{value: 'http', label: 'HTTP'},
                {value: 'https', label: 'HTTPS'}],
        checkHeadList: [],
        checkParameterList: [],
        ParameterTyep: true,
        group: [],
        radio: "form-data",
        secondGroup: [],
        status: [{value: 'True', label: '启用'},
                    {value: 'False', label: '禁用'}],
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
        required4:[{value: 'True', label: '是'},
            {value: 'False', label: '否'}],
        httpCode:[{value: '200', label: '200'},
            {value: '404', label: '404'},
            {value: '400', label: '400'},
            {value: '500', label: '500'},
            {value: '502', label: '502'},
            {value: '302', label: '302'}],
        radioType: "",
        result: true,
        activeNames: ['1', '2', '3', '4'],
        id: "",
        form: {
            firstGroup: '',
            secondGroup: '',
            name: '',
            status: 'True',
            request4: 'GET',
            Http4: 'HTTP',
            addr: '',
            head: [{name: "", value: ""},
            {name: "", value: ""}],
            parameterRaw: "",
            parameter: [{name: "", value: "", required:"", restrict: "", description: ""},
            {name: "", value: "", required:"", restrict: "", description: ""}],
            parameterType: "",
            response: [{name: "", value: "", required:"", restrict: "", description: ""},
            {name: "", value: "", required:"", restrict: "", description: ""}],
            mockCode: '',
            mockData: '',
        },
        FormRules: {
            name : [{ required: true, message: '请输入名称', trigger: 'blur' }],
            addr : [{ required: true, message: '请输入地址', trigger: 'blur' }],
            required : [{ required: true, message: '请输入地址', trigger: 'blur' }],
            firstGroup : [{ required: true, message: '请选择父分组', trigger: 'blur'}],
            secondGroup : [{ required: true, message: '请选择父分组', trigger: 'blur'}]
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
        addApi: function () {
            this.$refs.form.validate((valid) => {
                if (valid) {
                    let self = this;
                    this.$confirm('确认提交吗？', '提示', {}).then(() => {
                        self.form.parameterType = self.radio;
                        let _type = self.form.parameterType;
                        let _parameter;
                        if ( _type === 'form-data') {
                            if ( self.radioType === '3') {
                                _type = 'raw'
                            }
                             _parameter = self.form.parameter;
                        } else {
                             _parameter = self.form.parameterRaw
                        }
                        $.ajax({
                            type: "post",
                            url: test+"/api/api/add_api",
                            async: true,
                            data: { project_id: self.$route.params.project_id,
                            first_group_id: self.form.firstGroup,
                            second_group_id: self.form.secondGroup,
                            name: self.form.name,
                            httpType: self.form.Http4,
                            requestType: self.form.request4,
                            address: self.form.addr,
                            status: self.form.status,
                            headDict: self.form.head,
                            requestParameterType: _type,
                            requestList: _parameter,
                            responseList: self.form.response,
                            mockStatus: self.form.mockCode,
                            code: self.form.mockData},
                            headers: {
                                Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                            },
                            timeout: 5000,
                            success: function(data) {
                                if (data.code === '999999') {
                                    self.$router.push({ name: "接口列表"});
                                    self.$message({
                                        message: '保存成功',
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
                    })
                }
            })
        },
        addHead() {
            let headers = {name: "", value: ""};
            this.form.head.push(headers)
        },
        delHead(index) {
            if (this.form.head.length !== 1) {
                this.form.head.splice(index, 1)
            }
        },
        addParameter() {
            let headers = {name: "", value: "", required:"True", restrict: "", description: ""};
            this.form.parameter.push(headers)
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
                this.ParameterTyep = !this.ParameterTyep
            } else {
                this.ParameterTyep = !this.ParameterTyep
            }
        },
        handleChange(val) {
      },
      onSubmit() {
        console.log('submit!');
      }
    },
    watch: {
        radio() {
            this.changeParameterType()
        }
    },
    mounted() {
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
</style>
